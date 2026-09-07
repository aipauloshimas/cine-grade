# Cine-Grade

Turn a raw take into **a scene from any film or series** with **one text prompt** for **Seedance 2.5** — the film's color grade and lighting **plus its director's camera work**, cut on your own speech beats. Same face, same performance, same voice. No reference still, no LUT, no manual grading.

You shoot (or AI-generate) a plain, ungraded clip. The skill reads it — word-level timestamps and frames — decomposes the film's look into **8 axes of light**, designs a shot list in the **director's own camera grammar** (Refn's glacial symmetrical tableaux, Villeneuve's monumental wides, Jenkins' circling handheld, the Wachowskis' surveillance descents…), and fuses both into a single prompt. Upload the video alone, paste, and the clip comes back as a multi-camera scene inside the film: the room grows into the director's compositions, the light is the film's, and you are still you.

## How it works
1. Name the film (or paste a still) and drop your clip — or say you haven't shot yet.
2. **Viability filter.** Only films whose look lives in *light* pass. A film that needs its set to be recognized (Wes Anderson's pink hotel, Amélie's painted walls) is redirected to the closest look that works. A soft look that would barely change your take triggers a **delta check**: stronger films of the same palette, your call.
3. **Ingest.** Word-level timestamps (Whisper, local) and frames. The skill reads what is really in the frame — sky, wall, window, desk, objects, skin.
4. **Shot list in the director's grammar.** Cuts on phrase starts and silences, one dynamic move at most, and a hard **scale rule**: no camera ever frames you smaller than your own take does (that is how a generation loses the performance).
5. **Checkpoint.** You see the breakdown and the shot list with cut times before anything is written. Accept or adjust.
6. **The prompt.** One paste-ready block: identity and performance locks, the grade written onto your frame's real elements, the camera sequence, continuity and negatives. Plus two result checks and a defect → countermeasure table for the second run.

**Grade only?** Say "grade only" or "keep my cameras" and you get the light-and-color prompt alone, your framing untouched.

No footage yet? The skill designs the raw take instead: which composition of the film to quote, where the camera sits, the "honest before" rules (neutral wardrobe, natural light, no filters), and an AI-generation prompt with placeholders for your own character.

## Validated in production
Blade Runner 2049 (Vegas amber), Moonlight (blue-violet night), The Matrix (green interrogation room), Only God Forgives (Refn red, full director cut) — prompts included. Plus approved treatments (Pulp Fiction, Se7en, Mad Max, Drive, Her, Euphoria, BR2049 interiors), thirteen director camera grammars, a derivation method for any other director, and a rejected list with the reasons.

## Install the skill
This is a **Claude Code skill**. Clone it into your skills folder:

```bash
git clone https://github.com/aipauloshimas/cine-grade ~/.claude/skills/cine-grade
```

(Windows: clone into `C:\Users\<you>\.claude\skills\cine-grade`.)

Then open Claude Code, drop your clip and say: **"make my clip look like The Matrix"** — or `/cine-grade`.

## Setup (free and local, no API keys)
The director cut needs word-level timestamps of your speech. `scripts/check_env.py` reports what is missing and how to install it:
- **Python 3.8+**
- **ffmpeg** (includes `ffprobe`) — macOS `brew install ffmpeg` · Windows `winget install Gyan.FFmpeg` · Linux `sudo apt install ffmpeg`
- `pip install -r requirements.txt` (openai-whisper; the first run downloads a ~460 MB model once)

Everything runs locally. Whisper is multilingual — speak any language; the prompt is always English.

## Files
- `SKILL.md` — the skill (hard rules, the director-cut workflow, canvas → film table, red flags).
- `references/director-cut.md` — the default mode: director camera grammars, derivation method, the hybrid camera + grade skeleton, the scale rule, a validated Refn example.
- `references/prompt-skeleton.md` — the grade written as prose, the preservation block, validated grades; the grade-only prompt.
- `references/eight-axis.md` — the 8-axis decomposition method with a worked example.
- `references/film-looks.md` — viability filter, validated / approved / rejected films, palette families, delta check, series pairing.
- `references/take-design.md` — the honest "before": canvas, framing quotes, AI-generated takes, series planning.
- `references/troubleshooting.md` — defect → countermeasure.
- `scripts/beats.py` — local word-level transcription (Whisper) + silences + first-guess cut points.
- `scripts/check_env.py` — preflight dependency check.
- `requirements.txt` — the single Python dependency.

## License
MIT. See `LICENSE`.

By The Creator Stack.
