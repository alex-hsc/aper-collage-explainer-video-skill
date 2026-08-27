---
name: paper-collage-explainer-video
description: Create or reproduce coherent paper-collage/Vox-style explainer videos end to end, from topic research, factual script, narration lines and visual metaphors through structured visual specs, consistent keyframes, image-to-video shots, authorized TTS, timed subtitles, editing, rendering and QA. Use when users ask for 纸拼贴动画、贴纸动画、Vox 风格科普视频、横屏或竖屏知识解说、首尾帧生视频、逐镜可返工的 AI 动画，or want to analyze a reference video's narrative/visual grammar and produce an original—not copied—version.
---

# Paper-collage explainer video

Build a modular five-layer pipeline. Save every intermediate artifact and rerun only failed shots. Treat audio as the master clock in the final edit.

## Start the project

1. Determine topic, audience, language, target duration, aspect ratio, factual stakes, voice source and output directory from the request. Default to 60–90 seconds, 16:9, 1280×720, 24 fps and 4–6 seconds per shot.
2. If facts may be current, disputed, medical, legal or financial, research with primary/authoritative sources and preserve citations in `research/sources.md`. Separate educational explanation from advice.
3. Run `python3 scripts/init_project.py <project-dir> --title "..." --duration 90 --aspect 16:9` from this skill directory.
4. Read [references/art-direction.md](references/art-direction.md) before writing visual specs. Read [references/schemas.md](references/schemas.md) before producing machine-readable manifests. Read [references/tool-adapters.md](references/tool-adapters.md) when selecting generation, TTS or composition tools. Read [references/agnes-ai-video.md](references/agnes-ai-video.md) before generating motion with Agnes AI.
5. First complete one 5-second pilot shot. Expand only after it passes the same gates and QA used by the full project.

## Execute the five layers

### 1. Directing layer

1. Distill one central claim and a narrative arc: hook → intuitive example → mechanism → consequence → takeaway.
2. Write conversational narration at a pace suitable for the target language. Split it into shots of roughly 4–6 seconds; keep one idea per shot.
3. Translate every line into one visible action and one visual metaphor. Avoid literal keyword illustration, generic charts, decorative clutter and on-screen prose.
4. Write `story/storyboard.json` using the schema reference. Include narration, target duration, metaphor, composition, assembly order, factual support and transition intent.
5. Present a concise shot table and stop at **Gate 1: metaphor approval** when the user is actively collaborating. If the user explicitly requests autonomous completion, record the self-review decision in `qa/gate-1.md` and continue.

Gate 1 passes only when each shot remains understandable without subtitles, communicates one idea, and does not depend on logos, UI, fake text or copyrighted characters.

### 2. Visual layer

1. Establish one project-wide style bible in `visual/style-bible.json`: palette, background, halftone treatment, paper edges, outlines, shadows, recurring character design, aspect ratio and negative constraints.
2. Write one `visual/specs/shot-NN.json` per shot. Specify 3–6 large paper groups, their position/depth, start state, end state, assembly order and prohibited elements.
3. Generate a confirmed end frame first. Use the same style bible and recurring reference assets for every shot. Do not put captions, numbers, logos, UI or watermarks into generated frames unless essential and explicitly requested.
4. Create the start frame by removing staged paper groups from the approved end frame while preserving the background and camera. Prefer an empty or nearly empty color field.
5. Inspect metaphor clarity, anatomy/hands, accidental text, palette continuity, clean cut-paper edges and whether the scene can be decomposed into 3–6 groups.
6. Stop at **Gate 2: keyframe approval** under interactive collaboration. Under autonomous execution, log the visual QA and continue only when all critical checks pass.

Do not proceed to animation when the end frame is conceptually wrong. Regenerate the failed frame, not the entire project.

### 3. Motion layer

1. Use Agnes AI `agnes-video-v2.0` as the default motion model. Generate one shot at a time from the approved start/end frames with the `video keyframes` workflow. Keep the camera locked.
2. Prompt only the motion between frames: paper pieces slide, pop, unfold or assemble in the exact `assembly_order`. Prohibit cuts, zooms, morphing, new objects, text and generated audio.
3. Run `python3 scripts/agnes_ai_video.py ... --dry-run` for the pilot before any live request. After explicit authorization for external execution, run the emitted Agnes CLI command, poll the asynchronous job, download the completed MP4, and save it as `motion/raw/shot-NN.mp4`. Normalize accepted clips to project resolution/fps under `motion/accepted/`.
4. Run per-shot QA: start-frame cleanliness, sequential entry, stable camera, object identity, end-frame similarity, no extras/fake text/logo/watermark and no audio track.
5. Mark each shot `pass`, `pass_with_deviation`, or `redo` in `qa/motion.json`. Keep harmless deviations only when comprehension and continuity remain intact.

### 4. Audio layer

1. Default to Microsoft Edge Neural TTS `zh-CN-XiaoyiNeural` for Chinese child-friendly explainers. Use `scripts/edge_xiaoyi_tts.py` with rate `+6%`, pitch `+10Hz`, volume `+0%`, 80 Hz high-pass, loudness `-18 LUFS`, true peak `-2 dB`, LRA `7`, and `0.45` seconds of tail padding per shot. This is the established voice used by the series; do not replace it with an operating-system voice.
2. Treat XiaoyiNeural as a generic synthetic preset, not a real-person identity. Never clone another person's voice without explicit authorization. Send narration text only to the online synthesizer; do not upload keyframes or personal files for TTS.
3. Generate narration per shot, not as one long file. Save provider MP3 files in `audio/raw/` and normalized 48 kHz mono WAV files in `audio/aligned/`.
4. Measure actual WAV duration and write it cumulatively to `audio/timing.json`. Treat this duration as authoritative for the edit; retime visuals, never the narration.
5. Check pronunciation, child-friendly warmth, intelligibility, clipping, noise and line-to-shot mapping. If Edge TTS or XiaoyiNeural is unavailable, stop at the audio layer and create a handoff rather than silently switching to `say`, another system voice, a cloned voice or a large local model.

### 5. Composition layer

1. Build the timeline from `audio/timing.json`. Start each shot at the cumulative end of the previous narration segment.
2. Conform accepted clips to the delivery format; remove or mute all model-generated audio.
3. Retiming visuals—not narration—to match each audio segment. Trim idle tails and pauses when possible; otherwise adjust clip playback speed conservatively.
4. Generate subtitles from the approved narration using the same start/duration values. Use high-contrast text with outline/shadow inside safe margins; do not bake subtitles into source frames. When wrapping Chinese subtitles, never begin a continuation line with punctuation. Keep `，。！？；：、）》】”’` and equivalent Western punctuation attached to the preceding phrase; move the break earlier when necessary.
5. Place video, narration, subtitles and optional licensed music on separate tracks. Keep music below speech and preserve model-generated ambience only when explicitly desired and verified.
6. Render the final MP4 and a timeline manifest. Re-render only the composition layer when changing captions, timing, music or voice.

## Validate and deliver

1. Run `python3 scripts/validate_project.py <project-dir>`.
2. Watch the complete rendered video from start to finish. Check A/V sync, subtitle timing/safe area, continuation-line leading punctuation, abrupt cuts, frozen frames, color/style drift, missing audio, duplicated lines, spelling, factual accuracy and final-frame integrity.
3. Save `qa/final.md` with pass/fail findings and any accepted deviations.
4. Deliver the final MP4 plus a brief report listing duration, resolution/fps, shot count, tools/models used, factual sources, voice authorization basis, XiaoyiNeural parameters, known deviations and paths to editable manifests.
5. Never claim completion when a required tool is missing or a render has not been watched. Produce a handoff manifest and name the exact blocked layer instead.

## Analyze a reference video

Extract only transferable grammar: hook timing, average shot length, metaphor density, palette, paper texture, assembly vocabulary, subtitle rhythm and narrative structure. Create new wording, imagery and shot designs. Do not reproduce distinctive frames, characters, logos, music or a creator's exact sequence.

## Replacement and recovery rules

- Keep layers tool-independent; consult the adapter reference and use the best available tool.
- Preserve stable filenames and manifest schemas when replacing a model.
- Retry only the failed shot or layer.
- If generation repeatedly violates a constraint, simplify the scene before increasing prompt length.
- If duration drifts, update from measured WAV durations and rebuild the timeline.
- If text appears in images, remove it from the prompt and add the text later in composition.
