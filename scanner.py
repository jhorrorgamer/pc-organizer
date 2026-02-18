from __future__ import annotations

import os
import time
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


def iter_files(root: Path) -> Iterable[Path]:
    """Yield files under root, skipping broken/denied paths."""
    for dirpath, _, filenames in os.walk(root, topdown=True, onerror=lambda e: None):
        for name in filenames:
            path = Path(dirpath) / name
            try:
                if path.is_file():
                    yield path
            except OSError:
                continue


def scan_directory_usage(root: Path) -> Dict[str, object]:
    total_size = 0
    file_count = 0
    by_extension = defaultdict(int)

    for path in iter_files(root):
        try:
            size = path.stat().st_size
        except OSError:
            continue

        total_size += size
        file_count += 1
        ext = path.suffix.lower() or "<no extension>"
        by_extension[ext] += size

    if by_extension:
        top_extension = max(by_extension.items(), key=lambda item: item[1])[0]
    else:
        top_extension = "N/A"

    return {
        "total_size": total_size,
        "file_count": file_count,
        "by_extension": dict(by_extension),
        "top_extension": top_extension,
    }


def find_large_files(root: Path, threshold_bytes: int) -> List[Tuple[Path, int]]:
    rows: List[Tuple[Path, int]] = []
    for path in iter_files(root):
        try:
            size = path.stat().st_size
        except OSError:
            continue
        if size >= threshold_bytes:
            rows.append((path, size))

    rows.sort(key=lambda x: x[1], reverse=True)
    return rows


def find_old_large_files(root: Path, threshold_bytes: int, age_days: int) -> List[Tuple[Path, int, int]]:
    now = time.time()
    cutoff_seconds = age_days * 86400
    rows: List[Tuple[Path, int, int]] = []

    for path in iter_files(root):
        try:
            stat = path.stat()
        except OSError:
            continue

        if stat.st_size < threshold_bytes:
            continue

        age_seconds = now - stat.st_mtime
        if age_seconds >= cutoff_seconds:
            days = int(age_seconds // 86400)
            rows.append((path, stat.st_size, days))

    rows.sort(key=lambda x: (x[2], x[1]), reverse=True)
    return rows


def estimate_temp_data() -> int:
    """Estimate removable temp/cache data in common locations."""
    candidates = [
        Path(os.environ.get("TEMP", "")),
        Path(os.environ.get("TMP", "")),
        Path.home() / ".cache",
        Path.home() / "AppData" / "Local" / "Temp",
    ]
    total = 0

    seen = set()
    for folder in candidates:
        if not folder or not folder.exists() or folder in seen:
            continue
        seen.add(folder)
        for path in iter_files(folder):
            try:
                total += path.stat().st_size
            except OSError:
                continue
    return total


def human_size(num_bytes: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(num_bytes)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"
