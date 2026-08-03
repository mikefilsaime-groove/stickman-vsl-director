#!/usr/bin/env python3
"""Verify CFR structure and source-slide coverage for a rendered slideshow."""

from __future__ import annotations

import argparse
import json
import math
import subprocess
from pathlib import Path


THUMB_WIDTH = 64
THUMB_HEIGHT = 36
CHANNELS = 3
FRAME_BYTES = THUMB_WIDTH * THUMB_HEIGHT * CHANNELS


class VerificationError(RuntimeError):
    """Raised when a rendered slideshow cannot prove complete slide coverage."""


def run(command: list[str], *, capture: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(command, check=True, capture_output=capture)


def frame_allocation(manifest: dict, fps: int) -> dict:
    slides = manifest.get("slides", [])
    if not slides:
        raise VerificationError("Manifest contains no slides")
    if fps <= 0:
        raise VerificationError("FPS must be positive")

    for previous, current in zip(slides, slides[1:]):
        if abs(float(previous["end_seconds"]) - float(current["start_seconds"])) > 0.001:
            raise VerificationError(
                f"Timing gap or overlap between slides {previous['slide']} and {current['slide']}"
            )

    duration = float(slides[-1]["end_seconds"])
    total_frames = math.floor(duration * fps + 1e-9)
    boundaries = [round(float(slide["start_seconds"]) * fps) for slide in slides]
    boundaries.append(total_frames)
    counts = [right - left for left, right in zip(boundaries, boundaries[1:])]
    if boundaries[0] != 0:
        raise VerificationError("Storyboard must begin at 0 seconds")
    if any(count <= 0 for count in counts):
        raise VerificationError("At least one slide has no allocated video frames")
    if sum(counts) != total_frames:
        raise VerificationError("Slide frame counts do not reconcile to the total timeline")

    return {
        "fps": fps,
        "duration_seconds": duration,
        "total_frames": total_frames,
        "boundaries": boundaries,
        "frame_counts": counts,
    }


def probe_video(path: Path) -> dict:
    result = run(
        [
            "ffprobe",
            "-v",
            "error",
            "-count_frames",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=codec_name,width,height,pix_fmt,r_frame_rate,avg_frame_rate,duration,nb_frames,nb_read_frames",
            "-of",
            "json",
            str(path),
        ],
        capture=True,
    )
    streams = json.loads(result.stdout).get("streams", [])
    if not streams:
        raise VerificationError(f"No video stream found in {path}")
    return streams[0]


def probe_media(path: Path) -> dict:
    result = run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration,size:stream=index,codec_name,codec_type,duration,sample_rate,channels",
            "-of",
            "json",
            str(path),
        ],
        capture=True,
    )
    return json.loads(result.stdout)


def keyframe_count(path: Path) -> int:
    result = run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_frames",
            "-show_entries",
            "frame=key_frame",
            "-of",
            "json",
            str(path),
        ],
        capture=True,
    )
    return sum(frame.get("key_frame", 0) for frame in json.loads(result.stdout)["frames"])


def image_thumb(path: Path) -> bytes:
    result = run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-i",
            str(path),
            "-frames:v",
            "1",
            "-vf",
            f"scale={THUMB_WIDTH}:{THUMB_HEIGHT}:flags=lanczos,format=rgb24",
            "-f",
            "rawvideo",
            "pipe:1",
        ],
        capture=True,
    )
    if len(result.stdout) != FRAME_BYTES:
        raise VerificationError(f"Could not decode source slide {path}")
    return result.stdout


def video_thumbs(path: Path, frame_numbers: list[int]) -> list[bytes]:
    expression = "+".join(f"eq(n\\,{number})" for number in frame_numbers)
    result = run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-i",
            str(path),
            "-vf",
            (
                f"select={expression},"
                f"scale={THUMB_WIDTH}:{THUMB_HEIGHT}:flags=lanczos,format=rgb24"
            ),
            "-vsync",
            "0",
            "-f",
            "rawvideo",
            "pipe:1",
        ],
        capture=True,
    )
    expected_bytes = len(frame_numbers) * FRAME_BYTES
    if len(result.stdout) != expected_bytes:
        raise VerificationError(
            f"Decoded {len(result.stdout) // FRAME_BYTES} audit frames; "
            f"expected {len(frame_numbers)}"
        )
    return [
        result.stdout[index : index + FRAME_BYTES]
        for index in range(0, len(result.stdout), FRAME_BYTES)
    ]


def mean_absolute_error(left: bytes, right: bytes) -> float:
    return sum(abs(a - b) for a, b in zip(left, right)) / len(left)


def audit_slide_content(
    video: Path,
    manifest: dict,
    images_dir: Path,
    allocation: dict,
    threshold: float,
) -> dict:
    slides = manifest["slides"]
    missing = [
        str(images_dir / slide["image_file"])
        for slide in slides
        if not (images_dir / slide["image_file"]).exists()
    ]
    if missing:
        raise VerificationError(f"Missing source slides: {missing[:10]}")

    source_thumbs = [image_thumb(images_dir / slide["image_file"]) for slide in slides]
    frame_numbers: list[int] = []
    source_indexes: list[int] = []
    sample_kinds: list[str] = []
    boundaries = allocation["boundaries"]
    for index in range(len(slides)):
        start = boundaries[index]
        end = boundaries[index + 1]
        midpoint = (start + end - 1) // 2
        for sample_kind, frame_number in (
            ("start", start),
            ("midpoint", midpoint),
            ("end", end - 1),
        ):
            frame_numbers.append(frame_number)
            source_indexes.append(index)
            sample_kinds.append(sample_kind)

    decoded = video_thumbs(video, frame_numbers)
    samples = []
    for frame_number, source_index, sample_kind, video_thumb in zip(
        frame_numbers, source_indexes, sample_kinds, decoded
    ):
        error = mean_absolute_error(source_thumbs[source_index], video_thumb)
        samples.append(
            {
                "slide": slides[source_index]["slide"],
                "sample": sample_kind,
                "frame": frame_number,
                "time_seconds": frame_number / allocation["fps"],
                "mean_absolute_error": round(error, 6),
                "passed": error <= threshold,
            }
        )

    slide_results = []
    for slide in slides:
        slide_samples = [sample for sample in samples if sample["slide"] == slide["slide"]]
        slide_results.append(
            {
                "slide": slide["slide"],
                "samples_checked": len(slide_samples),
                "maximum_error": max(sample["mean_absolute_error"] for sample in slide_samples),
                "passed": all(sample["passed"] for sample in slide_samples),
                "samples": slide_samples,
            }
        )

    failed = [result["slide"] for result in slide_results if not result["passed"]]
    return {
        "slides_checked": len(slide_results),
        "slides_passed": len(slide_results) - len(failed),
        "slides_failed": len(failed),
        "failed_slides": failed,
        "samples_checked": len(samples),
        "threshold": threshold,
        "maximum_error": max(result["maximum_error"] for result in slide_results),
        "results": slide_results,
    }


def verify_slideshow(
    video: Path,
    manifest: dict,
    images_dir: Path,
    *,
    fps: int = 30,
    threshold: float = 6.0,
    expect_audio: bool = False,
    report_path: Path | None = None,
    full_decode: bool = True,
) -> dict:
    allocation = frame_allocation(manifest, fps)
    probe = probe_video(video)
    actual_frames = int(probe.get("nb_read_frames") or probe.get("nb_frames") or 0)
    expected_rate = f"{fps}/1"
    keys = keyframe_count(video)
    content = audit_slide_content(video, manifest, images_dir, allocation, threshold)
    media = probe_media(video)
    audio_streams = [stream for stream in media.get("streams", []) if stream["codec_type"] == "audio"]
    format_duration = float(media["format"]["duration"])

    failures = []
    if actual_frames != allocation["total_frames"]:
        failures.append(
            f"video has {actual_frames} frames; expected {allocation['total_frames']}"
        )
    if probe.get("avg_frame_rate") != expected_rate or probe.get("r_frame_rate") != expected_rate:
        failures.append(
            f"video is not strict {fps} fps CFR: avg={probe.get('avg_frame_rate')}, "
            f"nominal={probe.get('r_frame_rate')}"
        )
    if keys != len(manifest["slides"]):
        failures.append(f"video has {keys} keyframes; expected {len(manifest['slides'])}")
    if content["slides_failed"]:
        failures.append(f"source-image audit failed for slides {content['failed_slides']}")
    if expect_audio and not audio_streams:
        failures.append("final video has no audio stream")
    if abs(format_duration - allocation["duration_seconds"]) > max(0.05, 1 / fps):
        failures.append(
            f"container duration is {format_duration:.6f}; "
            f"expected {allocation['duration_seconds']:.6f}"
        )

    if full_decode:
        command = ["ffmpeg", "-v", "error", "-i", str(video), "-map", "0:v:0"]
        if expect_audio:
            command.extend(["-map", "0:a:0"])
        command.extend(["-f", "null", "-"])
        run(command)

    report = {
        "video": str(video.resolve()),
        "fps": fps,
        "duration_seconds": allocation["duration_seconds"],
        "expected_video_frames": allocation["total_frames"],
        "actual_video_frames": actual_frames,
        "expected_keyframes": len(manifest["slides"]),
        "actual_keyframes": keys,
        "frame_rate": probe.get("avg_frame_rate"),
        "audio_present": bool(audio_streams),
        "container_duration": format_duration,
        "slides_checked": content["slides_checked"],
        "slides_passed": content["slides_passed"],
        "slides_failed": content["slides_failed"],
        "samples_checked": content["samples_checked"],
        "maximum_error": content["maximum_error"],
        "failures": failures,
        "slide_results": content["results"],
    }
    if report_path:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2) + "\n")
    if failures:
        raise VerificationError("; ".join(failures))
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--images-dir", type=Path, required=True)
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--threshold", type=float, default=6.0)
    parser.add_argument("--expect-audio", action="store_true")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text())
    report_path = args.report or args.video.with_suffix(".verification.json")
    report = verify_slideshow(
        args.video,
        manifest,
        args.images_dir,
        fps=args.fps,
        threshold=args.threshold,
        expect_audio=args.expect_audio,
        report_path=report_path,
    )
    print(f"Slides verified: {report['slides_passed']}/{report['slides_checked']}")
    print(
        f"Video frames verified: {report['actual_video_frames']}/"
        f"{report['expected_video_frames']}"
    )
    print(
        f"Slide keyframes verified: {report['actual_keyframes']}/"
        f"{report['expected_keyframes']}"
    )
    print(f"Decoded source-image samples: {report['samples_checked']}")
    print(f"Verification report: {report_path}")


if __name__ == "__main__":
    main()
