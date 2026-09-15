from pathlib import Path
from typing import Protocol

from bambi_sings.models import TranscriptionResult


class Transcriber(Protocol):
    def transcribe_file(self, audio_path: Path) -> TranscriptionResult:
        ...
