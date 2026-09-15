from pathlib import Path
from unittest.mock import MagicMock, patch

from bambi_sings.transcribe.local import LocalWhisperTranscriber


def test_transcribe_file_success(tmp_path: Path):
    audio = tmp_path / "x.wav"
    audio.write_bytes(b"wav")
    segment = MagicMock(text=" hello ")
    model = MagicMock()
    model.transcribe.return_value = ([segment], None)
    transcriber = LocalWhisperTranscriber(model_size="tiny")
    with patch.object(transcriber, "_load_model", return_value=model):
        result = transcriber.transcribe_file(audio)
    assert result.ok
    assert result.text == "hello"
    assert result.provider == "local"


def test_transcribe_file_empty(tmp_path: Path):
    audio = tmp_path / "x.wav"
    audio.write_bytes(b"wav")
    model = MagicMock()
    model.transcribe.return_value = ([], None)
    transcriber = LocalWhisperTranscriber()
    with patch.object(transcriber, "_load_model", return_value=model):
        result = transcriber.transcribe_file(audio)
    assert not result.ok
    assert result.error == "empty transcription"
