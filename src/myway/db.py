"""SQLite persistence.

Deliberately stdlib-only: the schema is small, and keeping it plain SQL makes
the Postgres swap (for multi-instance deploys) a mechanical change rather than
an ORM migration.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from .models import Lang, Session, State, Turn

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    telegram_id   INTEGER PRIMARY KEY,
    lang          TEXT    NOT NULL DEFAULT 'en',
    created_at    TEXT    NOT NULL,
    last_seen_at  TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER NOT NULL REFERENCES users(telegram_id),
    state         TEXT    NOT NULL,
    lang          TEXT    NOT NULL,
    pulse         TEXT    NOT NULL DEFAULT '{}',
    focus_domain  TEXT,
    probe_count   INTEGER NOT NULL DEFAULT 0,
    verdict       TEXT,
    commitment    TEXT,
    created_at    TEXT    NOT NULL,
    updated_at    TEXT    NOT NULL,
    closed_at     TEXT
);

CREATE TABLE IF NOT EXISTS turns (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id  INTEGER NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    role        TEXT    NOT NULL,
    kind        TEXT    NOT NULL DEFAULT 'text',
    domain      TEXT,
    text        TEXT    NOT NULL,
    created_at  TEXT    NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_turns_session ON turns(session_id, id);
CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id, id);
"""


def _now() -> str:
    return datetime.now(UTC).isoformat()


class Store:
    def __init__(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA foreign_keys=ON")
        self._conn.executescript(SCHEMA)
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    # --- users -------------------------------------------------------------

    def upsert_user(self, telegram_id: int, lang: Lang) -> None:
        now = _now()
        self._conn.execute(
            """
            INSERT INTO users (telegram_id, lang, created_at, last_seen_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(telegram_id) DO UPDATE SET last_seen_at = excluded.last_seen_at
            """,
            (telegram_id, lang.value, now, now),
        )
        self._conn.commit()

    def get_user_lang(self, telegram_id: int) -> Lang | None:
        row = self._conn.execute(
            "SELECT lang FROM users WHERE telegram_id = ?", (telegram_id,)
        ).fetchone()
        return Lang(row["lang"]) if row else None

    def set_user_lang(self, telegram_id: int, lang: Lang) -> None:
        self._conn.execute(
            "UPDATE users SET lang = ?, last_seen_at = ? WHERE telegram_id = ?",
            (lang.value, _now(), telegram_id),
        )
        self._conn.commit()

    # --- sessions ----------------------------------------------------------

    def create_session(self, user_id: int, lang: Lang) -> Session:
        # A session cannot exist without its user, so guarantee the row rather
        # than making every caller remember to upsert first. upsert_user never
        # overwrites an existing language preference.
        self.upsert_user(user_id, lang)
        now = _now()
        cur = self._conn.execute(
            """
            INSERT INTO sessions (user_id, state, lang, pulse, created_at, updated_at)
            VALUES (?, ?, ?, '{}', ?, ?)
            """,
            (user_id, State.OPENING.value, lang.value, now, now),
        )
        self._conn.commit()
        return Session(
            id=cur.lastrowid, user_id=user_id, state=State.OPENING, lang=lang
        )

    def active_session(self, user_id: int) -> Session | None:
        row = self._conn.execute(
            """
            SELECT * FROM sessions
            WHERE user_id = ? AND closed_at IS NULL
            ORDER BY id DESC LIMIT 1
            """,
            (user_id,),
        ).fetchone()
        if row is None:
            return None
        session = Session(
            id=row["id"],
            user_id=row["user_id"],
            state=State(row["state"]),
            lang=Lang(row["lang"]),
            pulse=json.loads(row["pulse"]),
            focus_domain=row["focus_domain"],
            probe_count=row["probe_count"],
            verdict=json.loads(row["verdict"]) if row["verdict"] else None,
            commitment=json.loads(row["commitment"]) if row["commitment"] else None,
        )
        session.transcript = self.load_turns(session.id)
        return session

    def save_session(self, session: Session) -> None:
        if session.id is None:
            raise ValueError("cannot save a session without an id")
        self._conn.execute(
            """
            UPDATE sessions SET
                state = ?, lang = ?, pulse = ?, focus_domain = ?,
                probe_count = ?, verdict = ?, commitment = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                session.state.value,
                session.lang.value,
                json.dumps(session.pulse),
                session.focus_domain,
                session.probe_count,
                json.dumps(session.verdict) if session.verdict else None,
                json.dumps(session.commitment) if session.commitment else None,
                _now(),
                session.id,
            ),
        )
        self._conn.commit()

    def close_session(self, session_id: int) -> None:
        self._conn.execute(
            "UPDATE sessions SET closed_at = ?, state = ?, updated_at = ? WHERE id = ?",
            (_now(), State.IDLE.value, _now(), session_id),
        )
        self._conn.commit()

    def past_commitments(self, user_id: int, limit: int = 5) -> list[dict]:
        rows = self._conn.execute(
            """
            SELECT commitment, focus_domain, created_at FROM sessions
            WHERE user_id = ? AND commitment IS NOT NULL
            ORDER BY id DESC LIMIT ?
            """,
            (user_id, limit),
        ).fetchall()
        out = []
        for row in rows:
            entry = json.loads(row["commitment"])
            entry["focus_domain"] = row["focus_domain"]
            entry["created_at"] = row["created_at"]
            out.append(entry)
        return out

    # --- turns -------------------------------------------------------------

    def add_turn(self, session_id: int, turn: Turn) -> None:
        self._conn.execute(
            """
            INSERT INTO turns (session_id, role, kind, domain, text, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (session_id, turn.role, turn.kind, turn.domain, turn.text, _now()),
        )
        self._conn.commit()

    def load_turns(self, session_id: int) -> list[Turn]:
        rows = self._conn.execute(
            "SELECT role, kind, domain, text, created_at FROM turns "
            "WHERE session_id = ? ORDER BY id",
            (session_id,),
        ).fetchall()
        return [
            Turn(
                role=row["role"],
                text=row["text"],
                kind=row["kind"],
                domain=row["domain"],
                created_at=datetime.fromisoformat(row["created_at"]),
            )
            for row in rows
        ]

    def delete_user_data(self, user_id: int) -> int:
        """Wipe everything for one user. Returns the number of sessions removed."""
        session_ids = [
            row["id"]
            for row in self._conn.execute(
                "SELECT id FROM sessions WHERE user_id = ?", (user_id,)
            ).fetchall()
        ]
        self._conn.executemany(
            "DELETE FROM turns WHERE session_id = ?", [(sid,) for sid in session_ids]
        )
        self._conn.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
        self._conn.execute("DELETE FROM users WHERE telegram_id = ?", (user_id,))
        self._conn.commit()
        return len(session_ids)
