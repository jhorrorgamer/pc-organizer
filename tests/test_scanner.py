from pathlib import Path
import time

from scanner import scan_directory_usage, find_large_files, find_old_large_files, human_size


def make_file(path: Path, size: int):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"a" * size)


def test_scan_and_large_files(tmp_path: Path):
    make_file(tmp_path / "big.iso", 6000)
    make_file(tmp_path / "docs" / "note.txt", 300)
    make_file(tmp_path / "docs" / "movie.mkv", 7000)

    stats = scan_directory_usage(tmp_path)
    assert stats["file_count"] == 3
    assert stats["total_size"] == 13300

    large = find_large_files(tmp_path, 5000)
    assert [p.name for p, _ in large] == ["movie.mkv", "big.iso"]


def test_find_old_large_files(tmp_path: Path):
    old = tmp_path / "old.bin"
    new = tmp_path / "new.bin"
    make_file(old, 9000)
    make_file(new, 9000)

    old_time = time.time() - (200 * 86400)
    new_time = time.time() - (10 * 86400)
    import os
    os.utime(old, (old_time, old_time))
    os.utime(new, (new_time, new_time))

    rows = find_old_large_files(tmp_path, 8000, 90)
    assert len(rows) == 1
    assert rows[0][0].name == "old.bin"


def test_human_size():
    assert human_size(1024) == "1.0 KB"
    assert human_size(1024 * 1024) == "1.0 MB"
