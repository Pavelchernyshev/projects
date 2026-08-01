# moyput.com — landing page

A single self-contained `index.html`: no build step, no external fonts, scripts,
or images, and no JavaScript. Russian only — the English version will live on a
separate domain.

Light, minimal design: white rounded cards, pill buttons, one accent colour
(`#0f7a5f`), system fonts, committed to a single light theme. Full copy
inventory and design notes: [`docs/texts-landing.md`](../docs/texts-landing.md).

## Before you deploy

**Set the real Telegram handle.** `index.html` has three
`https://t.me/moyput_bot` links (header, hero, closing CTA) using a placeholder.
Replace all three with the handle BotFather gave you:

```bash
sed -i '' 's|t.me/moyput_bot|t.me/YOUR_REAL_HANDLE|g' web/index.html
```

Nothing else is required — the page works as-is.

## Part 1 — move DNS from GoDaddy to Cloudflare

You stay registered at GoDaddy. Only the nameservers change, so there is no
transfer, no fee, and no 60-day lock.

**Do these two checks first — this is where people break things.**

1. **Does anything use email on this domain?** If you have mailboxes at
   moyput.com (GoDaddy email, Microsoft 365, Google Workspace), open the GoDaddy
   DNS page and write down every `MX` record plus any `TXT` records for SPF,
   DKIM, and DMARC. These must exist in Cloudflare *before* you switch
   nameservers, or mail stops being delivered the moment the switch takes effect.
2. **Is DNSSEC on at GoDaddy?** GoDaddy → domain → *DNSSEC*. If it is enabled,
   **turn it off and wait an hour** before switching. Leaving it on with new
   nameservers makes the domain fail to resolve entirely — the site goes dark and
   a cache flush will not fix it.

Also turn off any GoDaddy **domain forwarding** or parking page on the domain.

### Then

1. **Cloudflare → Add a site** → `moyput.com` → Free plan.
2. Cloudflare scans your existing records and shows what it found. **Read this
   list against what you wrote down in step 1** and add anything missing. The
   scan is best-effort, not authoritative.
3. Cloudflare shows two nameservers, e.g.
   `ada.ns.cloudflare.com` / `bob.ns.cloudflare.com`. Copy both.
4. **GoDaddy → My Products → moyput.com → DNS → Nameservers → Change** →
   *I'll use my own nameservers* → paste both Cloudflare nameservers, remove any
   others, save.
5. Wait. Usually 5–30 minutes, occasionally up to 48 hours. Cloudflare emails you
   when the zone goes active. Check progress with:
   ```bash
   dig +short NS moyput.com
   ```
6. Once active: **SSL/TLS → Overview → Full (strict)**, and
   **SSL/TLS → Edge Certificates → Always Use HTTPS: on**.
7. If you disabled DNSSEC in the pre-check, re-enable it now on the Cloudflare
   side (**DNS → Settings → DNSSEC → Enable**), then add the `DS` record
   Cloudflare gives you back at GoDaddy.

## Part 2 — deploy the page to Cloudflare Pages

### Option A: connect the Git repo (recommended — deploys on every push)

**Cloudflare → Workers & Pages → Create → Pages → Connect to Git**, pick this
repo, then:

| Setting | Value |
|---|---|
| Production branch | your default branch |
| Framework preset | None |
| Build command | *(leave empty)* |
| Build output directory | `web` |

### Option B: direct upload from your machine

```bash
npx wrangler pages deploy web --project-name moyput
```

### Attach the domain

In the Pages project → **Custom domains → Set up a custom domain** → `moyput.com`,
then repeat for `www.moyput.com`. Because DNS is already at Cloudflare, the
records are created for you and the certificate is issued automatically — usually
within a minute or two.

To make `www` redirect to the apex instead of serving a duplicate, add a
**Redirect Rule**: *Rules → Redirect Rules → Create* → hostname equals
`www.moyput.com` → 301 to `https://moyput.com/${http.request.uri.path}`.

## Verifying it worked

```bash
dig +short NS moyput.com                                    # Cloudflare nameservers
dig +short MX moyput.com                                    # unchanged, if you have email
curl -sSI https://moyput.com | head -1                       # HTTP/2 200
curl -sSI https://moyput.com | grep -i strict-transport      # headers applied
curl -sSI https://www.moyput.com | head -1                   # 301 if you added the rule
```

Then open the page on a phone. The layout is fluid rather than having a separate
mobile version, so it is worth actually looking at rather than assuming.

The page commits to a single light theme (`color-scheme: light`) — that is a
deliberate choice for this design, not an omission, so the browser will not
substitute a dark version.

## Editing the copy

All copy is plain HTML in `web/index.html` — open it, change the text, save.
[`docs/texts-landing.md`](../docs/texts-landing.md) lists every string with the
block it belongs to, so you can find things without reading markup.

The page deliberately does not overpromise: the limits section states that effect
sizes are small-to-moderate and population-level, and that the bot is not a
clinician. That matches what the bot itself tells users. If you soften it here,
the landing page starts contradicting the product.
