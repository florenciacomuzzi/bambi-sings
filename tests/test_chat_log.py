from pathlib import Path

import pytest

from bambi_sings.chat_log import find_chat_log, normalize_text, parse_chat_log

FIXTURES = Path(__file__).parent / "fixtures"


def test_normalize_strips_bom():
    assert normalize_text("\ufeffhello") == "hello"


def test_parse_sample_chat(tmp_path: Path):
    text = (FIXTURES / "sample_chat.txt").read_text(encoding="utf-8")
    opus = tmp_path / "00000001-AUDIO-2024-01-02-10-01-00.opus"
    opus.write_bytes(b"x")
    messages = parse_chat_log(text, export_root=tmp_path)
    assert len(messages) == 5
    voice = messages[1]
    assert voice.sender == "Bob"
    assert voice.attachment is not None
    assert voice.attachment.filename.endswith(".opus")


def test_find_chat_log_ios(tmp_path: Path):
    (tmp_path / "_chat.txt").write_text("x")
    assert find_chat_log(tmp_path).name == "_chat.txt"


def test_find_chat_log_android(tmp_path: Path):
    (tmp_path / "WhatsApp Chat with Bob.txt").write_text("x")
    assert find_chat_log(tmp_path).name == "WhatsApp Chat with Bob.txt"


def test_find_chat_log_missing(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        find_chat_log(tmp_path)
