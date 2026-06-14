from datetime import datetime
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
zip_path = ROOT / f"project3_snapshot_{timestamp}.zip"

exclude_dirs = {".git", ".venv", "__pycache__", ".pytest_cache"}

with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
    for path in ROOT.rglob("*"):
        if any(part in exclude_dirs for part in path.parts):
            continue
        if path == zip_path:
            continue
        archive.write(path, path.relative_to(ROOT))

print(f"Created snapshot: {zip_path}")
