from pathlib import Path

from bambi_sings.attachments import (
    classify_media,
    extract_attachment_filename,
    is_voice_note,
    resolve_attachment,
)


def test_classify_media_types():
    assert classify_media("0001-AUDIO-2024.opus").value == "audio"
    assert classify_media("0001-VIDEO-2024.mp4").value == "video"
    assert classify_media("IMG-20240101-WA0001.jpg").value == "photo"
    assert classify_media("0001-STICKER-2024.webp").value == "sticker"


def test_extract_attachment_ios():
    body = "Hi ‎<attached: note.opus>"
    assert extract_attachment_filename(body) == "note.opus"


def test_extract_attachment_android():
    body = "file.pdf (file attached)"
    assert extract_attachment_filename(body) == "file.pdf"


def test_voice_note_requires_file(tmp_path: Path):
    root = tmp_path
    opus = root / "0001-AUDIO-2024.opus"
    opus.write_bytes(b"data")
    attachment = resolve_attachment(opus.name, root)
    assert is_voice_note(attachment, body="")


def test_voice_note_skips_omitted(tmp_path: Path):
    root = tmp_path
    opus = root / "0001-AUDIO-2024.opus"
    opus.write_bytes(b"data")
    attachment = resolve_attachment(opus.name, root)
    assert not is_voice_note(attachment, body="‎audio omitted")
