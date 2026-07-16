#!/usr/bin/env python3
"""Render slide images at manifest timings, optionally with final voiceover audio."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path


def ffconcat_quote(path: Path) -> str:
    return path.resolve().as_posix().replace("'", "'\\''")


def manifest_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_storyboard_approval(manifest_path: Path, approval_path: Path) -> dict:
    if not approval_path.exists():
        raise PermissionError(
            "Video rendering is blocked until the user reviews the completed storyboard. "
            f"After explicit approval, create {approval_path.name} with "
            "scripts/approve_storyboard.py."
        )
    receipt = json.loads(approval_path.read_text(encoding="utf-8"))
    if receipt.get("approval_type") != "explicit-user-storyboard-approval":
        raise PermissionError("Storyboard approval receipt has an invalid approval type")
    current_hash = manifest_sha256(manifest_path)
    if receipt.get("manifest_sha256") != current_hash:
        raise PermissionError(
            "Storyboard approval is stale because the slide manifest changed. "
            "Present the revised storyboard and obtain explicit approval again."
        )
    return receipt


def build_concat(manifest: dict, images_dir: Path, concat_path: Path) -> list[Path]:
    files = []
    lines = ["ffconcat version 1.0"]
    missing = []
    for slide in manifest["slides"]:
        image = images_dir / slide["image_file"]
        if not image.exists():
            missing.append(image)
            continue
        duration = float(slide["duration_seconds"])
        if duration <= 0:
            raise ValueError(f"Slide {slide['slide']} has a non-positive duration")
        files.append(image)
        lines.append(f"file '{ffconcat_quote(image)}'")
        lines.append(f"duration {duration:.6f}")
    if missing:
        preview = "\n".join(f"- {path}" for path in missing[:20])
        suffix = f"\n...and {len(missing) - 20} more" if len(missing) > 20 else ""
        raise FileNotFoundError(f"Missing {len(missing)} slide images:\n{preview}{suffix}")
    if not files:
        raise ValueError("Manifest contains no slides")
    # The concat demuxer ignores the final duration unless the last file repeats.
    lines.append(f"file '{ffconcat_quote(files[-1])}'")
    # Keep the sentinel duplicate to one millisecond so filters do not inherit
    # and repeat the preceding slide's full duration.
    lines.append("duration 0.001000")
    concat_path.parent.mkdir(parents=True, exist_ok=True)
    concat_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return files


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--images-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--audio", type=Path)
    parser.add_argument(
        "--approval",
        type=Path,
        help="Approval receipt; defaults to storyboard-approval.json beside the manifest.",
    )
    parser.add_argument("--width", type=int, default=1920)
    parser.add_argument("--height", type=int, default=1080)
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text())
    if not args.check_only:
        approval_path = args.approval or args.manifest.parent / "storyboard-approval.json"
        receipt = verify_storyboard_approval(args.manifest, approval_path)
        print(f"Storyboard approval verified: {receipt['approved_at_utc']}")
    concat_path = args.output.with_suffix(".ffconcat")
    files = build_concat(manifest, args.images_dir, concat_path)
    total = sum(float(slide["duration_seconds"]) for slide in manifest["slides"])
    print(f"Slides verified: {len(files)}")
    print(f"Timeline duration: {total:.3f} seconds")
    print(f"Concat timeline: {concat_path}")
    if args.check_only:
        return
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg is required to render the slideshow")
    if args.audio and not args.audio.exists():
        raise FileNotFoundError(args.audio)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat_path),
    ]
    if args.audio:
        command.extend(["-i", str(args.audio)])
    command.extend(
        [
            "-vf",
            (
                f"scale={args.width}:{args.height}:force_original_aspect_ratio=decrease,"
                f"pad={args.width}:{args.height}:(ow-iw)/2:(oh-ih)/2:color=black,"
                f"fps={args.fps},format=yuv420p"
            ),
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "18",
        ]
    )
    if args.audio:
        command.extend(["-c:a", "aac", "-b:a", "192k", "-shortest"])
    else:
        command.append("-an")
    command.extend(["-t", f"{total:.6f}"])
    command.append(str(args.output))
    subprocess.run(command, check=True)
    print(f"Rendered video: {args.output}")


if __name__ == "__main__":
    main()
