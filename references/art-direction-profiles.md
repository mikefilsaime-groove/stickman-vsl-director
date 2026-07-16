# Art-Direction Profiles

Use this reference before planning, prompting, generating, or reviewing a storyboard. The user must choose one profile. Neither profile is an automatic default.

Public visual comparison: `https://stickman-vsl-director.mikefilsaime.chatgpt.site/#styles`

## Required choice prompt

Ask this when the user has not already made an explicit choice:

> Which visual direction would you like?
>
> **Option 1 — Simple & Cute:** A warm, minimal storybook look with cream backgrounds, generous open space, restrained accent colors, a compact blue-body character, and softer rounded expressions. It feels friendly, clear, and charming, with fewer environmental details competing with the message.
>
> **Option 2 — Full-Color & Expressive:** A saturated explainer-cartoon look with full cyan, blue, green, and brown environments; true stick-figure bodies; larger emotional reactions; more physical comedy; and denser visual storytelling. It feels more energetic, humorous, and faithful to the source-video world.
>
> Compare both complete storyboards here: https://stickman-vsl-director.mikefilsaime.chatgpt.site/#styles

Wait for the user's answer. Record `simple-cute` or `full-color-expressive` in the project manifest. Do not blend the profiles unless the user explicitly requests a hybrid.

## Profile 1: `simple-cute`

Use `references/art-direction-profiles/simple-cute-style-anchor.jpg` as the mandatory visual reference.

- Warm cream or off-white stage-like background on most slides.
- Generous negative space and one dominant focal idea.
- Rounded white head, compact royal-blue rectangular torso, thin black limbs, black mitten hands and oval feet.
- Soft, cute, immediately legible expressions; humor comes from innocence, contrast, and reaction.
- Restrained red, yellow, green, brown, gray, and navy accents for props or key symbols.
- Sparse props; diagrams and grids retain the cream ground rather than filling every cell with scenery.
- Use the old storyboard examples shown on the public comparison page as visual evidence.

Prompt style block:

```text
16:9 flat 2D hand-drawn educational cartoon in the Simple & Cute profile. Warm cream paper-like background; thick slightly uneven black outlines; white circular head; compact royal-blue rectangular torso; thin black stick limbs with simple mitten hands and oval feet; soft rounded expressive face; restrained red, yellow, green, brown, gray, and navy accents; generous empty space; one dominant visual idea; friendly, charming, clear, and lightly humorous.
```

Avoid saturated edge-to-edge scenery, busy full-frame environments, realistic anatomy, thin bare-line torsos, glossy rendering, 3D, photorealism, and excessive detail.

## Profile 2: `full-color-expressive`

Use `references/art-direction-profiles/full-color-expressive-style-anchor.jpg` plus the routed atlas references in `references/style-atlas/reference-atlas.md`.

- Saturated edge-to-edge cyan or blue skies, green ground, brown earth, and cream information surfaces.
- True stick-figure torsos and limbs with white circular heads and small role cues such as the blue bow tie.
- Larger eyes, brows, mouths, gestures, motion marks, and comic reactions.
- More environmental context, kinetic poses, visual metaphors, and humorous exaggeration.
- Use split screens, 2×2 grids, four-column sequences, timelines, boards, and diagrams when the concept earns them.
- Preserve a clear focal hierarchy even when the frame is denser.

Prompt style block:

```text
16:9 flat 2D hand-drawn stickman educational cartoon in the Full-Color & Expressive profile. Thick slightly uneven black outlines; white circular heads and thin black stick torsos and limbs; simple colored cartoon props and animals; broad flat fills; saturated edge-to-edge cyan, royal-blue, green, brown, cream, red, and yellow palette; large expressive faces; kinetic gestures; playful visual humor; energetic educational tone.
```

Avoid beige presentation minimalism, blue rectangular torsos, timid expressions, corporate vector polish, realistic anatomy, glossy rendering, 3D, and photorealism.

## Shared rules

Both profiles use the same narration timing, concept-selection logic, slide numbering, layout grammar, voiceover ownership, continuity discipline, storyboard review gate, and rendering workflow. The choice changes the character construction, color allocation, density, emotional intensity, and reference pack—not the script or editorial pacing.
