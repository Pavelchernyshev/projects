"""Turn engine output into Telegram-ready HTML.

Everything the model wrote goes through `esc()`. Only our own templates and tags
are allowed to contain markup, which keeps a stray `<` in a user's answer from
breaking the whole message.
"""

from __future__ import annotations

from html import escape

from .i18n import DOMAIN_ICON, domain_label, t
from .models import Citation, Domain, Lang
from .science import Library

MAX_MESSAGE = 4096


def esc(text: str) -> str:
    return escape(text or "", quote=False)


def verdict_messages(verdict, lang: Lang) -> list[str]:
    """Render a verdict as an ordered list of messages.

    Split into several deliberately: the diagnosis, the plan, and the evidence
    each want to be read on their own rather than as one wall of text.
    """
    focus = Domain(verdict.focus_domain)
    icon = DOMAIN_ICON[focus]

    diagnosis = [
        f"{t('verdict_header', lang)} — {icon} {esc(domain_label(focus, lang))}",
        "",
        f"<b>{esc(verdict.headline)}</b>",
        "",
        esc(verdict.honest_read),
        "",
        t("verdict_why", lang),
        esc(verdict.why_this_one),
    ]
    if verdict.not_now:
        deferred = ", ".join(
            domain_label(Domain(d), lang) for d in verdict.not_now
        )
        diagnosis += ["", t("verdict_notnow", lang, domains=esc(deferred))]

    action = verdict.action
    plan = [
        t("verdict_action", lang),
        "",
        f"→ {esc(action['if_then'])}",
        "",
        f"<b>{esc(action['first_rep_when'])}</b> · {esc(action['cadence'])}",
        f"✓ {esc(action['measure'])}",
        "",
        f"⚠ {esc(action['obstacle'])}",
        f"→ {esc(action['if_obstacle_then'])}",
    ]

    messages = ["\n".join(diagnosis)]
    if verdict.escalate_to_professional:
        note = t("escalation", lang)
        if verdict.escalation_note:
            note = f"{esc(verdict.escalation_note)}\n\n{note}"
        messages.append(note)
    messages.append("\n".join(plan))

    if verdict.citations:
        messages.append(citations_block(verdict.citations, lang))

    return [_clip(m) for m in messages]


def citations_block(citations: list[Citation], lang: Lang) -> str:
    lines = [t("verdict_evidence", lang), ""]
    for citation in citations:
        finding = citation.finding_ru if lang is Lang.RU else citation.finding_en
        lines.append(esc(finding))
        lines.append(f"<i>{esc(citation.reference())}</i>")
        if citation.design:
            lines.append(f"<i>{esc(citation.design)}</i>")
        lines.append("")
    lines.append(f"<i>{esc(t('evidence_caveat', lang))}</i>")
    return _clip("\n".join(lines))


def sources_messages(library: Library, lang: Lang) -> list[str]:
    """The whole library, chunked to fit Telegram's message limit."""
    header = t("sources_header", lang, count=len(library))
    blocks: list[str] = []
    for domain in [*[d.value for d in Domain.ordered()], "cross_cutting"]:
        citations = library.for_domain(domain)
        if not citations:
            continue
        title = (
            domain_label(Domain(domain), lang)
            if domain != "cross_cutting"
            else ("Изменение поведения" if lang is Lang.RU else "Behaviour change")
        )
        chunk = [f"<b>{esc(title)}</b>"]
        for citation in citations:
            flag = "" if citation.verified else " ⚠"
            chunk.append(f"• <i>{esc(citation.reference())}</i>{flag}")
        blocks.append("\n".join(chunk))

    messages: list[str] = []
    current = header
    for block in blocks:
        candidate = f"{current}\n\n{block}" if current else block
        if len(candidate) > MAX_MESSAGE - 200:
            messages.append(current)
            current = block
        else:
            current = candidate
    if current:
        messages.append(current)
    return messages


def _clip(text: str) -> str:
    if len(text) <= MAX_MESSAGE:
        return text
    return text[: MAX_MESSAGE - 1] + "…"
