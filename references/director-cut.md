# Director cut: camera grammar + grade in ONE prompt

Production-validated (2026-09-06, live generation reviewed frame by frame): one raw take re-filmed by virtual moving
cameras cut on the speech beats, in the director's own camera grammar, AND
re-lit to the film's look — a single Seedance 2.5 prompt, base video as the
only upload. The result read as a real multi-cam shoot inside the film.

**What the generation actually did (observed 2026-09-06):** more than
relight + re-film. Describing each shot's composition in the director's
grammar made the model EXTEND the environment to serve that composition —
a plain white table became a long black lacquered table with the red
window reflected as a line across it, the room grew black walls and a
matching second window, and the wide tableau placed the subject small and
dead-center at the far end of a room the original take never showed. Face,
wardrobe, gestures, timing and voice stayed identical. So in this mode the
"do not regenerate physical elements" clause holds for the PERSON and the
PERFORMANCE, while the set is allowed to grow into the director's frame —
and it stays coherent because the grade is locked across every shot. This
is a restaging, not a filter: the take becomes a scene from the film.
Write the wide shots as the director would compose them and let the model
build the room to match; keep the identity and performance locks absolute.

This mode borrows the cine-multicam skill's skeleton (load-bearing lines
fixed) and adds two things: a LIGHTING AND COLOR GRADE section carrying the
8-axis treatment, and shot bodies that say how the new light sits in each
framing.

## Inputs and ingest
1. The raw take (local file). Word-level timestamps: run the cine-multicam
   skill's `scripts/beats.py` on it (shared Whisper cache). Without that
   skill, any word-level transcription works — cuts need word start/end
   times and silences.
2. Frames at 1 fps (`ffmpeg -vf fps=1`) — read ALL of them alongside the
   words. Cuts are motivated by both: phrase starts, silences, gestures,
   posture changes, lean-ins.
3. The film passes the viability filter and its 8-axis treatment exists
   (`film-looks.md` / `eight-axis.md`).

## Director camera grammars (pick the film's director, never the default arc)
| Director / film | Camera grammar | Cut count | Never |
|---|---|---|---|
| **Refn** (Only God Forgives, Drive) | frontal symmetrical tableaux, glacial straight dolly-ins, impassive long holds through silences, one slow straight descent/rise | very few (3 in 5 s) | handheld, arcs, whips |
| **Villeneuve / Deakins** (BR2049) | monumental locked wides, subject small then large, extremely slow push, one crane reveal of scale | few | fast moves, close handheld |
| **Barry Jenkins** (Moonlight) | intimate handheld close-ups, slow circling, direct-to-lens gaze, shallow depth, lingering on skin | medium | locked symmetry |
| **Wachowskis** (The Matrix, interrogation) | precise dolly, surveillance high angle descending to eye level, overhead top-down, one slow push on the seated subject | medium | handheld |
| **Fincher** (Se7en) | locked-off, low and precise, minimal reframes, slow dolly, cuts on action | medium | operator breathing |
| **Tarantino** (Pulp Fiction) | trunk-shot low angle, long static two-shots, one slow push, hard cuts on lines | medium | drift |
| **Sam Levinson** (Euphoria) | circling steadicam, long glossy holds, in-and-out of colored light, close on skin | medium-high | static wides |

**Scale rule (hard, from a real failure):** every virtual camera stays at
human scale and never frames the subject SMALLER than the base video does.
No aerial, drone, overhead or god's-eye viewpoints, no "tiny figure in a
vast landscape" openings. When the subject becomes a dot there is no face,
mouth or gesture left to preserve, the model switches to pure generation
and never comes back: the whole clip returns with a stiff re-animated body,
plastic skin and generic lip sync (observed 2026-09-06, Villeneuve aerial
descent on a 7 s walk-in take — the environment was superb, the
performance was gone). Hype in the opening comes from camera MOVEMENT at
the source's scale (a low ground rush, a fast lateral, a whip-settle), not
from scale. Add to CRITICAL: "Every camera stays at human scale on the
ground… he is never framed smaller than in the base video — his face,
hands and gestures must remain readable in every shot" plus a skin/body
line: "Preserve his real skin texture and micro-expressions from the base
video: no smoothing, no plastic look, no re-animated body."

Shot count follows the director first, duration second (at least ~2 s per
shot; a 5 s take under Refn is 3 shots, not 4). Cuts land on phrase starts
or at the start of a silence, never mid-word. Every shot body double-anchors
its timecode to a spoken moment or gesture AND states how the light falls
in that framing ("the left side of his face burning red-amber, the right
sunk into near-black").

## Skeleton (validated hybrid — load-bearing lines fixed)
```
Edit the attached BASE VIDEO.

CRITICAL
The [man] must CONTINUE SPEAKING throughout the entire video exactly as in the original base video. Preserve [his] exact dialogue, voice, timing, lip sync, expressions, gestures and body movement. The ORIGINAL AUDIO must continue seamlessly across every cut.
Think of this as ONE uninterrupted speaking performance filmed simultaneously by several different cameras, in a room that is now lit completely differently.
THE PERFORMANCE NEVER CHANGES. ONLY THE CAMERA, THE EDITING AND THE LIGHTING CHANGE.
Preserve the same [man], clothing, [room, furniture, window]. Do not alter, replace, or regenerate any physical elements.
[His] facial identity must be taken entirely from the BASE VIDEO itself and stay identical from every new viewpoint and under the new light.

LIGHTING AND COLOR GRADE (applies identically to every shot)
[The 8-axis treatment written onto the frame's real elements — what the window, walls, table, floor, garments and skin BECOME. End with:] The grade is locked and identical across all cuts — the light never changes between shots, only the camera does. Not a [color] tint or filter: a physically lit [color] room.

CAMERA SEQUENCE

[MM:SS.d]–[MM:SS.d] — [SHOT NAME]
[Position → movement → speed → end position, in the director's grammar. Double anchor to a line/gesture. How the new light sits in this framing. One rig imperfection.]

[... N shot blocks, chained to one decimal, summing to the exact duration ...]

CAMERA RHYTHM
Controlled, cinematic, easy to read. No constant cuts. Use [N] distinct shots of uneven durations. Progression: [DIRECTOR ARC]. Clean hard cuts only — no transitions, no morphs, no artificial effects.

REAL CAMERA IMPERFECTIONS (occasional, almost subconscious — never constant, never exaggerated)
[Only the rigs used: dolly / crane / handheld / long lens lines from cine-multicam.]

CONTINUITY — ABSOLUTELY CRITICAL
Every shot represents the exact chronological moment occurring in the BASE VIDEO. Nothing resets because of a camera cut. Actions and gestures never repeat. Object interactions never restart. Dialogue and audio never restart. When [his] face is visible, [his] mouth matches the exact words at that timestamp. When [his] face is out of frame, [his] original voice continues normally. All shots respect the original screen direction: [his] eyeline stays consistent, and camera positions never flip [him] to the opposite side of the frame in a disorienting way. The lighting and color grade are identical in every shot. Imagine [N] real cameras filming the SAME performance simultaneously in the SAME [color]-lit room and the editor simply switching between them.

FINAL FEEL
[Director tone sentence.] The camera should enhance the performance, never compete with it.
Same scene. Same person. Same performance. Same dialogue. Same voice. Same timing. ONLY THE CINEMATOGRAPHY AND THE LIGHTING CHANGE.
No new dialogue. No replacement voice. No silent montage. No new actions, characters or objects. No added props, lamps or set dressing. No camera equipment, rigs or crew visible in frame. No music. No subtitles. No identity drift. No face changes, beautification or artificial skin. No slow motion. No speed ramps. No time remapping.
```

## Validated example — Refn / Only God Forgives on a 5.04 s take
Raw scene: seated at a plain white table in an empty room, phone propped
high in a corner, window with a city view top-left, overcast daylight; he
speaks one line, pauses, then pushes up toward the lens pointing.
Words: 0.0–2.0 first phrase (hand rolls in a circle, looks up) · 2.0–3.4
second phrase (smile back to lens) · 3.4–3.8 silence · 3.8–5.0 closer (rises,
points). Cuts at 2.0 and 3.8.

```
Edit the attached BASE VIDEO.

CRITICAL
The man must CONTINUE SPEAKING throughout the entire video exactly as in the original base video. Preserve his exact dialogue, voice, timing, lip sync, expressions, gestures and body movement. The ORIGINAL AUDIO must continue seamlessly across every cut.
Think of this as ONE uninterrupted speaking performance filmed simultaneously by several different cameras, in a room that is now lit completely differently.
THE PERFORMANCE NEVER CHANGES. ONLY THE CAMERA, THE EDITING AND THE LIGHTING CHANGE.
Preserve the same man, clothing, empty room, plain table, bare walls and window. Do not alter, replace, or regenerate any physical elements.
His facial identity must be taken entirely from the BASE VIDEO itself and stay identical from every new viewpoint and under the new light.

LIGHTING AND COLOR GRADE (applies identically to every shot)
Relight the entire scene as a saturated red-and-tungsten low-key night: the room is lit only by a deep blood-red light source coming through the window and a single warm tungsten practical. The window becomes a glowing deep red source, the city outside dissolving into dark crimson murk; its light spills as saturated crimson across the wall and table nearest to it. The bare walls fall into a dark oxblood-red field, nearly black away from the window, the far corners pure black; the floor sinks into warm black. The white table MUST become dark lacquer-black with only a narrow saturated red reflection of the window on its surface — no light grey left on it. His face carries a hard two-tone split in every shot: the window side glows saturated red-amber with a small hot tungsten-orange highlight on the cheekbone and nose bridge, the opposite side falls into near-black shadow with only a faint red edge; skin keeps natural texture and a living warm undertone inside the red. The black hoodie becomes absolute velvety black swallowing the shadows, with a thin red rim on its folds; the brown beanie turns deep burnt red-orange. Every hue stays in the red / crimson / tungsten-amber / warm-black family — no blue, no cyan, no green, no neutral grey anywhere. Contrast very high: crushed dense blacks dominate the frame, small areas of glowing saturated highlight, hard filmic shoulder; most of the frame is black and the red lives only where the window light reaches. Subtle halation around the red window and the tungsten highlight on the skin, fine film grain, heavy dark vignette, still humid night air. The grade is locked and identical across all cuts — the light never changes between shots, only the camera does. Not a red tint or filter: a physically lit red room.

CAMERA SEQUENCE

00:00.0–00:02.0 — FRONTAL SYMMETRICAL TABLEAU, GLACIAL DOLLY IN
Locked frontal composition at eye level, directly across the table from him: he sits dead center, the far edge of the black lacquered table a perfectly horizontal line across the lower third carrying a thin red reflection, the near-black walls balanced symmetrically around him, the red window glowing at frame left. Perform an almost imperceptible, very slow physical dolly in, starting wide enough to show the whole tabletop and ending a few inches closer, keeping him exactly centered as he opens his hands over the table and rolls one hand in a circle while looking up — his hands catching the red light, his face split red-and-black. Slight physical vibration of the dolly, natural deceleration. The frame observes, still and cold.

00:02.0–00:03.8 — LOCKED FRONTAL CLOSE-UP, LONG HOLD
Clean hard cut as he turns his eyes back to the lens and smiles. Tight frontal close-up of his face, absolutely static, centered, the wall behind him falling to black; the left side of his face burning red-amber with the tungsten highlight on the cheekbone, the right side sunk into near-black shadow. He says his short line, then the shot HOLDS impassively through the silence that follows, his hands settling onto the table just below frame. No movement at all — the stillness is the point. Occasional momentary soft focus as he begins to shift his weight.

00:03.8–00:05.0 — HIGH ANGLE DESCENDING TO EYE LEVEL, SLOW AND STRAIGHT
Hard cut to the original raised three-quarter high angle looking down at him over the black table, the red window glowing in the top-left corner. As he pushes up off the table and rises toward the lens pointing his finger, the camera performs a slow, perfectly straight physical descent, lowering from the high position to his eye level and settling face to face with him, his pointing finger arriving close to the lens at the last moment, the red-and-black split across his face filling the frame. Smooth physical inertia, subtle vibration during the move, a tiny settling movement when it stops.

CAMERA RHYTHM
Controlled, cinematic, easy to read. No constant cuts. Use 3 distinct shots of uneven durations. Progression: COLD SYMMETRICAL CALM → IMPASSIVE INTIMATE HOLD → SLOW DESCENDING CONFRONTATION. Clean hard cuts only — no transitions, no morphs, no artificial effects.

REAL CAMERA IMPERFECTIONS (occasional, almost subconscious — never constant, never exaggerated)
Dolly/travelling: slight physical vibration, natural acceleration and deceleration.
Crane: smooth physical inertia, subtle vibration during movement.

CONTINUITY — ABSOLUTELY CRITICAL
Every shot represents the exact chronological moment occurring in the BASE VIDEO. Nothing resets because of a camera cut. Actions and gestures never repeat. Object interactions never restart. Dialogue and audio never restart. When his face is visible, his mouth matches the exact words at that timestamp. When his face is out of frame, his original voice continues normally. All shots respect the original screen direction: his eyeline stays consistent, and camera positions never flip him to the opposite side of the frame in a disorienting way. The lighting and color grade are identical in every shot. Imagine 3 real cameras filming the SAME performance simultaneously in the SAME red-lit room and the editor simply switching between them.

FINAL FEEL
Slow, hypnotic, formally rigid — every frame composed like a symmetrical painting drowned in red and black, the camera moving only in straight glacial lines, holding on stillness longer than feels comfortable. The camera should enhance the performance, never compete with it.
Same scene. Same person. Same performance. Same dialogue. Same voice. Same timing. ONLY THE CINEMATOGRAPHY AND THE LIGHTING CHANGE.
No new dialogue. No replacement voice. No silent montage. No new actions, characters or objects. No added props, lamps or set dressing. No camera equipment, rigs or crew visible in frame. No music. No subtitles. No identity drift. No face changes, beautification or artificial skin. No slow motion. No speed ramps. No time remapping.
```

## Checkpoint (mandatory, from cine-multicam)
Present the breakdown table and the director shot list with cut times BEFORE
filling the skeleton; ask the user to accept or adjust the cuts and the
director grammar. Never ship unchecked.

## Watch for (failure modes, different fixes)
| Symptom | Fix |
|---|---|
| Grade good, cuts went soft / morphed | Move CAMERA SEQUENCE above the GRADE section and add "clean hard cut" to each shot header |
| Cuts good, grade flat / tinted | Strengthen the GRADE section with the film's countermeasures from `troubleshooting.md` (blacks, split, no pure white) |
| Grade differs between shots | Repeat "identical grade in every shot" inside each shot body |
| Sibling-template tokens leak in | Never `* At [Xs]:`, "Whip the camera", "kinetic super" — this is the cine-multicam grammar only |
| Whole clip comes back stiff, plastic, re-animated, generic lip sync | A shot framed the subject far smaller than the base (aerial / vast wide). Apply the scale rule: ground-level cameras, subject never smaller than in the source, dynamic move = movement not scale; add the CRITICAL scale + skin lines |
| Naming a rig renders it as a prop | Never "robot arm" / "robotic arm"; write "a precision camera move" and describe the trajectory (cine-multicam countermeasure) |
