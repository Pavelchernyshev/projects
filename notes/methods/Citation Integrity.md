---
type: note
category: method
tags: [method, provenance, writing]
origin: ai-distilled
sources: [S-20260803-claude-obsidian-transactional-knowledge-system, S-20260803-obsidian-second-brain-automation-system]
topics: ["[[Personal Knowledge Management]]"]
created: 2026-08-03
updated: 2026-08-03
confidence: high
---

**Let the model select source identifiers and render the reference text yourself, so the worst failure is a missing citation rather than an invented one.**

## Core idea

A model asked to produce a citation from memory will eventually produce a
plausible one that does not exist. A plausible fake citation is far worse than a
missing one, because nobody checks it - it passes review precisely because it
looks right [inferred].

The structural fix is to remove reference-writing from the model's job. The
model receives a list of stable keys with one-line descriptions and returns
keys. The reference text - author, title, URL, date - is rendered from the
source files on disk. A key that does not resolve fails lookup, gets logged, and
is dropped before rendering. The failure mode becomes a claim that lost its
citation, which is visible, rather than a citation pointing at nothing, which is
not.

Two supporting rules from the provenance-heavy end of the design space:
contradictory evidence is preserved rather than resolved, claims with no support
are explicitly marked unsupported, and a high-risk accepted claim requires two
independent sources
[S-20260803-claude-obsidian-transactional-knowledge-system]. And every external
claim carries its source URL inline rather than a paraphrased attribution, so it
can be re-verified years later
[S-20260803-obsidian-second-brain-automation-system].

## Key points

- The model picks identifiers; the system renders references. Never the reverse
  [inferred].
- Unresolvable keys must be caught mechanically, not by review - that is what
  makes the guarantee real rather than aspirational [inferred].
- Every factual sentence needs a marker distinguishing sourced claims from the
  owner's own claims from the model's synthesis; an unmarked factual sentence is
  a defect [inferred].
- Preserve contradictions instead of reconciling them; disagreement between
  sources is information
  [S-20260803-claude-obsidian-transactional-knowledge-system].

## My take

> prompt: For social posts, where a references list is impractical - do you want
> links in replies, or is complete frontmatter enough to check later?

## Connections

- [[Capture Without Obligation]] — this is why deferring distillation is safe:
  the citation resolves to the raw source, so an undistilled source still
  supports a published claim.
- [[Vault Rot]] — citation integrity governs claims leaving the vault; the
  freshness rule governs claims sitting inside it. Both are about text that
  reads as true after it stops being true.

## Sources

- S-20260803-claude-obsidian-transactional-knowledge-system
- S-20260803-obsidian-second-brain-automation-system
