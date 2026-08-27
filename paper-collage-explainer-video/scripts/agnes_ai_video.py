#!/usr/bin/env python3
"""Build, submit, or complete one Agnes AI keyframe-video job."""

import argparse
import json
import os
import shlex
import subprocess
import sys
import urllib.request
from pathlib import Path


CLI = ["npx", "-y", "agnes-ai-cli@^0.1.6"]
MODEL = "agnes-video-v2.0"


def parse_json(text):
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    for line in reversed(text.splitlines()):
        try:
            return json.loads(line)
        except json.JSONDecodeError:
            pass
    raise RuntimeError("Agnes CLI did not return JSON")


def find_value(value, keys):
    if isinstance(value, dict):
        for key in keys:
            if value.get(key):
                return value[key]
        for child in value.values():
            found = find_value(child, keys)
            if found:
                return found
    elif isinstance(value, list):
        for child in value:
            found = find_value(child, keys)
            if found:
                return found
    return None


def run(command):
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    return parse_json(result.stdout)


def main():
    parser = argparse.ArgumentParser(description="Generate an Agnes AI keyframe video")
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    parser.add_argument("--prompt")
    parser.add_argument("--prompt-file")
    parser.add_argument("--output", required=True)
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=720)
    parser.add_argument("--num-frames", type=int, default=121)
    parser.add_argument("--frame-rate", type=int, default=24)
    parser.add_argument("--ttl", default="1h")
    parser.add_argument("--poll-interval", type=int, default=10)
    parser.add_argument("--timeout", type=int, default=1200)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--submit-only", action="store_true")
    mode.add_argument("--execute", action="store_true")
    args = parser.parse_args()

    start = Path(args.start).expanduser().resolve()
    end = Path(args.end).expanduser().resolve()
    output = Path(args.output).expanduser().resolve()
    if not start.is_file() or not end.is_file():
        parser.error("Both --start and --end must be existing image files")
    if bool(args.prompt) == bool(args.prompt_file):
        parser.error("Pass exactly one of --prompt or --prompt-file")
    prompt = args.prompt or Path(args.prompt_file).read_text(encoding="utf-8").strip()
    if not prompt:
        parser.error("Prompt must not be empty")
    if args.num_frames > 441 or (args.num_frames - 1) % 8:
        parser.error("--num-frames must be no more than 441 and follow 8n + 1")

    create = CLI + [
        "video", "keyframes",
        "--image", str(start), "--image", str(end),
        "--prompt", prompt,
        "--width", str(args.width), "--height", str(args.height),
        "--num-frames", str(args.num_frames),
        "--frame-rate", str(args.frame_rate),
        "--ttl", args.ttl, "--json",
    ]
    preview = {
        "provider": "Agnes AI", "model": MODEL, "mode": "keyframes",
        "width": args.width, "height": args.height,
        "num_frames": args.num_frames, "frame_rate": args.frame_rate,
        "start": str(start), "end": str(end), "output": str(output),
        "command": " ".join(shlex.quote(part) for part in create),
    }
    if args.dry_run:
        print(json.dumps(preview, ensure_ascii=False, indent=2))
        return
    if not os.getenv("AGNES_API_KEY"):
        parser.error("Set AGNES_API_KEY before submitting a live request")

    submitted = run(create)
    video_id = find_value(submitted, ("videoId", "video_id", "taskId", "task_id", "id"))
    if not video_id:
        raise RuntimeError("Could not find a video/task ID in Agnes response")
    output.parent.mkdir(parents=True, exist_ok=True)
    submitted_path = output.with_suffix(output.suffix + ".submitted.json")
    submitted_meta = {**preview, "video_id": video_id, "submitted": submitted}
    submitted_path.write_text(
        json.dumps(submitted_meta, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    if args.submit_only:
        print(submitted_path)
        return

    completed = run(CLI + [
        "video", "poll", str(video_id),
        "--interval", str(args.poll_interval),
        "--timeout", str(args.timeout), "--json",
    ])
    video_url = find_value(completed, ("videoUrl", "video_url", "url"))
    if not video_url:
        raise RuntimeError("Could not find the completed video URL")
    urllib.request.urlretrieve(video_url, output)
    metadata = {**submitted_meta, "completed": completed}
    output.with_suffix(output.suffix + ".json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(output)


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or "").strip() or (exc.stdout or "").strip() or str(exc)
        print(detail, file=sys.stderr)
        raise SystemExit(exc.returncode)
