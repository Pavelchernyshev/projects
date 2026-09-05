# OHUET — the design

Internal. The public never reads this; every number in it is meant to be felt
and never noticed.

## The idea in one line

Old glass over a slow light. The glass is the organism's skin: it bends what
is behind it, it is not evenly thick, its edges are not straight, and it holds
a few bubbles it was born with. Liquid glass, made wabi.

## Where the two words meet

**Liquid glass** — Apple's material: a surface that refracts what is under it,
bends light hardest at its rim, carries one specular highlight from a fixed
light, and moves like something with mass.

**Wabi** — the beauty of what is imperfect, impermanent, and quiet. Nothing
symmetrical, nothing pristine, nothing shouting. A crack, a patina, an uneven
edge, and the good sense to stop.

Together: every glass shape here is a signed-distance field with noise on its
boundary (±3 px), a thickness map that is not flat (so the refraction is not
flat), three small bubbles in the slab, a smoky amber tint like a bottle that
has been in the sun for years, and grain over the whole picture. The
highlight comes from the upper left, always, and is never white — it is the
colour of the stone light.

## The three glass shapes

| Shape | Where | What it does |
|---|---|---|
| **Lens** | under a finger | Forms as the finger lands (72 pt at full press), magnifies the field inside, bends it hard at the rim, ripples very slightly, follows the finger 1:1, and lets go over ~400 ms. The skin. |
| **Slab** | behind the door | A rounded rectangle (28 pt, wobbled) the size of the words. Frosted a little, smoked a little (−28 % inside, so words sit), lifts 24 pt as it appears. Three bubbles. |
| **Pebble** | under the mark | A stone: a circle whose radius varies with the angle (±14 %). Sits in the lower-left corner, off-centre, cut by nothing. The one fixed object. |

Nothing else is glass. A fourth glass surface would be decoration.

## Colour

One grey family, warm. One accent — and the accent is *light*, not a hue:
the stone-coloured highlight. There is no blue, no purple, no gradient CTA.

| Token | Value | Use |
|---|---|---|
| `--bg` | `#070708` | the ground, night |
| base, day | `rgb(28 26 24)` | the ground drifts here by early afternoon |
| stone | `rgb(224 212 192)` | the main light; the highlight colour |
| moss | `rgb(150 168 142)` | a memory of moss, peak 0.55 — almost gone |
| mineral | `rgb(104 90 84)` | the third light, underneath |
| `--ink` | `#ece6dc` | words |
| `--ink-dim` | 50 % ink | the mark, the second line |
| `--ink-faint` | 28 % ink | the smallest text |
| glass tint | `× (1.03, 0.985, 0.93) + (0.045, 0.04, 0.032)` | smoke and amber inside any glass |

The hour is a colour: `daylight()` crosses the ground between night and day
and cools the lights toward blue after dark.

## Shape lock

Organic only. The one rectangle in the product (the slab) has 28 pt corners
and a wobbled edge, so it is not really a rectangle. Buttons are not drawn:
the mark's tap target is invisible (44 pt) and the pebble under it is the
affordance. No borders anywhere except a 1 px rule under a link.

## Type

- Mark: system sans, 11 px, tracking 0.42 em, uppercase. The only sans.
- Everything else: system serif (`ui-serif, Georgia`). The shirt line at
  20–26 px; a line from the state at 18–24 px; the smallest notes 10–11 px
  with 0.3 em tracking.
- One display size per screen. Numbers are set in the same serif; there are
  two of them in the whole product.

## Motion vocabulary

| Moment | Rule | Value |
|---|---|---|
| Arrival | narrative, once | 3000 ms, ease-out, from black |
| Breath | continuous | 6 s cycle, ±3.5 % (deeper under a finger) |
| Lens forms / lets go | finger involved → settles like a spring, no bounce | ~150 ms in, ~400 ms out (exponential, critically damped) |
| Door opens / closes | occasional → standard motion | 280 ms / 200 ms, `cubic-bezier(.23, 1, .32, 1)`; glass and words share the curve |
| Press feedback on the mark | tens a day → near-imperceptible | scale 0.97 in 120 ms |
| Voice in / out | slow by design | 8 s / 6 s |
| A line surfaces | rare | 2 s fade, stays 9 s |
| Reduce Motion | spatial → still | the field freezes, lens has no ripple, door cuts |

Nothing else moves. Idle the renderer runs at 30 fps; while a finger is down
or the door is moving it runs at 60.

## Voice

Five lines, none longer than four words, none naming the brand or the word.
The shirt line is a sentence and a number. That is the entire copy deck.

## What would break it

A second accent. A gradient button. A card. A tab bar. A hero. An "About".
A notification. A glass surface under something that is not glass-worthy. A
straight edge.
