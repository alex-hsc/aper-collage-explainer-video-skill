# Tool adapters

## Contents

- Selection rule
- Directing
- Image generation
- Image-to-video
- TTS
- Composition
- Fallback behavior

## Selection rule

Discover available skills, connectors and local executables before selecting a provider. Prefer a callable, authorized tool that can save local outputs and expose stable identifiers. Record tool/model/version and important parameters in the project manifest. Do not install software, transmit personal files or use paid services without the user's authorization.

## Directing

The article used `pyang5166/gbro-collage-broll`. If it is installed, use it for per-line visual direction and retain its confirmation gates. Otherwise implement the directing and schema steps in this skill directly.

## Image generation

Prefer the available ImageGen skill/tool for keyframes. Generate an approved end frame before deriving a start frame. When image editing supports references, use the approved style/character images to preserve continuity.

## Image-to-video

Use Agnes AI as the default provider with model `agnes-video-v2.0`. Read [agnes-ai-video.md](agnes-ai-video.md) and use `scripts/agnes_ai_video.py` to construct the keyframe command. Require a locked camera, exact aspect ratio, no generated audio and a locally downloaded MP4. Always run `--dry-run` before the pilot. External CLI execution can upload local keyframes and start a remote generation job; do it only after the user explicitly authorizes that transmission and any current cost. If Agnes is unavailable, stop after approved keyframes and create `handoff/motion-jobs.json` rather than silently switching providers.

## TTS

Use the bundled `scripts/edge_xiaoyi_tts.py` adapter as the default for Chinese child-friendly explainers. It calls the online Microsoft Edge Neural TTS preset `zh-CN-XiaoyiNeural` once per shot with rate `+6%`, pitch `+10Hz` and volume `+0%`, then creates 48 kHz mono WAV files using an 80 Hz high-pass, `loudnorm=I=-18:TP=-2:LRA=7`, and 0.45 seconds of natural tail padding. The adapter writes cumulative measured timing to `audio/timing.json`.

Resolve `edge-tts` from `--edge-tts`, `EDGE_TTS_BIN`, or `PATH`. The online request transmits narration text only. Do not use operating-system voices, do not upload media for TTS, and do not silently replace XiaoyiNeural with a cloned voice or a large local model. If the provider or executable is unavailable, preserve narration text and mark the audio layer blocked.

## Composition

The article used HyperFrames as an HTML-driven timeline. Prefer HyperFrames when callable. Otherwise use a local deterministic editor such as FFmpeg or a video-rendering skill. Maintain separate video, narration, subtitle and music tracks and export a reusable timeline manifest.

## Fallback behavior

Never pretend a named third-party skill is available. When a layer is unavailable, finish all preceding layers, write a handoff manifest containing inputs, prompts, expected outputs and QA criteria, and tell the user exactly what must be connected or installed.
