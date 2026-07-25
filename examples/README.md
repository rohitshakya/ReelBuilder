# Examples

## Sample reel (music + watermark)

Already rendered:

```bash
examples/output/sample_reel.mp4
```

Assets used:

| File | Role |
|------|------|
| `examples/slides/*.png` | Slide images |
| `examples/audio/demo_music.mp3` | Generated ambient bed (royalty-free) |
| `assets/watermark.png` | Logo watermark |

### Re-render

```bash
reelforge render \
  --images ./examples/slides \
  --music ./examples/audio/demo_music.mp3 \
  --watermark ./assets/watermark.png \
  --output ./examples/output/sample_reel.mp4 \
  --template modern \
  --preset instagram \
  --duration 2.0 \
  --seed 42
```

### Regenerate slides / music

```bash
python examples/generate_slides.py

# Soft sine ambient bed
ffmpeg -y -f lavfi -i "sine=frequency=220:duration=20" \
  -f lavfi -i "sine=frequency=330:duration=20" \
  -f lavfi -i "sine=frequency=440:duration=20" \
  -filter_complex "[0]volume=0.18[a0];[1]volume=0.10[a1];[2]volume=0.06,tremolo=f=0.25:d=0.4[a2];[a0][a1][a2]amix=inputs=3" \
  -c:a libmp3lame -q:a 4 examples/audio/demo_music.mp3
```
