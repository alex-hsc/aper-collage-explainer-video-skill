#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Initialize a modular paper-collage explainer project")
    parser.add_argument("project_dir")
    parser.add_argument("--title", required=True)
    parser.add_argument("--duration", type=float, default=90)
    parser.add_argument("--aspect", choices=("16:9", "9:16"), default="16:9")
    parser.add_argument("--language", default="zh-CN")
    args = parser.parse_args()

    root = Path(args.project_dir).expanduser().resolve()
    width, height = ((1280, 720) if args.aspect == "16:9" else (720, 1280))
    directories = (
        "research", "story", "visual/specs", "visual/start-frames", "visual/end-frames",
        "motion/raw", "motion/accepted", "audio/raw", "audio/aligned", "subtitles",
        "composition", "renders", "qa", "handoff"
    )
    for directory in directories:
        (root / directory).mkdir(parents=True, exist_ok=True)

    manifest = {
        "title": args.title,
        "language": args.language,
        "target_duration_s": args.duration,
        "aspect_ratio": args.aspect,
        "width": width,
        "height": height,
        "fps": 24,
        "status": "planning",
        "visual_quality": {
            "mode": "high-detail",
            "min_concrete_assets_per_shot": 5,
            "max_recommended_assets_per_shot": 12,
            "require_asset_manifest": True,
            "require_contact_sheet": True
        },
        "tools": {
            "motion": {
                "provider": "Agnes AI",
                "model": "agnes-video-v2.0",
                "mode": "keyframes"
            }
        }
    }
    path = root / "project.json"
    if not path.exists():
        path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(path)


if __name__ == "__main__":
    main()
