"""Claude-backed coaching engine.

Two calls, both returning validated JSON via structured outputs:

* `next_probe` — one adaptive interview question, or "I have enough".
* `diagnose`   — the one-thing-to-fix verdict plus a grounded action.

Citation integrity is enforced here, not trusted: the model returns ids, this
module resolves them against the library and drops anything unknown.
"""

from __future__ import annotations

import json
import logging

import anthropic

from ..config import Config
from ..models import Session
from ..science import Library
from . import prompts
from .results import Probe, Verdict
from .schemas import PROBE_SCHEMA, VERDICT_SCHEMA

log = logging.getLogger(__name__)


class EngineError(RuntimeError):
    """The model call failed or came back unusable."""


class CoachEngine:
    def __init__(self, config: Config, library: Library) -> None:
        self._config = config
        self._library = library
        self._client = anthropic.Anthropic(api_key=config.anthropic_api_key)

    # --- interview ---------------------------------------------------------

    def next_probe(self, session: Session) -> Probe:
        cfg = self._config
        payload = self._structured_call(
            model=cfg.model_probe,
            effort=cfg.effort_probe,
            max_tokens=2000,
            system=prompts.system_prompt(cfg.product_name, session.lang),
            user=prompts.probe_prompt(
                session, cfg.min_probe_questions, cfg.max_probe_questions
            ),
            schema=PROBE_SCHEMA,
            schema_name="probe",
        )
        probe = Probe(
            enough_signal=bool(payload["enough_signal"]),
            question=payload["question"].strip(),
            targets_domain=payload["targets_domain"],
            reading=payload["reading"],
        )
        # Guard both directions: a model that claims it needs more but supplies no
        # question would stall the interview, and one that keeps asking past the
        # cap would never reach a verdict.
        if not probe.enough_signal and not probe.question:
            log.warning("probe returned no question without enough_signal; forcing stop")
            probe.enough_signal = True
        if session.probe_count >= cfg.max_probe_questions:
            probe.enough_signal = True
        elif session.probe_count < cfg.min_probe_questions and probe.question:
            probe.enough_signal = False
        return probe

    # --- verdict -----------------------------------------------------------

    def diagnose(self, session: Session) -> Verdict:
        cfg = self._config
        # Scope the evidence to the domains actually in play. The library always
        # appends the cross-cutting behaviour-change entries on top of these.
        domains = session.weakest_domains()[:3] or ["time", "mental", "physical"]
        evidence = self._library.as_prompt_context(domains)

        payload = self._structured_call(
            model=cfg.model_diagnosis,
            effort=cfg.effort_diagnosis,
            max_tokens=8000,
            system=prompts.system_prompt(cfg.product_name, session.lang),
            user=prompts.verdict_prompt(session, evidence),
            schema=VERDICT_SCHEMA,
            schema_name="verdict",
        )

        citations, unknown = self._library.resolve(payload["citation_ids"])
        if unknown:
            # Not fatal, but it means the prompt is drifting — worth an alert.
            log.error(
                "model produced %d citation id(s) not in the corpus: %s",
                len(unknown),
                unknown,
            )

        return Verdict(
            focus_domain=payload["focus_domain"],
            headline=payload["headline"].strip(),
            honest_read=payload["honest_read"].strip(),
            why_this_one=payload["why_this_one"].strip(),
            not_now=[d for d in payload["not_now"] if d != payload["focus_domain"]],
            citations=citations[:3],
            action=payload["action"],
            escalate_to_professional=bool(payload["escalate_to_professional"]),
            escalation_note=payload["escalation_note"].strip(),
            dropped_citation_ids=unknown,
        )

    # --- transport ---------------------------------------------------------

    def _structured_call(
        self,
        *,
        model: str,
        effort: str,
        max_tokens: int,
        system: str,
        user: str,
        schema: dict,
        schema_name: str,
    ) -> dict:
        try:
            response = self._client.messages.create(
                model=model,
                max_tokens=max_tokens,
                # The identity/evidence rules are byte-stable across every call,
                # so caching them is close to free after the first request.
                system=[
                    {
                        "type": "text",
                        "text": system,
                        "cache_control": {"type": "ephemeral"},
                    }
                ],
                output_config={
                    "effort": effort,
                    "format": {"type": "json_schema", "schema": schema},
                },
                messages=[{"role": "user", "content": user}],
            )
        except anthropic.APIStatusError as exc:
            raise EngineError(f"{schema_name} call failed ({exc.status_code})") from exc
        except anthropic.APIConnectionError as exc:
            raise EngineError(f"{schema_name} call could not reach the API") from exc

        if response.stop_reason == "refusal":
            raise EngineError(f"{schema_name} call was refused by safety classifiers")
        if response.stop_reason == "max_tokens":
            raise EngineError(f"{schema_name} call hit max_tokens before finishing")

        text = next((b.text for b in response.content if b.type == "text"), "")
        if not text:
            raise EngineError(f"{schema_name} call returned no text block")
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise EngineError(f"{schema_name} call returned invalid JSON") from exc
