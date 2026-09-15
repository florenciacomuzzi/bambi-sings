from pathlib import Path


def discover_export_zip(exports_dir: Path, zip_path: Path | None = None) -> Path:
    if zip_path is not None:
        path = zip_path.expanduser().resolve()
        if not path.is_file():
            raise FileNotFoundError(f"Export zip not found: {path}")
        if path.suffix.lower() != ".zip":
            raise ValueError(f"Expected a .zip export, got: {path.name}")
        return path

    root = exports_dir.expanduser().resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"Exports directory not found: {root}")

    zips = sorted(p for p in root.glob("*.zip") if p.is_file())
    if not zips:
        raise FileNotFoundError(
            f"No .zip exports found in {root}. Add one WhatsApp export zip."
        )
    if len(zips) > 1:
        names = ", ".join(p.name for p in zips)
        raise ValueError(
            f"Expected exactly one .zip in {root}, found {len(zips)}: {names}"
        )
    return zips[0]


def transcribed_zip_name(source_zip: Path) -> str:
    stem = source_zip.stem
    return f"{stem}_transcribed.zip"
