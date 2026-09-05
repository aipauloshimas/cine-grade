# Cine-Grade

Recreate the look of **any film or series** on your raw footage with **one text prompt** for **Seedance 2.5**. No reference still, no LUT, no manual grading.

You shoot (or AI-generate) a plain, ungraded clip. The skill decomposes the film's look into **8 axes of light** — light, temperature, palette, contrast, curve, exposure, optics, atmosphere — writes them as prose onto the real elements of your frame, and locks everything else. Upload the video alone, paste, and the same clip comes back re-lit as the film. Same face, same motion, same room. Only the light changes.

## How it works
1. Name the film (or paste a still to analyze) and drop your clip, or say you haven't shot yet.
2. **Viability filter.** Only films whose look lives in *light* pass. If a film needs its set to be recognized (Wes Anderson pink hotels, Amélie's painted walls), the skill says so and hands you the closest look that works — it never "solves" it by regenerating your environment.
3. **Frame analysis.** It looks at a frame of your clip, names what is really there (sky, wall, window, table, garments, skin) and checks the film fits that canvas.
4. **The prompt.** One paste-ready block: the 8-axis treatment written onto your frame's elements, then a verbatim preservation block ending in `ONLY change: lighting, exposure, color grading…`.
5. **Result checks + iteration.** Two checks specific to the look, and a defect → countermeasure table for the second run.

No footage yet? The skill designs the raw take instead: which composition of the film to quote, where to prop the phone, the "honest before" rules (neutral wardrobe, natural light, no filters), and an AI-generation prompt with placeholders for your own character.

## Validated looks
Blade Runner 2049 (Vegas amber), Moonlight (blue-violet night), The Matrix (green interrogation room) — full production-validated prompts included. Plus approved-but-untested treatments (Pulp Fiction, Se7en, Mad Max, Drive, Her, BR2049 interiors) and a rejected list with the reasons.

## Install the skill
This is a **Claude Code skill**. Clone it into your skills folder:

```bash
git clone https://github.com/aipauloshimas/cine-grade ~/.claude/skills/cine-grade
```

(Windows: clone into `C:\Users\<you>\.claude\skills\cine-grade`.)

Then open Claude Code, drop your clip and say: **"make my clip look like Blade Runner 2049"** — or `/cine-grade`.

## Files
- `SKILL.md` — the skill (hard rules, workflow, canvas → film table, red flags).
- `references/prompt-skeleton.md` — assembly skeleton, the preservation block, three validated prompts.
- `references/eight-axis.md` — the 8-axis decomposition method with a worked example.
- `references/film-looks.md` — viability filter, validated / approved / rejected films, series pairing rule.
- `references/take-design.md` — the honest "before": canvas, framing quotes, AI-generated takes, series planning.
- `references/troubleshooting.md` — defect → countermeasure.

## License
MIT. See `LICENSE`.

By The Creator Stack.
