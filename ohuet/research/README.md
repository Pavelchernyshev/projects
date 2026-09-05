# Research board — waiting on the Appllama connector

The Appllama method (see the `appllama-usage` skill) is: name the question,
study every screen of the apps that already win, extract the pattern, then
build. The build exists; this pass has not run. It could not: the Appllama
connector is installed for the org but not enabled in the session that built
OHUET, and `mcp.appllama.io` is blocked at the network edge of that session,
so the only route is the claude.ai connector.

When it is on, this is the pass — questions first, so screens turn into a
spec and not a mood board.

## Questions

1. **The first five seconds.** In calm, ambient and sound apps — and in the
   few fashion houses with apps — what does the first-open moment do before
   any words? How many of them show the wordmark, for how long, and how is
   it let go?
2. **The one gesture that starts audio.** Browsers and phones require a
   touch before sound. How do the best sound apps ask for it without a
   button — or do they all use a button? What do they show while sound is
   on?
3. **Glass as material.** Where liquid glass appears in top-grossing apps
   (iOS 26 era), what sits on it and what never does? How thick, how much
   blur, where the highlight?
4. **Time as material.** Which apps show "with you since" or streak-like
   time without turning it into a score? What is the quietest treatment?
5. **The struck word.** Any app that uses a struck-through word in a
   caption as voice — how often, and does it wear out?

## Queries to run

```
get_credits
search_apps  "ambient sound calm minimal"                 sort revenue
search_apps  "meditation sleep sounds"                    launched_after 2024
search_apps  "luxury fashion brand"                       sort revenue
search_screens  mode=semantic  "welcome screen glass wordmark over a slow scene, no button"
search_screens  mode=semantic  "calm dark ambient sound screen with one control"
search_screens  mode=keyword   "welcome"   element="Swipe Up Hint"
list_flows   "welcome"   →  get_flow_apps "Welcome"  →  list_app_screens(flow="Welcome") for the top 5
list_ui_elements  →  get_element_screens for the glass / blur / play-toggle families
```

## Board structure (per the skill)

```
research/
  ambient/
    apps.md          shortlist: metrics, flows, verdicts
    <app>/screens.md id, name, flow, elements, colours — and img/ in journey order
  fashion/
    ...
  patterns.md        the cross-app synthesis: table stakes, edge, the opening
```

Media links die in an hour; screen ids (`app_id/screen_id`) do not. Note the
ids, download the pixels, synthesise with the images side by side.

## What the pass may change in the build

Only what the screens argue for. Candidates: how long the wordmark stays
(5.6 s now), whether the swipe hint is needed at all, whether the voice
needs any indicator beyond the dot, and whether the door should be a sheet
that drags rather than a slab that fades. Everything in `BRAND.md` that a
reference contradicts gets re-argued, not overwritten.
