---
name: stickman-vsl-director
description: Turn any video sales letter, narration, script, transcript, or voiceover into a timed slide-by-slide stickman explainer in the visual grammar of the analyzed reference video. Use for VSL image planning, “voiceover reads on this image” manifests, facial-expression direction, 2×2 grids, comparison panels, timelines, infographic concepts, Codex subscription image generation with GPT Image 2 by default, optional GenMedia generation with Nano Banana 2/Pro, SeedDream 5.0, or another chosen model, and optional static-slide video rendering synchronized to audio.
---

# Stickman VSL Director

Create an original slide sequence that matches the reference's cadence, composition system, expression language, and flat hand-drawn stickman direction. Treat every image as a numbered slide with explicit voiceover ownership.

## Load the direction

Read both references before planning:

- `references/style-bible.md` for style, expression, concept, layout, prompting, and QA rules.
- `references/reference-calibration.md` for measured pacing and narration/image ratios.

Read `references/production-contract.md` before generating images, handing off to GenMedia, or rendering a slideshow.

## Establish the requested scope

Infer the narrowest useful scope from the request:

1. **Analyze only:** measure a new reference video and report its visual grammar.
2. **Plan only:** create a timed, fully art-directed manifest and prompts without paid generation.
3. **Generate:** create the style anchor, proof slides, completed image batch, QA report, and timed storyboard review deck; then stop for user review.
4. **Produce:** only after explicit post-storyboard approval, record the approval and render the slide sequence with final voiceover audio.

Do not generate paid images or render a video when the user requested only a storyboard or prompt plan.

## Normalize inputs

Collect or infer:

- script or transcript;
- final voiceover audio, word timestamps, target duration, or permission to estimate;
- project title and output folder;
- image model override;
- any brand, character, palette, or content constraints.

Save the exact script as `source-script.txt`. Do not rewrite sales copy unless explicitly asked. Remove production notes from narration while preserving spoken wording.

Default to:

- 16:9, 1920×1080;
- 153.604 spoken words per minute;
- one image per 13.412 words;
- one image every 5.239 seconds;
- 11.453 images per minute;
- GPT Image 2 through Codex's built-in `image_gen` subscription route.

## Build the timing skeleton

For script-only planning, run:

```bash
python3 scripts/plan_slides.py \
  --script /absolute/path/source-script.txt \
  --output-dir /absolute/path/project \
  --title "Project title" \
  --model "gpt-image-2" \
  --generation-route "codex-built-in-image-gen"
```

Pass `--duration SECONDS` when the user supplies a target length. Pass `--target-slides N` only when the user explicitly specifies an image count.

For final audio, obtain word-level timestamps with the available transcription/alignment workflow. Normalize those words to the exact script, then pass a JSON list containing `start` and `end` for every token through `--timed-words`. Treat final audio timing as authoritative.

Do not cut mechanically at every sentence. Cut when the visible claim, location, time, comparison, example, mechanism, or emotional beat changes.

## Art-direct every slide

Open the generated manifest and replace every placeholder. For each slide:

1. Quote the exact `voiceover_reads_on_this_image` span.
2. Classify its narrative function.
3. State the smallest visual concept that communicates the line.
4. Select a layout from the style bible.
5. Direct the primary face, gaze, pose, and gesture.
6. Record recurring character, location, animal, and prop continuity.
7. List exact short labels or use no text.
8. Write a complete model-neutral image prompt using the style-bible prompt skeleton.

Use one or two slides for most sentences. Allow three or more only when a long sentence contains multiple visible actions, examples, stages, or a major payoff. Let one image carry one or two short sentences; let a strong diagram carry three or four only when all lines explain the same concept.

Use a deliberate composition rhythm:

- concrete action or emotion → single scene or reaction close-up;
- two states → split comparison;
- three or four examples/stages → sequence or 2×2 grid;
- cause/evidence → diagram or board;
- time → timeline/progression;
- place/origins → map;
- abstract idea → physical metaphor;
- closing payoff → simple emotional frame with longer hold.

Preserve the exact heading **Voiceover reads on this image** in the readable manifest.

## Freeze continuity before batch generation

Create one project style anchor containing:

- protagonist and supporting character turnarounds;
- wolf/dog or subject variants;
- recurring props and locations;
- fixed palette and line weight;
- a 3×3 facial-expression grid.

Generate three proof slides: a single scene, a 2×2 grid, and a diagram/timeline. Obtain approval before a large paid batch unless the user explicitly directs generation without a proof gate.

## Generate through Codex by default

Use the built-in `image_gen` tool for GPT Image 2. This is the preferred subscription path and does not require `OPENAI_API_KEY`. For batches, issue one built-in generation call per slide; do not switch to the API/CLI merely because there are many slides.

Save each selected project image into the project `images/` folder as the stable manifest filename. Do not leave a project image only in Codex's generated-images location. Inspect the style anchor before using it as a reference and reuse it on conditioned generations when supported.

If the built-in tool is unavailable or fails, report that blocker. Do not silently switch to a paid API, GPT Image 1, or GenMedia.

## Use GenMedia only for an alternate provider

Use the local GenMedia CLI. Resolve aliases with `genmedia models` and inspect unfamiliar endpoints with `genmedia schema` before running them. Never expose GenMedia credentials.

Use GenMedia only when the user chooses Nano Banana, SeedDream, GPT Image 1, or another GenMedia/fal model. Keep one model for the project whenever possible. Reuse the approved style anchor as a reference input when the endpoint supports image conditioning. Generate in small batches, then validate before continuing.

Use Nano Banana 2 when the user explicitly prefers it or its reference-editing behavior is advantageous. Consider Nano Banana Pro or SeedDream 5.0 for dense grids or typography-heavy slides, but avoid cross-model drift.

## Validate every result

Check concept clarity, expression, continuity, grid structure, palette, line style, labels, aspect ratio, safe margins, and unwanted text. Retry only failed slides. Preserve approved slide numbers and files.

Create `qa-report.md` listing each slide as approved, revised, or blocked. Do not mark the batch complete while any manifest field or required image is missing.

## Enforce the storyboard approval gate

Treat storyboard review as a mandatory human checkpoint before every video render, even when the initial request asks for end-to-end production or says to proceed automatically.

1. Finish and QA every numbered slide first.
2. Create a review deck or equivalent contact-sheet presentation that shows, for every slide:
   - the image;
   - slide number and exact in/out time;
   - the exact **Voiceover reads on this image** span;
   - the visual concept and layout.
3. Present the storyboard to the user and end the turn with this unambiguous request:

   **Please review the storyboard and tell me any changes you want. If none, reply: “I approve this storyboard for video rendering.”**

4. Do not render, queue, or begin composing the video in the storyboard-delivery turn.
5. If the user requests changes, revise only the affected slides, update timing when needed, regenerate the review deck, and ask for approval again.
6. Accept approval only from an explicit user response after the latest storyboard was presented. Do not infer approval from the original brief, prior general permission, silence, or a request to work autonomously.
7. After explicit approval, record it against the exact manifest before rendering:

```bash
python3 scripts/approve_storyboard.py \
  --manifest /absolute/path/project/slide-manifest.json \
  --confirm-user-approved \
  --approval-note "User explicitly approved the presented storyboard."
```

This creates `storyboard-approval.json` beside the manifest. Approval is invalidated automatically if the manifest changes; present the revised storyboard and obtain approval again.

## Render when requested

After all images pass QA **and** the user explicitly approves the presented storyboard, verify or render the direct-cut timeline:

```bash
python3 scripts/render_slideshow.py \
  --manifest /absolute/path/project/slide-manifest.json \
  --images-dir /absolute/path/project/images \
  --audio /absolute/path/voiceover.mp3 \
  --output /absolute/path/project/final-slideshow.mp4
```

Use `--check-only` to verify image completeness and timeline duration without rendering. Keep slides static and use hard cuts unless the user requests a different motion treatment.

The renderer requires a valid `storyboard-approval.json` for every actual render. It has no approval bypass. `--check-only` remains available before approval because it does not create a video.

## Analyze another reference

When the user supplies a new YouTube/video reference, route download and captions through `yt-dlp-superpowers`, visual evidence through `watch-video`, and scene changes through ffmpeg. Then run:

```bash
python3 scripts/analyze_reference.py \
  --vtt /absolute/path/captions.en-orig.vtt \
  --cuts /absolute/path/scene-cuts.txt \
  --duration SECONDS \
  --json-output /absolute/path/reference-analysis.json \
  --markdown-output /absolute/path/reference-analysis.md
```

Report both simple structural ratios and time-overlap ratios. Update calibration only when the new reference is intended to replace or extend this style.
