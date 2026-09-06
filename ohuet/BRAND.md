# OHUET — the design

Internal. The public never reads this; every number in it is meant to be felt
and never noticed.

## The idea in one line

A stone of milky glass on the bottom edge of a pale, slow light. Push it up
and it becomes a pebble; the words come in behind it. The glass is the
organism's skin: it bends what is behind it, it is not evenly thick, its edge
is not straight, and its light answers the hand. Liquid glass, made wabi, in
a light room.

## Where the two words meet

**Liquid glass** — a surface that refracts what is under it, bends light
hardest at its rim, carries one specular highlight from a fixed light, and
moves like something with mass.

**Wabi** — the beauty of what is imperfect, impermanent, and quiet. Nothing
symmetrical, nothing pristine, nothing shouting. A crack, a patina, an uneven
edge, and the good sense to stop.

Together: every glass shape here is a field with a normal and a noise-wobbled
boundary; the thickness is not flat, so the refraction is not flat; the body
is milk with a warm cast where it goes thick, like sea-glass; the far side of
every edge is a little darker so the form reads on a pale page; grain sits
over the whole picture. The highlight comes from the upper left, always, and
is the only white in the product. There is no colour in the light and the
three channels are never split.

## The reference

The gesture is a study of a publicly visible welcome screen, through the
open-source measurement of it by Appllama (liquid-glass-screens: 402 × 874
reference geometry, a dome that a swipe carries up the page and shrinks into
a button, a caustic that answers force, a spring seeded with the finger's
speed, copy that blurs where it stands, a plume of stickers). What OHUET keeps
is the grammar and the numbers; what it changes is everything the notice says
to change and more:

| Reference | OHUET |
|---|---|
| a chrome-balloon wordmark bitmap on a sky | OH / UET as thick glass letters, liquid on arrival, fading as the stone rises, gone by themselves after a while |
| a clear sphere with a grey halo, chromatic caustic, channel dispersion | milk with a warm cast, light-only caustic, no dispersion, a wobbled edge |
| forty stickers bursting into a plume | six bubbles surfacing through the pebble's glass and breathing above it |
| "Create and discover ~~screenshots~~ spots" + rotating lines + a pill "Let's go" | *There is a ~~store~~ T-shirt. 100.* + the five lines rotating + *Keep this on your phone.*, a line, not a pill |
| a "+" glyph on the button | nothing on the pebble |
| a page that ends in onboarding | a page that ends in nothing to do |

## The stone (the one gesture)

Authored at 402 × 874; `sx = width / 402`, `sy = height / 874`.

| Quantity | Value |
|---|---|
| Gate | a dome of radius `245 sx` centred on the bottom edge |
| Landed | a pebble of radius `44 sx` centred at `0.469 h`; thrown past it, a floor of `32 sx` approached as `RF + (R1 − RF) · e^(−overshoot / 40 sy)` |
| Travel | `p ∈ [0, 1]` maps the centre linearly from the bottom edge to `0.469 h`; the finger moves it 1:1; radius is a straight function of `p`, so shrinking up and growing back read identically |
| Rubber band | past either end the finger's travel counts at 25 % |
| Sideways | a soft leash: `150 sx · tanh(Δx / 150 sx)` |
| Release | lands when `p + 0.18 · v̂ > 0.5` (`v̂` = release velocity in travel units), else returns |
| Spring | `{ damping 15, stiffness 120, mass 1.05 }`, seeded with the release velocity, integrated in 1/120 s substeps; Reduce Motion: `{ 30, 160, 1 }` |
| Landed / left | `p > 0.97` with the finger lifted / `p < 0.80`, decided from position, never from the spring's end |
| Lens | thickness `0.42 → 0.62` and bevel `0.25 → 0.42` from dome to pebble; magnification `amount · (0.42 + 0.58 · bevel²)`; slosh `0.10 R` × the smoothed motion, most at the centre, none at the rim |
| Light | target `min(1, |force| / 430)` under the finger, `min(1, |deceleration| / 12000)` in free flight and only while slowing; eases 22 % up, 12 % down; gathers at the crown, tilts up to ~25° with a sideways shove, drops only when pulled straight down; faded out between radii `190 sx` and `100 sx` |
| Edge | wobbled by `0.6 % · sin 5θ + 0.25 % · sin 13θ` of the radius, half that on the pebble |
| Drag vs. hold | a finger that moves more than 6 pt carries the stone; a finger that stays forms the skin's lens (72 pt at full press); a lift within 320 ms and 12 pt is a touch, and touches the voice |

## The copy, with the stone

| Element | Motion |
|---|---|
| Wordmark | fades between `p = 0.08` and `0.62`, goes liquid between `0.05` and `0.60` |
| Hint (*swipe up*, 88.5 % of the height) | fades between `p = 0.06` and `0.30`, blurs 0 → 3 px, carried `0.04 R` with the slosh |
| Headline (61.6 %) and the keep line (88.5 %) | 520 ms `cubic-bezier(.23, 1, .32, 1)` in after landing, blur 3.5 px → 0, no travel; 240 ms `easeOutQuad` out |
| Third line (70.3 %) | a positional blur wipe, left to right, 560 ms `cubic-bezier(.16, .42, .40, 1)`, front ramp 34 % of the line; holds 1950 ms; out in 400 ms — blur to 4.75 px `easeOutQuad`, opacity to 0 `easeInQuad`, no travel; 460 ms before the next |
| Reduce Motion | no wipe; the line appears in place |

Blur is the reference's language for words coming and going: nothing
travels, it goes soft where it stands. The study's blur intensities map to
pixels here at a quarter.

## The bubbles

Six at most, sizes `6 4 5 3 4.5 3.5` pt. Emission starts 350 ms after landing,
one every 30 ms, born through the pebble's glass at scale 0.34 within 8 pt of
its centre, growing at 3.6 / s, launched at a third of the sticker plume's
speed within ±34° of straight up. Home is a plume narrowing at the base and
opening as it climbs (`x ∈ ±(14 + 78 t)`, `y ∈ −18 − 150 t`); buoyancy 16,
wander 11 and 7, a spring to home at 2.0 / s², drag `0.07 ^ dt`. Sent back
(`p < 0.35`) they dip under gravity with drag `0.55 ^ dt`; once the dome is
home they float up again and fade at 0.65 / s. Every landing starts a fresh
plume.

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
| `--ink-dim` | 56 % ink | the mark, the third line |
| `--ink-faint` | 36 % ink | the smallest text |
| milk | `mix(col, rgb(0.985 0.978 0.965), m)` | the glass body: 0.05–0.10 on the dome, 0.16–0.22 on the pebble, 0.3 in the letters, 0.14 in the finger's lens, 0.2 in a bubble |
| warm | `col × (1, 0.975, 0.935)` | where the glass goes thick and in the bowl of the light |
| shade | `− 0.16 × (far side of the edge)` | the halo below the stone, the bevel's shadow away from the light, the pebble's hairline |

The tints mix into the ground rather than add to it, so nothing ever blows
out to white except the highlight. The hour is a colour: `daylight()` crosses
the ground between day and night and cools the tints toward blue after dark.

## Shape lock

Organic only. There is no rectangle in the product. Buttons are not drawn:
the stone is the control, the mark's tap target is invisible (44 pt), and the
keep line becomes a tap target only when the phone can keep the app. No
borders anywhere except a 1 px rule under a link.

## Type

- Mark: system sans, 11 px, tracking 0.42 em, uppercase. The only sans.
- Everything else: system serif (`ui-serif, Georgia`). The headline and the
  third line at 22–30 px; the keep line at 16–19 px; the smallest notes 10–11
  px with 0.3 em tracking.
- One display size per screen. Numbers are set in the same serif; there are
  two of them in the whole product.

## Motion vocabulary

| Moment | Rule | Value |
|---|---|---|
| Arrival | narrative, once | 3000 ms from the page colour; the wordmark liquid → glass in 1600 ms; the hint at 2500 ms; the letters let go by themselves at 5600 ms |
| The stone | finger involved → rides 1:1, leaves with velocity | the table above; no bounce under Reduce Motion |
| Breath | continuous | 6 s cycle, ±3.5 % (deeper under a finger) |
| Lens forms / lets go | finger involved → settles like a spring, no bounce | ~150 ms in, ~400 ms out (exponential, critically damped) |
| Words | occasional → standard motion | 520 ms in, 240 ms out, the wipe as above |
| Press feedback on the mark | tens a day → near-imperceptible | scale 0.97 in 120 ms |
| Voice in / out | slow by design | 8 s / 6 s |
| A line surfaces, with the stone at the gate | rare | 2 s fade, stays 9 s |

Nothing else moves. Idle the renderer runs at 30 fps; while a finger is down,
a spring is live, the light is fading or the bubbles are up it runs at 60.

## Voice

Five lines, none longer than four words, none naming the brand or the word.
They are the rotating third line when the stone is up and the rare line when
it is not. The headline is a sentence, one struck word, and a number. "swipe
up", once, faint. That is the entire copy deck.

## What would break it

A second accent. A gradient button. A card. A tab bar. A hero. An "About". A
notification. A sticker. A "+". A glass surface under something that is not
glass-worthy. A straight edge.
