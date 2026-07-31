"""Environment-backed configuration.

Everything the bot needs to boot lives here so misconfiguration fails at
startup with a clear message instead of mid-conversation.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

REPO_ROOT = Path(__file__).resolve().parents[2]


class ConfigError(RuntimeError):
    """Raised when required configuration is missing or nonsensical."""


def _require(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ConfigError(
            f"{name} is not set. Copy .env.example to .env and fill it in."
        )
    return value


def _int(name: str, default: int) -> int:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise ConfigError(f"{name} must be an integer, got {raw!r}") from exc


def _allowlist() -> frozenset[int]:
    raw = os.getenv("ALLOWLIST", "").strip()
    if not raw:
        return frozenset()
    ids = set()
    for chunk in raw.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        try:
            ids.add(int(chunk))
        except ValueError as exc:
            raise ConfigError(
                f"ALLOWLIST entry {chunk!r} is not a Telegram user id"
            ) from exc
    return frozenset(ids)


@dataclass(frozen=True)
class Config:
    telegram_token: str
    anthropic_api_key: str
    product_name: str

    model_diagnosis: str
    effort_diagnosis: str
    model_probe: str
    effort_probe: str

    min_probe_questions: int
    max_probe_questions: int

    stt_backend: str
    whisper_model: str
    whisper_device: str
    whisper_compute_type: str
    openai_api_key: str | None

    database_path: Path
    log_level: str
    allowlist: frozenset[int] = field(default_factory=frozenset)

    @classmethod
    def from_env(cls) -> Config:
        stt_backend = os.getenv("STT_BACKEND", "local").strip().lower()
        if stt_backend not in {"local", "openai", "none"}:
            raise ConfigError(
                f"STT_BACKEND must be one of local|openai|none, got {stt_backend!r}"
            )

        openai_key = os.getenv("OPENAI_API_KEY", "").strip() or None
        if stt_backend == "openai" and not openai_key:
            raise ConfigError("STT_BACKEND=openai requires OPENAI_API_KEY")

        min_probe = _int("MIN_PROBE_QUESTIONS", 3)
        max_probe = _int("MAX_PROBE_QUESTIONS", 6)
        if min_probe < 1 or max_probe < min_probe:
            raise ConfigError(
                "Need 1 <= MIN_PROBE_QUESTIONS <= MAX_PROBE_QUESTIONS "
                f"(got {min_probe} and {max_probe})"
            )

        db_path = Path(os.getenv("DATABASE_PATH", "data/myway.db"))
        if not db_path.is_absolute():
            db_path = REPO_ROOT / db_path

        return cls(
            telegram_token=_require("TELEGRAM_BOT_TOKEN"),
            anthropic_api_key=_require("ANTHROPIC_API_KEY"),
            product_name=os.getenv("PRODUCT_NAME", "MyWay").strip() or "MyWay",
            model_diagnosis=os.getenv("MODEL_DIAGNOSIS", "claude-opus-5").strip(),
            effort_diagnosis=os.getenv("EFFORT_DIAGNOSIS", "high").strip(),
            model_probe=os.getenv("MODEL_PROBE", "claude-opus-5").strip(),
            effort_probe=os.getenv("EFFORT_PROBE", "low").strip(),
            min_probe_questions=min_probe,
            max_probe_questions=max_probe,
            stt_backend=stt_backend,
            whisper_model=os.getenv("WHISPER_MODEL", "small").strip(),
            whisper_device=os.getenv("WHISPER_DEVICE", "cpu").strip(),
            whisper_compute_type=os.getenv("WHISPER_COMPUTE_TYPE", "int8").strip(),
            openai_api_key=openai_key,
            database_path=db_path,
            log_level=os.getenv("LOG_LEVEL", "INFO").strip().upper(),
            allowlist=_allowlist(),
        )
