#!/usr/bin/env python3
"""Record explicit user approval for the exact storyboard manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def manifest_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a render approval receipt bound to one exact slide manifest."
    )
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--approval-note", required=True)
    parser.add_argument(
        "--confirm-user-approved",
        action="store_true",
        help="Confirm that the user explicitly approved the latest presented storyboard.",
    )
    args = parser.parse_args()

    if not args.confirm_user_approved:
        raise SystemExit(
            "Approval not recorded. Present the completed storyboard and obtain explicit "
            "user approval before using --confirm-user-approved."
        )
    if not args.manifest.exists():
        raise FileNotFoundError(args.manifest)

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    slides = manifest.get("slides")
    if not isinstance(slides, list) or not slides:
        raise ValueError("Manifest must contain at least one slide")

    output = args.output or args.manifest.parent / "storyboard-approval.json"
    receipt = {
        "schema_version": 1,
        "approval_type": "explicit-user-storyboard-approval",
        "approved_at_utc": datetime.now(timezone.utc).isoformat(),
        "approval_note": args.approval_note,
        "manifest_file": args.manifest.name,
        "manifest_sha256": manifest_sha256(args.manifest),
        "slide_count": len(slides),
        "duration_seconds": round(
            sum(float(slide["duration_seconds"]) for slide in slides), 6
        ),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(f"Storyboard approval: {output}")
    print(f"Approved slides: {receipt['slide_count']}")
    print(f"Approved duration: {receipt['duration_seconds']:.3f} seconds")


if __name__ == "__main__":
    main()
