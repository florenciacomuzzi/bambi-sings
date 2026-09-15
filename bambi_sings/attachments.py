import re
from pathlib import Path

from bambi_sings.models import Attachment, MediaKind

ATTACHED_IOS = re.compile(r"<attached:\s*([^>]+?)>", re.IGNORECASE)
ATTACHED_ANDROID = re.compile(
    r"(.+?)\s*\((?:file attached|Datei angehängt)\)",
    re.IGNORECASE,
)
OMITTED_AUDIO = re.compile(r"audio omitted", re.IGNORECASE)

VOICE_EXTENSIONS = {".opus", ".ogg", ".aac", ".m4a", ".mp3"}
AUDIO_NAME_MARKERS = ("-AUDIO-", "PTT-")


def classify_media(filename: str) -> MediaKind:
    upper = filename.upper()
    if "-PHOTO-" in upper or upper.startswith("IMG-"):
        return MediaKind.PHOTO
    if "-VIDEO-" in upper or upper.startswith("VID-"):
        return MediaKind.VIDEO
    if "-STICKER-" in upper:
        return MediaKind.STICKER
    if "-AUDIO-" in upper or "PTT-" in upper:
        return MediaKind.AUDIO
    suffix = Path(filename).suffix.lower()
    if suffix in {".jpg", ".jpeg", ".png", ".webp"} and "-STICKER-" not in upper:
        if upper.endswith(".WEBP") and "-STICKER-" in upper:
            return MediaKind.STICKER
        return MediaKind.PHOTO
    if suffix in VOICE_EXTENSIONS:
        return MediaKind.AUDIO
    if suffix in {".mp4", ".mov"}:
        return MediaKind.VIDEO
    if suffix in {".pdf", ".doc", ".docx", ".xlsx", ".pptx", ".zip"}:
        return MediaKind.DOCUMENT
    return MediaKind.UNKNOWN


def extract_attachment_filename(body: str) -> str | None:
    match = ATTACHED_IOS.search(body)
    if match:
        return match.group(1).strip()
    match = ATTACHED_ANDROID.search(body)
    if match:
        candidate = match.group(1).strip()
        if "." in candidate or "-" in candidate:
            return candidate
    return None


def is_audio_omitted(body: str) -> bool:
    return bool(OMITTED_AUDIO.search(body))


def resolve_attachment(
    filename: str,
    export_root: Path,
) -> Attachment:
    kind = classify_media(filename)
    path = export_root / filename
    resolved = path if path.is_file() else None
    return Attachment(filename=filename, media_kind=kind, resolved_path=resolved)


def is_voice_note(attachment: Attachment | None, body: str) -> bool:
    if is_audio_omitted(body):
        return False
    if attachment is None or attachment.resolved_path is None:
        return False
    if attachment.resolved_path.stat().st_size == 0:
        return False
    name = attachment.filename
    upper = name.upper()
    if attachment.media_kind == MediaKind.AUDIO:
        return True
    if any(marker in upper for marker in AUDIO_NAME_MARKERS):
        return True
    suffix = Path(name).suffix.lower()
    return suffix in {".opus", ".ogg"} and attachment.media_kind != MediaKind.VIDEO
