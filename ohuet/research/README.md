# Research board

The Appllama method: name the question, study the screens that already win,
extract the pattern, then build. The pass here ran on the material that could
be reached.

## What was studied

**Appllama's `liquid-glass-screens`** (open source, GPL-3.0 code, generated
artwork): an independent study of a publicly visible welcome screen with two
themed cookbooks, a measured motion spec, the glass and lens shaders, the
gesture, the copy motion and the sticker plume, verified frame by frame in the
simulator. Read in full: `README.md`, `NOTICE.md`, `docs/MOTION_SPEC.md`,
`src/liquid-glass/glass.ts`, `liquid-glass-screen.tsx`, `copy.tsx`,
`types.ts`, `cookbooks/sky.ts`, and the two showcase captures.

**Not studied:** the Appllama MCP library itself (top-grossing apps' first-open
moments, sound apps' one-gesture audio start, glass in iOS 26-era apps, quiet
"time with you" treatments). The connector was not enabled in the session and
the MCP host is unreachable from it. The questions stay below; the pass is
still owed.

## What the reference answered

1. **The first five seconds.** The name is up; nothing else is. The only
   instruction on the page is "Swipe up to enter", small, at 88.5 % of the
   height, and it goes soft and out within the first push. Landing is decided
   by *where the thing is*, not by an animation finishing, and it waits for
   the finger to lift so a hold at the top does not flash the copy in.
2. **One gesture, both ways.** The dome's size is a straight function of its
   position, so shrinking up and growing back read identically; the finger
   moves it 1:1; past either end the travel counts at 25 %; sideways it
   follows on a `tanh` leash; the release rule is distance *or* velocity
   (`p + 0.18 v̂ > 0.5`), and the spring is handed the finger's speed.
3. **Light answers force, not speed.** The caustic target is `|force| / 430`
   under the finger and `|deceleration| / 12000` in free flight, only while
   slowing — so a landing floods the crown and a throw is dark. It eases 22 %
   up and 12 % down.
4. **Words blur where they stand.** Nothing travels. In: 520 ms strong
   ease-out, blur 14 → 0. Out: 240 ms. The rotating third line uses a
   positional blur wipe — a front sweeping left to right, each word coming
   into focus as it passes — at a near-linear curve so the sweep does not
   dump into two frames.
5. **Glass on a page.** Thickness 0.42 at the dome and 0.62 at the button,
   bevel 0.25 → 0.42, the interior magnifies and the rim shears; a milky body,
   a halo outside the rim heavier below, one hairline of rim light, a sheen
   toward the light.

## What OHUET took, and what it changed

Took: the geometry, the travel, the release rule and spring, the lens
numbers, the force-driven light and its easing, the copy positions and
timings, the plume's timing and physics (scaled), the reduced-motion rules.
Each is in `BRAND.md` with its value.

Changed, per the study's own notice and the OHUET canon:

| Reference | OHUET | Why |
|---|---|---|
| a bitmap wordmark over a sky or stars | glass letters over the state, gone by themselves | the name is said once and let go; the state is the page |
| clear sphere, grey halo, cyan-blue-gold caustic, RGB dispersion | milk with a warm cast, light-only caustic, no dispersion, wobbled edge | one warm grey family, light as the only accent; wabi in the edge |
| forty stickers in a plume, a stardust vortex | six bubbles from the pebble's glass; dip and fade on return | "no accidental objects"; the bubbles were already the material's |
| headline with a struck word, rotating lines, a pill CTA | the same grammar; the five lines; the keep line instead of a pill | the one joke survives; no button, no onboarding |
| a "+" glyph | nothing on the pebble | the pebble is the door's handle, not a create button |
| Skia/Reanimated on the UI thread | one WebGL context, the gesture and spring in the renderer's own loop | web; nothing on a JS thread the browser does not own |

Rejected: auto-landing on a timer (the reference never lands on its own; the
letters may go by themselves, the stone does not); a dark theme (the light
room stands); any colour in the light.

## Questions still owed to the MCP pass

1. In calm, ambient and sound apps, how many show a wordmark on first open,
   for how long, and how is it let go — and does anyone let it go by itself?
2. How do the best sound apps start audio with one gesture and no button, and
   what do they show while sound is on?
3. Where liquid glass appears in top-grossing apps, what sits on it and what
   never does?
4. Which apps show "with you since" without turning it into a score?
5. Does a struck-through word in a caption wear out?

```
get_credits
search_apps  "ambient sound calm minimal"                 sort revenue
search_apps  "meditation sleep sounds"                    launched_after 2024
search_screens  mode=semantic  "welcome screen wordmark over a slow scene, no button"
search_screens  mode=keyword   "welcome"   element="Swipe Up Hint"
list_flows "welcome" → get_flow_apps "Welcome" → list_app_screens(flow="Welcome") for the top 5
```

Media links die in an hour; screen ids do not. Note the ids, download the
pixels, synthesise with the images side by side. Anything in `BRAND.md` a
screen contradicts gets re-argued, not overwritten.
