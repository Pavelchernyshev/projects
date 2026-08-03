---
description: Drop a source into the vault. URL, transcript, or both. Zero judgment.
argument-hint: <url and/or pasted text>
---

Capture this into `sources/`: $ARGUMENTS

This is Lane 1. **Speed is the whole point.** Do not summarize, do not evaluate,
do not link, do not ask whether it is worth keeping. Write the file and stop.

## Procedure

1. **Determine `source_type`** from what you were given: `article`, `video`,
   `podcast`, `book`, `paper`, or `conversation`. If a URL points at YouTube,
   it is `video`; a substack or blog, `article`; arxiv or a DOI, `paper`.
   If genuinely ambiguous, use `article`. Do not ask.

2. **Get the title and author.** If a transcript or text was pasted, take them
   from it. If only a URL was given and it is fetchable, fetch it for the
   title, author, and publication date only — do not read it for content, that
   is Lane 2 work. If the fetch fails or is blocked, use the URL slug as the
   title and leave `author: ""`. A capture with a bad title is fine; a capture
   that did not happen is not.

3. **Mint the key**: `S-<today YYYYMMDD>-<slug>`, slug from the title, kebab-case,
   about five words. Check `sources/` for a collision and add `-2` if needed.

4. **Write** `sources/<source_type>s/<key>.md` using `templates/source.md`.
   The pasted text goes under `## Source text` verbatim — no cleanup, no
   trimming, no reformatting. If only a URL was given, leave that section with
   the single line `<!-- not yet fetched -->`.

5. **Append to `log.md`**: `<date>  capture   <key>`.

6. **Report in one line**: the key and the path. Nothing else. No summary of
   what the source says, no suggestion to process it, no offer to do more.

## What not to do

- Do not update `index.md`. Sources are not catalogued until they are processed.
- Do not create notes, topics, or links.
- Do not say "would you like me to process this now?" Capture is complete on
  its own. Offering next steps re-introduces the decision that this lane exists
  to remove.
- Do not skip a capture because it looks similar to something already there.
  Duplicates are cheap; a lost source is not.

## Batch mode

If given several URLs or several pasted blocks, capture all of them. One file
each, one log line each, one summary line at the end with the count. Still no
processing.
