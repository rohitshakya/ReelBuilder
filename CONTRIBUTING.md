# Contributing to ReelForge

Thanks for helping make ReelForge better.

## Development setup

```bash
bash scripts/setup.sh
source .venv/bin/activate
pre-commit install
```

Or manually:

```bash
git clone https://github.com/reelforge/reelforge.git
cd reelforge
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pre-commit install
```

FFmpeg is required for rendering and integration tests:

```bash
# macOS
brew install ffmpeg

# Ubuntu
sudo apt install ffmpeg
```

## Checks before opening a PR

```bash
ruff check reelforge tests
black reelforge tests
mypy reelforge
pytest
```

## Guidelines

- Keep modules small and typed.
- Prefer Google-style docstrings on public APIs.
- Business logic stays out of FFmpeg command construction.
- Add unit tests for new behavior.
- Do not commit rendered videos, cache folders, or secrets.
