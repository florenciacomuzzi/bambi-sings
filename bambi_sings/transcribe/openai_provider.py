import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Callable, Optional

from bambi_sings.models import TranscriptionResult

DEFAULT_MODEL = "gpt-4o-mini-transcribe"
API_URL = "https://api.openai.com/v1/audio/transcriptions"


class OpenAITranscriber:
    """Cloud transcription via OpenAI's audio transcription REST API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = DEFAULT_MODEL,
        request_fn: Optional[Callable[[Path], bytes]] = None,
    ) -> None:
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.model = model
        self.model_label = model
        self._request_fn = request_fn or self._send_request

    def transcribe_file(self, audio_path: Path) -> TranscriptionResult:
        if not self.api_key:
            return TranscriptionResult(
                text="",
                provider="openai",
                model=self.model_label,
                error="OPENAI_API_KEY not set",
            )
        try:
            raw = self._request_fn(audio_path)
        except (urllib.error.URLError, OSError) as exc:
            return TranscriptionResult(
                text="",
                provider="openai",
                model=self.model_label,
                error=str(exc),
            )
        try:
            text = json.loads(raw).get("text", "").strip()
        except (json.JSONDecodeError, AttributeError) as exc:
            return TranscriptionResult(
                text="",
                provider="openai",
                model=self.model_label,
                error=f"invalid response: {exc}",
            )
        if not text:
            return TranscriptionResult(
                text="",
                provider="openai",
                model=self.model_label,
                error="empty transcription",
            )
        return TranscriptionResult(text=text, provider="openai", model=self.model_label)

    def _send_request(self, audio_path: Path) -> bytes:
        boundary = "bambiSingsBoundary"
        request = urllib.request.Request(
            API_URL,
            data=self._build_multipart(audio_path, boundary),
            method="POST",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": f"multipart/form-data; boundary={boundary}",
            },
        )
        with urllib.request.urlopen(request, timeout=120) as response:
            return response.read()

    def _build_multipart(self, audio_path: Path, boundary: str) -> bytes:
        parts: list[bytes] = [
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="model"\r\n\r\n'
            f"{self.model}\r\n".encode(),
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="file"; '
            f'filename="{audio_path.name}"\r\n'
            "Content-Type: application/octet-stream\r\n\r\n".encode(),
            audio_path.read_bytes(),
            f"\r\n--{boundary}--\r\n".encode(),
        ]
        return b"".join(parts)
