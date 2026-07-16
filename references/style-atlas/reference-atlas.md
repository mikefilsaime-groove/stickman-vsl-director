# Visual Reference Atlas Routing

Use this reference only when the selected art-direction profile is `full-color-expressive`. Do not use this atlas for `simple-cute` generations.

## Included evidence

- `original-video-complete-slide-atlas.pdf`: all 233 distinct visual slides, 3×4 across 20 pages.
- `model-ready-character-style-reference.pdf`: one palette/style-lock page plus eight curated visual-grammar pages.
- `model-ready-palette-and-style-lock.jpg`: mandatory global palette, line, proportion, and exclusion reference.
- `model-ready-pages/`: the eight curated category pages as individual JPEGs.
- `individual-frames/`: 32 full-resolution examples selected from the original.
- `slide-manifest.csv`: all slide times, holds, and matching voiceover.
- `model-ready-manifest.csv`: the curated frame category, purpose, timestamp, filename, and matching voiceover.
- `palette.json`: dominant colors measured across all extracted slides.

## Generation routing

Attach 2–4 references per image-generation call:

1. Always attach `model-ready-palette-and-style-lock.jpg`.
2. Add `model-ready-pages/style-reference-01.jpg` for people, faces, gestures, or character proportions.
3. Add `style-reference-02.jpg` for wolves, dogs, foxes, or other animals.
4. Add `style-reference-03.jpg` for day, night, camp, or outdoor color allocation.
5. Add one concept-specific page when needed:
   - `style-reference-04.jpg`: split screens, three-panel sequences, 2×2 grids, or dialogue;
   - `style-reference-05.jpg`: evidence scenes, timelines, maps, or branching diagrams;
   - `style-reference-06.jpg`: literal metaphors, oversized symbols, or visual comedy;
   - `style-reference-07.jpg`: bonding, puppy eyes, affection, or extreme reactions;
   - `style-reference-08.jpg`: dense explainer boards, posters, or historical paths.

Use `model-ready-manifest.csv` to choose an individual frame when a category page is too broad.

Do not attach the 20-page complete atlas to every generation. Search it when the current concept needs a reference that the curated pages do not cover, then attach only the most relevant frame or page.

## Style lock

- Fill the 16:9 frame with saturated cyan day skies, royal/deep-blue nights, green ground, and brown earth.
- Use rough, heavy, slightly uneven black outlines, flat fills, minimal shading, white circular heads, simple stick limbs, and large readable subjects.
- Push eyes, brows, mouths, gestures, motion marks, hearts, and question marks until the emotion reads immediately.
- Choose one full scene by default. Use a split, grid, timeline, map, or board only when the voiceover genuinely needs that structure.
- Use short imperfect hand lettering only when essential. Do not paste narration into the image.
- Avoid beige presentation backdrops, generic blue-shirt characters, polished corporate vectors, photorealism, and 3D rendering.

Use the images as art-direction evidence. Create a new original scene for the user's script rather than copying a source frame literally.
