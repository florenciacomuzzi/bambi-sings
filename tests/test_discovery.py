from pathlib import Path

import pytest

from bambi_sings.discovery import discover_export_zip, transcribed_zip_name


def test_discover_single_zip(tmp_path: Path):
    z = tmp_path / "WhatsApp Chat - A (2).zip"
    z.write_bytes(b"PK")
    found = discover_export_zip(tmp_path)
    assert found == z


def test_discover_explicit_path(tmp_path: Path):
    z = tmp_path / "custom.zip"
    z.write_bytes(b"PK")
    assert discover_export_zip(tmp_path, z) == z.resolve()


def test_discover_zero_or_many(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        discover_export_zip(tmp_path)
    (tmp_path / "a.zip").write_bytes(b"PK")
    (tmp_path / "b.zip").write_bytes(b"PK")
    with pytest.raises(ValueError):
        discover_export_zip(tmp_path)


def test_transcribed_zip_name():
    assert transcribed_zip_name(Path("Chat (21).zip")) == "Chat (21)_transcribed.zip"
