---
type: note
category: method
tags: [method, knowledge-management, linking]
origin: ai-distilled
sources: [S-20260803-built-second-brain-obsidian-claude, S-20260803-critiques-ai-maintained-knowledge-vaults]
topics: ["[[Personal Knowledge Management]]"]
created: 2026-08-03
updated: 2026-08-03
confidence: high
---

**Cap each note at the two or three connections where understanding A genuinely changes how you read B; a graph where everything connects carries no information.**

## Core idea

The instinct with an automated wiki is to let the model link generously, on the
theory that more edges mean more discoverable knowledge. The opposite holds.
Telling the model to "keep connections tight - only link where understanding A
genuinely changes how you see B" produced dramatically better cross-references
than an open-ended "link related concepts"
[S-20260803-built-second-brain-obsidian-claude].

The reason is information-theoretic rather than aesthetic. If every note links
to every vaguely related note, the presence of an edge tells you nothing, and
the graph degrades into a slow full-text search [inferred]. A link is a claim -
that these two ideas inform each other - and claims that are always true are
worthless.

The practical test: write the one-line justification *before* creating the link.
If the line comes out as "both are about knowledge management", the link fails
and gets discarded. This forces the judgment to happen at write time, where it
is cheap, rather than at read time, where it is expensive and usually skipped.

## Key points

- Two to three connections per note, in a curated section; inline mentions of
  people and named things are navigation and do not count against the cap
  [inferred].
- Every connection states what it *does*, not merely that it exists. A bare
  wikilink is an incomplete link [S-20260803-built-second-brain-obsidian-claude].
- Cross-domain edges are the high-value ones. Within a topic, the connection is
  usually already obvious; the edge from biology to negotiation is the one worth
  a slot [inferred].
- The critique that AI-made connections "do not count" because the owner did not
  make them [S-20260803-critiques-ai-maintained-knowledge-vaults] is partly
  answered by this rule: a strict bar plus a written justification means every
  edge is reviewable, and an edge the owner reads and keeps is an edge the owner
  made [inferred].

## My take

> prompt: Do you want to review proposed links before they are written, or trust
> the bar and audit later? The first is slower and keeps the graph fully yours.

## Connections

- [[LLM Wiki Pattern]] — the pattern generates the graph; this is the constraint
  that decides whether the graph is worth having.
- [[Vault Rot]] — orphans and over-linking are the two ways a graph fails, and
  they need opposite corrections.

## Sources

- [[S-20260803-built-second-brain-obsidian-claude]]
- [[S-20260803-critiques-ai-maintained-knowledge-vaults]]