import zipfile
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixture_export(tmp_path: Path) -> Path:
    export_dir = tmp_path / "export"
    export_dir.mkdir()
    chat = FIXTURES / "sample_chat.txt"
    (export_dir / "_chat.txt").write_text(chat.read_text(encoding="utf-8"))
    opus = export_dir / "00000001-AUDIO-2024-01-02-10-01-00.opus"
    opus.write_bytes(b"\x00" * 64)
    photo = export_dir / "00000002-PHOTO-2024-01-02-10-03-00.jpg"
    photo.write_bytes(b"\xff\xd8\xff")

    zip_path = tmp_path / "WhatsApp Chat - Sample (1).zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in export_dir.iterdir():
            archive.write(path, arcname=path.name)
    return zip_path
