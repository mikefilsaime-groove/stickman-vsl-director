#!/usr/bin/env python3
"""Measure narration-to-slide cadence from YouTube VTT captions and ffmpeg cuts."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path


TIMING_RE = re.compile(
    r"(?P<start>\d{2}:\d{2}:\d{2}\.\d{3})\s+-->\s+"
    r"(?P<end>\d{2}:\d{2}:\d{2}\.\d{3})"
)
INLINE_TIME_RE = re.compile(r"<(\d{2}:\d{2}:\d{2}\.\d{3})>")
WORD_RE = re.compile(
    r"(?:\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?|[A-Za-z]+(?:['’\-][A-Za-z]+)*)"
    r"(?:[.!?]+[\"'”’)]*)?"
)
SCENE_TIME_RE = re.compile(r"pts_time:([0-9.]+)")
ABBREVIATIONS = {"mr.", "mrs.", "ms.", "dr.", "prof.", "st.", "vs.", "etc."}


def parse_time(value: str) -> float:
    hours, minutes, seconds = value.split(":")
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def tokenize_chunk(chunk: str) -> list[str]:
    return WORD_RE.findall(chunk)


def parse_youtube_vtt(path: Path) -> list[dict]:
    """Extract each newly spoken token from YouTube rolling-caption VTT."""
    blocks = re.split(r"\n\s*\n", path.read_text(encoding="utf-8-sig"))
    words: list[dict] = []
    block_index = 0
    while block_index < len(blocks):
        block = blocks[block_index]
        lines = block.splitlines()
        timing_index = next((i for i, line in enumerate(lines) if "-->" in line), None)
        if timing_index is None:
            block_index += 1
            continue
        timing = TIMING_RE.search(lines[timing_index])
        if not timing:
            block_index += 1
            continue
        cue_start = parse_time(timing.group("start"))
        cue_end = parse_time(timing.group("end"))
        # YouTube inserts 0.01-second carry-forward cues. They contain no new speech.
        if cue_end - cue_start <= 0.05:
            block_index += 1
            continue
        payload = [line for line in lines[timing_index + 1 :] if line.strip()]
        # Some YouTube VTT files put a whitespace-only line after the timing line,
        # which makes a permissive blank-block split separate the first payload.
        if not payload and block_index + 1 < len(blocks) and "-->" not in blocks[block_index + 1]:
            payload = [line for line in blocks[block_index + 1].splitlines() if line.strip()]
            block_index += 1
        if not payload:
            block_index += 1
            continue
        line = payload[-1]
        line = re.sub(r"</?c(?:\.[^>]*)?>", "", line)
        pieces = INLINE_TIME_RE.split(line)
        timed_chunks: list[tuple[float, str]] = []
        if pieces and pieces[0].strip():
            timed_chunks.append((cue_start, pieces[0]))
        for i in range(1, len(pieces), 2):
            if i + 1 < len(pieces):
                timed_chunks.append((parse_time(pieces[i]), pieces[i + 1]))

        for chunk_index, (chunk_start, chunk) in enumerate(timed_chunks):
            tokens = tokenize_chunk(chunk)
            if not tokens:
                continue
            next_start = (
                timed_chunks[chunk_index + 1][0]
                if chunk_index + 1 < len(timed_chunks)
                else cue_end
            )
            step = max(0.0, next_start - chunk_start) / max(1, len(tokens))
            for token_index, token in enumerate(tokens):
                words.append(
                    {
                        "text": token,
                        "start": round(chunk_start + token_index * step, 3),
                    }
                )
        block_index += 1

    # Caption jitter can repeat a token at the exact same time. Remove only exact duplicates.
    deduped: list[dict] = []
    for word in words:
        if deduped and word == deduped[-1]:
            continue
        deduped.append(word)
    for index, word in enumerate(deduped):
        if index + 1 < len(deduped):
            word["end"] = deduped[index + 1]["start"]
        else:
            word["end"] = round(word["start"] + 0.35, 3)
    return deduped


def is_sentence_end(token: str) -> bool:
    lowered = token.lower().rstrip("\"'”’)")
    if lowered in ABBREVIATIONS:
        return False
    return bool(re.search(r"[.!?][\"'”’)]*$", token))


def build_sentences(words: list[dict]) -> list[dict]:
    sentences: list[dict] = []
    current: list[dict] = []
    for word in words:
        current.append(word)
        if is_sentence_end(word["text"]):
            sentences.append(_sentence_record(len(sentences) + 1, current))
            current = []
    if current:
        sentences.append(_sentence_record(len(sentences) + 1, current))
    return sentences


def _sentence_record(number: int, words: list[dict]) -> dict:
    text = " ".join(word["text"] for word in words)
    text = re.sub(r"\s+([.!?,;:])", r"\1", text)
    return {
        "sentence": number,
        "text": text,
        "start": words[0]["start"],
        "end": words[-1]["end"],
        "word_count": len(words),
    }


def parse_scene_cuts(path: Path, duration: float) -> list[dict]:
    cuts = [float(match.group(1)) for match in SCENE_TIME_RE.finditer(path.read_text())]
    starts = [0.0] + cuts
    slides = []
    for index, start in enumerate(starts):
        end = starts[index + 1] if index + 1 < len(starts) else duration
        slides.append(
            {
                "slide": index + 1,
                "start": round(start, 3),
                "end": round(end, 3),
                "duration": round(end - start, 3),
            }
        )
    return slides


def overlap(a_start: float, a_end: float, b_start: float, b_end: float) -> float:
    return max(0.0, min(a_end, b_end) - max(a_start, b_start))


def distribution(values: list[int]) -> dict[str, int]:
    return {str(key): count for key, count in sorted(Counter(values).items())}


def analyze(words: list[dict], sentences: list[dict], slides: list[dict], duration: float) -> dict:
    for sentence in sentences:
        sentence["slides"] = [
            slide["slide"]
            for slide in slides
            if overlap(sentence["start"], sentence["end"], slide["start"], slide["end"])
            >= 0.10
        ]
        sentence["image_count"] = len(sentence["slides"])

    for slide in slides:
        slide["sentences"] = [
            sentence["sentence"]
            for sentence in sentences
            if overlap(slide["start"], slide["end"], sentence["start"], sentence["end"])
            >= 0.10
        ]
        slide["sentence_count"] = len(slide["sentences"])

    word_count = len(words)
    sentence_count = len(sentences)
    slide_count = len(slides)
    sentence_image_counts = [sentence["image_count"] for sentence in sentences]
    slide_sentence_counts = [slide["sentence_count"] for slide in slides]
    minutes = duration / 60
    per_minute = []
    for minute in range(int(minutes) + 1):
        lower = minute * 60
        upper = min((minute + 1) * 60, duration)
        per_minute.append(
            {
                "minute": minute + 1,
                "start": lower,
                "end": round(upper, 3),
                "slide_starts": sum(lower <= slide["start"] < upper for slide in slides),
            }
        )

    return {
        "summary": {
            "duration_seconds": duration,
            "duration_minutes": round(minutes, 3),
            "word_count": word_count,
            "sentence_count": sentence_count,
            "slide_count": slide_count,
            "cut_count": max(0, slide_count - 1),
            "speaking_rate_wpm": round(word_count / minutes, 3),
            "images_per_minute": round(slide_count / minutes, 3),
            "images_per_word": round(slide_count / word_count, 5),
            "words_per_image": round(word_count / slide_count, 3),
            "structural_images_per_sentence": round(slide_count / sentence_count, 3),
            "structural_sentences_per_image": round(sentence_count / slide_count, 3),
            "overlap_images_per_sentence": round(
                sum(sentence_image_counts) / sentence_count, 3
            ),
            "overlap_sentences_per_image": round(
                sum(slide_sentence_counts) / slide_count, 3
            ),
            "median_image_duration_seconds": round(
                sorted(slide["duration"] for slide in slides)[slide_count // 2], 3
            ),
            "mean_image_duration_seconds": round(duration / slide_count, 3),
        },
        "distributions": {
            "images_per_sentence": distribution(sentence_image_counts),
            "sentences_per_image": distribution(slide_sentence_counts),
        },
        "slides_per_minute": per_minute,
        "sentences": sentences,
        "slides": slides,
    }


def markdown_report(data: dict) -> str:
    summary = data["summary"]
    lines = [
        "# Reference Timing Analysis",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|---|---:|",
    ]
    for key, value in summary.items():
        lines.append(f"| {key.replace('_', ' ').title()} | {value} |")
    lines.extend(
        [
            "",
            "## Distribution",
            "",
            f"- Images per sentence: `{json.dumps(data['distributions']['images_per_sentence'])}`",
            f"- Sentences per image: `{json.dumps(data['distributions']['sentences_per_image'])}`",
            "",
            "## Slides Per Minute",
            "",
            "| Minute | Slide starts |",
            "|---:|---:|",
        ]
    )
    for row in data["slides_per_minute"]:
        lines.append(f"| {row['minute']} | {row['slide_starts']} |")
    lines.extend(
        [
            "",
            "## Sentence-to-Slide Map",
            "",
            "| Sentence | Time | Words | Images | Voiceover |",
            "|---:|---:|---:|---|---|",
        ]
    )
    for sentence in data["sentences"]:
        text = sentence["text"].replace("|", "\\|")
        slides = ", ".join(str(value) for value in sentence["slides"]) or "—"
        lines.append(
            f"| {sentence['sentence']} | {sentence['start']:.2f}–{sentence['end']:.2f} | "
            f"{sentence['word_count']} | {slides} | {text} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--vtt", type=Path, required=True)
    parser.add_argument("--cuts", type=Path, required=True)
    parser.add_argument("--duration", type=float, required=True)
    parser.add_argument("--json-output", type=Path, required=True)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()

    words = parse_youtube_vtt(args.vtt)
    sentences = build_sentences(words)
    slides = parse_scene_cuts(args.cuts, args.duration)
    data = analyze(words, sentences, slides, args.duration)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    if args.markdown_output:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_output.write_text(markdown_report(data), encoding="utf-8")
    print(json.dumps(data["summary"], indent=2))


if __name__ == "__main__":
    main()
