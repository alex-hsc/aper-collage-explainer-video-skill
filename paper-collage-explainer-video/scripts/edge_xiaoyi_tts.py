#!/usr/bin/env python3
"""Generate the series-standard XiaoyiNeural narration and measured timing."""

import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path


def resolve_program(explicit, env_name, name):
    if explicit:
        path = Path(explicit).expanduser()
        if path.is_file():
            return str(path.resolve())
        raise SystemExit("Missing executable: {}".format(path))
    env_value = os.getenv(env_name)
    if env_value and Path(env_value).expanduser().is_file():
        return str(Path(env_value).expanduser().resolve())
    found = shutil.which(name)
    if found:
        return found
    raise SystemExit("Could not resolve {}. Pass --{} or set {}.".format(name, name, env_name))


def duration(ffprobe, path):
    output = subprocess.check_output([
        ffprobe, "-v", "error", "-show_entries", "format=duration",
        "-of", "default=nw=1:nk=1", str(path)
    ], universal_newlines=True)
    return round(float(output.strip()), 3)


def main():
    parser = argparse.ArgumentParser(description="Generate XiaoyiNeural narration per storyboard shot")
    parser.add_argument("project_dir")
    parser.add_argument("--storyboard", default="story/storyboard.json")
    parser.add_argument("--edge-tts")
    parser.add_argument("--ffmpeg")
    parser.add_argument("--ffprobe")
    parser.add_argument("--voice", default="zh-CN-XiaoyiNeural")
    parser.add_argument("--rate", default="+6%")
    parser.add_argument("--pitch", default="+10Hz")
    parser.add_argument("--volume", default="+0%")
    parser.add_argument("--tail-padding", type=float, default=0.45)
    args = parser.parse_args()

    project = Path(args.project_dir).expanduser().resolve()
    storyboard = project / args.storyboard
    if not storyboard.is_file():
        parser.error("Missing storyboard: {}".format(storyboard))
    edge_tts = resolve_program(args.edge_tts, "EDGE_TTS_BIN", "edge-tts")
    ffmpeg = resolve_program(args.ffmpeg, "FFMPEG_BIN", "ffmpeg")
    ffprobe = resolve_program(args.ffprobe, "FFPROBE_BIN", "ffprobe")
    shots = json.loads(storyboard.read_text(encoding="utf-8"))
    if not isinstance(shots, list) or not shots:
        parser.error("Storyboard must be a non-empty JSON array")

    raw_dir = project / "audio" / "raw"
    aligned_dir = project / "audio" / "aligned"
    raw_dir.mkdir(parents=True, exist_ok=True)
    aligned_dir.mkdir(parents=True, exist_ok=True)
    timing = []
    cursor = 0.0
    for shot in shots:
        shot_id = shot["id"]
        narration = shot["narration"].strip()
        if not narration:
            raise SystemExit("Empty narration for {}".format(shot_id))
        mp3 = raw_dir / (shot_id + ".mp3")
        wav = aligned_dir / (shot_id + ".wav")
        subprocess.run([
            edge_tts, "--voice", args.voice, "--rate", args.rate,
            "--pitch", args.pitch, "--volume", args.volume,
            "--text", narration, "--write-media", str(mp3)
        ], check=True)
        audio_filter = (
            "highpass=f=80,loudnorm=I=-18:TP=-2:LRA=7,"
            "apad=pad_dur={}".format(args.tail_padding)
        )
        subprocess.run([
            ffmpeg, "-y", "-loglevel", "error", "-i", str(mp3),
            "-af", audio_filter, "-ar", "48000", "-ac", "1", str(wav)
        ], check=True)
        measured = duration(ffprobe, wav)
        timing.append({
            "id": shot_id,
            "audio_file": "audio/aligned/{}.wav".format(shot_id),
            "start_s": round(cursor, 3),
            "duration_s": measured
        })
        cursor += measured

    output = {
        "provider": "Microsoft Edge Neural TTS",
        "voice": args.voice,
        "rate": args.rate,
        "pitch": args.pitch,
        "volume": args.volume,
        "postprocess": "highpass=f=80,loudnorm=I=-18:TP=-2:LRA=7",
        "tail_padding_s": args.tail_padding,
        "sample_rate_hz": 48000,
        "channels": 1,
        "master_clock": "audio",
        "shots": timing,
        "total_duration_s": round(cursor, 3)
    }
    timing_path = project / "audio" / "timing.json"
    timing_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(timing_path)


if __name__ == "__main__":
    main()
