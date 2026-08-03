---
type: note
category: concept
tags: [concept, knowledge-management, critique]
origin: ai-distilled
sources: [S-20260803-critiques-ai-maintained-knowledge-vaults, S-20260803-obsidian-second-brain-automation-system]
topics: ["[[Personal Knowledge Management]]"]
created: 2026-08-03
updated: 2026-08-03
confidence: high
---

**An AI-maintained vault fails in four specific ways, none of which are about individual notes being badly written.**

## Core idea

The case against putting an LLM in charge of a knowledge base is not that the
output is poor. It is that the output is *plausible*, and plausible output
accumulates faster than anyone reviews it. Four distinct failure modes, worth
separating because they need different corrections:

**Slop.** After enough time the owner can no longer tell which content they
wrote and which the model wrote, and their own thinking gets diluted by the
volume around it [S-20260803-critiques-ai-maintained-knowledge-vaults]. The
correction is provenance at the note level - an explicit origin field, and a
section the model is forbidden from writing in.

**Orphans.** Vault decay is a graph problem, not a note-quality problem. A note
with zero backlinks may have excellent content and still be functionally
invisible, because nothing leads to it
[S-20260803-critiques-ai-maintained-knowledge-vaults]. The correction is
mechanical orphan detection plus a deliberate linking pass.

**Confident mediocrity.** Without review, the agent ships output that gets
accepted by default, and iteration without review pulls the vault toward average
internet quality until it is useless
[S-20260803-critiques-ai-maintained-knowledge-vaults]. The correction is a
review gate on anything that modifies existing notes, and a compilation bar that
permits writing nothing.

**Rot proper.** An undated present-tense claim about something that changes is
the sentence that becomes a lie next Tuesday while still reading as truth
[S-20260803-obsidian-second-brain-automation-system]. The correction is the
freshness rule: every fact must be timeless, dated, or a pointer to where the
truth actually lives.

## Key points

- The four modes are independent; fixing linking does nothing about rot, and
  fixing rot does nothing about slop [inferred].
- The strongest version of the counter-argument is not "keep AI out" but "put AI
  in charge of the plumbing" - the mechanical filing, linking, and maintenance,
  not the thinking [S-20260803-critiques-ai-maintained-knowledge-vaults].
- Every correction above is checkable by a script except the review gate, which
  is the one that requires the owner. That asymmetry is worth respecting when
  deciding what to automate [inferred].

## My take

> prompt: Slop is the only one of the four you cannot lint for. Is the
> owner-only section enough of a defence, or do you want AI-written prose
> visually marked in Obsidian too?

## Connections

- [[Selective Linking]] — orphans and over-linking are the two graph failures;
  the linking rule addresses both from opposite sides.
- [[Capture Without Obligation]] — separating capture from processing is what
  prevents slop at the source, by never processing anything nobody asked for.

## Sources

- [[S-20260803-critiques-ai-maintained-knowledge-vaults]]
- [[S-20260803-obsidian-second-brain-automation-system]]