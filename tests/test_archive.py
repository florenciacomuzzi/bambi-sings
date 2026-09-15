import zipfile
from pathlib import Path

from bambi_sings.archive import build_zip, extract_zip


def test_extract_and_build_round_trip(tmp_path: Path):
    source = tmp_path / "src"
    source.mkdir()
    (source / "a.txt").write_text("hello")
    inner = source / "nested"
    inner.mkdir()
    (inner / "b.txt").write_text("world")

    original_zip = tmp_path / "in.zip"
    build_zip(source, original_zip)

    dest = tmp_path / "dest"
    extract_zip(original_zip, dest)
    assert (dest / "a.txt").read_text() == "hello"
    assert (dest / "nested" / "b.txt").read_text() == "world"

    out_zip = tmp_path / "out.zip"
    build_zip(dest, out_zip)
    with zipfile.ZipFile(out_zip, "r") as archive:
        assert "a.txt" in archive.namelist()
