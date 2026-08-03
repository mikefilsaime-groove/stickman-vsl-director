#!/usr/bin/env python3
"""Render every approved slide through a frame-counted CFR segment timeline."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from verify_slideshow import VerificationError, frame_allocation, probe_video, verify_slideshow


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


def run(command: list[str], *, capture: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(command, check=True, capture_output=capture)


def validate_inputs(manifest: dict, images_dir: Path, fps: int) -> tuple[list[Path], dict]:
    slides = manifest.get("slides", [])
    if not slides:
        raise ValueError("Manifest contains no slides")
    expected_numbers = list(range(1, len(slides) + 1))
    if [slide["slide"] for slide in slides] != expected_numbers:
        raise ValueError("Manifest slide numbers are not continuous from 1")

    images = [images_dir / slide["image_file"] for slide in slides]
    missing = [str(image) for image in images if not image.exists()]
    if missing:
        preview = "\n".join(f"- {path}" for path in missing[:20])
        suffix = f"\n...and {len(missing) - 20} more" if len(missing) > 20 else ""
        raise FileNotFoundError(f"Missing {len(missing)} slide images:\n{preview}{suffix}")
    allocation = frame_allocation(manifest, fps)
    return images, allocation


def write_timeline_artifacts(
    manifest: dict,
    images: list[Path],
    allocation: dict,
    output: Path,
) -> tuple[Path, Path]:
    timeline_path = output.with_suffix(".ffconcat")
    timeline_lines = ["ffconcat version 1.0"]
    for slide, image in zip(manifest["slides"], images):
        timeline_lines.append(f"file '{ffconcat_quote(image)}'")
        timeline_lines.append("option framerate 1000")
        timeline_lines.append(f"duration {float(slide['duration_seconds']):.6f}")
    timeline_lines.append(f"file '{ffconcat_quote(images[-1])}'")
    timeline_lines.append("option framerate 1000")
    timeline_lines.append("duration 0.001000")
    timeline_path.write_text("\n".join(timeline_lines) + "\n")

    allocation_path = output.with_suffix(".frame-allocation.json")
    allocation_report = {
        "fps": allocation["fps"],
        "duration_seconds": allocation["duration_seconds"],
        "total_frames": allocation["total_frames"],
        "slides": [],
    }
    for index, (slide, frame_count) in enumerate(
        zip(manifest["slides"], allocation["frame_counts"])
    ):
        allocation_report["slides"].append(
            {
                "slide": slide["slide"],
                "image_file": slide["image_file"],
                "start_frame": allocation["boundaries"][index],
                "end_frame_exclusive": allocation["boundaries"][index + 1],
                "frame_count": frame_count,
            }
        )
    allocation_path.write_text(json.dumps(allocation_report, indent=2) + "\n")
    return timeline_path, allocation_path


def encode_segment(
    image: Path,
    output: Path,
    frame_count: int,
    fps: int,
    width: int,
    height: int,
) -> tuple[Path, int]:
    key_interval = frame_count + 1
    run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-loop",
            "1",
            "-framerate",
            str(fps),
            "-i",
            str(image),
            "-vf",
            (
                f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
                f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:color=black,"
                "format=yuv420p"
            ),
            "-frames:v",
            str(frame_count),
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "18",
            "-tune",
            "stillimage",
            "-pix_fmt",
            "yuv420p",
            "-r",
            str(fps),
            "-fps_mode",
            "cfr",
            "-g",
            str(key_interval),
            "-keyint_min",
            str(key_interval),
            "-sc_threshold",
            "0",
            "-bf",
            "0",
            "-threads",
            "2",
            "-video_track_timescale",
            "90000",
            "-movflags",
            "+faststart",
            str(output),
        ]
    )
    probe = probe_video(output)
    actual_frames = int(probe.get("nb_read_frames") or probe.get("nb_frames") or 0)
    if actual_frames != frame_count:
        raise VerificationError(
            f"Segment {output.name} contains {actual_frames} frames; expected {frame_count}"
        )
    if probe.get("avg_frame_rate") != f"{fps}/1":
        raise VerificationError(
            f"Segment {output.name} is {probe.get('avg_frame_rate')}; expected {fps}/1 CFR"
        )
    return output, actual_frames


def render_segments(
    images: list[Path],
    allocation: dict,
    segment_dir: Path,
    *,
    fps: int,
    width: int,
    height: int,
    workers: int,
) -> list[Path]:
    segment_dir.mkdir(parents=True, exist_ok=True)
    jobs = []
    for index, (image, frame_count) in enumerate(
        zip(images, allocation["frame_counts"]), start=1
    ):
        jobs.append((image, segment_dir / f"slide-{index:04d}.mp4", frame_count))

    print(
        f"Encoding {len(jobs)} independent CFR slide segments: "
        f"{allocation['total_frames']} total frames at {fps} fps",
        flush=True,
    )
    completed = 0
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(
                encode_segment,
                image,
                segment,
                frame_count,
                fps,
                width,
                height,
            ): segment
            for image, segment, frame_count in jobs
        }
        for future in as_completed(futures):
            future.result()
            completed += 1
            if completed == 1 or completed % 10 == 0 or completed == len(jobs):
                print(f"Segments verified: {completed}/{len(jobs)}", flush=True)
    return [segment for _, segment, _ in jobs]


def concatenate_segments(segments: list[Path], output: Path, concat_path: Path) -> None:
    lines = ["ffconcat version 1.0"]
    lines.extend(f"file '{ffconcat_quote(segment)}'" for segment in segments)
    concat_path.write_text("\n".join(lines) + "\n")
    run(
        [
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
            "-map",
            "0:v:0",
            "-c:v",
            "copy",
            "-movflags",
            "+faststart",
            str(output),
        ]
    )


def mux_audio(video: Path, audio: Path, output: Path, duration: float) -> None:
    run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(video),
            "-i",
            str(audio),
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-t",
            f"{duration:.6f}",
            "-movflags",
            "+faststart",
            str(output),
        ]
    )


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
    parser.add_argument("--workers", type=int, default=min(4, os.cpu_count() or 1))
    parser.add_argument("--verification-threshold", type=float, default=6.0)
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()

    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        raise RuntimeError("ffmpeg and ffprobe are required to render the slideshow")
    manifest = json.loads(args.manifest.read_text())
    images, allocation = validate_inputs(manifest, args.images_dir, args.fps)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    timeline_path, allocation_path = write_timeline_artifacts(
        manifest, images, allocation, args.output
    )
    print(f"Slides verified before render: {len(images)}")
    print(f"Timeline duration: {allocation['duration_seconds']:.3f} seconds")
    print(f"Required CFR frames: {allocation['total_frames']}")
    print(f"Timeline record: {timeline_path}")
    print(f"Frame allocation: {allocation_path}")
    if args.check_only:
        return

    approval_path = args.approval or args.manifest.parent / "storyboard-approval.json"
    receipt = verify_storyboard_approval(args.manifest, approval_path)
    print(f"Storyboard approval verified: {receipt['approved_at_utc']}")
    if receipt.get("slide_count") not in (None, len(images)):
        raise PermissionError(
            f"Approval covers {receipt.get('slide_count')} slides; manifest contains {len(images)}"
        )
    if args.audio and not args.audio.exists():
        raise FileNotFoundError(args.audio)

    candidate = args.output.with_name(f".{args.output.stem}.verified-candidate{args.output.suffix}")
    report_path = args.output.with_suffix(".verification.json")
    with tempfile.TemporaryDirectory(
        prefix=f".{args.output.stem}-render-", dir=args.output.parent
    ) as temporary:
        temporary_dir = Path(temporary)
        segments = render_segments(
            images,
            allocation,
            temporary_dir / "segments",
            fps=args.fps,
            width=args.width,
            height=args.height,
            workers=args.workers,
        )
        video_only = temporary_dir / "all-slides-video-only.mp4"
        concatenate_segments(
            segments,
            video_only,
            temporary_dir / "all-slides-segments.ffconcat",
        )
        if args.audio:
            mux_audio(video_only, args.audio, candidate, allocation["duration_seconds"])
        else:
            shutil.copy2(video_only, candidate)

        report = verify_slideshow(
            candidate,
            manifest,
            args.images_dir,
            fps=args.fps,
            threshold=args.verification_threshold,
            expect_audio=bool(args.audio),
            report_path=report_path,
        )

    os.replace(candidate, args.output)
    report["video"] = str(args.output.resolve())
    report_path.write_text(json.dumps(report, indent=2) + "\n")
    print(f"Rendered and verified video: {args.output}")
    print(f"Slides matched: {report['slides_passed']}/{report['slides_checked']}")
    print(
        f"CFR frames matched: {report['actual_video_frames']}/"
        f"{report['expected_video_frames']}"
    )
    print(
        f"Slide keyframes matched: {report['actual_keyframes']}/"
        f"{report['expected_keyframes']}"
    )
    print(f"Decoded source-image samples: {report['samples_checked']}")
    print(f"Verification report: {report_path}")


if __name__ == "__main__":
    main()
