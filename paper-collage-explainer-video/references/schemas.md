# Project schemas

## Contents

- Project manifest
- Storyboard
- Visual specification
- Asset manifest
- Timing
- QA

Use zero-padded shot IDs: `shot-01`, `shot-02`, and so on. Store UTF-8 JSON with two-space indentation.

## Project manifest

```json
{
  "title": "Example",
  "language": "zh-CN",
  "target_duration_s": 90,
  "aspect_ratio": "16:9",
  "width": 1280,
  "height": 720,
  "fps": 24,
  "status": "planning"
}
```

## Storyboard

`story/storyboard.json` is an array of objects:

```json
{
  "id": "shot-01",
  "narration": "Why do people sell winners and hold losers?",
  "target_duration_s": 5,
  "claim": "People treat gains and losses asymmetrically.",
  "source_ids": ["src-01"],
  "visual_metaphor": "One figure pushes away a blooming rising card while hugging a sinking wilted card.",
  "composition": "Centered figure; red rising path left; teal falling path right.",
  "assembly_order": ["background", "figure", "red_path", "teal_path"],
  "transition": "hard_cut"
}
```

## Visual specification

Each `visual/specs/shot-NN.json` contains `id`, `aspect_ratio`, `palette`, `background`, `camera`, `paper_groups`, `start_state`, `end_state`, `assembly_order`, `generation_prompt`, `motion_prompt`, `negative_constraints`, and `continuity_refs`.

Each paper group contains `name`, `appearance`, `position`, `depth`, `entrance`, and `final_state`.

In high-detail mode each visual spec also contains `concrete_assets` with 5–12 narration-relevant recognizable items and `unique_composition_key` describing what makes the shot spatially distinct.

## Asset manifest

`visual/asset-manifest.json` is required when `project.json.visual_quality.mode` is `high-detail`:

```json
{
  "shots": [
    {
      "id": "shot-01",
      "primary_subjects": ["child observer", "family car"],
      "environment_assets": ["highway", "utility poles", "mountains"],
      "mechanism_assets": ["heat haze", "curved light path"],
      "supporting_assets": ["truck", "shrubs"],
      "concrete_asset_count": 9,
      "unique_composition_key": "low road perspective toward false puddle"
    }
  ]
}
```

Count only visible, narration-relevant assets. Do not count texture, shadows, background color, repeated particles or decorative clutter as separate assets.

## Timing

```json
{
  "shots": [
    {"id": "shot-01", "audio_file": "audio/aligned/shot-01.wav", "start_s": 0.0, "duration_s": 4.82}
  ],
  "total_duration_s": 4.82
}
```

Derive `start_s` cumulatively. Never estimate it from target script duration after WAV files exist.

## QA

Machine-readable QA records contain `id`, `status` (`pass`, `pass_with_deviation`, or `redo`), `checks`, `deviations`, `action`, `reviewer`, and `reviewed_at`. Critical failures—wrong metaphor, unsafe voice use, unreadable shot, missing narration, severe anatomy, fake text or watermark—must use `redo`.
