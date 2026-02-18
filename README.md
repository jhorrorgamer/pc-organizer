# PC Organizer

A desktop Python application to help you:

- scan folders and summarize disk usage,
- find very large files quickly,
- detect old large files that are likely cleanup candidates,
- estimate temporary/cache data that could be consuming disk space.

## Features

- **Summary tab** with file count, total size, and top extension.
- **Large Files tab** sorted by biggest files first.
- **Old + Large tab** to highlight stale files that consume space.
- Built with **Tkinter** (included in standard Python installations).

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip pytest
python app.py
```

## Run tests

```bash
pytest -q
```

## Notes

- The app does not delete files automatically; it helps you identify cleanup targets safely.
- On very large drives, scanning may take some time.

## Create a downloadable ZIP

If you want all project files in one archive:

```bash
python bundle_files.py
```

This creates `pc-organizer-files.zip` in the project root.

