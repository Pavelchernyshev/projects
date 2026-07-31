"""Speech-to-text for voice notes.

Claude has no audio input, so this is the one place the stack reaches outside
Anthropic. Three backends:

* ``local``  — faster-whisper in-process. No third-party API, no audio leaves the
  host. Default, because the product asks people about the worst parts of their
  life and shipping that to an extra vendor should be an opt-in.
* ``openai`` — Whisper API. Lower memory, needs OPENAI_API_KEY.
* ``none``   — voice rejected with a friendly message.

The model is loaded lazily on first use and transcription runs in a worker
thread, so importing this module (and bot startup) stays fast.
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Protocol

from .config import Config
from .models import Lang

log = logging.getLogger(__name__)


class TranscriptionError(RuntimeError):
    """Audio could not be turned into usable text."""


class Transcriber(Protocol):
    async def transcribe(self, audio_path: Path, lang: Lang | None) -> str: ...

    @property
    def enabled(self) -> bool: ...


class DisabledTranscriber:
    @property
    def enabled(self) -> bool:
        return False

    async def transcribe(self, audio_path: Path, lang: Lang | None) -> str:
        raise TranscriptionError("speech-to-text is disabled on this instance")


class LocalWhisper:
    """faster-whisper, loaded on first use and shared thereafter."""

    def __init__(self, model: str, device: str, compute_type: str) -> None:
        self._name = model
        self._device = device
        self._compute_type = compute_type
        self._model = None
        self._lock = asyncio.Lock()

    @property
    def enabled(self) -> bool:
        return True

    async def _ensure_model(self):
        if self._model is not None:
            return self._model
        async with self._lock:
            if self._model is None:
                try:
                    from faster_whisper import WhisperModel
                except ImportError as exc:  # pragma: no cover - env-dependent
                    raise TranscriptionError(
                        "faster-whisper is not installed; set STT_BACKEND=openai "
                        "or STT_BACKEND=none"
                    ) from exc
                log.info("loading whisper model %s on %s", self._name, self._device)
                self._model = await asyncio.to_thread(
                    WhisperModel,
                    self._name,
                    device=self._device,
                    compute_type=self._compute_type,
                )
        return self._model

    async def transcribe(self, audio_path: Path, lang: Lang | None) -> str:
        model = await self._ensure_model()

        def run() -> str:
            segments, _info = model.transcribe(
                str(audio_path),
                language=lang.value if lang else None,
                vad_filter=True,
                beam_size=5,
            )
            return " ".join(segment.text.strip() for segment in segments).strip()

        try:
            return await asyncio.to_thread(run)
        except Exception as exc:  # noqa: BLE001 - surface any decode failure uniformly
            raise TranscriptionError(f"local transcription failed: {exc}") from exc


class OpenAIWhisper:
    """Whisper API. Opt-in, since it sends the recording to a third party."""

    def __init__(self, api_key: str, model: str = "whisper-1") -> None:
        self._api_key = api_key
        self._model = model

    @property
    def enabled(self) -> bool:
        return True

    async def transcribe(self, audio_path: Path, lang: Lang | None) -> str:
        import httpx

        data = {"model": self._model}
        if lang:
            data["language"] = lang.value

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                with audio_path.open("rb") as handle:
                    response = await client.post(
                        "https://api.openai.com/v1/audio/transcriptions",
                        headers={"Authorization": f"Bearer {self._api_key}"},
                        data=data,
                        files={"file": (audio_path.name, handle, "audio/ogg")},
                    )
            response.raise_for_status()
            return (response.json().get("text") or "").strip()
        except Exception as exc:  # noqa: BLE001
            raise TranscriptionError(f"whisper API transcription failed: {exc}") from exc


def build(config: Config) -> Transcriber:
    if config.stt_backend == "none":
        return DisabledTranscriber()
    if config.stt_backend == "openai":
        assert config.openai_api_key  # guaranteed by Config.from_env
        return OpenAIWhisper(config.openai_api_key)
    return LocalWhisper(
        config.whisper_model, config.whisper_device, config.whisper_compute_type
    )
