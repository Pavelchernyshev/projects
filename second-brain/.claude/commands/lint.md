---
description: Vault health report — unresolved citations, dead links, orphans, stale facts.
argument-hint: [--fix]
---

Run the vault health check. Arguments: $ARGUMENTS

## Procedure

1. Run the checker:

   ```bash
   python3 scripts/lint.py
   ```

   It reports, by severity:

   - **CITE-1/2 (error)** — citation keys that resolve to nothing. Fix these
     before publishing anything.
   - **LINK-1 (error)** — `[[wikilinks]]` with no target file.
   - **FRESH-1 (error)** — undated present-tense claims about things that
     change. These are the sentences that silently become lies.
   - **CITE-3, LINK-2 (warning)** — frontmatter and inline citations out of
     sync; links pointing at stubs that were never filled in.
   - **ORPHAN (warning)** — notes with zero inbound links.
   - **SCHEMA (warning)** — missing required frontmatter fields.
   - **info** — unprocessed source count, note and topic counts, tag list.

2. **Read the findings and judge them.** The script is a heuristic. FRESH-1 in
   particular will flag prose that only reads like a volatile claim. Do not
   mechanically edit everything it prints.

3. **Report grouped by what the owner should actually do**, not by rule number:

   - Blocking publication (unresolved citations in drafts).
   - Breaking retrieval (dead links, orphans in areas being actively used).
   - Slowly rotting (stale stamps).
   - Cosmetic (schema gaps in old notes).

## The backlog is not a finding

The count of unprocessed sources is reported as **information only**. Never
present it as a problem, a to-do, or something to clean up. The pile is the
point — it is what makes capture free. A vault with four hundred unprocessed
sources and forty good notes is working exactly as designed.

## With `--fix`

Only these are safe to fix without asking:

- Adding a missing `key:` to a source file (derive it from the path and date).
- Adding missing `created:`/`updated:` from git history or file mtime.
- Creating stubs for dead wikilinks.
- Syncing `sources:` frontmatter with keys actually cited inline.

Everything else — rewriting a stale claim, deleting an orphan, resolving a
contradiction — is a proposal. List them and wait.

## Cadence

Weekly matches the 7-day freshness window. Also run before any `/draft` goes
out, since that is when an unresolved citation stops being cosmetic.
