# The 8-axis decomposition

A film's look is not "a vibe" — it is eight measurable decisions about light.
Decompose the target (from memory of the film, or from a still the user
supplies), then write each axis as a prose sentence aimed at the real
elements of the user's frame. This is what separates a colorist's prompt
from "make it look like [movie]" (which yields a tint).

| # | Axis | What to decide | Prompt vocabulary |
|---|---|---|---|
| 1 | **Light** | source count, direction, hardness, key-to-fill ratio | "single hard high key, no fill", "soft directionless enveloping light", "single-source side light, unfilled shadow" |
| 2 | **Temperature / split-tone** | highlight color vs shadow color | "neutral-warm highlights, cool blue shadows", "monochromatic amber, no cool tones anywhere" |
| 3 | **Palette** | the 2–4 dominant hues and how saturated | "saturated cyan-blue dominant, charcoal blacks, amber skin", "deep blues and violets, high saturation" |
| 4 | **Contrast** | global contrast, black density, highlight protection | "high contrast, dense nearly crushed blacks, protected unclipped highlights", "soft gentle contrast" |
| 5 | **Curve** | shoulder/toe shape | "filmic shoulder rolloff, deep shadow toe", "smooth rolloff, shadows never fully crushed" |
| 6 | **Exposure** | what the exposure favors | "expose for the highlights, let shadows fall", "lift the midtones, keep faces readable" |
| 7 | **Optics** | grain, halation, bloom, diffusion, vignette | "fine 35mm negative grain, subtle halation on warm edges, no diffusion, natural vignette" |
| 8 | **Atmosphere** | what is in the air | "dry clean air, hard speculars, zero haze", "thick luminous dust, strong atmospheric perspective", "humid night air" |

## How to write an axis onto the frame
Every axis sentence should touch a real element:

- Light → the face and the source: "the window side of his face becomes
  luminous, the other side falls into deep shadow".
- Temperature/palette → sky, wall, floor, garments, skin: "the overcast
  white sky becomes a deep saturated amber wall of haze".
- Contrast/curve → blacks in clothing and shadows, highlights in the
  brightest surface: "dense soft blacks in the hoodie, protected glowing
  highlights in the haze".
- Optics → global, one sentence.
- Atmosphere → distance: "the farther from camera, the hazier and brighter".
- A view through a window (building, street, sky) is a distant element too:
  "the building visible through the window dissolves into a flat blue-grey
  murk, its facade reduced to soft ghostly shapes, as if a thin mist hangs
  between it and the glass" — the view is re-lit, never replaced.

## Skin is its own axis in practice
Grades that shift hue (blue, green, amber) kill skin first. Always state how
skin reads under the new light AND what keeps it alive:
- Blue/violet: "skin keeps a warm undertone fighting through the cool light,
  never grey or corpse-like".
- Green: "skin turns pale green-olive with drained reds" (here dead IS the
  look — say so explicitly).
- Amber: "skin in a warm amber register with natural texture".

## Worked example: analyzing a supplied still
Daylight exterior, subject low-angle against a hard blue sky (Pulp Fiction
trunk shot):

- Light — hard midday sun, high and slightly frontal, single key, no fill,
  closed nasolabial and orbital shadows, high ratio
- Temperature — neutral-warm highlights on skin, shadows pulled cool blue,
  strong separation
- Palette — saturated cyan-blue dominant, charcoal black, off-white,
  neutral amber skin; high but not digital saturation
- Contrast — high; dense, nearly crushed blacks; protected highlights
- Curve — photochemical rolloff, soft shoulder, dense toe
- Exposure — for the highlights, shadows fall
- Optics — fine 35mm grain, light halation on warm edges, no diffusion,
  natural spherical vignette
- Atmosphere — clean dry air, hard speculars, zero haze

Rendered as prompt prose: *"Apply a high-contrast photochemical 35mm
daylight grade: a single hard high-angle key source with no fill, producing
dense directional shadows and a high key-to-fill ratio. Split-tone the image
with neutral-warm highlights and cool blue-leaning shadows, holding a
saturated cyan-blue in the brightest cool areas. Keep skin in a neutral
amber register. Push global contrast high with dense, nearly crushed blacks
and protected, unclipped highlights, using a filmic shoulder rolloff and a
deep shadow toe. Expose for the highlights and let shadows fall. Add fine
35mm negative grain, subtle halation around warm highlight edges, natural
spherical-lens vignetting, no diffusion, dry clean air with hard specular
highlights and no atmospheric haze."*

## Distance check before you write
If any axis sentence requires an object that is not in the frame (a neon
sign, a practical lamp, wet streets, a colored wall), the look does not
live in the light — go back to the viability filter in `film-looks.md`.
