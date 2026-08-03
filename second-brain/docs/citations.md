# The citation contract

The rule that makes this vault safe to publish from: **the model never writes a
reference.** It selects source keys; the reference text is rendered from the
source files on disk.

This is the same guarantee used in the `myway` bot's research library, for the
same reason. A model asked to produce a citation from memory will eventually
produce a plausible one that does not exist, and a plausible fake citation is
much worse than a missing one, because nobody checks it.

## The flow

```
sources/*.md  ->  keys + titles in context  ->  model picks keys  ->  we render
                                                      |
                                            unknown key -> lint error, dropped
```

At draft time the model has a list of keys with one-line descriptions. It writes
`[S-20260803-rusev-second-brain]` inline. When the references section is built,
each key is looked up in `sources/`, and the `title`, `author`, `url`,
`published`, and `accessed` fields are read off the file. A key with no matching
file is a lint error and never renders.

So the failure mode is a claim that loses its citation, not a citation that
points at nothing.

## Key format

```
S-YYYYMMDD-slug
```

- `S-` marks it as a source key.
- `YYYYMMDD` is the **capture** date, not the publication date. Capture dates
  are always known; publication dates often are not.
- `slug` is kebab-case, derived from the title, trimmed to about five words.

Keys are permanent. If a title changes, the key does not. If the same article is
captured twice, keep both files and mark the second `duplicate_of:` — do not
merge, because notes may already cite the first key.

Collisions on the same day get a numeric suffix: `-2`, `-3`.

## Claim markers

Every factual sentence in `notes/` and `drafts/` carries exactly one marker.

| Marker | Means | Example |
|---|---|---|
| `[S-key]` | Stated by that source | `Vaults rot at the graph level, not the note level [S-20260803-vault-rot].` |
| `[S-key1, S-key2]` | Multiple sources agree | Raises confidence; note it in frontmatter. |
| `[mine]` | The owner's own claim | From `daily/`, `## My take`, or a conversation. |
| `[inferred]` | Synthesis across sources | Not stated by any single one. |

An unmarked factual sentence is a bug. Framing sentences, transitions, and
definitions of your own terms do not need markers.

## Rendering references

In a draft, `## References` is generated, never typed. For each key in the
draft's `sources:` frontmatter, in order of first appearance:

```markdown
1. Rusev, E. "How I Built My Second Brain with Obsidian + Claude Code."
   github.com/evgenirusev/obsidian-second-brain (accessed 2026-08-03).
```

Fields come from the source file. Missing fields are omitted, not guessed:
no author means the reference starts with the title; no publication date means
only `accessed` appears.

For social posts, references collapse to a short list of links at the end, or a
"sources in replies" convention — but the `sources:` frontmatter is still
complete, so the claim can be checked later.

## What lint checks

`scripts/lint.py` enforces this contract:

- **CITE-1 (error)** — a `[S-...]` key in any note or draft with no matching
  `key:` in `sources/`.
- **CITE-2 (error)** — a key in a draft's `sources:` frontmatter that does not
  resolve.
- **CITE-3 (warning)** — a key cited inline but absent from the file's
  `sources:` frontmatter, or the reverse.
- **CITE-4 (warning)** — a source file with no `key:` at all.

Run it before publishing anything.
