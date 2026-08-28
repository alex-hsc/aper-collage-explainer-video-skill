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
    visual_quality = (manifest or {}).get("visual_quality", {})
    high_detail = visual_quality.get("mode") == "high-detail"
    min_assets = int(visual_quality.get("min_concrete_assets_per_shot", 5))

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

    asset_manifest_path = root / "visual/asset-manifest.json"
    if high_detail and shots:
        if not asset_manifest_path.exists():
            errors.append("High-detail project missing visual/asset-manifest.json")
        else:
            asset_manifest = load_json(asset_manifest_path, errors)
            asset_shots = asset_manifest.get("shots", []) if isinstance(asset_manifest, dict) else []
            by_id = {item.get("id"): item for item in asset_shots if isinstance(item, dict)}
            composition_keys = []
            for shot in shots:
                shot_id = shot.get("id")
                item = by_id.get(shot_id)
                if not item:
                    errors.append(f"Asset manifest missing {shot_id}")
                    continue
                required_lists = ("primary_subjects", "environment_assets", "mechanism_assets", "supporting_assets")
                for key in required_lists:
                    if not isinstance(item.get(key), list):
                        errors.append(f"Asset manifest {shot_id} missing list {key}")
                count = item.get("concrete_asset_count")
                if not isinstance(count, int) or count < min_assets:
                    errors.append(f"Asset manifest {shot_id} has fewer than {min_assets} concrete assets")
                composition_key = item.get("unique_composition_key")
                if not composition_key:
                    errors.append(f"Asset manifest {shot_id} missing unique_composition_key")
                composition_keys.append((shot_id, composition_key))
            for previous, current in zip(composition_keys, composition_keys[1:]):
                if previous[1] and previous[1] == current[1]:
                    errors.append(f"Adjacent shots reuse composition key: {previous[0]} and {current[0]}")

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
    elif high_detail and visual_quality.get("require_contact_sheet", True):
        contact_candidates = list((root / "qa").glob("*contact-sheet*"))
        if not contact_candidates:
            errors.append("High-detail final render missing all-shot contact sheet under qa/")
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
