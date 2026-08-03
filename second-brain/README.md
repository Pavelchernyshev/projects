# Second Brain

A knowledge vault you own outright: plain markdown files in git, readable by
Obsidian, maintained by Claude Code. Built to do three things that pull against
each other — capture anything without it costing you, connect what you capture
into a graph worth having, and produce cited drafts from it.

The reasoning behind every design decision, and what was taken from and rejected
in seven reference systems, is in [`docs/research.md`](docs/research.md).

## The idea in one page

Three lanes, deliberately kept at different speeds.

**Capture** is free. Drop a link and a transcript; you get a file with a
permanent citation key. No summary, no tagging, no decision about whether it is
worth keeping. **An unprocessed source is not debt** — the pile is allowed to
grow forever, the health check reports its size as information and is explicitly
forbidden from presenting it as a to-do. That rule is the whole FOMO answer. Not
that you can capture things, but that capturing them obligates you to nothing.

**Refine** is slow and only runs when you ask. A source becomes atomic notes,
one idea each, wired into topic hubs, linked to at most two or three other notes
— only where understanding one genuinely changes how you read the other.

**Produce** turns notes into drafts. Every factual claim carries a marker, and
the references section is rendered from the source files on disk rather than
written from memory, so the worst failure is a missing citation instead of an
invented one.

## Setup

```bash
cd second-brain
python3 scripts/lint.py        # verify the vault is intact
claude                         # Claude Code reads CLAUDE.md automatically
```

Then **Open folder as vault** in Obsidian and point it at `second-brain/` — not
the repository root. It works with no conversion step; `.obsidian/` ships with
graph colours and sane defaults already configured.

[`docs/obsidian.md`](docs/obsidian.md) covers the rest: which core plugins to
enable, how the graph is coloured and what a healthy one looks like, mobile
capture, and the sync topology (Obsidian Sync ignores `.git`, which is what you
want — mobile syncs to the laptop, the laptop commits).

If you want the vault in its own private repo rather than inside `projects`,
copy the `second-brain/` directory out and `git init` it. Nothing here depends on
its location.

## Daily use

| You want to | Do this |
|---|---|
| Save something, now, with no thought | `/capture <url>` — or pipe a transcript to `scripts/capture.py` |
| Turn a source into knowledge | `/process <key> [focus instruction]` |
| Build or refresh a topic hub | `/topic <name>` |
| Find missing links, fix orphans | `/connect <note>` or `/connect orphans` |
| Ask your own knowledge base | `/ask <question>` |
| Write something publishable | `/draft article\|chapter\|social <angle>` |
| Check vault health | `/lint` |

Capture also works without Claude running, which matters — the point of a free
capture lane is that nothing gatekeeps it:

```bash
python3 scripts/capture.py "https://example.com/post" -t "Title"
pbpaste | python3 scripts/capture.py "https://youtu.be/xyz" -t "Talk" --type video
```

## Layout

```
CLAUDE.md          The schema. Everything else follows from it.
index.md           Catalog. Read before searching.
log.md             Append-only operations record.

inbox/             Unfiled dumps.
sources/           One file per source. Bodies are immutable.
notes/             Atomic knowledge. One idea per file. The graph.
topics/            Maps of Content, one hub per topic.
drafts/            Articles, book chapters, social posts.
voice/             STYLE.md plus your published writing. Read before drafting.
daily/             Journal. Raw thinking; the best voice input for drafts.
projects/          Active work context.
templates/         Note templates.
docs/              research.md (why this is built this way), citations.md (the contract).
scripts/           lint.py, capture.py. Python 3.9+, stdlib only.
```

## Two languages, one graph

Sources keep their original language, verbatim, always. **The knowledge layer —
notes, topics, tags, filenames — is English regardless of what the source was.**
That is what keeps a Russian podcast and an English book about the same idea
landing on the same note instead of splitting the graph in half.

Quotes are the exception: they stay verbatim in the original with an English
gloss beneath, so a Russian draft can quote its own sources without a round trip
through translation. Drafts go in whichever language the audience speaks.

## The three rules worth knowing

**Sources are immutable.** You can edit a source file's frontmatter; never its
body. Everything else in the vault is derived and could be rebuilt from
`sources/` — which is only true if `sources/` is never rewritten.

**`## My take` is yours.** Claude never writes in that section, in any note. It
may leave a `> prompt:` question there. Every note declares whether its prose is
`ai-distilled`, `mine`, or `mixed`, and drafting pulls voice from your own
content first. This is the defence against the failure where, a year in, you
cannot tell your thinking from the model's.

**Every fact is timeless, dated, or a pointer.** Never write an undated
present-tense claim about something that changes; it becomes a lie next month
while still reading as true. `scripts/lint.py` catches these.

## What the linter checks

```bash
python3 scripts/lint.py            # full report
python3 scripts/lint.py --orphans  # notes nothing links to
python3 scripts/lint.py --json     # machine-readable
```

Citation keys that resolve to nothing, dead wikilinks, undated volatile claims,
stamps older than 180 days, orphan notes, missing frontmatter fields, and invalid
`origin` values. Exit code 1 on any error. Run it before publishing anything.

## Where to start

The vault is seeded with five sources, five notes, and one topic — the research
that produced it, ingested through its own pipeline. So the graph is not empty
and every convention has a worked example.

Three things to do first:

1. Fill in `voice/STYLE.md` and drop two or three published pieces into
   `voice/samples/`. Drafting is weak until this exists, and the command will
   tell you so rather than faking your voice.
2. Capture ten things without processing any of them. The point is to feel that
   capture costs nothing.
3. Then process one, and read what `/process` reports it *declined* to write.
   That report is where you tune the quality bar.
