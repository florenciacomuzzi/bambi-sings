from pathlib import Path
from unittest.mock import patch
import zipfile

from bambi_sings.models import TranscriptionResult
from bambi_sings.pipeline import TranscriptionPipeline
from bambi_sings.transcribe.local import LocalWhisperTranscriber


class FakeTranscriber(LocalWhisperTranscriber):
    def transcribe_file(self, audio_path: Path) -> TranscriptionResult:
        return TranscriptionResult(
            text=f"heard {audio_path.name}",
            provider="local",
            model="faster-whisper/test",
        )


def test_pipeline_dry_run(fixture_export: Path, tmp_path: Path):
    exports = fixture_export.parent
    pipeline = TranscriptionPipeline(
        exports_dir=exports,
        output_dir=tmp_path / "out",
        dry_run=True,
    )
    assert pipeline.run() is None


def test_pipeline_writes_transcribed_zip(fixture_export: Path, tmp_path: Path):
    exports = fixture_export.parent
    output_dir = tmp_path / "out"
    pipeline = TranscriptionPipeline(
        exports_dir=exports,
        output_dir=output_dir,
        transcriber=FakeTranscriber(),
    )
    with patch("bambi_sings.pipeline.convert_to_wav") as mock_convert:
        mock_convert.side_effect = lambda src, dest, **_: dest.write_bytes(b"wav")
        result = pipeline.run()
    assert result is not None
    assert result.name == "WhatsApp Chat - Sample (1)_transcribed.zip"
    with zipfile.ZipFile(result, "r") as archive:
        chat = archive.read("_chat.txt").decode("utf-8")
    assert "[transcription via local/faster-whisper/test]" in chat
    assert "heard" in chat
