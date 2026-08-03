---
description: Draft an article, book chapter, or social post from the vault, with references.
argument-hint: <article|chapter|social> <topic or angle>
---

Draft from the vault: $ARGUMENTS

This is Lane 3. The output is a file in `drafts/`, and every factual claim in it
traces to a source key. Read `docs/citations.md` and `voice/STYLE.md` before you
start.

## Step 1 — Gather, and be honest about what you have

1. Read `index.md`, then read every note and topic relevant to the angle. Read
   them fully. Then grep `sources/` for captured-but-unprocessed material on the
   same subject — an unprocessed source is still citable, you just have to read
   it now.
2. Assemble the evidence list: every key you might cite, with what it supports.
3. **Assess the voice inputs.** How much of this can come from `## My take`
   blocks, `daily/` entries, `origin: mine` notes, and `voice/samples/`?

Then say, before writing:

- What the vault supports well.
- What the angle needs that the vault does not have. Name the gap. Do not fill
  it from general knowledge and let it pass as vault-derived.
- The voice assessment. If everything available is `ai-distilled`, say plainly:
  *this will be a research memo with citations, not a piece in your voice* — and
  ask whether to proceed or whether they want to add a take first.

## Step 2 — Outline

Produce the outline before the prose, and get agreement on it. For each section:
the claim it makes, and the keys backing it. A section with no keys and no
`[mine]` is a section built on nothing; flag it rather than writing it.

## Step 3 — Write

- **Argument and phrasing come from the owner.** Their `## My take` lines, their
  daily-note phrasing, their published samples. Facts and structure come from
  `ai-distilled` notes. Never lift `ai-distilled` prose into a draft — it was
  written for retrieval and it reads like it.
- **Every factual sentence carries a marker**: `[S-key]`, `[mine]`, or
  `[inferred]`. Keep them inline in the draft. They are stripped at publish
  time, not at write time; a draft without markers cannot be audited.
- **Never write a citation key you have not confirmed exists** in `sources/`.
  If you want to cite something the vault does not have, write
  `[NEEDS SOURCE: <what you would need>]` and leave it. That is a visible hole,
  which is the point.

Format by type:

- `article` → `drafts/articles/YYYY-MM-DD - Title.md`
- `chapter` → `drafts/book/NN - Title.md` (ask for the chapter number if the
  book structure is not already in `projects/`)
- `social` → `drafts/social/YYYY-MM-DD - Hook.md`. Produce two or three
  variants, not one — hooks are cheap to generate and expensive to guess at.

## Step 4 — References

Build `## References` by **looking up each key in `sources/` and reading the
actual frontmatter fields.** Author, title, url, published, accessed. Do not
write a reference from memory, ever. Omit fields that are missing rather than
guessing them.

For social, collapse to a link list at the end, but still fill the `sources:`
frontmatter completely.

## Step 5 — Close out

1. Fill the draft's `sources:` and `notes:` frontmatter with everything used.
2. Run `python3 scripts/lint.py --path drafts/<file>` and fix what it reports.
3. Append to `log.md`.
4. Report: word count, how many claims are `[mine]` vs `[S-key]` vs `[inferred]`,
   and every `[NEEDS SOURCE]` hole left open.

That last ratio matters more than the word count. A draft that is 90 percent
`[S-key]` is a literature review. A publishable piece is mostly `[mine]`, with
sources holding up the load-bearing facts.
