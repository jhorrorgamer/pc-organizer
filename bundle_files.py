from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "pc-organizer-files.zip"

FILES = [
    "app.py",
    "scanner.py",
    "README.md",
    "tests/conftest.py",
    "tests/test_scanner.py",
]

with zipfile.ZipFile(OUTPUT, "w", compression=zipfile.ZIP_DEFLATED) as zf:
    for rel in FILES:
        path = ROOT / rel
        if path.exists():
            zf.write(path, arcname=rel)

print(f"Created: {OUTPUT}")
