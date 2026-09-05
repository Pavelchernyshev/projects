# OHUET — the design

Internal. The public never reads this; every number in it is meant to be felt
and never noticed.

## The idea in one line

Milky glass over a pale, slow light. The glass is the organism's skin: it
bends what is behind it, it is not evenly thick, its edges are not straight,
and it holds a few bubbles it was born with. Liquid glass, made wabi, in a
light room.

## Where the two words meet

**Liquid glass** — Apple's material: a surface that refracts what is under it,
bends light hardest at its rim, carries one specular highlight from a fixed
light, and moves like something with mass.

**Wabi** — the beauty of what is imperfect, impermanent, and quiet. Nothing
symmetrical, nothing pristine, nothing shouting. A crack, a patina, an uneven
edge, and the good sense to stop.

Together: every glass shape here is a signed-distance field with noise on its
boundary (±3 px), a thickness map that is not flat (so the refraction is not
flat), three small bubbles in the slab, a milky semi-transparent body with a
warm cast like sea-glass, the far side of every edge a little darker so the
form reads, and grain over the whole picture. The highlight comes from the
upper left, always, and is the only white in the product.

## The four glass shapes

| Shape | Where | What it does |
|---|---|---|
| **Wordmark** | on arrival | OH / UET, stacked, in thick glass: a height map with a wide bevel, chrome at the bevel, clear and light-holding in the middle. Arrives liquid (bending far more than glass should), settles into glass over 1.6 s, and is let go — by a swipe up that it rides 1:1 and leaves with the finger's speed, or by itself after 5.6 s. The one time the brand says its name. |
| **Lens** | under a finger | Forms as the finger lands (72 pt at full press), magnifies the field inside, bends it hard at the rim, ripples very slightly, follows the finger 1:1, and lets go over ~400 ms. The skin. |
| **Slab** | behind the door | A rounded rectangle (28 pt, wobbled) the size of the words. Frosted a little, smoked a little (−28 % inside, so words sit), lifts 24 pt as it appears. Three bubbles. |
| **Horizon** | along the bottom | The top edge of a large stone, its centre far below the screen, crossing at 82 % of the height; one long highlight along the edge, the field thick and smoky beneath it. The mark sits on it. The one fixed object. |

Nothing else is glass. A fifth glass surface would be decoration.

## The reference, and where OHUET departs from it

The reference is a welcome screen whose wordmark is liquid glass over a
scene with a glass planet's edge along the bottom and "swipe up to enter",
followed by an onboarding carousel with a struck-through word in each
caption. OHUET keeps the glass wordmark, the horizon and the swipe, and
drops the carousel: there is nothing to onboard. The struck-through word
survives once, in the door — *There is a ~~store~~ T-shirt.* — because it
is the one joke the brand tells and it is true.

## Colour

One grey family, warm, and light. One accent — and the accent is *light*, not
a hue: the white highlight on glass. There is no blue, no purple, no gradient
CTA, and no black.

| Token | Value | Use |
|---|---|---|
| `--bg`, base day | `#ece7de` / `rgb(237 232 223)` | the ground: paper, stone |
| base, night | `rgb(206 198 186)` | the ground dims to this after dark |
| light on paper | `rgb(255 248 234)` | the main tint, peak 0.9 |
| moss | `rgb(170 186 158)` | a memory of moss, peak 0.7 — almost gone |
| mineral | `rgb(178 160 148)` | the third tint, underneath |
| `--ink` | `#2a2622` | words |
| `--ink-dim` | 56 % ink | the mark, the second line |
| `--ink-faint` | 36 % ink | the smallest text |
| milk | `mix(col, rgb(0.985 0.978 0.965), m)` | the glass body: 0.5 in the slab, 0.6 in the horizon, 0.22 in the letters, 0.14 in the lens |
| shade | `− 0.16 × (far side of the edge)` | what makes an edge read on a light ground |

The tints mix into the ground rather than add to it, so nothing ever blows
out to white except the highlight. The hour is a colour: `daylight()` crosses
the ground between day and night and cools the tints toward blue after dark.

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
| Arrival | narrative, once | 3000 ms from black; the wordmark liquid → glass in 1600 ms; the hint at 2500 ms; let go by itself at 5600 ms |
| Swipe up | finger involved → rides 1:1, leaves with velocity | dismiss at 80 pt or a flick past 700 pt/s; otherwise springs back, no bounce |
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
The shirt line is a sentence, one struck word, and a number. "swipe up",
once, faint. That is the entire copy deck.

## What would break it

A second accent. A gradient button. A card. A tab bar. A hero. An "About".
A notification. A glass surface under something that is not glass-worthy. A
straight edge.
