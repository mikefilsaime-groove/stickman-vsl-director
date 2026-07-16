# Production Contract

Use this reference when creating deliverables, selecting a model, generating images, or rendering the timed slideshow.

## Project folder

Create one task-specific folder with this structure:

```text
project-name/
├── source-script.txt
├── art-direction-selection.json
├── slide-manifest.json
├── slide-manifest.md
├── style-anchor.png
├── prompts/
│   ├── slide-0001.txt
│   └── ...
├── images/
│   ├── slide-0001.png
│   └── ...
├── qa-report.md
├── storyboard-approval.json  # only after explicit post-review approval
├── timeline.ffconcat
└── final-slideshow.mp4        # only when rendering is requested
```

Keep slide numbers zero-padded and stable. Never renumber approved slides silently; insert a suffix or regenerate the manifest when timing changes.

## Required manifest fields

Every `slide-manifest.json` slide must contain:

- `slide`
- `image_file`
- `start_seconds`
- `end_seconds`
- `duration_seconds`
- `voiceover_reads_on_this_image`
- `word_count`
- `sentence_ids`
- `narrative_function`
- `visual_concept`
- `layout`
- `primary_expression`
- `continuity_notes`
- `on_image_text`
- `image_prompt`
- `negative_prompt`
- `generation_model`
- `generation_route`
- `status`

The top-level `project` object must contain `art_direction_profile` with exactly `simple-cute` or `full-color-expressive`. Record the explicit user choice and public comparison URL in `art-direction-selection.json`. Do not generate images while either record is missing or inconsistent.

The readable Markdown plan must use the exact column heading **Voiceover reads on this image**.

## Art-direction enrichment

After `scripts/plan_slides.py` creates timing beats, fill every placeholder before generation:

1. `narrative_function`: setup, action, danger, contrast, list, sequence, mechanism, evidence, number, objection, question, humor, payoff, or bridge.
2. `visual_concept`: one visible claim stated in concrete language.
3. `layout`: select one layout from the style bible.
4. `primary_expression`: select one expression and pose from the expression library.
5. `continuity_notes`: name the recurring character/location/prop anchors that must remain unchanged.
6. `on_image_text`: list exact short labels. Use an empty list when no text is required.
7. `image_prompt`: write a complete prompt using the style-bible skeleton.

Do not allow `TBD`, `null`, or vague concepts such as “show what the narration says” in a generation-ready manifest.

## Default image route: Codex GPT Image 2

Use Codex's built-in `image_gen` tool by default. It uses GPT Image 2 through the user's Codex subscription and does not require `OPENAI_API_KEY`.

- Generate one asset per built-in call, including for batches.
- Generate the project style anchor first and reuse it as a reference where supported.
- Move or copy every selected image into the project `images/` folder under its manifest filename.
- Do not leave a project-bound image only under Codex's generated-images directory.
- If the built-in tool is unavailable, stop and report the blocker. Do not silently downgrade to GPT Image 1, the API/CLI, or GenMedia.

Set manifest values to:

```json
{
  "generation_model": "gpt-image-2",
  "generation_route": "codex-built-in-image-gen"
}
```

## Optional model routing through GenMedia

Resolve model aliases with `genmedia models` before a paid run because endpoint names can change. These endpoints were active when the skill was created:

| User-facing alternate | GenMedia/fal endpoint |
|---|---|
| GPT Image 1 | `fal-ai/gpt-image-1/text-to-image` |
| Nano Banana 2 | `fal-ai/nano-banana-2` |
| Nano Banana Pro | `fal-ai/nano-banana-pro` |
| SeedDream 5.0 Pro | `bytedance/seedream/v5/pro/text-to-image` |

Use this table only when the user selects an alternate provider/model. Keep one model for an entire project when consistency matters.

Prefer Nano Banana Pro or SeedDream 5.0 for unusually dense grids or typography-heavy infographic slides. Mixing models can create style drift, so use a different model only for a failed slide or with user approval.

Before an unfamiliar endpoint, run:

```bash
genmedia schema ENDPOINT_ID
genmedia run --help
```

Never expose the GenMedia configuration or API key.

## Consistency workflow

1. Confirm the explicit `simple-cute` or `full-color-expressive` selection and load only that profile's reference pack.
2. Generate a project style anchor containing the protagonist, supporting roles, animals, recurring props, palette, line examples, and the 3×3 expression grid.
3. Generate three proof slides:
   - one single narrative scene;
   - one 2×2 grid;
   - one text-light diagram or timeline.
4. Obtain approval before generating a large paid batch.
5. Use the approved style anchor as a reference input whenever the endpoint supports it.
6. Keep the same model, profile, aspect ratio, style block, character description, and reference inputs across the batch.
7. Generate in small batches and run QA before continuing.

## QA per image

Check and record:

- file exists and is 16:9;
- voiceover concept is immediately recognizable;
- required characters and props are present;
- expression matches the manifest;
- character continuity matches the style anchor;
- grid cell count and reading order are correct;
- exact labels are spelled correctly;
- no extra text, logos, signatures, or watermarks;
- no realistic, painterly, glossy, or 3D style drift;
- safe margins are respected.

Retry only failed slides. Preserve approved images and their slide numbers.

## Timing modes

### Script only

Run `scripts/plan_slides.py`. It estimates at the calibrated reference rate and partitions narration at sentence/clause boundaries.

### Target duration

Pass `--duration SECONDS`. Keep the same concept cadence but scale timestamps to the requested duration.

### Final voiceover audio

Transcribe or align the final audio to word-level timestamps first. Pass a JSON word list to `--timed-words`; every entry must contain `start` and `end`, and its word count must match the tokenized script. Treat audio timings as authoritative.

### Rendering

Rendering has a mandatory post-storyboard approval gate:

1. Complete and QA all slides.
2. Present a timed review deck containing every numbered slide and its exact **Voiceover reads on this image** span.
3. Stop and ask the user for changes or the exact approval phrase: **I approve this storyboard for video rendering.**
4. Revise and re-present when changes are requested.
5. Only after explicit approval of the latest storyboard, run `scripts/approve_storyboard.py --confirm-user-approved` to bind the approval to the current manifest hash.
6. Run `scripts/render_slideshow.py` with the manifest, images folder, and optional final audio.

The renderer refuses to create video without a valid approval receipt. Any manifest change invalidates the receipt and requires another user review. `--check-only` may run before approval because it validates inputs without rendering.

## Completion definition

Do not call a project complete until:

- every voiceover word belongs to a slide;
- no slide has missing timing, concept, expression, prompt, or image;
- image count and duration are reconciled;
- the first and final frames are intentional;
- all labels pass proofreading;
- the latest timed storyboard was presented and explicitly approved by the user;
- `storyboard-approval.json` matches the exact current manifest;
- the rendered timeline, when requested, matches the final voiceover duration.
