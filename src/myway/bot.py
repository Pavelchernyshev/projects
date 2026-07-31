"""Telegram front end.

The interview is a small explicit state machine:

    OPENING → PULSE → PROBE ⟳ → VERDICT → COMMIT → (closed)

State lives in SQLite rather than in memory, so a restart mid-interview resumes
where the person left off instead of losing their answers.
"""

from __future__ import annotations

import asyncio
import logging
import tempfile
from pathlib import Path

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.constants import ChatAction, ParseMode
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from . import language, render, safety, transcribe
from .coach import CoachEngine, EngineError
from .config import Config
from .db import Store
from .i18n import DOMAIN_ICON, domain_hint, domain_label, state_label, t
from .models import Domain, Lang, Session, State, Turn
from .science import Library
from .transcribe import TranscriptionError

log = logging.getLogger(__name__)

MIN_ANSWER_CHARS = 15
AFFIRMATIVE = {
    "yes", "y", "ok", "okay", "sure", "deal", "done", "agreed", "i will",
    "да", "ага", "хорошо", "ок", "окей", "согласен", "согласна", "буду",
}


class Deps:
    """Everything the handlers need, hung off `application.bot_data`."""

    def __init__(self, config: Config, store: Store, library: Library) -> None:
        self.config = config
        self.store = store
        self.library = library
        self.engine = CoachEngine(config, library)
        self.transcriber = transcribe.build(config)


def _deps(context: ContextTypes.DEFAULT_TYPE) -> Deps:
    return context.application.bot_data["deps"]


# --- helpers ---------------------------------------------------------------


async def _send(update: Update, text: str) -> None:
    await update.effective_chat.send_message(
        text, parse_mode=ParseMode.HTML, disable_web_page_preview=True
    )


async def _typing(update: Update) -> None:
    await update.effective_chat.send_action(ChatAction.TYPING)


def _lang(deps: Deps, user_id: int, fallback_text: str = "") -> Lang:
    stored = deps.store.get_user_lang(user_id)
    if stored is not None:
        return stored
    detected = language.detect(fallback_text)
    deps.store.upsert_user(user_id, detected)
    return detected


def _allowed(deps: Deps, user_id: int) -> bool:
    return not deps.config.allowlist or user_id in deps.config.allowlist


def _pulse_keyboard(domain: Domain) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(str(n), callback_data=f"p:{domain.value}:{n}")
                for n in range(1, 6)
            ]
        ]
    )


# --- commands --------------------------------------------------------------


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    deps = _deps(context)
    user_id = update.effective_user.id
    if not _allowed(deps, user_id):
        await _send(update, t("not_allowed", Lang.EN))
        return
    lang = _lang(deps, user_id, update.effective_user.language_code or "")
    if (update.effective_user.language_code or "").startswith("ru"):
        lang = Lang.RU
        deps.store.set_user_lang(user_id, lang)
    await _send(update, t("greeting", lang, product=deps.config.product_name))


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    deps = _deps(context)
    await _send(update, t("help", _lang(deps, update.effective_user.id)))


async def cmd_about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    deps = _deps(context)
    lang = _lang(deps, update.effective_user.id)
    await _send(update, t("about", lang, product=deps.config.product_name))


async def cmd_sources(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    deps = _deps(context)
    lang = _lang(deps, update.effective_user.id)
    for message in render.sources_messages(deps.library, lang):
        await _send(update, message)


async def cmd_lang(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    deps = _deps(context)
    user_id = update.effective_user.id
    current = _lang(deps, user_id)
    new = Lang.EN if current is Lang.RU else Lang.RU
    deps.store.set_user_lang(user_id, new)
    session = deps.store.active_session(user_id)
    if session:
        session.lang = new
        deps.store.save_session(session)
    await _send(update, t("lang_switched", new))


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    deps = _deps(context)
    user_id = update.effective_user.id
    lang = _lang(deps, user_id)
    session = deps.store.active_session(user_id)
    if session is None:
        await _send(update, t("no_session", lang))
        return
    answers = sum(1 for turn in session.transcript if turn.role == "user")
    await _send(
        update,
        t(
            "status",
            lang,
            state=state_label(session.state.value, lang),
            answers=answers,
        ),
    )


async def cmd_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    deps = _deps(context)
    user_id = update.effective_user.id
    lang = _lang(deps, user_id)
    session = deps.store.active_session(user_id)
    if session is None:
        await _send(update, t("no_session", lang))
        return
    deps.store.close_session(session.id)
    await _send(update, t("cancelled", lang))


async def cmd_forget(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    deps = _deps(context)
    user_id = update.effective_user.id
    lang = _lang(deps, user_id)
    count = deps.store.delete_user_data(user_id)
    await _send(update, t("forgotten", lang, count=count))


async def cmd_begin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    deps = _deps(context)
    user_id = update.effective_user.id
    if not _allowed(deps, user_id):
        await _send(update, t("not_allowed", Lang.EN))
        return
    lang = _lang(deps, user_id)

    existing = deps.store.active_session(user_id)
    if existing is not None:
        deps.store.close_session(existing.id)

    session = deps.store.create_session(user_id, lang)
    question = t("opening_question", lang)
    deps.store.add_turn(session.id, Turn(role="coach", text=question))
    await _send(update, question)


# --- pulse callbacks -------------------------------------------------------


async def on_pulse(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    deps = _deps(context)
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    session = deps.store.active_session(user_id)
    if session is None or session.state is not State.PULSE:
        return

    _, domain_value, score_raw = query.data.split(":")
    if domain_value in session.pulse:
        return  # double tap; the rating is already in
    session.pulse[domain_value] = int(score_raw)

    domain = Domain(domain_value)
    lang = session.lang
    await query.edit_message_text(
        f"{DOMAIN_ICON[domain]} <b>{render.esc(domain_label(domain, lang))}</b> — "
        f"{score_raw}/5",
        parse_mode=ParseMode.HTML,
    )

    pending = session.pending_pulse_domain()
    if pending is not None:
        deps.store.save_session(session)
        await _ask_pulse(update, pending, lang)
        return

    session.state = State.PROBE
    session.focus_domain = session.weakest_domains()[0]
    deps.store.save_session(session)
    await _send(update, t("pulse_done", lang))
    await _ask_next_probe(update, deps, session)


async def _ask_pulse(update: Update, domain: Domain, lang: Lang) -> None:
    await update.effective_chat.send_message(
        t(
            "pulse_prompt",
            lang,
            icon=DOMAIN_ICON[domain],
            domain=render.esc(domain_label(domain, lang)),
            hint=render.esc(domain_hint(domain, lang)),
        ),
        parse_mode=ParseMode.HTML,
        reply_markup=_pulse_keyboard(domain),
    )


# --- message routing -------------------------------------------------------


async def on_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    deps = _deps(context)
    user_id = update.effective_user.id
    if not _allowed(deps, user_id):
        await _send(update, t("not_allowed", Lang.EN))
        return

    message = update.effective_message
    if message.voice or message.audio:
        text = await _transcribe_message(update, deps)
        kind = "voice"
        if text is None:
            return
    else:
        text = (message.text or "").strip()
        kind = "text"

    lang = _lang(deps, user_id, text)

    if safety.is_crisis(text):
        log.warning("crisis keyword matched for user %s; halting session", user_id)
        session = deps.store.active_session(user_id)
        if session is not None:
            deps.store.close_session(session.id)
        await _send(update, t("crisis", lang))
        return

    session = deps.store.active_session(user_id)
    if session is None:
        await _send(update, t("no_session", lang))
        return

    if session.state is State.OPENING:
        await _handle_opening(update, deps, session, text, kind)
    elif session.state is State.PULSE:
        pending = session.pending_pulse_domain()
        if pending is not None:
            await _ask_pulse(update, pending, session.lang)
    elif session.state is State.PROBE:
        await _handle_probe_answer(update, deps, session, text, kind)
    elif session.state is State.VERDICT:
        await _deliver_verdict(update, deps, session)
    elif session.state is State.COMMIT:
        await _handle_commitment(update, deps, session, text)


async def _transcribe_message(update: Update, deps: Deps) -> str | None:
    lang = _lang(deps, update.effective_user.id)
    if not deps.transcriber.enabled:
        await _send(update, t("voice_unsupported", lang))
        return None

    await _typing(update)
    note = await update.effective_chat.send_message(t("transcribing", lang))
    voice = update.effective_message.voice or update.effective_message.audio
    tg_file = await voice.get_file()

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "note.ogg"
        await tg_file.download_to_drive(custom_path=path)
        try:
            text = await deps.transcriber.transcribe(path, lang)
        except TranscriptionError as exc:
            log.warning("transcription failed: %s", exc)
            await note.delete()
            await _send(update, t("transcribe_failed", lang))
            return None

    await note.delete()
    if not text:
        await _send(update, t("transcribe_failed", lang))
        return None
    return text


# --- state handlers --------------------------------------------------------


async def _handle_opening(
    update: Update, deps: Deps, session: Session, text: str, kind: str
) -> None:
    if len(text) < MIN_ANSWER_CHARS:
        await _send(update, t("too_short", session.lang))
        return

    deps.store.add_turn(session.id, Turn(role="user", text=text, kind=kind))
    session.transcript.append(Turn(role="user", text=text, kind=kind))
    session.state = State.PULSE
    deps.store.save_session(session)

    await _send(update, t("pulse_intro", session.lang))
    pending = session.pending_pulse_domain()
    assert pending is not None  # a fresh session has no ratings yet
    await _ask_pulse(update, pending, session.lang)


async def _handle_probe_answer(
    update: Update, deps: Deps, session: Session, text: str, kind: str
) -> None:
    if len(text) < MIN_ANSWER_CHARS:
        await _send(update, t("too_short", session.lang))
        return

    turn = Turn(role="user", text=text, kind=kind, domain=session.focus_domain)
    deps.store.add_turn(session.id, turn)
    session.transcript.append(turn)
    deps.store.save_session(session)

    await _ask_next_probe(update, deps, session)


async def _ask_next_probe(update: Update, deps: Deps, session: Session) -> None:
    # Guard the loop here as well as in the engine: this is where the cycle
    # actually lives, and stopping early also saves a pointless API call.
    if session.probe_count >= deps.config.max_probe_questions:
        session.state = State.VERDICT
        deps.store.save_session(session)
        await _deliver_verdict(update, deps, session)
        return

    await _typing(update)
    try:
        probe = await asyncio.to_thread(deps.engine.next_probe, session)
    except EngineError as exc:
        log.error("probe failed: %s", exc)
        await _send(update, t("engine_error", session.lang))
        return

    if probe.enough_signal:
        session.state = State.VERDICT
        deps.store.save_session(session)
        await _deliver_verdict(update, deps, session)
        return

    log.debug("probe reading: %s", probe.reading)
    session.probe_count += 1
    session.focus_domain = probe.targets_domain
    turn = Turn(role="coach", text=probe.question, domain=probe.targets_domain)
    deps.store.add_turn(session.id, turn)
    session.transcript.append(turn)
    deps.store.save_session(session)

    await _send(update, render.esc(probe.question))


async def _deliver_verdict(update: Update, deps: Deps, session: Session) -> None:
    lang = session.lang
    await _send(update, t("thinking", lang))
    await _typing(update)

    try:
        verdict = await asyncio.to_thread(deps.engine.diagnose, session)
    except EngineError as exc:
        log.error("diagnosis failed: %s", exc)
        await _send(update, t("engine_error", lang))
        return

    session.verdict = verdict.to_json()
    session.focus_domain = verdict.focus_domain
    session.state = State.COMMIT
    deps.store.save_session(session)
    deps.store.add_turn(
        session.id,
        Turn(role="coach", text=verdict.headline, domain=verdict.focus_domain),
    )

    for message in render.verdict_messages(verdict, lang):
        await _send(update, message)
    await _send(update, t("commit_prompt", lang))


async def _handle_commitment(
    update: Update, deps: Deps, session: Session, text: str
) -> None:
    accepted = text.strip().lower().rstrip(".!") in AFFIRMATIVE
    session.commitment = {
        "action": (session.verdict or {}).get("action", {}),
        "accepted": accepted,
        "user_note": "" if accepted else text,
    }
    deps.store.add_turn(session.id, Turn(role="user", text=text))
    deps.store.save_session(session)
    deps.store.close_session(session.id)
    await _send(update, t("committed", session.lang))


# --- errors ----------------------------------------------------------------


async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    log.exception("unhandled error", exc_info=context.error)
    if isinstance(update, Update) and update.effective_chat:
        try:
            deps = _deps(context)
            lang = (
                _lang(deps, update.effective_user.id)
                if update.effective_user
                else Lang.EN
            )
            await update.effective_chat.send_message(t("engine_error", lang))
        except Exception:  # noqa: BLE001 - never let the handler itself raise
            log.exception("failed to report error to the user")


# --- wiring ----------------------------------------------------------------


def build_application(config: Config) -> Application:
    library = Library()
    unverified = library.unverified()
    if unverified:
        log.warning(
            "%d of %d citations are not marked verified: run "
            "scripts/verify_corpus.py and set verified: true before launch",
            len(unverified),
            len(library),
        )

    store = Store(config.database_path)
    deps = Deps(config, store, library)

    app = Application.builder().token(config.telegram_token).build()
    app.bot_data["deps"] = deps

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("about", cmd_about))
    app.add_handler(CommandHandler("sources", cmd_sources))
    app.add_handler(CommandHandler("lang", cmd_lang))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("cancel", cmd_cancel))
    app.add_handler(CommandHandler("forget", cmd_forget))
    app.add_handler(CommandHandler("begin", cmd_begin))
    app.add_handler(CallbackQueryHandler(on_pulse, pattern=r"^p:"))
    app.add_handler(
        MessageHandler(
            (filters.TEXT & ~filters.COMMAND) | filters.VOICE | filters.AUDIO,
            on_message,
        )
    )
    app.add_error_handler(on_error)
    return app
