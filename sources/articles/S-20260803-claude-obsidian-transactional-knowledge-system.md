---
key: S-20260803-claude-obsidian-transactional-knowledge-system
type: source
source_type: article
title: "claude-obsidian transactional knowledge system"
author: "Daniel Agrici"
url: "https://github.com/AgriciDaniel/claude-obsidian"
published: ""
accessed: 2026-08-03
tags: [knowledge-management, obsidian, provenance]
processed: true
notes: ["[[Capture Without Obligation]]", "[[Citation Integrity]]"]
---

# claude-obsidian transactional knowledge system

## Why captured

Reference system: the rigorous end. Source of the provenance model.

## Distilled into

- [[Capture Without Obligation]]
- [[Citation Integrity]]

## Source text

Python core plus 15 composable skills, exposed as /claude-obsidian:wiki-ingest etc. Key contributions: (1) Transaction model - operations read targets with SHA-256 checksums, collect worker drafts, merge into one bundle, inspect, then apply atomically with recovery. Vault lock, journaled backups, atomic replacement, restore on failure. (2) Provenance ledgers - separate source ledger and claim ledger tracking authority, freshness, support, contradiction, confidence, and review state. Contradictory evidence is preserved, not resolved. No-data claims marked 'unsupported'. An accepted claim needs a fresh active non-synthetic source; a high-risk accepted claim needs two independent sources. (3) The compilation-value gate - create or expand a page only when the source adds durable synthesis, navigation, a decision, or a reusable connection beyond the captured source; a concise searchable source may need only its ledger record or a no-op; do not paraphrase merely to create pages. (4) wiki-mode supports Generic, LYT, PARA, Zettelkasten filing without reorganizing existing knowledge. (5) Honest capability boundaries - declares maturity levels and gates high-risk features rather than pretending media was read. Loop: 'retain the source, ground the claims, connect the knowledge, then put it back to work.'
