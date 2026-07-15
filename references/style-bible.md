# Stickman VSL Style Bible

Use this reference when choosing concepts, writing prompts, checking continuity, or judging generated images.

## Visual identity

- Canvas: 16:9 landscape, normally 1920×1080. Keep essential content inside a 5% safe area.
- Medium: flat 2D digital cartoon with an intentionally hand-drawn finish.
- People: thin black stick limbs and torsos, white circular heads, black facial marks, little or no clothing unless role recognition requires it.
- Animals: simplified colored cartoon bodies with heavier outlines and slightly more anatomical detail than the people.
- Line: black, confident, slightly uneven, medium-thick. Avoid delicate sketching and realistic contours.
- Fill: broad flat colors. Avoid realistic lighting, gradients, airbrushing, 3D form, and painterly texture.
- Background: sparse stage-like environments made from a horizon, sky/ground blocks, one or two trees, a campfire, a tent, a cave, or a simple building.
- Typography: imperfect uppercase hand lettering on white boards, cream cards, signs, arrows, and labels. Keep it short and legible.
- Tone: educational, playful, lightly absurd, emotionally clear, never visually luxurious.

## Core palette

Use a small recurring palette rather than choosing new colors per slide.

| Role | Suggested color |
|---|---|
| Day sky | `#4AAFE5` |
| Night sky | `#263D7B` |
| Grass | `#35AF36` |
| Earth | `#8B4F2D` |
| Tree canopy | `#2EA936` |
| Tree trunk | `#713D24` |
| Wolf | `#8A8A86` |
| Dog/fox accents | `#C9783A` / `#F07728` |
| Paper/card | `#F4F0D8` |
| Fire | `#FFB31A` with `#F15A24` outline/accent |
| Emphasis | red `#E12727`, yellow `#FFD52B`, black `#111111` |

Night scenes may add a soft circular fire glow or edge vignette. Treat that as the exception to flat lighting.

## Character continuity

Freeze these details in a project style anchor before batch generation:

- Protagonist head shape, eye spacing, line weight, and neutral smile.
- Supporting human variants: scientist with glasses/lab coat, hunter with hide tunic/spear, modern owner with minimal clothing cues.
- Wolf silhouette: gray, pointed ears, long muzzle, angular tail, cautious or suspicious eyes.
- Dog silhouette: rounder muzzle, softer ears, curled or wagging tail, larger friendly eyes.
- Tree, campfire, tent, cave, signboard, arrow, and thought-bubble shapes.
- Palette swatches and a 3×3 protagonist expression grid.

Reuse the style-anchor image as a reference input whenever the selected model supports image conditioning or editing. Do not redesign recurring characters slide by slide.

## Expression library

Make the face communicate the narrative beat before adding labels.

| Beat | Face and pose |
|---|---|
| Neutral exposition | dot eyes, short level mouth, relaxed vertical posture |
| Curiosity/question | one raised brow, slightly open mouth, tilted head, question mark optional |
| Surprise/reveal | wide circular eyes, O-shaped mouth, arms lifted |
| Fear/danger | wide eyes, brows arched inward, trembling or leaning away |
| Suspicion | narrowed eyes, one brow lower, side-eye, arms folded |
| Anger/conflict | V-shaped brows, clenched mouth or teeth, forward lean |
| Confusion | uneven brows, small crooked mouth, scattered question marks |
| Sadness/loss | inner brows raised, downturned mouth, drooped shoulders |
| Embarrassment/awkwardness | blank stare or forced grin, rigid posture, tiny sweat mark |
| Delight/payoff | broad smile, crescent eyes, open arms, hearts or motion marks |
| Tenderness/bonding | softened eyes, small smile, kneeling or touch gesture |
| Comic manipulation | oversized glossy “puppy eyes,” tiny mouth, hearts; use rarely for maximum contrast |

Expression selection rule: show the emotion the audience should feel or recognize at that exact line. If the narrator is explaining a mechanism, use neutral/curious faces; if delivering the payoff, switch to surprise, delight, or tenderness.

## Layout grammar

Choose the smallest layout that can explain the voiceover beat.

### Single scene

Use for concrete actions, encounters, emotional beats, rhetorical one-liners, and visual jokes. Keep one dominant interaction and at most three important props.

### Reaction close-up

Use for a reveal, objection, surprise, fear, awkward pause, or emotional turn. Enlarge the head and expression; simplify the background.

### Two-panel comparison

Use for before/after, dog versus wolf, ancient versus modern, with versus without, or claim versus reality. Mirror camera angle and scale so the contrast reads instantly.

### Three-panel sequence

Use for a short process, escalating behavior, or beginning/middle/end. Read left to right.

### Four-cell grid

Use a 2×2 “tic-tac-toe-like” grid for four examples, four eras, day/night plus with/without, or a four-step mechanism. Give every cell a distinct mini-scene and reuse the same characters. Keep cell backgrounds simple and use one short label per cell.

### Four-column progression

Use for generations, eras, stages, or transformation. Keep baselines aligned and show one variable changing per column.

### Diagram/infographic

Use for cause and effect, biology, research findings, classifications, or a named concept. Combine a simple central visual with arrows, checks/crosses, or a short title. Avoid dense paragraphs.

### Timeline/map/tree

Use a timeline for time, a map for geography or multiple origins, and a branching tree for ancestry or diversification. Add only labels needed to understand the narrated claim.

### Board within a scene

Place a scientist, teacher, or protagonist beside a board when the narration shifts into formal explanation. The face supplies tone; the board supplies structure.

### Thought or speech bubble

Use for imagined motives, anthropomorphism, a joke, or internal conflict. Keep bubble copy below eight words.

## Concept-selection decision tree

1. Identify the line's narrative function: setup, action, danger, contrast, list, sequence, mechanism, evidence, number, objection, rhetorical question, humor, emotional payoff, or bridge.
2. Extract the smallest visual claim that would still make sense with the audio muted.
3. Choose the representation:
   - concrete action → single scene;
   - emotion/reveal → reaction close-up;
   - two opposing states → split comparison;
   - three or four examples/stages → multi-panel grid;
   - causal explanation → arrows or diagram;
   - dates/evolution → timeline or progression;
   - locations/origins → map;
   - abstract idea → physical metaphor or visual gag;
   - named evidence/study → board within a scene.
4. Choose the primary character's expression from the intended audience response.
5. Preserve the current location and characters when the narration remains on the same story beat. Change the full composition only when the concept changes.
6. Put one concept on one slide. If a slide needs more than four labeled regions, split it.

## Visual metaphor rules

- Make abstract concepts physical: selection becomes a choosing hand; cause and effect become dominoes or arrows; mutual change becomes two-way arrows or matching puzzle pieces; time becomes a road or timeline; diversity becomes a branching tree.
- Prefer familiar, literal metaphors over clever but slow metaphors.
- Use one absurd detail for humor, not a frame full of jokes.
- Let narration carry nuance. The image should carry the instantly recognizable gist.

## Text rules

- Do not paste narration into the image.
- Use 0–8 words per label and normally no more than 20 total visible words on one slide.
- Use high-contrast black lettering on cream/white cards or directly on simple sky areas.
- For text-heavy diagrams, generate the art without text and overlay verified lettering during composition when the model cannot render it reliably.
- Proofread every generated label against the manifest.

## Prompt skeleton

Use this order so the model sees style before detail:

```text
16:9 flat 2D hand-drawn stickman educational cartoon. Thick slightly uneven black outlines; white circular stick-figure heads and thin black limbs; simple colored cartoon animals; broad flat fills; sparse stage-like background; limited cyan, indigo, green, brown, cream, red, and yellow palette; playful educational tone.

LAYOUT: [single scene / reaction close-up / split comparison / 2x2 grid / four-column progression / diagram / timeline / map / board within scene].

SCENE: [one-sentence description of the visible concept and left-to-right composition].

CHARACTERS AND EXPRESSIONS: [who appears, continuity identity, face, pose, gaze, gesture].

PROPS AND LABELS: [only essential objects; exact short text in quotes or state “no text”].

COMPOSITION: strong readable silhouettes, generous empty space, one dominant focal point, safe margins, no cropped heads or labels.

Avoid photorealism, 3D rendering, gradients, detailed anatomy, painterly texture, cinematic realism, clutter, illegible text, watermarks, and logos.
```

## Quality gate

Reject or revise a slide when any of these are true:

- The concept is unclear without reading the prompt.
- The face does not match the voiceover's emotional beat.
- A recurring character changes head shape, line weight, clothing cue, or animal markings.
- A grid cell is decorative rather than meaningfully distinct.
- The slide contains unnecessary narration text.
- The palette, line, or rendering becomes realistic, glossy, painterly, or 3D.
- Labels are misspelled, too small, or partially cropped.
- The composition cannot be understood in roughly one second.
