---
description: Find the strongest missing links for a note or topic.
argument-hint: <note name, topic, or "orphans">
---

Find connections for: $ARGUMENTS

The value of a note is its connections. An orphan with excellent content is
functionally invisible — nothing leads to it, so it is never read again. This
command is the deliberate repair of that, and it is deliberately conservative.

## Procedure

1. **Read the target** fully — the note, or every note in the topic. If the
   argument is `orphans`, run `python3 scripts/lint.py --orphans` and work the
   list, highest-value first.

2. **Read broadly.** `index.md`, then candidate notes across *all* categories.
   Deliberately look outside the target's own topic. Within-topic links are
   usually already there; the connections worth finding are the cross-domain
   ones.

3. **Apply the bar.** Propose a link only if **understanding A genuinely changes
   how you read B.** Test it by writing the one-line justification first. If the
   line comes out as "both are about knowledge management", the link fails.
   Discard it. This bar is strict on purpose — a graph where everything connects
   to everything carries no information.

4. **Cap at 2-3** per note in `## Connections`. If you find a fourth that is
   genuinely stronger than an existing one, propose the *swap* explicitly rather
   than growing the list.

## Report before writing

Present the proposed links as a list — source, target, and the justification
line — and wait for approval before editing notes. Modifying existing notes
needs confirmation.

Say plainly when you found nothing. "Three candidates considered, none met the
bar" is a good outcome and a true one. Manufacturing weak links to have
something to show is the failure this command must not commit.

## Also worth reporting

While reading, note and report without acting on:

- **Contradictions** — two notes making incompatible claims. Do not resolve
  them; surface both with their keys and let the owner decide. Contradictions
  between sources are information, not errors.
- **Duplicates** — two notes covering the same idea under different names.
  Propose a merge, do not perform one.
- **Missing hubs** — a cluster of five or more notes with no topic MOC.
