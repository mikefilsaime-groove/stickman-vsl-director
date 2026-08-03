# Stickman VSL Director

Turn any video sales letter into a timed, image-by-image production plan with exact voiceover ownership, consistent art direction, and generation-ready prompts.

**Live portal:** [stickman-vsl-director.mikefilsaime.chatgpt.site](https://stickman-vsl-director.mikefilsaime.chatgpt.site)

**Compare both art directions:** [Simple & Cute vs. Full-Color & Expressive](https://stickman-vsl-director.mikefilsaime.chatgpt.site/#styles)

**Reference video:** [Watch the analyzed YouTube example](https://www.youtube.com/watch?v=nv7HuwnofW0)

## What This Skill Does

Stickman VSL Director converts a script into a visual production manifest. It decides where the image changes belong, what concept each image should communicate, which composition makes that concept readable, and exactly which voiceover words play over every slide.

Before art direction begins, the skill requires the user to choose one of two complete workflows:

- **Option 1 — Simple & Cute:** warm cream backgrounds, restrained accent colors, generous negative space, a compact blue-body character, and softer charming expressions.
- **Option 2 — Full-Color & Expressive:** saturated full-frame environments, true stick bodies, larger emotional reactions, denser visual metaphors, and more physical humor.

The two public example storyboards use the same audio and identical 23-slide timing, so the comparison isolates the art direction rather than the script or pacing.

The default image-generation route is **GPT Image 2 through the Codex subscription**. Gen Media is optional when you deliberately want a different model such as Nano Banana 2 or SeedDream 5.0.

The skill produces:

- A numbered slide manifest with in/out timing.
- A recorded `simple-cute` or `full-color-expressive` art-direction choice.
- The exact voiceover assigned to every image.
- A visual concept and emotional job for each slide.
- Model-ready image prompts with continuity constraints.
- Layout direction for single scenes, contrasts, grids, timelines, and diagrams.
- A production contract that renders every approved slide into a frame-verified CFR slideshow.

## Frame-Accurate Rendering Guarantee

The renderer fails closed instead of trusting container duration alone. It gives every approved storyboard slide an explicit integer frame range, encodes each slide as an independent constant-frame-rate segment with its own keyframe, and concatenates those verified segments without re-timing.

Before replacing the requested MP4, it automatically proves:

- the decoded video frame count equals `floor(manifest duration × FPS)`;
- nominal and average frame rate are both strict CFR;
- slide-start keyframes equal the manifest slide count;
- the decoded start, midpoint, and end of every interval match that slide's source image;
- the complete video and audio streams decode without errors.

The evidence is saved beside the video as `final-slideshow.verification.json`. A missing, skipped, duplicated, or over-held slide makes the render fail rather than silently producing a bad deliverable.

## Reference Calibration

The included calibration study was measured from the example video—not estimated.

| Measurement | Result |
| --- | ---: |
| Spoken words | 3,125 |
| Sentences | 240 |
| Visual slides | 233 |
| Detected transitions | 232 |
| Images per minute | 11.453 |
| Images per word | 0.07456 |
| Words per image | 13.412 |
| Average image hold | 5.239 seconds |
| Median image hold | 4.800 seconds |
| Structural images per sentence | 0.971 |
| Structural sentences per image | 1.030 |

These numbers calibrate pacing. They are not a rigid formula: the skill changes visuals at semantic and emotional beats.

## Visual Reference Atlas

The repository includes the complete visual study behind the style direction:

- [Model-ready character and style reference](references/style-atlas/model-ready-character-style-reference.pdf): a palette/style-lock page plus eight curated visual-grammar pages.
- [Complete 233-slide atlas](references/style-atlas/original-video-complete-slide-atlas.pdf): all distinct source slides arranged 3×4 across 20 pages.
- [Reference routing guide](references/style-atlas/reference-atlas.md): tells the agent which 2–4 references to attach for characters, environments, panels, diagrams, comedy, emotion, or dense boards.
- `model-ready-pages/` and `individual-frames/`: JPEG references for models that work better with selected images than a multipage PDF.

The full atlas is a searchable library. The skill uses the smaller routed reference set for generation so image inputs stay focused.

## How Concept Selection Works

For every voiceover beat, the skill identifies:

1. The literal subject.
2. The persuasive job: problem, proof, contrast, mechanism, benefit, objection, or action.
3. The emotional turn: worry, surprise, curiosity, confidence, relief, urgency, or delight.
4. The clearest visual device: character scene, metaphor, comparison, expression grid, process, timeline, or annotated diagram.
5. The continuity constraints inherited from the style bible.

That decision becomes one slide brief with a single dominant idea, an image prompt, timing, and the exact words the image owns.

## Install

Clone the repository:

```bash
git clone https://github.com/mikefilsaime-groove/stickman-vsl-director.git
```

Install it in Codex:

```bash
cp -R stickman-vsl-director ~/.codex/skills/
```

The folder is also compatible with installations that discover skills through `~/.claude/skills/`.

## Use

Invoke the skill with a script or transcript:

```text
Use $stickman-vsl-director on this script. Create a timed slide manifest,
quote the exact voiceover for every image, and render with GPT Image 2
through my Codex subscription. Ask me to choose the visual direction first.
```

You can also request planning only:

```text
Use $stickman-vsl-director to analyze this VSL and deliver the complete
slide manifest, but do not generate images yet.
```

## Included Files

```text
SKILL.md
agents/openai.yaml
references/
  art-direction-profiles.md
  production-contract.md
  reference-calibration.md
  style-bible.md
  style-atlas/
    reference-atlas.md
    model-ready-character-style-reference.pdf
    original-video-complete-slide-atlas.pdf
    model-ready-pages/
    individual-frames/
scripts/
  analyze_reference.py
  plan_slides.py
  render_slideshow.py
  verify_slideshow.py
```

The profile reference anchors live in `references/art-direction-profiles/`. The Full-Color & Expressive workflow additionally uses the routed source-video atlas.

The repository also contains the source for the public tabbed portal in `app/`.

## Rendering Routes

| Route | Use |
| --- | --- |
| GPT Image 2 via Codex | Default. Uses the image generation included with the Codex subscription. |
| Gen Media | Optional. Use when a named external model or specialized capability is requested. |
| Planning only | Produces the complete manifest without generating images. |

Approved slideshow production always uses the bundled frame-counted CFR renderer and automatic all-slide verification, regardless of which image-generation route produced the slides.

## Skill Hub

This skill is also indexed in [Mike Filsaime's public AI Skills Library](https://github.com/mikefilsaime-groove/mikefilsaime-skills).

## License

MIT
