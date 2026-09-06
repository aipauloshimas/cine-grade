# Film looks library

## The viability filter (run first, every time)
**A look passes only if it lives in LIGHT and COLOR.** Ask: with the user's
plain room / street / wall left exactly as it is, would the graded frame be
recognized as the film? If recognition needs the film's objects, wardrobe,
walls or set dressing, the look lives in production design and the edit
cannot deliver it without regenerating the scene — which is forbidden.

Fails → say why in one sentence and offer the three closest passing looks
by mood (pastel/bright → Her or Pulp Fiction daylight; warm-nostalgic →
Blade Runner 2049 amber; dense-red interiors → Moonlight or Drive).

## Validated in production (paste-ready treatments in `prompt-skeleton.md`)

| Film | Signature (as light) | Canvas it needs | Result checks |
|---|---|---|---|
| **Blade Runner 2049** (Vegas sequence) | monochromatic amber daylight, thick luminous dust, strong atmospheric perspective, subject as soft silhouette emerging into amber | open space / sky, low horizon, depth | horizon must dissolve into haze; not just an orange tint |
| **Moonlight** | deep saturated blue-violet night, luminous cool skin on the lit side, rich never-crushed shadow, warm undertone alive in skin | single-window side light, unfilled shadow | strong side gradient on the face; skin alive, not grey |
| **The Matrix** | controlled sickly green cast on everything incl. skin, dense green-edged blacks, no pure white, clinical fluorescent | sparse interior or close-up skin | green must be IN the skin; no pure white left |
| **Only God Forgives** (Refn) | blood-red source light + one tungsten practical, oxblood walls to black, lacquer-black table, hard red/black split on the face | sparse interior, table, window | table must go black; shadow side of face near-black — the grade-only run came out flat, the director-cut run (with the blacks reinforcement) nailed it; full prompt in `director-cut.md` |

One film, several signatures: a validated film may have a second look that
lives in light (BR2049 amber exterior vs. cyan interior). Match the
signature to the canvas before switching films.

## Approved by the filter, not yet run
| Film | Signature (as light) | Best canvas | Notes |
|---|---|---|---|
| **Blade Runner 2049** (LA interiors) | cold desaturated cyan-blue-grey, diffused window light through haze, city outside dissolving into murk, warm undertone kept in skin, no pure white | window-lit sparse interior | second signature of a validated film — use when the canvas has no horizon |
| **Pulp Fiction** (daylight) | hard midday key, cyan-blue saturated sky, dense blacks, amber skin, dry air | open sky, low angle | full 8-axis in `eight-axis.md` |
| **Mad Max: Fury Road** | extreme orange/teal split, recolored sky, brutal contrast, blown saturation | open space, hard sun | most "Instagram-filter" of the list — least distinctive |
| **Se7en** | bleach-bypass desaturation, sickly green-grey, dirty blacks, heavy grain, damp air | side light, garage/alley grey | needs unfilled shadow |
| **Drive** | night, magenta and cyan neon wash on the face, warm sodium amber, absolute blacks | window/side light, close | the wash is light on skin — no sign needed |
| **Her** | cream and peach, ultra-soft, low contrast, warm haze | frontal close-up | beautiful but less instantly nameable |

## Rejected by the filter (look lives in the set)
| Film | Why the edit cannot deliver it |
|---|---|
| **The Grand Budapest Hotel** | the pink is the hotel, the costumes, the symmetry of built sets; a pink-tinted plain wall is just a pink wall |
| **Amélie** | the red-and-green is painted walls and props; the gold tint alone reads as "warm filter" |
| **In the Mood for Love** | patterned wallpaper, cheongsams, practical lamps; tungsten alone does not get there — same palette, light-based: Only God Forgives (red/tungsten), Suspiria 1977 (red + green gel light) |
| **Wes Anderson / Jeunet / Wong Kar-wai in general** | production-design auteurs — steer to a light-based look with the same mood |

## Delta check: soft looks make weak reveals
A grade that keeps the take's color family (warm window light → warmer
window light) changes little on screen. Warn, then offer stronger films of
the same vibe and let the user choose. "Same vibe" means the same COLOR
FAMILY (pastel peach/pink, warm amber, cool blue, green, orange/teal) pushed
to a stronger intensity — not the same emotional mood, and not merely the
same temperature: pastel peach and dense amber are different families. A
stronger film with a different dominant hue is a different vibe.

Palette families (match within a row, never across):
- **Pastel peach / pink / cream, high-key** — Her, Spring Breakers day, Euphoria (pushed to saturated pink/magenta)
- **Dense amber / orange, low-key or hazy** — Blade Runner 2049 Vegas, Mad Max orange side
- **Cyan sky + amber skin, hard daylight** — Pulp Fiction
- **Cool blue / violet night** — Moonlight, Blade Runner 2049 interiors
- **Sickly green** — The Matrix, Se7en
- **Neon magenta + cyan** — Drive, Spring Breakers night

| Soft look asked for | Why it's weak | Stronger, same vibe |
|---|---|---|
| **Her** (pastel peach/cream/coral, high-key) | close-up window light is already soft and warm | Euphoria (saturated pink/magenta/peach as light, close-up skin), Spring Breakers daytime (candy peach-pink, sun-blown highlights), a "pushed" Her (heavy peach flood, lifted blacks, blown window) — NOT BR2049 amber or Mad Max (dark dense orange, not pastel), NOT Pulp Fiction (cyan) |
| Naturalistic dramas (Nomadland, Marriage Story) | the look IS natural light — no dominant hue | pick by the take's canvas: Moonlight (blue), BR2049 (amber), Matrix (green) |
| Warm nostalgic (Call Me by Your Name, Amélie-adjacent) | warms what is already warm | Blade Runner 2049 amber, Mad Max orange side |
| Cool minimal (Ex Machina interiors, slight cyan) | cools a neutral room slightly | Blade Runner 2049 cyan interior, Moonlight blue-violet |
| Muted green-grey (Se7en-lite, Fincher naturalism) | subtle cast on a grey room | The Matrix green, Se7en full bleach bypass |

"Pushed" variants are allowed when the user chooses to stay: push every
axis (saturation, bloom, lifted blacks, overexposure) while still changing
only light.

## Pairing rule for a series
Different canvas, different angle, different mood per episode: e.g. amber
day exterior → blue night side-light → green interior high angle. Two
saturated night looks in a row (Moonlight + Drive) read as the same post in
a feed. First fix: reorder so a day look sits between them. Second fix:
vary the take (seated vs standing, close vs medium). Keeping them
back-to-back is allowed only if the user prioritizes the before/after over
feed variety.

## Entry format (append after a look survives production)
```
| **Film** | signature as light (one line) | canvas it needs | the two result checks |
```
plus the full validated prompt in `prompt-skeleton.md` with a one-line
description of the raw scene it ran on.
