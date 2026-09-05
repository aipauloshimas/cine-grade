---
name: cine-grade
description: Use when the user wants raw footage (a real phone clip or an AI-generated take) to get the look, color grade, lighting or "vibe" of a specific film or series through a Seedance 2.5 video-edit prompt, or wants to design the raw take that will be graded later, or is fighting the failure modes of this workflow (result looks like a color filter, environment or wardrobe got regenerated, skin went dead/grey, no depth or haze, the "before" already looks staged). Triggers on /cine-grade, "make my clip look like [film]", "color grade like [movie]", "recreate the look of [series]", "cinematic look from a film", a film name plus a clip. PT examples for reliability: "deixa meu vídeo com a cara de [filme]", "faz o grade do [filme] no meu take", "recria o look de [série] nesse vídeo", "qual filme funciona pra esse take". NOT for multi-camera edits (/multicam, /cine-multicam), kinetic text (/kinetic-multicam), or hero-object ads.
---

# cine-grade: recreate any film's look on raw footage (Seedance 2.5)

One raw clip + one text prompt = the clip re-lit and re-graded to a named
film. No reference still, no LUT, no manual grading. The magic is honest
only when the BEFORE is genuinely plain and the AFTER changes nothing but
light — so this skill guards both ends.

**Core principle: describe the LIGHT, never rebuild the SET.** A film's look
is decomposed into 8 axes of light and written into the prompt as prose; the
edit is forbidden from regenerating any physical element.

## Read these
1. **`references/prompt-skeleton.md` — ALWAYS.** The assembly skeleton, the
   verbatim preservation block, and three production-validated prompts.
2. **`references/eight-axis.md` — Step 3.** How to decompose a look and write
   each axis as prompt prose.
3. **`references/film-looks.md` — Step 1 and 3.** Validated looks ready to
   paste, approved-but-untested looks, rejected films and why.
4. **`references/take-design.md` — only when** the user has no footage yet
   (real recording instructions or AI-generation take design) or is planning
   a multi-film series.
5. **`references/troubleshooting.md` — Step 6.** Defect → countermeasure.

## Hard rules (never break)
- **Light, not set.** Only films whose look lives in lighting/color pass the
  viability filter. If recognizing the film needs the right objects, walls,
  wardrobe or set dressing (Grand Budapest, Amélie, In the Mood for Love),
  say so, offer the 3 closest films that pass, and deliver the full prompt
  for the best-fitting one (don't stop at a list). Never "solve" it by
  regenerating the environment.
- **A film can have more than one light signature.** Pick the signature that
  matches the user's canvas (Blade Runner 2049 = amber Vegas exterior OR cold
  cyan LA interior), deriving it with `eight-axis.md` if the library only
  holds the other one. Canvas mismatch means another scene of the same film
  before it means another film.
- **The edit prompt changes ONLY light.** Lighting, exposure, color, contrast,
  shadows, highlights, atmosphere. Never wardrobe recolors, never swapped
  furniture, never a replaced window view, never added objects or fog
  machines "in the room". Existing surfaces are described by what they
  BECOME under the new light ("the grey concrete becomes warm dusty amber").
- **Text only — no reference still.** The 8-axis treatment is baked into the
  prompt; the user uploads the video alone. The image+text hybrid ("Edit
  Video 1 using Image 1 as a reference for lighting…") exists and works for
  some creators, but a still also carries the film's composition, subject
  and identity into the edit and lets the model skip the analysis. This
  skill's method IS the analysis written as text — offer the hybrid only as
  a fallback when a text-only result fails twice on the same defect.
- **Preservation block verbatim** (in `prompt-skeleton.md`), ending with the
  "ONLY change:" clause. Never trimmed for length.
- **Calibrate to the real frame.** When a clip or frame is available, look at
  it (extract a frame with ffmpeg if given a file) and name the actual
  elements — sky, wall, table, window, floor, garments — and what each turns
  into. Generic prompts produce generic tints.
- **Honest before.** The raw take is ungraded, auto-exposure, neutral
  wardrobe, natural light, no portrait mode, no filter — but its FRAMING may
  quote an iconic composition of the target film. Composition is free; light
  and set dressing are not.
- **Canvas decides the film.** Sky/open space, side-lit shadow, close-up
  skin, sparse interior — the take's big repaintable area is matched to the
  film that repaints it (`take-design.md`).
- **Delta check — warn when the look is soft.** The reveal is only as strong
  as the distance between the take's own light and the film's look. If the
  film is gentle (Her, Amélie-adjacent warmth, low-contrast naturalism) or
  merely warms/cools what the take already has, say plainly: "this look is
  soft — on this take the before/after will be weak." Then suggest 2–3
  STRONGER films with the same vibe (see the delta table in
  `film-looks.md`) and ASK which the user wants: stay soft, or go strong.
  Do not silently deliver a weak reveal; do not silently swap the film.

## Workflow
1. **Inputs.** Target film/series (name or a still to analyze); footage
   (file, frame or description) or none yet; single clip or series.
   Run the **viability filter** on the film (`film-looks.md`).
2. **Footage branch.**
   - Has footage → extract/inspect a frame, list the visible elements and the
     canvas it offers, check the film fits that canvas (redirect if not).
   - No footage → design the take with `take-design.md`: real-recording
     instructions, or an AI-generation prompt (see the ugc-craft skill for
     talking-head anatomy) with the ungraded-look clauses. The edit prompt
     is NOT written yet — deliver the take design plus the film's result
     checks, and write the grade once the footage exists.
3. **8-axis treatment.** Pull the film from `film-looks.md` or derive it
   with `eight-axis.md` (from memory of the film or a supplied still).
4. **Assemble** with the skeleton: treatment prose calibrated to the frame's
   elements → preservation block → "ONLY change:". One dense block.
5. **Deliver** the prompt plus two result checks specific to that look
   (e.g. "the horizon must dissolve into haze", "skin must stay alive").
6. **Iterate** with `troubleshooting.md`; a look that survives production
   is appended to `film-looks.md` (ask before writing).

## Quick reference
| Take canvas | Films that repaint it |
|---|---|
| Open space / sky, low horizon | Blade Runner 2049 (amber), Pulp Fiction, Mad Max |
| Single-window side light, unfilled shadow | Moonlight, Se7en, Drive |
| Frontal close-up, soft light, skin fills frame | The Matrix, Her |
| Sparse institutional interior, high angle | The Matrix |

## Red flags — stop and re-read the hard rules
- The prompt contains "replace", "recolor his", "add a [object]", "swap the".
- You are about to tell the user to upload a still from the film.
- The film needs its set to be recognized and you are trying anyway.
- The raw take already has colored lights, costume or a graded look.
- The prompt never names an element that is actually in the frame.
- The film only warms or cools the take's existing light and you haven't
  warned that the reveal will be weak.
