# Мой Путь (moyput.com)

A Telegram coaching bot that interviews you about the five types of wealth, then
names **one** thing to fix — not five. Every claim about what tends to work is
drawn from a fixed library of peer-reviewed studies that ships with the bot, so
it cannot cite a paper it does not have.

**Documentation in Russian is in [`docs/`](docs/)** — product, bot logic, all
copy, the research library, architecture, and deploy steps, written so the
product can be changed without reading code. Start at
[`docs/README.md`](docs/README.md).

## What it does

1. **One open question** — what you keep meaning to deal with and keep not dealing with.
2. **A five-domain pulse** — a 1–5 tap for time, social, mental, physical, financial.
3. **An adaptive interview** — 3–6 follow-ups, generated from your answers, going
   after the specific thing you are talking around.
4. **A verdict** — one domain, one honest read, the other four explicitly deferred,
   backed by one to three real citations.
5. **One action** — an if-then plan with the obstacle named and a countable measure.

Answers can be typed or spoken. The product is Russian (`DEFAULT_LANG=ru`); the
English strings remain in the code for a future English-domain deployment and
`/lang` still switches between them.

## Quick start

```bash
cp .env.example .env      # add TELEGRAM_BOT_TOKEN and ANTHROPIC_API_KEY
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=src python -m myway
```

Get a bot token from [@BotFather](https://t.me/BotFather). With Docker:

```bash
cp .env.example .env      # then edit
docker compose up -d
```

## How the citation guarantee works

This is the part worth understanding before you change anything.

The model **never writes a reference**. It receives a list of study ids with
one-line summaries, and returns ids. `science/library.py` resolves those ids
against the YAML corpus and renders authors, year, journal, and DOI from our own
data. An id the model invents fails lookup, gets logged as an error, and is
dropped before rendering.

```
corpus/*.yaml  →  ids + summaries  →  model picks ids  →  we render the reference
                                            ↓
                                   unknown id → logged, dropped
```

So the failure mode is a *missing* citation, never a fabricated one. `/sources`
shows a user the entire library, which is the whole point: the claim "this is
scientific" is checkable.

### Before you launch: verify the corpus

The 28 entries in `src/myway/science/corpus/` were assembled from well-known
literature, and **every one is currently marked `verified: false`**. That flag
means no human has yet opened the paper and confirmed our one-sentence summary is
a fair statement of what it found. Do not ship to real users until they are
checked.

```bash
python scripts/verify_corpus.py                # structure, ids, DOIs present
python scripts/verify_corpus.py --resolve-doi  # confirm each DOI resolves to the right paper
```

`--resolve-doi` catches the dangerous case — a plausible reference that points at
a different paper — but it cannot check whether the *finding* is stated fairly.
That needs a person. Once you have read a paper and confirmed the summary, set
`verified: true` on that entry.

Adding a study: append to the relevant YAML with an `id`, `use_when` (which tells
the model when it applies), and both `finding_en` and `finding_ru`. Tests enforce
that both languages are present and actually in the right language.

## Configuration

Everything is environment-driven — see `.env.example` for the annotated list.
The settings you are most likely to touch:

| Variable | Default | Notes |
|---|---|---|
| `PRODUCT_NAME` | `Мой Путь` | Appears in the greeting and `/about` |
| `DEFAULT_LANG` | `ru` | Language for a user who hasn't chosen one |
| `MODEL_DIAGNOSIS` / `EFFORT_DIAGNOSIS` | `claude-opus-5` / `high` | The verdict; quality matters most here |
| `MODEL_PROBE` / `EFFORT_PROBE` | `claude-opus-5` / `low` | Interview questions; frequent and cheap |
| `MIN`/`MAX_PROBE_QUESTIONS` | 3 / 6 | Interview length. The max is enforced in two places |
| `STT_BACKEND` | `local` | `local` \| `openai` \| `none` — see below |
| `ALLOWLIST` | empty | Comma-separated Telegram user ids; empty means open |

### Voice notes

Claude has no audio input, so speech-to-text is the one component outside
Anthropic. Three options:

- **`local`** (default) — faster-whisper in-process. No audio leaves your host.
  The default because this product asks people about the worst parts of their
  life, and sending that to an extra vendor should be a deliberate choice. Costs
  roughly 1GB of RAM at `WHISPER_MODEL=small`.
- **`openai`** — Whisper API. Lower memory, needs `OPENAI_API_KEY`, sends
  recordings to a third party.
- **`none`** — voice notes are declined with a message asking for text.

## Commands

| Command | |
|---|---|
| `/begin` | Start an interview (replaces any unfinished one) |
| `/status` | Which stage you are at |
| `/lang` | Toggle Russian / English |
| `/sources` | The full research library |
| `/cancel` | Abandon the current interview |
| `/forget` | Delete every session, transcript, and preference for your account |
| `/about` | What this is, and what the evidence does and does not show |

## Landing page

`web/` holds the moyput.com landing page — one self-contained `index.html`, no
build step, no JavaScript, Russian only. Light minimal design: rounded white
cards, pill buttons, one accent colour. Deploys to Cloudflare Pages with build
output directory `web` and no build command.

`web/README.md` covers the GoDaddy → Cloudflare nameserver move (including the
two pre-checks that break email and DNS resolution if skipped) and the Pages
setup. **The Telegram handle in the CTA links is a placeholder** — replace
`t.me/moyput_bot` before deploying.

## Development

```bash
pip install -r requirements-dev.txt
PYTHONPATH=src python -m pytest        # 71 tests, no network or API key needed
python scripts/build_docs.py           # after editing i18n.py or the corpus
python -m ruff check src tests scripts
```

The suite covers the citation-integrity path (including the fabricated-id case),
storage round-trips, i18n and placeholder parity across both languages, crisis
screening, HTML escaping of model output, and a full interview walkthrough
against stubbed Telegram objects and a scripted engine, and that the generated
docs have not drifted from the code. No test calls the API.

### Layout

```
src/myway/
  bot.py            Telegram handlers and the interview state machine
  coach/
    engine.py       Two Claude calls, both structured-output constrained
    prompts.py      System prompt and the probe/verdict templates
    schemas.py      Strict JSON schemas for both calls
    results.py      Probe and Verdict types (no SDK dependency)
  science/
    library.py      Corpus loading, id resolution, prompt rendering
    corpus/*.yaml   The vetted studies
  render.py         Engine output → escaped Telegram HTML
  safety.py         Crisis keyword screen, runs before any model call
  db.py             SQLite persistence
  i18n.py           All bot copy, RU + EN
```

State lives in SQLite rather than memory, so restarting mid-interview resumes
where the person left off.

## Safety posture

- A bilingual keyword screen runs **before** any model call. On a match the
  session is closed and the user is pointed at emergency services. It is
  deliberately blunt: a false positive costs one unnecessary signpost, a false
  negative is unacceptable.
- The verdict schema carries an `escalate_to_professional` flag for the subtler
  clinical cases, rendered ahead of the plan rather than instead of it.
- The bot states plainly that it is not a clinician, and `/about` is explicit
  that these effect sizes are population-level and mostly small to moderate.

None of this makes the product clinically safe by itself. If you take this to
real users at scale, get a qualified review of the escalation copy and check what
your jurisdiction requires of a mental-health-adjacent service.

## Known gaps

- **Check-in loop.** Commitments are stored and the copy promises a follow-up,
  but no scheduled job sends it yet. `Store.past_commitments()` and PTB's
  `JobQueue` are both in place for it.
- **No corpus retrieval ranking.** All entries for the domains in play go into
  the prompt. Fine at 28 studies; needs embedding-based selection past a few hundred.
- **Single instance.** SQLite plus polling assumes one process. Multi-instance
  means Postgres and webhooks.
- **Interview quality is unevaluated.** There is no eval set scoring whether the
  verdicts are actually good. That is the highest-value next piece of work, and
  it needs real transcripts.

## Also in this repository

`ohuet/` — a separate product with no shared code or dependencies: OHUET, the
state carried on a phone. A calm field of light that breathes, a synthesised
voice, a skin that yields to a finger; nothing sold, nothing explained. Internal
notes are in [`ohuet/README.md`](ohuet/README.md).
