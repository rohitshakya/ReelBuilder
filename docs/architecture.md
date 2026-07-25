# Architecture

ReelForge keeps **business logic** separate from **FFmpeg execution**.

```
CLI (Typer)
  └─ ProjectConfig (Pydantic) + Templates
       └─ RenderPipeline
            ├─ ImageLoader          (discover / natural-sort / probe)
            ├─ CanvasPreparer       (cover + blur fill)
            ├─ KenBurnsAnimator     (crop path → frames)
            ├─ TransitionFactory    (fade / slide / zoom / …)
            ├─ MusicMixer           (trim / loop / fade → AAC)
            └─ VideoEncoder         (PNG sequence → H.264 MP4)
```

## Design principles

- **SOLID** — small classes with single responsibilities; transitions and
  encoders are swappable via factories/interfaces.
- **Dependency injection** — `RenderPipeline` receives a `ProjectConfig`
  and constructs collaborators; tests can substitute fakes.
- **Typed everywhere** — `mypy --strict` friendly public APIs.
- **Cache** — per-slide Ken Burns frame caches under `.reelforge_cache/`.

## Phase roadmap

| Phase | Focus |
|-------|--------|
| 1 | Images → Ken Burns + transitions + music + watermark |
| 2 | SRT/ASS captions, word highlight, typewriter |
| 3 | AI voice-over (OpenAI, ElevenLabs, Piper, Kokoro) |
| 4 | Richer template system (fonts shipped with package) |
