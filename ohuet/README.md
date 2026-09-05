# OHUET, carried

Internal notes. Nothing in here is consumer-facing, and none of it should leak
into the product: the public experiences first and understands later.

This is the state on a phone. It opens with its name in thick glass — OH /
UET, stacked, arriving liquid and settling — over a warm, near-dark field
with three lights drifting through it, breathing slower than a person. A
swipe up lets the letters go (or they go by themselves), and the state is
there, seen through old glass, with the edge of a glass stone along the
bottom. A touch brings the voice. A hold presses the skin: a
lens of liquid glass forms under the finger and bends the light. One small
mark on a glass pebble in the corner opens the one door — a slab of glass
with words on it — and the words are: there is a T-shirt, and keep this on
your phone. That is the entire interface.

The design — the glass, the colour, the type, the motion vocabulary and what
would break it — is written down in [BRAND.md](BRAND.md).

Nothing is sold inside. Nothing is explained inside. Time does the rest.

## Where this sits in the canon

The concept spec (v1, September 2026) is the source of truth. This build maps
onto it like so:

| Canon | Here |
|---|---|
| Give first; money stops working inside the threshold | The state is there on open. No entry, no acceptance, no purchase, no account. |
| The organism has skin, voice, rhythm, memory | Skin: `glass.js` — a hold forms a lens under the finger that refracts the field, and the nearest light leans in. Voice: `sound.js`. Rhythm: the six-second breath. Memory: one timestamp. |
| Visual language: minimal, organic, natural material, subtle tonal shifts | Liquid glass, made wabi: every glass shape has a noise-wobbled edge, uneven thickness, a smoky amber tint and grain; the slab holds three bubbles. See BRAND.md. |
| The word is not a slogan | The wordmark appears once, on arrival, and is let go. After that the name is a small mark on the horizon. |
| Sound is architectural material; changes without changing; the source migrates | Three synthesised layers on independent slow stereo drifts, a filter that wanders, a fifth that swells and dissolves every minute or two. Nothing downloaded, nothing findable elsewhere. |
| Time is a material | "today / 3 days / one month" surfaces after twenty seconds. The first line surfaces after three minutes, the next after nine more. |
| Occasional minimal language; never explain | Five lines in `data.js`. None names the brand or the word. |
| The T-shirt is the door into ordinary reality; working price 100; commerce is outside | One line behind the mark: "There is a T-shirt. 100." It becomes a link only when `SHIRT.url` is set. The storefront is not this app. |
| Hidden wolf / an unexplained object; folklore, not gamification | On roughly one opening in forty (and at 04:04), a faint ring crosses the field once over forty seconds. Nothing points at it. Do not mention it. |
| The hour is part of the space | Night: near-black, cooler. Day: a warm dark stone. `daylight()` in `object.js`. |
| Anti-patterns: concept store, luxury boutique, editions, scarcity, VIP, CRM, push, explanatory copy | None of it. There is no nav, no catalogue, no price beyond the shirt's, no edition numbers, no About, no notifications. |

Decision rules from §16, applied: every element here gives before it asks,
leaves the visitor alone, is quieter than what it contains, and gets better
when discovered rather than read.

## How to look at it

Needs http, not a file: modules and the service worker will not run from
`file://`.

```bash
cd ohuet
python3 -m http.server 8788
# http://127.0.0.1:8788
```

On a phone, open the same address on the same network and add it to the home
screen. Sound needs a touch to start (browser policy) and pauses when the app
is hidden.

## What is in the box

```
ohuet/
  index.html            the shell — no copy beyond the door
  app.js                arrival, touch → voice, mark → door, presence timers
  glass.js              the state in glass: WebGL, field pass + glass pass (wordmark, lens, slab, horizon)
  object.js             the same state on a 2D canvas, for devices without WebGL
  sound.js              the voice: synthesised, three layers, slow drift
  BRAND.md              the design: material, colour, type, motion, what breaks it
  data.js               the palette, the lines, the shirt line, the timings
  app.css               all styling
  manifest.webmanifest  install
  sw.js                 offline — network first, cache as the fallback
  _headers              Cloudflare Pages headers incl. a CSP without unsafe-inline
  icons/                app icons; tools/make_icons.py regenerates them (no deps)
```

No build, no dependencies, no outbound requests. No fonts, no analytics, no
images. Everything on screen and in the ear is computed on the device.

Tune the product in `data.js`: the three lights, the lines, the shirt line and
price, how long before the first line. The palette is `base` (night and day)
plus three `blobs`; that is the entire visual vocabulary and it is meant to
stay that small.

## What is real and what is not

| | |
|---|---|
| The state, the skin, the voice, the hour | real; computed on the device |
| Install and offline | real; manifest, service worker, cached shell |
| Memory | `localStorage`, one timestamp — reinstalling forgets it |
| The T-shirt | a line; the storefront does not exist yet (`SHIRT.url` is empty) |
| The unexplained object | real, rare, unmentioned |

## Not decided here (and not to be invented)

From the spec's open questions, the ones this app touches: the shirt's actual
price and where it is sold; whether the state should ever be sold as an object
in its own right (this build says no — it is given — and the canon's economic
loop puts commerce outside); whether memory should survive a change of phone
(would need an account, which the canon is wary of); what the lines say,
and whether they should exist at all.

## How it was verified

There is no simulator for a web app, so the loop was run in headless Chromium
(software GL): stills at 2×, and every transition captured frame by frame
through the CDP screencast and laid out as contact sheets — arrival, the lens
forming and letting go, the door opening and closing. The sheets showed no
unstyled or wrong-colour frame in any transition (the one white frame in the
arrival sheet is the browser's blank page before navigation, not ours;
`<meta name="color-scheme" content="dark">` is there so a slow stylesheet
could never produce one either). Frame timing on the software renderer is
~25 fps and says nothing about a phone; the 60 fps bar has to be measured on
a real device.

The Appllama research pass (study the category's real screens before drawing)
was not run: the connector is installed for the org but not enabled in the
session that built this. When it is, the screens to study are: first-open
moments in ambient / sound / meditation apps, and how they handle the one
gesture that starts audio.

## Deploying

Static. On Cloudflare Pages, as with `web/`: project root `ohuet/`, no build
command. `_headers` sets a CSP without `unsafe-inline` and `no-cache` on
`sw.js`, or updates take a day to arrive.

```bash
python3 ohuet/tools/make_icons.py   # if the palette changes
```
