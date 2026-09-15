from pathlib import Path

from bambi_sings.models import TranscriptionResult


class LocalWhisperTranscriber:
    """Free on-device transcription via faster-whisper (CTranslate2)."""

    def __init__(
        self,
        model_size: str = "base",
        device: str = "cpu",
        compute_type: str = "int8",
    ) -> None:
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self._model = None
        self.model_label = f"faster-whisper/{model_size}"

    def _load_model(self):
        if self._model is None:
            from faster_whisper import WhisperModel

            self._model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type,
            )
        return self._model

    def transcribe_file(self, audio_path: Path) -> TranscriptionResult:
        try:
            model = self._load_model()
            segments, _info = model.transcribe(
                str(audio_path),
                beam_size=1,
                vad_filter=True,
            )
            parts = [
                segment.text.strip() for segment in segments if segment.text.strip()
            ]
            text = " ".join(parts).strip()
            if not text:
                return TranscriptionResult(
                    text="",
                    provider="local",
                    model=self.model_label,
                    error="empty transcription",
                )
            return TranscriptionResult(
                text=text,
                provider="local",
                model=self.model_label,
            )
        except Exception as exc:  # pragma: no cover - exercised via mock in tests
            return TranscriptionResult(
                text="",
                provider="local",
                model=self.model_label,
                error=str(exc),
            )
