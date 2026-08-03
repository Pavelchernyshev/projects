---
description: Create or refresh a Map of Content for a topic.
argument-hint: <topic name>
---

Create or refresh the topic MOC: $ARGUMENTS

A topic is a hub. It is how the vault stays navigable once there are hundreds of
notes and the graph view stops being readable. One file per topic in `topics/`.

## Procedure

1. **Check it does not already exist** under another name. Grep `topics/` for
   the term and its synonyms. Two MOCs covering the same ground is the main way
   a topic layer decays.

2. **Gather members.** Every note whose `topics:` frontmatter names this topic,
   plus every note that clearly belongs but is not yet tagged — search by the
   topic's vocabulary, not just its name. Add the topic to those notes'
   frontmatter as you go.

3. **Gather undistilled sources.** Sources with `processed: false` that belong to
   this topic. These go in a separate section so the topic shows both what you
   have thought about and what you have only collected. That gap is useful
   information.

4. **Write the file** at `topics/<Topic Name>.md` using `templates/topic.md`:

   - **Framing paragraph** — what this topic covers and, more usefully, where
     its boundary is. What is *not* in it.
   - **`## Notes`** — wikilink plus a one-line gloss each. Order by importance,
     not alphabetically; the first three should be the ones to read first.
   - **`## Sources not yet distilled`** — keys with titles.
   - **`## Open questions`** — what the vault cannot currently answer here. This
     section drives what to capture next, and it is the most valuable part of a
     MOC. Never leave it empty just to look finished.

5. Update `index.md` and append to `log.md`.

## Refreshing an existing topic

Same procedure, but preserve everything under `## Open questions` and any
human-written framing — merge rather than overwrite. Set `updated:` and
`note_count:`. If the note count has grown past roughly twenty, propose a split
into sub-topics rather than doing it unilaterally.
