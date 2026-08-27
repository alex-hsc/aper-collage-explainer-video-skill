# Agnes AI video setup

Use Agnes AI model `agnes-video-v2.0` for the motion layer. The API is asynchronous and supports image-to-video and explicit keyframe interpolation.

## Preconditions

1. Create an API key at `https://platform.agnes-ai.com/settings/apiKeys`.
2. Export it as `AGNES_API_KEY`; never store it in the project or print it.
3. Prefer the published `agnes-ai-cli` execution layer. Verify current syntax with its `video keyframes --help` before live use because provider interfaces can change. The bundled adapter targets the `0.1.x` CLI syntax verified with `0.1.6`.
4. Treat local keyframes as uploaded data. Obtain authorization before uploading them or starting a remote job.

## Per-shot workflow

1. Confirm both keyframes exist and match the project aspect ratio.
2. Build the request without executing it:

```bash
python3 scripts/agnes_ai_video.py \
  --start visual/start-frames/shot-01.png \
  --end visual/end-frames/shot-01.png \
  --prompt-file motion/prompts/shot-01.txt \
  --output motion/raw/shot-01.mp4 \
  --dry-run
```

3. Inspect the command and prompt. The motion prompt must say what moves, what stays fixed, the assembly order, and that the camera is locked. Prohibit cuts, zooms, morphs, new objects, text, logos, watermarks and audio.
4. After authorization, rerun with `--execute`. The adapter invokes the CLI keyframe workflow, requests JSON output, saves the submitted task ID immediately, polls the returned video ID and downloads the resulting URL.
5. Save request metadata beside the MP4 as `shot-NN.mp4.json`, excluding credentials.
6. Normalize and QA the clip using the main skill gates.

## Operational constraints

- Use `AGNES_API_KEY` only from the environment.
- Default to model `agnes-video-v2.0`.
- Agnes video jobs are asynchronous; never treat submission as completion.
- Agnes frame counts must be no more than 441 and follow `8n + 1` when exposed by the current CLI/API.
- Provider rate limits may allow only one new video task per minute. Submit shots sequentially and retry only an individual rate-limited shot after the reported cooldown.
- Do not silently switch providers. Produce a motion handoff manifest when Agnes cannot run.
