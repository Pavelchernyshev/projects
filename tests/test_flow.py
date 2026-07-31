"""Tests for interview state, storage round-tripping, and citation integrity."""

from __future__ import annotations

import pytest

from myway.db import Store
from myway.models import Domain, Lang, Session, State, Turn


@pytest.fixture
def store(tmp_path) -> Store:
    store = Store(tmp_path / "test.db")
    yield store
    store.close()


# --- pulse / focus selection ----------------------------------------------


def test_pulse_is_asked_in_canonical_order() -> None:
    session = Session(id=1, user_id=1)
    asked = []
    while (pending := session.pending_pulse_domain()) is not None:
        asked.append(pending)
        session.pulse[pending.value] = 3

    assert asked == Domain.ordered()
    assert session.pending_pulse_domain() is None


def test_weakest_domains_are_ordered_worst_first() -> None:
    session = Session(
        id=1,
        user_id=1,
        pulse={"time": 2, "social": 5, "mental": 1, "physical": 4, "financial": 3},
    )

    assert session.weakest_domains() == [
        "mental",
        "time",
        "financial",
        "physical",
        "social",
    ]


def test_ties_fall_back_to_canonical_order() -> None:
    session = Session(
        id=1,
        user_id=1,
        pulse={"time": 2, "social": 2, "mental": 2, "physical": 5, "financial": 5},
    )

    assert session.weakest_domains()[:3] == ["time", "social", "mental"]


# --- persistence -----------------------------------------------------------


def test_session_survives_a_round_trip(store: Store) -> None:
    store.upsert_user(42, Lang.RU)
    session = store.create_session(42, Lang.RU)

    session.pulse = {"time": 2, "mental": 1}
    session.focus_domain = "mental"
    session.probe_count = 3
    session.state = State.PROBE
    session.verdict = {"headline": "Sleep is the bottleneck"}
    store.save_session(session)
    store.add_turn(session.id, Turn(role="coach", text="What happened last night?"))
    store.add_turn(session.id, Turn(role="user", text="I was up until 3", kind="voice"))

    loaded = store.active_session(42)

    assert loaded.id == session.id
    assert loaded.state is State.PROBE
    assert loaded.lang is Lang.RU
    assert loaded.pulse == {"time": 2, "mental": 1}
    assert loaded.focus_domain == "mental"
    assert loaded.probe_count == 3
    assert loaded.verdict["headline"] == "Sleep is the bottleneck"
    assert [turn.role for turn in loaded.transcript] == ["coach", "user"]
    assert loaded.transcript[1].kind == "voice"


def test_closed_sessions_are_not_returned_as_active(store: Store) -> None:
    store.upsert_user(42, Lang.EN)
    session = store.create_session(42, Lang.EN)
    store.close_session(session.id)

    assert store.active_session(42) is None


def test_begin_starts_a_fresh_session(store: Store) -> None:
    store.upsert_user(42, Lang.EN)
    first = store.create_session(42, Lang.EN)
    store.close_session(first.id)
    second = store.create_session(42, Lang.EN)

    active = store.active_session(42)
    assert active.id == second.id
    assert active.id != first.id
    assert active.state is State.OPENING


def test_language_preference_persists_across_sessions(store: Store) -> None:
    store.upsert_user(7, Lang.EN)
    store.set_user_lang(7, Lang.RU)

    assert store.get_user_lang(7) is Lang.RU


def test_upsert_does_not_clobber_a_chosen_language(store: Store) -> None:
    """A returning user's /lang choice must outlive their next message."""
    store.upsert_user(7, Lang.EN)
    store.set_user_lang(7, Lang.RU)
    store.upsert_user(7, Lang.EN)

    assert store.get_user_lang(7) is Lang.RU


def test_forget_removes_everything_for_that_user_only(store: Store) -> None:
    store.upsert_user(1, Lang.EN)
    store.upsert_user(2, Lang.EN)
    keep = store.create_session(2, Lang.EN)
    store.add_turn(keep.id, Turn(role="user", text="keep me"))
    drop = store.create_session(1, Lang.EN)
    store.add_turn(drop.id, Turn(role="user", text="delete me"))

    removed = store.delete_user_data(1)

    assert removed == 1
    assert store.get_user_lang(1) is None
    assert store.active_session(1) is None
    assert store.get_user_lang(2) is Lang.EN
    assert store.active_session(2).transcript[0].text == "keep me"


def test_past_commitments_are_returned_newest_first(store: Store) -> None:
    store.upsert_user(9, Lang.EN)
    for headline in ("first", "second"):
        session = store.create_session(9, Lang.EN)
        session.commitment = {"action": {"if_then": headline}, "accepted": True}
        session.focus_domain = "time"
        store.save_session(session)
        store.close_session(session.id)

    commitments = store.past_commitments(9)

    assert [c["action"]["if_then"] for c in commitments] == ["second", "first"]
    assert commitments[0]["focus_domain"] == "time"
