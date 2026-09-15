from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from bambi_sings.audio import AudioConversionError, convert_to_wav


def test_convert_to_wav_success(tmp_path: Path):
    source = tmp_path / "note.opus"
    source.write_bytes(b"fake")
    dest = tmp_path / "out.wav"
    mock_run = MagicMock(return_value=MagicMock(returncode=0))
    with patch("bambi_sings.audio.subprocess.run", mock_run):
        convert_to_wav(source, dest, ffmpeg_executable="ffmpeg")
    mock_run.assert_called_once()


def test_convert_to_wav_missing_ffmpeg(tmp_path: Path):
    source = tmp_path / "note.opus"
    source.write_bytes(b"fake")
    dest = tmp_path / "out.wav"
    with patch(
        "bambi_sings.audio.subprocess.run",
        side_effect=FileNotFoundError,
    ):
        with pytest.raises(AudioConversionError, match="ffmpeg not found"):
            convert_to_wav(source, dest)


def test_convert_to_wav_failure(tmp_path: Path):
    source = tmp_path / "note.opus"
    source.write_bytes(b"fake")
    dest = tmp_path / "out.wav"
    mock_run = MagicMock(return_value=MagicMock(returncode=1, stderr="bad"))
    with patch("bambi_sings.audio.subprocess.run", mock_run):
        with pytest.raises(AudioConversionError, match="ffmpeg failed"):
            convert_to_wav(source, dest)
