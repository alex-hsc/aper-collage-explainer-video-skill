#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path


def load_json(path, errors):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"Invalid JSON {path}: {exc}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Validate a paper-collage explainer project")
    parser.add_argument("project_dir")
    args = parser.parse_args()
    root = Path(args.project_dir).expanduser().resolve()
    errors, warnings = [], []

    manifest_path = root / "project.json"
    if not manifest_path.exists():
        errors.append("Missing project.json")
        manifest = None
    else:
        manifest = load_json(manifest_path, errors)
    if manifest:
        for key in ("title", "aspect_ratio", "width", "height", "fps"):
            if key not in manifest:
                errors.append(f"project.json missing {key}")

    storyboard_path = root / "story/storyboard.json"
    storyboard = load_json(storyboard_path, errors) if storyboard_path.exists() else None
    if storyboard is None:
        warnings.append("Storyboard not present yet")
        shots = []
    else:
        shots = storyboard if isinstance(storyboard, list) else storyboard.get("shots", [])
        if not shots:
            errors.append("Storyboard contains no shots")
        ids = [shot.get("id") for shot in shots]
        if len(ids) != len(set(ids)):
            errors.append("Storyboard has duplicate shot IDs")
        for shot in shots:
            for key in ("id", "narration", "visual_metaphor", "assembly_order"):
                if not shot.get(key):
                    errors.append(f"Storyboard shot missing {key}: {shot.get('id', '?')}")
            shot_id = shot.get("id")
            if shot_id and not (root / f"visual/specs/{shot_id}.json").exists():
                warnings.append(f"Missing visual spec for {shot_id}")

    timing_path = root / "audio/timing.json"
    if timing_path.exists():
        timing = load_json(timing_path, errors)
        if timing:
            cursor = 0.0
            for item in timing.get("shots", []):
                if abs(float(item.get("start_s", -1)) - cursor) > 0.05:
                    errors.append(f"Non-cumulative timing at {item.get('id', '?')}")
                cursor += float(item.get("duration_s", 0))
    elif shots:
        warnings.append("Audio timing not present yet")

    final_candidates = list((root / "renders").glob("*.mp4")) if (root / "renders").exists() else []
    if not final_candidates:
        warnings.append("No final MP4 render yet")
    if not (root / "qa/final.md").exists():
        warnings.append("Final watch-through QA not recorded")

    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    print(f"Validation complete: {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
