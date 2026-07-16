#!/usr/bin/env python3
"""Partition a VSL script into reference-calibrated, voiceover-aligned slide beats."""

from __future__ import annotations

import argparse
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path


TOKEN_RE = re.compile(
    r"(?:\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?|[A-Za-z]+(?:['’\-][A-Za-z]+)*)"
    r"(?:[.,;:!?]+[\"'”’)]*)?"
)
SENTENCE_END_RE = re.compile(r"[.!?][\"'”’)]*$")
CLAUSE_END_RE = re.compile(r"[,;:][\"'”’)]*$")
CONNECTORS = {
    "and",
    "but",
    "because",
    "except",
    "however",
    "if",
    "meanwhile",
    "or",
    "so",
    "then",
    "therefore",
    "when",
    "which",
    "while",
    "yet",
}
DEFAULT_WORDS_PER_SLIDE = 13.412
DEFAULT_WPM = 153.604
DEFAULT_IMAGE_SECONDS = 5.239


def tokenize(text: str) -> list[dict]:
    tokens = []
    sentence = 1
    for index, match in enumerate(TOKEN_RE.finditer(text), start=1):
        value = match.group(0)
        tokens.append(
            {
                "index": index,
                "text": value,
                "start_char": match.start(),
                "end_char": match.end(),
                "sentence": sentence,
            }
        )
        if SENTENCE_END_RE.search(value):
            sentence += 1
    return tokens


def boundary_penalty(tokens: list[dict], end_index: int) -> float:
    """Return a lower cost for a more natural boundary after end_index."""
    token = tokens[end_index - 1]["text"]
    if SENTENCE_END_RE.search(token):
        return 0.0
    if re.search(r"[;:][\"'”’)]*$", token):
        return 0.18
    if CLAUSE_END_RE.search(token):
        return 0.45
    if end_index < len(tokens):
        next_word = re.sub(r"[^A-Za-z]", "", tokens[end_index]["text"]).lower()
        if next_word in CONNECTORS:
            return 0.7
    return 1.65


def choose_slide_count(word_count: int, requested: int | None, target_words: float) -> int:
    if requested:
        return max(1, requested)
    return max(1, round(word_count / target_words))


def partition_tokens(tokens: list[dict], slide_count: int, target_words: float) -> list[tuple[int, int]]:
    """Use dynamic programming to make exactly slide_count natural script beats."""
    word_count = len(tokens)
    if not word_count:
        return []
    min_words = 3
    max_words = max(24, math.ceil(target_words * 1.9))
    slide_count = min(slide_count, max(1, word_count // min_words))
    slide_count = max(slide_count, math.ceil(word_count / max_words))

    infinity = float("inf")
    previous_cost = [infinity] * (word_count + 1)
    previous_cost[0] = 0.0
    backtrack: list[list[int]] = [[-1] * (word_count + 1) for _ in range(slide_count + 1)]

    for slide in range(1, slide_count + 1):
        current_cost = [infinity] * (word_count + 1)
        earliest_end = slide * min_words
        latest_end = min(word_count, slide * max_words)
        for end in range(earliest_end, latest_end + 1):
            lower = max((slide - 1) * min_words, end - max_words)
            upper = min(end - min_words, (slide - 1) * max_words)
            for start in range(lower, upper + 1):
                if previous_cost[start] == infinity:
                    continue
                length = end - start
                length_cost = ((length - target_words) / target_words) ** 2
                break_cost = 0.0 if end == word_count else boundary_penalty(tokens, end)
                # Preserve rhetorical one-liners when they form a complete sentence.
                if length <= 6 and SENTENCE_END_RE.search(tokens[end - 1]["text"]):
                    length_cost *= 0.45
                total = previous_cost[start] + length_cost + break_cost
                if total < current_cost[end]:
                    current_cost[end] = total
                    backtrack[slide][end] = start
        previous_cost = current_cost

    if previous_cost[word_count] == infinity:
        raise RuntimeError("Unable to partition script with the requested slide count")

    ranges = []
    end = word_count
    for slide in range(slide_count, 0, -1):
        start = backtrack[slide][end]
        ranges.append((start, end))
        end = start
    ranges.reverse()
    return ranges


def load_timed_words(path: Path | None, expected: int) -> list[dict] | None:
    if not path:
        return None
    payload = json.loads(path.read_text())
    words = payload.get("words", payload) if isinstance(payload, dict) else payload
    if len(words) != expected:
        raise ValueError(
            f"Timed-word count ({len(words)}) does not match script word count ({expected})"
        )
    return words


def format_time(seconds: float) -> str:
    minutes = int(seconds // 60)
    remainder = seconds - minutes * 60
    return f"{minutes:02d}:{remainder:05.2f}"


def make_plan(
    text: str,
    title: str,
    duration: float | None,
    wpm: float,
    target_words: float,
    target_slides: int | None,
    model: str,
    generation_route: str,
    timed_words: list[dict] | None,
    art_direction_profile: str,
    art_direction_selection_note: str,
) -> dict:
    tokens = tokenize(text)
    if not tokens:
        raise ValueError("The script has no countable words")
    word_count = len(tokens)
    slide_count = choose_slide_count(word_count, target_slides, target_words)
    ranges = partition_tokens(tokens, slide_count, target_words)
    if timed_words:
        total_duration = float(timed_words[-1]["end"])
    else:
        total_duration = duration if duration is not None else word_count / wpm * 60

    slides = []
    cumulative_words = 0
    for number, (start, end) in enumerate(ranges, start=1):
        first = tokens[start]
        last = tokens[end - 1]
        voiceover = text[first["start_char"] : last["end_char"]].strip()
        if timed_words:
            start_seconds = float(timed_words[start]["start"])
            end_seconds = float(timed_words[end - 1]["end"])
        else:
            start_seconds = cumulative_words / word_count * total_duration
            cumulative_words += end - start
            end_seconds = cumulative_words / word_count * total_duration
        sentence_ids = sorted({token["sentence"] for token in tokens[start:end]})
        slides.append(
            {
                "slide": number,
                "image_file": f"slide-{number:04d}.png",
                "start_seconds": round(start_seconds, 3),
                "end_seconds": round(end_seconds, 3),
                "duration_seconds": round(end_seconds - start_seconds, 3),
                "voiceover_reads_on_this_image": voiceover,
                "word_count": end - start,
                "sentence_ids": sentence_ids,
                "narrative_function": None,
                "visual_concept": None,
                "layout": None,
                "primary_expression": None,
                "continuity_notes": None,
                "on_image_text": [],
                "image_prompt": None,
                "negative_prompt": (
                    "photorealism, 3D render, gradients, detailed anatomy, painterly texture, "
                    "cinematic realism, illegible text, watermark, logo"
                ),
                "generation_model": model,
                "generation_route": generation_route,
                "status": "needs-art-direction",
            }
        )

    sentence_count = max(token["sentence"] for token in tokens)
    if not SENTENCE_END_RE.search(tokens[-1]["text"]):
        sentence_count = max(1, sentence_count)
    return {
        "project": {
            "title": title,
            "aspect_ratio": "16:9",
            "word_count": word_count,
            "sentence_count": sentence_count,
            "slide_count": len(slides),
            "duration_seconds": round(total_duration, 3),
            "estimated_wpm": round(word_count / (total_duration / 60), 3),
            "target_words_per_slide": target_words,
            "target_image_seconds": DEFAULT_IMAGE_SECONDS,
            "reference_images_per_minute": 11.453,
            "default_model": model,
            "default_generation_route": generation_route,
            "art_direction_profile": art_direction_profile,
            "art_direction_selection_note": art_direction_selection_note,
        },
        "slides": slides,
    }


def markdown_plan(plan: dict) -> str:
    project = plan["project"]
    lines = [
        f"# {project['title']} — Stickman VSL Slide Plan",
        "",
        f"- Words: {project['word_count']}",
        f"- Slides: {project['slide_count']}",
        f"- Duration: {format_time(project['duration_seconds'])}",
        f"- Model: {project['default_model']}",
        f"- Art direction: {project['art_direction_profile']}",
        "",
        "## Slide Manifest",
        "",
        "| Slide | Time | Voiceover reads on this image | Words | Concept | Layout | Expression |",
        "|---:|---:|---|---:|---|---|---|",
    ]
    for slide in plan["slides"]:
        voiceover = slide["voiceover_reads_on_this_image"].replace("|", "\\|")
        lines.append(
            f"| {slide['slide']} | {format_time(slide['start_seconds'])}–"
            f"{format_time(slide['end_seconds'])} | {voiceover} | {slide['word_count']} | "
            "Needs art direction | Needs art direction | Needs art direction |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--script", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--title")
    parser.add_argument("--duration", type=float)
    parser.add_argument("--wpm", type=float, default=DEFAULT_WPM)
    parser.add_argument("--target-words-per-slide", type=float, default=DEFAULT_WORDS_PER_SLIDE)
    parser.add_argument("--target-slides", type=int)
    parser.add_argument("--timed-words", type=Path)
    parser.add_argument("--model", default="gpt-image-2")
    parser.add_argument("--generation-route", default="codex-built-in-image-gen")
    parser.add_argument(
        "--art-direction-profile",
        required=True,
        choices=("simple-cute", "full-color-expressive"),
    )
    parser.add_argument("--art-direction-selection-note", required=True)
    args = parser.parse_args()

    text = args.script.read_text(encoding="utf-8-sig").strip()
    tokens = tokenize(text)
    timed_words = load_timed_words(args.timed_words, len(tokens))
    plan = make_plan(
        text=text,
        title=args.title or args.script.stem,
        duration=args.duration,
        wpm=args.wpm,
        target_words=args.target_words_per_slide,
        target_slides=args.target_slides,
        model=args.model,
        generation_route=args.generation_route,
        timed_words=timed_words,
        art_direction_profile=args.art_direction_profile,
        art_direction_selection_note=args.art_direction_selection_note,
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.output_dir / "slide-manifest.json"
    md_path = args.output_dir / "slide-manifest.md"
    selection_path = args.output_dir / "art-direction-selection.json"
    json_path.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n")
    md_path.write_text(markdown_plan(plan), encoding="utf-8")
    selection_path.write_text(
        json.dumps(
            {
                "profile": args.art_direction_profile,
                "selection_source": "explicit-user-choice",
                "selection_note": args.art_direction_selection_note,
                "selected_at_utc": datetime.now(timezone.utc).isoformat(),
                "comparison_url": "https://stickman-vsl-director.mikefilsaime.chatgpt.site/#styles",
            },
            indent=2,
        )
        + "\n"
    )
    print(f"Slide manifest: {json_path}")
    print(f"Readable plan: {md_path}")
    print(f"Art-direction selection: {selection_path}")


if __name__ == "__main__":
    main()
