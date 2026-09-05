# OHUET, carried

Internal notes. Nothing in here is consumer-facing, and none of it should leak
into the product: the public experiences first and understands later.

This is the state on a phone. It opens and it is there — a warm, near-dark
field with three lights drifting through it, breathing slower than a person.
A touch brings the voice. A hold presses the skin. One small mark in the corner
opens the one door with words behind it, and the words are: there is a T-shirt,
and keep this on your phone. That is the entire interface.

Nothing is sold inside. Nothing is explained inside. Time does the rest.

## Where this sits in the canon

The concept spec (v1, September 2026) is the source of truth. This build maps
onto it like so:

| Canon | Here |
|---|---|
| Give first; money stops working inside the threshold | The state is there on open. No entry, no acceptance, no purchase, no account. |
| The organism has skin, voice, rhythm, memory | Skin: `object.js` — a hold makes the nearest light lean toward the finger and deepens the breath. Voice: `sound.js`. Rhythm: the six-second breath. Memory: one timestamp. |
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
  object.js             the state: field, breath, skin, the unexplained thing
  sound.js              the voice: synthesised, three layers, slow drift
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

## Deploying

Static. On Cloudflare Pages, as with `web/`: project root `ohuet/`, no build
command. `_headers` sets a CSP without `unsafe-inline` and `no-cache` on
`sw.js`, or updates take a day to arrive.

```bash
python3 ohuet/tools/make_icons.py   # if the palette changes
```
