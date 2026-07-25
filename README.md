<p align="center">
  <img src="assets/logo.svg" alt="ReelForge logo" width="120" />
</p>

<h1 align="center">ReelForge</h1>

<p align="center">
  <strong>Forge cinematic vertical videos from a folder of images.</strong><br/>
  Instagram Reels · YouTube Shorts · TikTok — CapCut-quality motion, open-source Python.
</p>

<p align="center">
  <a href="https://github.com/reelforge/reelforge/actions/workflows/test.yml"><img src="https://img.shields.io/github/actions/workflow/status/reelforge/reelforge/test.yml?label=tests" alt="Tests" /></a>
  <a href="https://pypi.org/project/reelforge/"><img src="https://img.shields.io/pypi/v/reelforge" alt="PyPI" /></a>
  <a href="https://pypi.org/project/reelforge/"><img src="https://img.shields.io/pypi/pyversions/reelforge" alt="Python" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License" /></a>
</p>

---

## Why ReelForge?

Most “image → video” tools are slideshows. ReelForge is built to feel edited:

- **Ken Burns** camera moves (zoom, pan, random)
- **Smooth transitions** (fade, crossfade, slide, push, zoom)
- **Blur-fill backgrounds** when aspect ratios don’t match
- **Progress bar** + slide counter overlays
- **Logo watermark** + **music** with fade in/out and auto-trim
- **Templates** (minimal, modern, documentary, dark, tech, education)
- **Export presets** for Instagram, YouTube Shorts, and TikTok

> ![Demo placeholder](assets/demo.gif)
> *Replace `assets/demo.gif` with a real render preview.*

---

## Features (Phase 1)

| Feature | Status |
|---------|--------|
| Natural-sorted image folders (`001.png`, `002.png`, …) | ✅ |
| 1080×1920 · 30 FPS · H.264 + AAC | ✅ |
| Auto-resize + blur background | ✅ |
| Ken Burns (zoom / pan / random) | ✅ |
| Transitions (fade / crossfade / slide / push / zoom / random) | ✅ |
| Progress bar + “Slide N / Total” | ✅ |
| Logo watermark | ✅ |
| Background music (fade + auto-trim/loop) | ✅ |
| YAML config · Typer CLI · Rich progress | ✅ |
| Clip cache · multi-thread preprocess · HW accel | ✅ |
| Subtitles (SRT/ASS animated) | 🚧 Phase 2 |
| AI voice-over sync | 🚧 Phase 3 |
| Full template font packs | 🚧 Phase 4 |

---

## Requirements

- **Python 3.12+**
- **[FFmpeg](https://ffmpeg.org/download.html)** on your `PATH`

```bash
# macOS
brew install ffmpeg

# Ubuntu / Debian
sudo apt install ffmpeg
```

---

## Installation

```bash
pip install reelforge

# or from source
git clone https://github.com/reelforge/reelforge.git
cd reelforge
pip install -e ".[dev]"
```

---

## Quick start

```bash
# Preview the slide list
reelforge preview --images ./examples/slides

# Render a reel
reelforge render \
  --images ./examples/slides \
  --output reel.mp4 \
  --template modern \
  --preset instagram

# With music + watermark
reelforge render \
  --images ./slides \
  --music ./music.mp3 \
  --watermark ./logo.png \
  --output reel.mp4 \
  --template dark
```

### YAML config

```bash
reelforge render --images ./slides --config examples/config.yaml -o reel.mp4
```

See [`examples/config.yaml`](examples/config.yaml) for the full schema.

---

## CLI

| Command | Description |
|---------|-------------|
| `reelforge render` | Render a final MP4 |
| `reelforge preview` | List slides + orientations without encoding |
| `reelforge templates` | Show built-in templates |
| `reelforge version` | Print version |

```text
reelforge render \
    --images ./slides \
    --music music.mp3 \
    --output reel.mp4 \
    --template modern
```

---

## Templates

| Name | Vibe |
|------|------|
| `minimal` | Soft fades, gentle zoom |
| `modern` | CapCut energy — random motion + pink progress |
| `documentary` | Slow pans, long fades |
| `dark` | High-contrast zoom transitions |
| `tech` | Snappy push cuts |
| `education` | Clear slide pacing |

```bash
reelforge templates
```

---

## Architecture

Modular pipeline — easy to extend:

```text
reelforge/
├── animation/      # Ken Burns + movement planning
├── transition/     # fade, slide, zoom, …
├── audio/          # music bed + voice-over stubs
├── subtitles/      # SRT / ASS (Phase 2)
├── renderer/       # canvas, encoder, pipeline
├── templates/      # visual presets
├── models/         # Pydantic config
├── utils/          # FFmpeg, images, progress
└── cli/            # Typer entrypoint
```

Details: [`docs/architecture.md`](docs/architecture.md)

---

## Roadmap

- **Phase 2** — Animated captions (SRT/ASS, word highlight, typewriter)
- **Phase 3** — AI voice-over (OpenAI, ElevenLabs, Piper, Kokoro) with duration sync
- **Phase 4** — Shipped font packs + richer template theming
- Effects pack, multi-scene timelines, remote render workers

---

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md).

```bash
pip install -e ".[dev]"
pre-commit install
pytest
```

---

## License

MIT — see [`LICENSE`](LICENSE).

---

<p align="center">
  <sub>Made for creators who want CapCut motion without CapCut lock-in.</sub>
</p>
