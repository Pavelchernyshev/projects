# Obsidian setup

The vault is plain markdown with `[[wikilinks]]`, so Obsidian needs no
conversion step. Open it and everything works. This document covers the setup
worth doing anyway, and the one decision that actually matters — how it syncs.

## Opening it

**Open folder as vault** → point at `second-brain/`. Not the repository root:
you do not want Obsidian indexing Python files, and you do not want `.git`
inside the vault (see sync below).

`.obsidian/app.json` and `.obsidian/graph.json` ship with the vault, so the
graph is already coloured by type and new notes default to `inbox/`. Everything
else is stock.

## Graph view

The graph is the reason to use Obsidian here, so the vault is built to render
well in it. Colours, already configured:

| Colour | What |
|---|---|
| Orange | `topics/` — the hubs. Should be the visible centres of clusters. |
| Blue | `notes/concepts/` |
| Green | `notes/methods/` |
| Grey | `sources/` — the raw material, deliberately dim |
| Purple | `drafts/` |

The chain you should see is `source → note → topic`, with a few cross-links
between notes in different clusters. Those cross-links are the valuable part;
there should be *few* of them, because the linking rule caps connections at two
or three per note. A graph where everything connects to everything means the
rule is being ignored.

**Structural note:** every edge in the graph is a body-level `[[wikilink]]`.
Obsidian's handling of wikilinks inside YAML frontmatter has changed across
versions and community plugins exist specifically to patch it, so the vault does
not depend on it. Each note lists its sources as clickable links under
`## Sources`, and each source lists what it fed under `## Distilled into`. The
frontmatter fields are still there for scripts; the body links are what draw the
graph.

Useful graph filters:

- `-path:sources` — hide raw material, see the idea graph alone.
- `path:topics OR path:notes` — the same thing, stated positively.
- Local graph on a topic, depth 2 — the best way to read a cluster.

## Core plugins to enable

Settings → Core plugins. All first-party, no installs:

- **Backlinks** and **Outgoing links** — the panels that make the graph usable
  as text.
- **Templates** — set the folder to `templates/`.
- **Tag pane** and **Search**.
- **Properties view** — renders the frontmatter as a form, which makes
  `origin:` and `confidence:` visible without reading YAML.
- **Daily notes** — set the folder to `daily/`, format `YYYY-MM-DD`, template
  `templates/daily.md`. `daily/` is the single best voice input for drafting,
  so it is worth the friction being low.

## Community plugins worth having

Only two earn their place:

- **Web Clipper** (a browser extension, not a plugin) — set the destination to
  `inbox/`. This is the capture lane's front door on desktop, and it is the
  thing that most determines whether you actually capture.
- **Copilot** — chat against the vault from a phone or tablet. Useful for
  reading on a device where Claude Code is not running. It is a retrieval
  surface, not a writing one: let it answer questions, and let Claude Code do
  the writing, so the Origin rule survives.

Not recommended: anything that auto-generates notes, auto-links, or
auto-summarizes on a schedule. That is exactly the mechanism that produces the
slop failure described in `docs/research.md`.

## Sync

Obsidian Sync is a good fit and worth paying for, with one thing to understand.

**Obsidian Sync ignores hidden folders** — anything starting with a dot, which
includes `.git`
([forum discussion](https://forum.obsidian.md/t/obsidian-sync-sync-hidden-files-and-folders-as-well-start-with-a-dot/32123)).
That is exactly what you want here: git and a file syncer both writing to `.git`
is how repositories get corrupted, and Sync not touching it removes the problem.

Vault *settings* under `.obsidian/` are a separate opt-in toggle inside Sync
(there are switches for appearance, core plugin settings, community plugins).
Turn on what you want to share across devices; it is independent of the
hidden-folder behaviour above.

The topology that works:

```
phone / tablet  <--- Obsidian Sync --->  laptop  ---git--->  GitHub
   capture, read, review                  Claude Code runs here
```

Mobile is a capture and reading surface. Claude Code runs on the laptop, and the
laptop is the only machine that commits. Nothing on mobile needs git.

**Commit regularly.** Sync is replication, not history — it will happily
replicate a mistake to every device. Git is what lets you recover a note you
overwrote three weeks ago. A weekly commit is enough; commit before any bulk
operation.

### If you split the vault into its own repo

Sensible eventually — this vault is personal, and the repo it currently lives in
is not. Copy `second-brain/` out, `git init`, done; nothing depends on its
location. `.git` then sits *inside* the vault, which is still fine because Sync
ignores it.

### If you use iCloud or Dropbox instead

Workable, but they do *not* reliably ignore `.git`, and both are known to corrupt
repositories they sync concurrently with git writes. If you go that route, keep
the git directory outside the vault (`git --separate-git-dir`) or do not use git
on that machine.

## Mobile capture

The capture lane has to work from a phone or it does not work at all — most
things worth capturing are encountered away from a desk.

- **iOS/Android share sheet** → Obsidian → append to a note in `inbox/`. Fastest
  path, no configuration.
- **Web Clipper** on mobile Safari/Chrome → `inbox/`.
- Anything in `inbox/` is safe but not yet citable. Running `/capture` on the
  laptop turns it into a real source file with a key.

That two-step is deliberate. Mobile capture stays instant, and key assignment
happens where the vault's conventions can actually be applied.

## What not to do in Obsidian

- **Do not edit files under `sources/` below `## Source text`.** The bodies are
  immutable; everything else in the vault can be rebuilt from them, which is
  only true while that holds.
- **Do write in `## My take`.** That section exists for you and Claude will
  never touch it. It is also where drafting gets your voice from, so writing
  there is the highest-leverage thing you can do in Obsidian.
