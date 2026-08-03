---
type: note
category: concept
tags: [concept, llm-wiki, knowledge-management]
origin: ai-distilled
sources: [S-20260803-llm-wiki-pattern, S-20260803-built-second-brain-obsidian-claude]
topics: ["[[Personal Knowledge Management]]"]
created: 2026-08-03
updated: 2026-08-03
confidence: high
---

**Give an LLM a folder of plain markdown and a schema file, and it will maintain the wiki you would otherwise maintain by hand.**

## Core idea

The pattern is one sentence: feed a model raw information, give it a schema to
follow, and let it do the structuring [S-20260803-llm-wiki-pattern]. Everything
else is elaboration. Every system examined while building this vault descends
from it, and their differences are entirely about how much machinery sits
between the raw input and the finished page [inferred].

What makes it work is not the model but the format. Markdown files are portable
(no vendor can take them), composable (frontmatter, tags, and wikilinks are just
text any tool can parse), and native to the model, which reads and writes them
without an API wrapper or an export step
[S-20260803-built-second-brain-obsidian-claude]. The knowledge base and the
model's working surface are the same artifact, which is why there is no
synchronization problem to solve.

The load-bearing file is the schema. It is what turns a general-purpose
assistant into a domain-specific knowledge worker: without it, every session
starts by re-explaining the system; with it, the structure, conventions, and
quality bar are already in context
[S-20260803-built-second-brain-obsidian-claude]. A vague schema produces vague
output, which is the failure most people attribute to the model.

## Key points

- Raw information in, schema-shaped pages out; the schema is the product
  [S-20260803-llm-wiki-pattern].
- Plain markdown means the knowledge outlives the tool that made it
  [S-20260803-built-second-brain-obsidian-claude].
- Knowledge compounds: the tenth source is worth more than the first because
  there is more for it to attach to
  [S-20260803-built-second-brain-obsidian-claude].
- The pattern says nothing about *quality control*, which is where all three
  reference implementations diverge and where most of the design work actually
  lives [inferred].

## My take

> prompt: Which of your domains has enough depth already that a tenth source
> would connect to nine others? Start there - the compounding argument only
> pays off inside a domain that is already dense.

## Connections

- [[Selective Linking]] — the pattern produces a graph; selective linking is
  what stops that graph from becoming uniformly connected and therefore
  meaningless.
- [[Vault Rot]] — the same automation that makes the pattern fast is what lets
  a vault fill with material nobody chose to keep.

## Sources

- [[S-20260803-llm-wiki-pattern]]
- [[S-20260803-built-second-brain-obsidian-claude]]