# Troubleshooting: defect → countermeasure

Ask the user to describe the defect in one line, then reinforce the matching
clause and re-run. Reinforcements are ADDED to the treatment prose, before
the preservation block.

| Symptom | Reinforce with |
|---|---|
| Just a color tint, no depth or haze | "Atmospheric perspective must be strong: the horizon MUST almost dissolve into glowing light, far hazier than the foreground" |
| Face flat, no side gradient (Moonlight-type looks) | "Strong side gradient: the [right] side of the face MUST fall into deep [blue-violet] shadow, the [left] side luminous" |
| Skin dead / grey / corpse-like under a cool grade | "Keep a warm human undertone in the skin fighting through the [blue] light; skin stays alive" |
| Green did not reach the skin (Matrix) | "His skin MUST turn pale green-olive, reds fully drained — the cast is in the skin, not only the room" |
| Pure white survived (table, window, sky) | "No pure white anywhere — every highlight slightly [green/amber], dimmed and tinted" |
| Blacks went grey / milky | "Blacks rich and velvety, never grey; dense [color]-edged blacks in the clothing" |
| Blacks crushed, detail gone | "Shadows dense but never fully crushed, with visible detail breathing inside them; smooth filmic rolloff" |
| Environment changed (furniture, window view, wall) | You wrote a set change. Rewrite the sentence as what the surface BECOMES under the light; keep the preservation block verbatim |
| Wardrobe color shifted unrealistically | Name the garment and its fate: "the black hoodie stays deep soft black; the warm beanie falls into a muted tone under the light" |
| Identity drift | The preservation block is intact? Add "the same person, same face, unchanged" at the start of the treatment; never add a film still as reference — it pulls identity |
| Flicker between frames | "Consistent frame-to-frame, the grade locked across the whole clip"; trim to a shorter segment and re-run |
| Looks like a preset / Instagram filter | Add two more axes from `eight-axis.md` (usually optics and atmosphere) — the prompt was palette-only |
| The "before" already looks graded or staged | Regenerate/reshoot the take with the honest-before rules; the reveal is dead otherwise |
| Wrong film chosen for the canvas | Check the canvas table in `take-design.md`; a sky-canvas take cannot carry a side-light look |

## Rationalizations to refuse
| Thought | Reality |
|---|---|
| "I'll just swap the window view to sell the look" | That is regeneration. The before/after is now a lie and the model will warp the rest of the frame with it. |
| "A reference still will make it more accurate" | It transfers composition and identity along with the look. Bake the 8 axes into text instead. |
| "This film needs its set but a tint will be close enough" | The user will get a pink wall and lose trust. Redirect to a light-based look. |
| "The before looks boring — add a lamp" | Boring is the point. Give it geometry (framing quote), not light. |
