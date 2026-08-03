---
type: topic
tags: [knowledge-management, llm-wiki]
created: 2026-08-03
updated: 2026-08-03
note_count: 5
---

# Personal Knowledge Management

How a knowledge base built and maintained by an LLM stays worth owning: what to
capture, what earns a note, how notes connect, and what has to be true before
anything drawn from the vault gets published.

The boundary: this topic covers the *system* - capture, structure, linking,
provenance, output. It does not cover the domains the vault stores knowledge
about. When a second topic appears, this one stops absorbing everything.

## Notes

- [[LLM Wiki Pattern]] — the origin idea all of these systems descend from.
  Read first.
- [[Capture Without Obligation]] — why the pile is allowed to grow, and why
  that is the thing that makes capture free.
- [[Selective Linking]] — the constraint that decides whether the graph is
  worth having.
- [[Citation Integrity]] — the mechanism that makes drafts publishable.
- [[Vault Rot]] — the four ways this fails, and which corrections a script can
  carry.

## Sources not yet distilled

<!-- All five research sources are distilled. New captures land here. -->

## Open questions

- Does the two-to-three link cap hold at 500 notes, or does the vault need
  intermediate hub notes below the topic level?
- Where does voice actually come from once `voice/samples/` is populated - can a
  draft built from `origin: mine` notes alone carry a full article, or does the
  owner always have to write the connective prose?
- The bi-temporal fact model (never overwrite a status, append to a timeline
  with both event time and learned time) was deliberately left out as too heavy
  for a vault that is mostly reading rather than tracking people. Revisit if
  `notes/people/` grows past roughly twenty entries.
- Nothing here addresses retrieval at scale. Keyword search and the topic layer
  are enough for hundreds of notes; embeddings become the question in the
  thousands.
