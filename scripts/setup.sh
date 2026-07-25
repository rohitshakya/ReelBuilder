#!/usr/bin/env bash
# ReelForge — one-command local setup
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

BOLD='\033[1m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m'

info()  { printf "${CYAN}→${NC} %s\n" "$*"; }
ok()    { printf "${GREEN}✓${NC} %s\n" "$*"; }
warn()  { printf "${YELLOW}!${NC} %s\n" "$*"; }
fail()  { printf "${RED}✗${NC} %s\n" "$*"; exit 1; }

echo ""
printf "${BOLD}ReelForge setup${NC}\n"
echo "────────────────"

# --- Python ---
PYTHON=""
for candidate in python3.13 python3.12 python3; do
  if command -v "$candidate" >/dev/null 2>&1; then
    PYTHON="$candidate"
    break
  fi
done
[[ -n "$PYTHON" ]] || fail "Python 3.12+ is required. Install from https://www.python.org/downloads/"

PY_VER="$("$PYTHON" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
PY_MAJOR="$("$PYTHON" -c 'import sys; print(sys.version_info.major)')"
PY_MINOR="$("$PYTHON" -c 'import sys; print(sys.version_info.minor)')"
if (( PY_MAJOR < 3 || (PY_MAJOR == 3 && PY_MINOR < 12) )); then
  fail "Python 3.12+ required (found $PY_VER via $PYTHON)"
fi
ok "Python $PY_VER ($PYTHON)"

# --- FFmpeg ---
if command -v ffmpeg >/dev/null 2>&1; then
  ok "FFmpeg $(ffmpeg -version 2>/dev/null | head -1 | awk '{print $3}')"
else
  warn "FFmpeg not found — attempting install…"
  if [[ "$(uname -s)" == "Darwin" ]] && command -v brew >/dev/null 2>&1; then
    info "brew install ffmpeg"
    brew install ffmpeg
  elif command -v apt-get >/dev/null 2>&1; then
    info "sudo apt-get install -y ffmpeg"
    sudo apt-get update -qq
    sudo apt-get install -y ffmpeg
  else
    fail "Install FFmpeg manually: https://ffmpeg.org/download.html"
  fi
  ok "FFmpeg installed"
fi

# --- Virtualenv ---
if [[ ! -d .venv ]]; then
  info "Creating .venv…"
  "$PYTHON" -m venv .venv
  ok "Created .venv"
else
  ok ".venv already exists"
fi

# shellcheck disable=SC1091
source .venv/bin/activate

info "Upgrading pip…"
python -m pip install --upgrade pip -q || warn "pip upgrade skipped (continuing)"

info "Installing ReelForge (editable)…"
pip install -e ".[dev]" -q
ok "Package installed"

# --- Optional: sample slides ---
if [[ ! -f examples/slides/001.png ]]; then
  info "Generating example slides…"
  python examples/generate_slides.py
  ok "Example slides ready"
else
  ok "Example slides present"
fi

# --- Verify ---
VERSION="$(reelforge version 2>/dev/null || true)"
ok "${VERSION:-ReelForge installed}"

echo ""
printf "${BOLD}Ready!${NC} Activate and render:\n"
echo ""
echo "  source .venv/bin/activate"
echo ""
echo "  # Your own images"
echo "  reelforge preview --images ~/Desktop/my-slides"
echo "  reelforge render \\"
echo "    --images ~/Desktop/my-slides \\"
echo "    --output ~/Desktop/my_reel.mp4 \\"
echo "    --template modern"
echo ""
echo "  # With music + watermark"
echo "  reelforge render \\"
echo "    --images ~/Desktop/my-slides \\"
echo "    --music ~/Desktop/song.mp3 \\"
echo "    --watermark ~/Desktop/logo.png \\"
echo "    --output ~/Desktop/my_reel.mp4 \\"
echo "    --template modern \\"
echo "    --preset instagram \\"
echo "    --duration 3.0"
echo ""
