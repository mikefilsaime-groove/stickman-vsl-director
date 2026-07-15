# Reference Calibration

These measurements come from the 20:21 reference video `nv7HuwnofW0`, using YouTube word-timed captions and ffmpeg scene detection. Scene thresholds `0.04` and `0.08` both found the same 232 hard cuts, so the count is stable.

## Exact cadence

| Metric | Value |
|---|---:|
| Measured duration | 1,220.668 seconds (20.344 minutes) |
| Spoken words | 3,125 |
| Narration sentences | 240 |
| Distinct slides/images | 233 |
| Hard cuts | 232 |
| Speaking rate | 153.604 words/minute |
| Images per minute | 11.453 |
| Images per word | 0.07456 |
| Words per image | 13.412 |
| Mean image duration | 5.239 seconds |
| Median image duration | 4.800 seconds |
| Structural images per sentence | 0.971 |
| Structural sentences per image | 1.030 |
| Time-overlap images per sentence | 1.796 |
| Time-overlap sentences per image | 1.850 |

“Structural” is the simple total ratio. “Time-overlap” counts every image that is visible during part of a sentence and every sentence that overlaps part of an image. The overlap values are higher because cuts usually occur inside sentences rather than exactly at punctuation.

## Images used by each sentence

| Images overlapping one sentence | Sentence count | Share |
|---:|---:|---:|
| 1 | 89 | 37.1% |
| 2 | 118 | 49.2% |
| 3 | 27 | 11.3% |
| 4 | 5 | 2.1% |
| 5 | 1 | 0.4% |

Operational rule: most sentences should use one or two slides. Give three or more only to a long sentence containing multiple visible actions, stages, examples, or a major closing payoff.

## Sentences carried by each image

| Sentences overlapping one image | Image count | Share |
|---:|---:|---:|
| 1 | 79 | 33.9% |
| 2 | 118 | 50.6% |
| 3 | 28 | 12.0% |
| 4 | 8 | 3.4% |

Operational rule: a slide normally carries one or two short sentences. Let one strong diagram carry three or four sentences only when all lines explain the same visual mechanism.

## Slide starts by minute

| Minute | Slides | Minute | Slides | Minute | Slides |
|---:|---:|---:|---:|---:|---:|
| 1 | 17 | 8 | 5 | 15 | 11 |
| 2 | 10 | 9 | 8 | 16 | 7 |
| 3 | 16 | 10 | 9 | 17 | 10 |
| 4 | 17 | 11 | 11 | 18 | 12 |
| 5 | 16 | 12 | 10 | 19 | 10 |
| 6 | 16 | 13 | 10 | 20 | 12 |
| 7 | 12 | 14 | 11 | 21 (partial) | 3 |

The hook uses faster visual turnover. The scientific/mechanism middle uses longer infographic holds. The ending returns to roughly 10–12 images per minute and lingers on the emotional final image.

## Editorial rhythm

- Use direct hard cuts between static slides. Do not add constant camera movement or elaborate transitions.
- Hold ordinary narrative images for roughly 3–6 seconds.
- Hold a comparison, map, chart, or dense multi-panel frame for roughly 6–12 seconds.
- Use a 2–3 second reaction image for a short punch line, “No,” “Read that again,” or a reveal.
- Change images when the visual claim changes, not automatically at every sentence boundary.
- Keep the same location and characters across adjacent slides when only the action or expression changes.
- In the hook, favor a fresh visual every 2–5 seconds. In the body, allow longer explanatory holds.

## Observed composition mix

The following mix is a visual-direction target, not a machine-labeled count:

- About 45–50% single narrative scenes or reaction frames.
- About 25–30% diagrams, boards, timelines, maps, branching trees, and other infographic frames.
- About 20–25% split comparisons, three-panel sequences, 2×2 grids, and four-column progressions.
- About 5% title, bridge, or end-card compositions.

Avoid running more than five ordinary single scenes without a structural change such as a comparison, diagram, timeline, map, or grid. Avoid running multiple dense infographics back to back unless one is a continuation of the other.

## Planning defaults

When only a script is available:

- Estimate narration at `153.604 WPM` unless the user provides audio or a target duration.
- Plan one slide per `13.412` words.
- Target one image every `5.239` seconds.
- Let sentence and clause boundaries influence cuts, but prioritize visual-concept changes.

When final voiceover audio is available, replace all estimates with word-level timestamps and preserve the same concept boundaries. The manifest must state exactly which voiceover text plays on every image.
