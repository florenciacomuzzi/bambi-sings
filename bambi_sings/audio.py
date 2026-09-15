import subprocess
from pathlib import Path


class AudioConversionError(RuntimeError):
    pass


def convert_to_wav(
    source: Path,
    destination: Path,
    ffmpeg_executable: str = "ffmpeg",
) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    command = [
        ffmpeg_executable,
        "-y",
        "-i",
        str(source),
        "-ac",
        "1",
        "-ar",
        "16000",
        str(destination),
    ]
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError as exc:
        raise AudioConversionError(
            "ffmpeg not found; install ffmpeg to convert voice notes."
        ) from exc
    if completed.returncode != 0:
        stderr = (completed.stderr or "").strip()
        raise AudioConversionError(
            f"ffmpeg failed for {source.name}: {stderr or 'unknown error'}"
        )
    return destination
