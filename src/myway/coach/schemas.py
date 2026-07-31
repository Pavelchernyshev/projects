"""JSON schemas for structured model output.

Both schemas are strict (`additionalProperties: false`, everything required) so
the API constrains the shape and the bot never has to defend against a missing
key at render time.
"""

from __future__ import annotations

DOMAIN_ENUM = ["time", "social", "mental", "physical", "financial"]

PROBE_SCHEMA = {
    "type": "object",
    "properties": {
        "enough_signal": {
            "type": "boolean",
            "description": (
                "True when the transcript already supports a specific, defensible "
                "diagnosis. False when a material ambiguity remains."
            ),
        },
        "question": {
            "type": "string",
            "description": (
                "One follow-up question in the user's language. Concrete and "
                "answerable in under a minute. Empty string if enough_signal is true."
            ),
        },
        "targets_domain": {
            "type": "string",
            "enum": DOMAIN_ENUM,
            "description": "Which domain this question is probing.",
        },
        "reading": {
            "type": "string",
            "description": (
                "Internal note: the current working hypothesis and what would "
                "falsify it. Never shown to the user."
            ),
        },
    },
    "required": ["enough_signal", "question", "targets_domain", "reading"],
    "additionalProperties": False,
}

ACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "if_then": {
            "type": "string",
            "description": (
                "The single action as an implementation intention: 'If <specific "
                "cue/time/place>, then I will <specific behaviour>.' Small enough "
                "to be done this week without rearranging their life."
            ),
        },
        "obstacle": {
            "type": "string",
            "description": (
                "The most likely specific thing that will stop them, named plainly."
            ),
        },
        "if_obstacle_then": {
            "type": "string",
            "description": "A second if-then covering that obstacle.",
        },
        "first_rep_when": {
            "type": "string",
            "description": "When the first repetition happens. A day and a time.",
        },
        "cadence": {
            "type": "string",
            "description": "How often it repeats, e.g. 'twice a week' or 'every weekday'.",
        },
        "measure": {
            "type": "string",
            "description": (
                "The observable signal that tells them it happened. Countable, "
                "not a feeling."
            ),
        },
    },
    "required": [
        "if_then",
        "obstacle",
        "if_obstacle_then",
        "first_rep_when",
        "cadence",
        "measure",
    ],
    "additionalProperties": False,
}

VERDICT_SCHEMA = {
    "type": "object",
    "properties": {
        "focus_domain": {
            "type": "string",
            "enum": DOMAIN_ENUM,
            "description": "The single domain to work on. Exactly one.",
        },
        "headline": {
            "type": "string",
            "description": (
                "The one thing to fix, in one sentence, in the user's own "
                "vocabulary. No hedging, no preamble."
            ),
        },
        "honest_read": {
            "type": "string",
            "description": (
                "Two to four sentences saying what is actually going on, "
                "including the part they have been talking around. Direct, "
                "specific to what they said, not cruel."
            ),
        },
        "why_this_one": {
            "type": "string",
            "description": (
                "Why this domain and not the others they raised — what it "
                "unblocks downstream."
            ),
        },
        "not_now": {
            "type": "array",
            "items": {"type": "string", "enum": DOMAIN_ENUM},
            "description": (
                "Domains explicitly deferred. Naming them is part of the "
                "product: it gives permission to drop them for now."
            ),
        },
        "citation_ids": {
            "type": "array",
            "items": {"type": "string"},
            "description": (
                "Between one and three ids copied EXACTLY from the evidence "
                "list supplied in this request. Never invent an id. Never cite "
                "a paper that is not on the list."
            ),
        },
        "action": ACTION_SCHEMA,
        "escalate_to_professional": {
            "type": "boolean",
            "description": (
                "True when the picture is clinical in shape — persistent low mood, "
                "possible substance dependence, any self-harm signal, or anything "
                "that needs a licensed professional rather than a coaching plan."
            ),
        },
        "escalation_note": {
            "type": "string",
            "description": (
                "If escalating: one or two sentences saying so plainly and without "
                "diagnosing. Empty string otherwise."
            ),
        },
    },
    "required": [
        "focus_domain",
        "headline",
        "honest_read",
        "why_this_one",
        "not_now",
        "citation_ids",
        "action",
        "escalate_to_professional",
        "escalation_note",
    ],
    "additionalProperties": False,
}
