---
name: cine-grade
description: Use when the user wants raw footage (a real phone clip or an AI-generated take) turned into a scene from a specific film or series through one Seedance 2.5 video-edit prompt — the film's look, color grade and lighting PLUS its director's camera work cut on the speech beats (the default), or the grade alone when they say "grade only" / "keep my cameras". Also for designing the raw take that will be graded later, and for fighting this workflow's failure modes (result looks like a color filter, performance went stiff/plastic, environment or wardrobe got regenerated, skin went dead/grey, no depth or haze, the "before" already looks staged). Triggers on /cine-grade, "make my clip look like [film]", "color grade like [movie]", "recreate the look of [series]", "cinematic look from a film", "shoot it like [director]", "multicam + grading", a film name plus a clip. PT examples for reliability: "deixa meu vídeo com a cara de [filme]", "faz o grade do [filme] no meu take", "recria o look de [série] nesse vídeo", "qual filme funciona pra esse take". NOT for camera-only edits (/multicam, /cine-multicam), kinetic text (/kinetic-multicam), or hero-object ads.
---

# cine-grade: turn a raw take into a scene from any film (Seedance 2.5)

One raw clip + one text prompt = the same person, same performance, same
voice, now inside the film: its light and color decomposed into 8 axes,
its director's cameras cut on the speech beats, the room grown into the
director's compositions. No reference still, no LUT, no manual grading.

**Default mode is the DIRECTOR CUT** — camera + grade in one prompt
(`references/director-cut.md`). **Grade-only** — light and color, the
user's own cameras and framing untouched — runs only when asked ("grade
only", "keep my cameras", "just the color").

**Core principle: lock the PERSON, describe the LIGHT.** The face,
performance, wardrobe, timing and voice are never regenerated. The film's
look is written as prose onto the real elements of the frame. In the
director cut the set may grow to fit the director's framing; in grade-only
nothing but light changes.

## Read these
1. **`references/director-cut.md` — ALWAYS.** The default mode: director
   camera grammars, the hybrid skeleton, the scale rule, a validated example.
2. **`references/prompt-skeleton.md` — ALWAYS.** The grade written as prose
   (source of the GRADE section), the preservation block, validated grades;
   also the whole prompt for grade-only mode.
3. **`references/eight-axis.md` — Step 6.** Decompose a look into 8 axes and
   write each onto the frame.
4. **`references/film-looks.md` — Steps 1 and 6.** Viability filter,
   validated / approved / rejected films, palette families, delta check.
5. **`references/take-design.md` — only when** the user has no footage yet,
   or is planning a multi-film series.
6. **`references/troubleshooting.md` — Step 9.** Defect → countermeasure.

## Hard rules (never break)
- **The film must live in light.** Only films whose look is lighting and
  color pass the viability filter. If recognizing the film needs its
  objects, walls, wardrobe or set dressing (Grand Budapest, Amélie, In the
  Mood for Love), say so, offer the 3 closest films that pass, and deliver
  the prompt for the best-fitting one. Never "solve" it by inserting the
  film's props — the director cut grows the user's room, it never builds
  the film's set.
- **The person is locked.** Identity from the base video only; dialogue,
  voice, timing, lip sync, gestures, skin texture preserved in every mode.
  Never wardrobe recolors, never a re-animated body. In grade-only mode the
  environment is locked too: surfaces are described by what they BECOME
  under the new light, never replaced.
- **Scale rule (director cut).** No camera ever frames the subject smaller
  than the base video does; no aerial, drone or god's-eye viewpoints. A
  dot-sized subject flips the model into pure generation and the whole clip
  comes back stiff and plastic. Hype comes from movement, not scale.
- **Checkpoint before the prompt (director cut).** Present the breakdown
  table and the director shot list with cut times, ask "accept or adjust?",
  and wait. Never ship a director cut unchecked.
- **A film can have more than one light signature.** Pick the one that
  matches the canvas (Blade Runner 2049 = amber Vegas exterior OR cyan LA
  interior), deriving it with `eight-axis.md` if the library only holds the
  other. Canvas mismatch means another scene of the same film before it
  means another film.
- **Text only — no reference still.** The 8-axis treatment is baked into the
  prompt; the user uploads the video alone. The image+text hybrid exists
  and works for some creators, but a still also carries the film's
  composition, subject and identity into the edit. Offer it only as a
  fallback when a text-only result fails twice on the same defect.
- **Load-bearing lines verbatim.** Director cut: CRITICAL, CAMERA RHYTHM,
  CONTINUITY and FINAL FEEL lines from `director-cut.md`. Grade-only: the
  preservation block ending in "ONLY change:" from `prompt-skeleton.md`.
  Never trimmed for length.
- **Calibrate to the real frame.** Extract frames (ffmpeg) and name the
  actual elements — sky, wall, table, window, floor, objects, garments,
  skin — and what each becomes. Generic prompts produce generic tints.
- **Honest before.** The raw take is ungraded, auto-exposure, neutral
  wardrobe, natural light, no portrait mode, no filter, no colored light —
  but its FRAMING may quote an iconic composition of the target film.
- **Canvas decides the film.** Sky/open space, side-lit shadow, close-up
  skin, interior high angle — the take's big repaintable area is matched
  to the film that repaints it (`take-design.md`).
- **Delta check — warn when the look is soft.** If the film merely
  warms/cools what the take already has (Her on soft window light), say
  plainly that the before/after will be weak, suggest 2–3 STRONGER films of
  the SAME PALETTE, and ASK: stay soft, or go strong. Never silently
  deliver a weak reveal; never silently swap the film.
- **Compare palettes, not temperatures.** "Same vibe" = same dominant hues
  at the same lightness/saturation register (pastel peach-pink, dense
  amber, cool blue-violet, sickly green, orange/teal) — never "warm ↔ warm".
  Her (pastel peach, high-key) is NOT the family of Blade Runner 2049 amber;
  its stronger siblings are Euphoria and Spring Breakers. Name the palette
  in words before proposing alternatives.

## Workflow (director cut — the default)
1. **Inputs.** Target film/series (name or a still); footage (file) or none
   yet; single clip or series. Mode: director cut unless the user asked for
   grade only. Run the **viability filter** and the **delta check**
   (`film-looks.md`). With a still or a clip of the film,
   `python "<this skill's base directory>/scripts/measure_look.py" <take> <film still>`
   measures both looks (hue, saturation, black level, contrast) and gives the
   delta check a verdict instead of a guess (its thresholds are starting
   values: if the verdict surprises you, look at the frames).
2. **No footage yet?** Design the take with `take-design.md` (real recording
   instructions, or an AI-generation prompt via the ugc-craft skill with the
   ungraded-look clauses). Deliver the take design and the film's result
   checks; the edit prompt is written once the footage exists.
3. **Preflight (first run in a session).** `python scripts/check_env.py`
   checks Python, ffmpeg/ffprobe and Whisper. Relay anything missing with
   its install command and ask before installing; never guess around a
   missing tool.
4. **Ingest.** Word-level timestamps: `python scripts/beats.py <video>`
   (Whisper, local; note its EDGES line — a tail silence is a usable hold).
   Frames as two contact sheets, never one image per frame: 2 fps for
   clips up to 10 s, 1 fps above (command in `director-cut.md`); read
   both sheets alongside the words. Seedance 2.5 generates up to 30 s
   (confirmed 2026-09-26); other 2.5 specs are unverified. beats.py
   flags longer takes (LONG_VIDEO), so design for the strongest 30 s
   window.
5. **Breakdown + shot list.** Table: time → spoken phrase → visual event.
   Pick the director from the film (table in `director-cut.md`; derive from
   memory or web search if absent — never ask the user to describe the
   camera). Design the shot list in that grammar: cuts on phrase starts or
   silences, ≥ ~2 s per shot, one dynamic move at most, scale rule on.
6. **Checkpoint.** Show the breakdown and the shot list with cut times (and
   the derived director row if new). Ask: accept or adjust? Wait.
7. **8-axis treatment.** Pull the film from `film-looks.md` /
   `prompt-skeleton.md` or derive with `eight-axis.md`; write it onto the
   frame's real elements, including how the light sits in each framing.
8. **Assemble** the hybrid skeleton in `director-cut.md`: CRITICAL (with the
   scale + skin lines) → LIGHTING AND COLOR GRADE → CAMERA SEQUENCE →
   RHYTHM → IMPERFECTIONS → CONTINUITY → FINAL FEEL. One block. Save it as
   `<video basename>_cine_grade_prompt.txt` next to the video and run
   `python "<this skill's base directory>/scripts/verify_director_cut.py" "<prompt.txt>" --duration <seconds>`;
   it must print `PASS` (fix and re-run on `FAIL`). Deliver with
   two result checks specific to the look, and the usage line: upload the
   base video alone into Seedance 2.5, paste, nothing else attached.
9. **Iterate** with `troubleshooting.md` and the failure table in
   `director-cut.md`. A look or director cut that survives production is
   appended to the references (ask before writing). To check a result in
   numbers, run `measure_look.py <generated video> <film still> --role result`:
   it names the axes that are off and the `troubleshooting.md` reinforcement
   for each.

**Grade-only (on request):** steps 1–2, then extract one or two frames,
then step 6 → assemble with `prompt-skeleton.md` (treatment prose →
preservation block → "ONLY change:") → deliver with checks → iterate.

## Quick reference
| Take canvas | Films that repaint it |
|---|---|
| Open space / sky, low horizon | Blade Runner 2049 (amber), Pulp Fiction, Mad Max |
| Single-window side light, unfilled shadow | Moonlight, Se7en, Drive |
| Frontal close-up, soft light, skin fills frame | The Matrix, Her |
| Interior, high angle over a table/desk | The Matrix, Only God Forgives |

Director ↔ film pairs and the derivation method: `director-cut.md`.

## Red flags — stop and re-read the hard rules
- You are writing a director cut and have not shown the checkpoint.
- A shot frames the subject smaller than the base video, or from the air.
- The prompt contains "replace", "recolor his", "add a [object]", "swap the".
- You are about to tell the user to upload a still from the film.
- The film needs its set to be recognized and you are trying anyway.
- The raw take already has colored lights, costume or a graded look.
- The prompt never names an element that is actually in the frame.
- The film only warms or cools the take's existing light and you haven't
  warned that the reveal will be weak.
- You matched a "stronger" alternative by temperature instead of palette.
