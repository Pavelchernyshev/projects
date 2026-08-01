"""End-to-end interview walkthrough against fake Telegram objects.

The handlers only touch a small surface of the Telegram API, so stubbing it is
cheaper and far faster than a live bot — and it catches the routing and
state-transition bugs that unit tests on `Session` cannot.
"""

from __future__ import annotations

import pytest

from myway import bot
from myway.coach.results import Probe, Verdict
from myway.config import Config
from myway.db import Store
from myway.models import Domain, Lang, State
from myway.science import Library

# --- fakes -----------------------------------------------------------------


class FakeMessage:
    def __init__(self, text: str = "", voice=None) -> None:
        self.text = text
        self.voice = voice
        self.audio = None
        self.deleted = False

    async def delete(self) -> None:
        self.deleted = True


class FakeChat:
    def __init__(self) -> None:
        self.sent: list[str] = []
        self.keyboards: list[object] = []
        self.actions: list[str] = []

    async def send_message(self, text, parse_mode=None, reply_markup=None, **kwargs):
        self.sent.append(text)
        if reply_markup is not None:
            self.keyboards.append(reply_markup)
        return FakeMessage(text)

    async def send_action(self, action):
        self.actions.append(action)


class FakeUser:
    def __init__(self, user_id: int, language_code: str = "en") -> None:
        self.id = user_id
        self.language_code = language_code


class FakeQuery:
    def __init__(self, data: str) -> None:
        self.data = data
        self.answered = False
        self.edited: str | None = None

    async def answer(self) -> None:
        self.answered = True

    async def edit_message_text(self, text, parse_mode=None) -> None:
        self.edited = text


class FakeUpdate:
    def __init__(self, chat, user, text="", query=None) -> None:
        self.effective_chat = chat
        self.effective_user = user
        self.effective_message = FakeMessage(text)
        self.callback_query = query


class FakeApp:
    def __init__(self, deps) -> None:
        self.bot_data = {"deps": deps}


class FakeContext:
    def __init__(self, deps) -> None:
        self.application = FakeApp(deps)
        self.error = None


class StubEngine:
    """Scripted engine: N probe questions, then a fixed verdict."""

    def __init__(self, library: Library, questions: list[str]) -> None:
        self._library = library
        self._questions = list(questions)
        self.probe_calls = 0
        self.diagnose_calls = 0
        self.last_session = None

    def next_probe(self, session):
        self.probe_calls += 1
        self.last_session = session
        if self._questions:
            return Probe(
                enough_signal=False,
                question=self._questions.pop(0),
                targets_domain="mental",
                reading="working hypothesis: sleep",
            )
        return Probe(
            enough_signal=True, question="", targets_domain="mental", reading="done"
        )

    def diagnose(self, session):
        self.diagnose_calls += 1
        self.last_session = session
        return Verdict(
            focus_domain="mental",
            headline="Sleep is the bottleneck",
            honest_read="You described being tired four separate times.",
            why_this_one="Everything else you raised gets easier once you sleep.",
            not_now=["time", "financial"],
            citations=[self._library.get("mental.cappuccio2010")],
            action={
                "if_then": "If it is 23:30, then my phone goes on the kitchen counter.",
                "obstacle": "One more episode.",
                "if_obstacle_then": "If an episode is running, I stop it anyway.",
                "first_rep_when": "Tonight, 23:30",
                "cadence": "Every weeknight",
                "measure": "Nights counted on Sunday",
            },
            escalate_to_professional=False,
            escalation_note="",
        )


# --- fixtures --------------------------------------------------------------


@pytest.fixture
def config(tmp_path, monkeypatch) -> Config:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123:FAKE")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-fake")
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "t.db"))
    monkeypatch.setenv("STT_BACKEND", "none")
    monkeypatch.setenv("MIN_PROBE_QUESTIONS", "2")
    monkeypatch.setenv("MAX_PROBE_QUESTIONS", "4")
    monkeypatch.delenv("ALLOWLIST", raising=False)
    monkeypatch.delenv("DEFAULT_LANG", raising=False)  # exercise the ru default
    return Config.from_env()


@pytest.fixture
def harness(config):
    """A Deps object with a stubbed engine, plus the chat/user/context fakes."""
    library = Library()
    store = Store(config.database_path)
    deps = bot.Deps.__new__(bot.Deps)
    deps.config = config
    deps.store = store
    deps.library = library
    deps.engine = StubEngine(library, ["Question one?", "Question two?"])
    deps.transcriber = None  # voice is off in these tests

    chat = FakeChat()
    user = FakeUser(555)
    context = FakeContext(deps)
    yield deps, chat, user, context
    store.close()


def update_for(chat, user, text=""):
    return FakeUpdate(chat, user, text)


# --- the walkthrough -------------------------------------------------------


@pytest.mark.asyncio
async def test_full_interview_reaches_a_committed_plan(harness) -> None:
    deps, chat, user, context = harness

    await bot.cmd_start(update_for(chat, user), context)
    assert "Мой Путь" in chat.sent[0]

    await bot.cmd_begin(update_for(chat, user), context)
    session = deps.store.active_session(555)
    assert session.state is State.OPENING
    assert "никак не решаете" in chat.sent[-1]

    # Opening answer moves us to the pulse and offers the first rating keyboard.
    await bot.on_message(
        update_for(chat, user, "I keep meaning to fix my sleep and never do"), context
    )
    assert deps.store.active_session(555).state is State.PULSE
    assert len(chat.keyboards) == 1

    # Rate all five domains.
    for domain in Domain.ordered():
        score = 1 if domain is Domain.MENTAL else 4
        query = FakeQuery(f"p:{domain.value}:{score}")
        await bot.on_pulse(FakeUpdate(chat, user, query=query), context)
        assert query.answered
        assert f"{score}/5" in query.edited

    session = deps.store.active_session(555)
    assert session.pulse == {
        "time": 4, "social": 4, "mental": 1, "physical": 4, "financial": 4
    }
    # Completing the pulse should have kicked off the interview.
    assert session.state is State.PROBE
    assert deps.engine.probe_calls == 1
    assert "Question one?" in chat.sent[-1]

    # Two probe answers, then the stub reports it has enough signal.
    await bot.on_message(
        update_for(chat, user, "I go to bed after 2am most nights"), context
    )
    assert "Question two?" in chat.sent[-1]
    await bot.on_message(
        update_for(chat, user, "Because that is my only quiet time"), context
    )

    assert deps.engine.diagnose_calls == 1
    transcript = "\n".join(chat.sent)
    assert "Sleep is the bottleneck" in transcript
    assert "kitchen counter" in transcript
    assert "Cappuccio" in transcript
    assert deps.store.active_session(555).state is State.COMMIT

    # Accepting closes the session and records the commitment.
    await bot.on_message(update_for(chat, user, "yes"), context)
    assert deps.store.active_session(555) is None
    commitments = deps.store.past_commitments(555)
    assert commitments[0]["accepted"] is True
    assert "kitchen counter" in commitments[0]["action"]["if_then"]


@pytest.mark.asyncio
async def test_declining_the_plan_is_recorded_as_a_decline(harness) -> None:
    deps, chat, user, context = harness
    session = deps.store.create_session(555, Lang.RU)
    session.state = State.COMMIT
    session.verdict = {"action": {"if_then": "something"}}
    deps.store.save_session(session)

    await bot.on_message(
        update_for(chat, user, "No, 23:30 is not realistic for me"), context
    )

    commitment = deps.store.past_commitments(555)[0]
    assert commitment["accepted"] is False
    assert "not realistic" in commitment["user_note"]


@pytest.mark.asyncio
async def test_short_answers_are_rejected_without_advancing(harness) -> None:
    deps, chat, user, context = harness
    await bot.cmd_begin(update_for(chat, user), context)

    await bot.on_message(update_for(chat, user, "dunno"), context)

    assert "не поработать" in chat.sent[-1]
    assert deps.store.active_session(555).state is State.OPENING


@pytest.mark.asyncio
async def test_crisis_language_halts_the_session_before_any_model_call(harness) -> None:
    deps, chat, user, context = harness
    await bot.cmd_begin(update_for(chat, user), context)

    await bot.on_message(
        update_for(chat, user, "honestly I have been thinking about killing myself"),
        context,
    )

    assert "findahelpline.com" in chat.sent[-1]
    assert deps.store.active_session(555) is None
    assert deps.engine.probe_calls == 0
    assert deps.engine.diagnose_calls == 0


@pytest.mark.asyncio
async def test_messages_outside_a_session_prompt_to_begin(harness) -> None:
    deps, chat, user, context = harness

    await bot.on_message(
        update_for(chat, user, "here is a long thought about life"), context
    )

    assert "/begin" in chat.sent[-1]


@pytest.mark.asyncio
async def test_probe_cap_forces_a_verdict(config) -> None:
    """A model that keeps asking must still be cut off at MAX_PROBE_QUESTIONS."""
    library = Library()
    store = Store(config.database_path)
    deps = bot.Deps.__new__(bot.Deps)
    deps.config = config
    deps.store = store
    deps.library = library
    deps.engine = StubEngine(library, [f"Question {i}?" for i in range(20)])
    deps.transcriber = None

    chat, user, context = FakeChat(), FakeUser(777), FakeContext(deps)
    session = store.create_session(777, Lang.RU)
    session.state = State.PROBE
    session.pulse = {d.value: 3 for d in Domain.ordered()}
    session.probe_count = config.max_probe_questions
    store.save_session(session)

    await bot.on_message(
        update_for(chat, user, "another reasonably long answer about my week"), context
    )

    assert deps.engine.diagnose_calls == 1
    store.close()


@pytest.mark.asyncio
async def test_double_tapping_a_rating_does_not_overwrite_it(harness) -> None:
    deps, chat, user, context = harness
    session = deps.store.create_session(555, Lang.RU)
    session.state = State.PULSE
    deps.store.save_session(session)

    await bot.on_pulse(FakeUpdate(chat, user, query=FakeQuery("p:time:2")), context)
    await bot.on_pulse(FakeUpdate(chat, user, query=FakeQuery("p:time:5")), context)

    assert deps.store.active_session(555).pulse["time"] == 2


@pytest.mark.asyncio
async def test_lang_switch_applies_to_the_running_session(harness) -> None:
    deps, chat, user, context = harness
    await bot.cmd_begin(update_for(chat, user), context)

    await bot.cmd_lang(update_for(chat, user), context)

    assert deps.store.get_user_lang(555) is Lang.EN
    assert deps.store.active_session(555).lang is Lang.EN


@pytest.mark.asyncio
async def test_begin_replaces_an_abandoned_interview(harness) -> None:
    deps, chat, user, context = harness
    await bot.cmd_begin(update_for(chat, user), context)
    first = deps.store.active_session(555).id

    await bot.cmd_begin(update_for(chat, user), context)
    second = deps.store.active_session(555)

    assert second.id != first
    assert second.state is State.OPENING


@pytest.mark.asyncio
async def test_allowlist_blocks_unlisted_users(config, monkeypatch) -> None:
    monkeypatch.setenv("ALLOWLIST", "999")
    gated = Config.from_env()
    store = Store(gated.database_path)
    deps = bot.Deps.__new__(bot.Deps)
    deps.config = gated
    deps.store = store
    deps.library = Library()
    deps.engine = StubEngine(deps.library, [])
    deps.transcriber = None

    chat, context = FakeChat(), FakeContext(deps)
    await bot.cmd_begin(update_for(chat, FakeUser(555)), context)

    assert "приватный" in chat.sent[-1]
    assert store.active_session(555) is None
    store.close()


@pytest.mark.asyncio
async def test_voice_is_refused_politely_when_stt_is_off(harness) -> None:
    deps, chat, user, context = harness
    deps.transcriber = bot.transcribe.DisabledTranscriber()
    await bot.cmd_begin(update_for(chat, user), context)

    update = update_for(chat, user)
    update.effective_message.voice = object()
    await bot.on_message(update, context)

    assert "отключены" in chat.sent[-1]
    assert deps.store.active_session(555).state is State.OPENING
