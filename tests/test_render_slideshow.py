from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RENDERER = ROOT / "scripts" / "render_slideshow.py"


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "ffmpeg required")
class RenderSlideshowIntegrationTest(unittest.TestCase):
    def test_renders_every_slide_as_strict_cfr_frames(self) -> None:
        with tempfile.TemporaryDirectory(prefix="stickman-render-test-") as temporary:
            project = Path(temporary)
            images = project / "images"
            images.mkdir()
            for number, color in enumerate(("red", "green", "blue"), start=1):
                subprocess.run(
                    [
                        "ffmpeg",
                        "-y",
                        "-v",
                        "error",
                        "-f",
                        "lavfi",
                        "-i",
                        f"color=c={color}:s=320x180",
                        "-frames:v",
                        "1",
                        str(images / f"slide-{number:04d}.png"),
                    ],
                    check=True,
                )

            slides = [
                {
                    "slide": 1,
                    "image_file": "slide-0001.png",
                    "start_seconds": 0.0,
                    "end_seconds": 0.7,
                    "duration_seconds": 0.7,
                },
                {
                    "slide": 2,
                    "image_file": "slide-0002.png",
                    "start_seconds": 0.7,
                    "end_seconds": 1.6,
                    "duration_seconds": 0.9,
                },
                {
                    "slide": 3,
                    "image_file": "slide-0003.png",
                    "start_seconds": 1.6,
                    "end_seconds": 2.533,
                    "duration_seconds": 0.933,
                },
            ]
            manifest = project / "slide-manifest.json"
            manifest.write_text(json.dumps({"slides": slides}, indent=2) + "\n")
            approval = {
                "schema_version": 1,
                "approval_type": "explicit-user-storyboard-approval",
                "approved_at_utc": "2026-01-01T00:00:00+00:00",
                "approval_note": "Integration test approval.",
                "manifest_file": manifest.name,
                "manifest_sha256": hashlib.sha256(manifest.read_bytes()).hexdigest(),
                "slide_count": 3,
                "duration_seconds": 2.533,
            }
            (project / "storyboard-approval.json").write_text(
                json.dumps(approval, indent=2) + "\n"
            )
            output = project / "final-slideshow.mp4"

            subprocess.run(
                [
                    sys.executable,
                    str(RENDERER),
                    "--manifest",
                    str(manifest),
                    "--images-dir",
                    str(images),
                    "--output",
                    str(output),
                    "--width",
                    "320",
                    "--height",
                    "180",
                    "--fps",
                    "30",
                    "--workers",
                    "2",
                ],
                check=True,
            )

            report = json.loads(output.with_suffix(".verification.json").read_text())
            self.assertEqual(report["expected_video_frames"], 75)
            self.assertEqual(report["actual_video_frames"], 75)
            self.assertEqual(report["frame_rate"], "30/1")
            self.assertEqual(report["expected_keyframes"], 3)
            self.assertEqual(report["actual_keyframes"], 3)
            self.assertEqual(report["slides_checked"], 3)
            self.assertEqual(report["slides_passed"], 3)
            self.assertEqual(report["slides_failed"], 0)
            self.assertEqual(report["samples_checked"], 9)
            self.assertEqual(report["failures"], [])


if __name__ == "__main__":
    unittest.main()
