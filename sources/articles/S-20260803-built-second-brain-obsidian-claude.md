---
key: S-20260803-built-second-brain-obsidian-claude
type: source
source_type: article
title: "How I Built My Second Brain with Obsidian + Claude Code"
author: "Evgeni Rusev"
url: "https://github.com/evgenirusev/obsidian-second-brain"
published: ""
accessed: 2026-08-03
tags: [knowledge-management, llm-wiki, obsidian]
processed: true
notes: ["[[LLM Wiki Pattern]]", "[[Selective Linking]]"]
---

# How I Built My Second Brain with Obsidian + Claude Code

## Why captured

Reference system: the minimal end of the design space.

## Source text

Companion repo to the Medium article. Two files: README.md (the article) and CLAUDE.md (the schema). Structure: books/, articles/, posts/, wiki/mental-models/, index.md, log.md, CLAUDE.md. Core claims: markdown is portable, composable, LLM-native; the schema file turns Claude from a general assistant into a domain-specific knowledge worker; constraint improves quality - 'keep connections tight, only link where understanding A genuinely changes how you see B' produced dramatically better cross-references than open-ended 'link related concepts'; knowledge compounds - the 10th book produces more insight than the 1st because there is more to connect to. Frontmatter: tags, source, author, date_ingested, related. Workflows: ingest, query, lint. Reports 86 mental model pages across eight domains from two books. Human directs every ingest; Claude does not auto-process.
