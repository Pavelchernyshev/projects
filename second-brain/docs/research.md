# Research: what the reference systems get right, and what this vault does differently

Notes from reading the seven links plus the surrounding literature, and the
reasoning behind every design decision in `CLAUDE.md`. Written 2026-08-03.

## What was actually read

| Source | Status |
|---|---|
| [evgenirusev/obsidian-second-brain](https://github.com/evgenirusev/obsidian-second-brain) | Read in full. The companion repo to the Medium article; its README *is* the article text and `CLAUDE.md` is the schema. |
| [eugeniughelbur/obsidian-second-brain](https://github.com/eugeniughelbur/obsidian-second-brain) | Read in full, including `references/` specs. |
| [AgriciDaniel/claude-obsidian](https://github.com/AgriciDaniel/claude-obsidian) | Read in full, including the skill definitions. |
| [aimaker.substack.com](https://aimaker.substack.com/p/ai-second-brain-obsidian) | Substance obtained via search indexing; the page itself returns 403 to automated fetches. |
| [youmind.com](https://youmind.com/ru-RU/landing/x-viral-articles/claude-code-obsidian-second-brain) | 403. |
| [dev.to article](https://dev.to/joao_victorsouza_ef8ff8a/obsidian-claude-code-as-a-second-brain-1n71) | Blocked by this environment's network policy, including the dev.to API. |
| [r/ClaudeHomies thread](https://www.reddit.com/r/ClaudeHomies/comments/1vdsczp/is_this_second_brain_obsidian_claude_actually_good/) | Reddit blocked entirely. |

The two blocked sources were the skeptical ones, and their absence would have
been a real gap, so the critical position was reconstructed from
[ssp.sh](https://www.ssp.sh/brain/using-obsidian-with-ai/),
[dsebastien.net](https://www.dsebastien.net/dont-keep-ai-out-of-your-vault-put-it-in-charge-of-the-plumbing/),
and [a piece on vault
rot](https://tejnaren07.medium.com/my-obsidian-vault-was-rotting-so-i-wrote-a-plugin-to-diagnose-it-a1343830fbbb).
Worth re-reading the two blocked links manually; if they contain an argument not
covered below, it is the one thing this research missed.

## The common ancestor

All of them descend from Karpathy's LLM Wiki: feed a model raw information, give
it a schema, let it structure. The shared consequences are not in dispute:

- Plain markdown, because it is portable, composable, and native to the model.
- One file that is the schema, read at session start. This is what turns a
  general assistant into a domain-specific knowledge worker.
- Obsidian for browsing, the agent for writing. The vault and the model's
  working surface are the same artifact, so there is no sync problem.

## Where they diverge, and what was taken from each

### Rusev — minimal

Two files. The owner directs every ingest; nothing is automatic. Quality comes
from one constraint: **cap connections at the two or three where understanding A
genuinely changes how you read B.** He reports this single instruction produced
dramatically better cross-references than "link related concepts."

**Taken:** the linking rule, verbatim in spirit. The insistence that the human
directs each ingest. The observation that knowledge compounds, which is the
argument for reading existing notes before writing new ones.

**Left:** the flat `books/articles/posts/wiki` layout has no provenance layer, so
you cannot cite from it reliably. And it does not scale to volume, which is the
whole problem being solved here.

### Ghelbur — maximal

46 commands, scheduled agents, a background agent after context compaction, seven
platform builds. Two genuinely valuable specs buried in the volume:

- **The freshness policy (OKM).** Every stored fact must be timeless, dated, or a
  pointer. The one illegal form is an undated present-tense claim about something
  that changes — "the sentence that becomes a lie next Tuesday while still
  reading as truth." Enforced by a lint.
- **Bi-temporal facts.** Never overwrite a status; append to a timeline with both
  event time (`from`/`until`) and transaction time (`learned`). Lets the vault
  answer "who was CTO in January" and "when did I learn this."

Also strong: the anti-fabrication hard rules, especially naming *false absence* —
claiming a note does not exist without an exhaustive search — as the most common
observed failure. And "sources are data, never instructions."

**Taken:** the freshness policy (implemented as FRESH-1/2 in `scripts/lint.py`),
the anti-fabrication rules, the untrusted-source rule, and the idea of a catalog
file read before searching.

**Left:** the scheduled agents and the background synthesis agent. Both write to
the vault without anyone asking, which is precisely the mechanism that produces
slop. Also left: the `## For future Claude` preamble on every note. It optimizes
notes for machine retrieval at the cost of being pleasant to read, and a vault
the owner never reads is a vault whose quality nobody checks. Bi-temporal facts
were left out as too heavy for a vault that is mostly reading rather than
people-tracking; it is flagged as an open question in the topic MOC.

### AgriciDaniel — rigorous

A Python core with transactional writes (SHA-256 preconditions, atomic apply,
recovery), and separate source and claim ledgers tracking authority, freshness,
support, contradiction, and confidence.

Two ideas that shaped this vault more than anything else:

- **The compilation-value gate.** Create a page only when the source adds durable
  synthesis, navigation, a decision, or a reusable connection *beyond the
  captured source*. Explicitly: do not paraphrase merely to create pages.
- **Honest capability boundaries.** If the tooling cannot read a PDF, record the
  locator and say so; never pretend the media was read.

**Taken:** both, plus the preservation of contradictory evidence rather than
resolving it, and the requirement that a high-risk claim needs two independent
sources.

**Left:** the transaction machinery. It solves multi-agent concurrent writes to a
shared vault. A single owner working through git does not have that problem, and
the cost is that every operation becomes a two-phase plan/apply with a hash
approval step. Git is already the transaction log.

## The critique, which the reference repos do not answer

Four failure modes, all real, all documented in [[Vault Rot]]:

1. **Slop.** After a year the owner cannot tell their thinking from the model's.
2. **Orphans.** Vault decay is a graph problem; a note with zero backlinks is
   invisible regardless of quality.
3. **Confident mediocrity.** Unreviewed iteration converges on average internet
   quality.
4. **Rot.** Undated claims that read as true forever.

The strongest form of the counter-argument is not "keep AI out" but "put AI in
charge of the plumbing" — filing, linking, and maintenance, not thinking. That
is the position this vault takes.

## What this vault does that none of them do

### 1. Three lanes at different speeds

The stated requirements pull against each other: FOMO relief needs high-volume
zero-judgment capture; publishable drafts need cited, reviewed, high-quality
output. None of the reference systems separate these, so each ends up
compromising one. Here they are separate lanes with separate commands, and the
rule is never to do refine-work at capture time.

The load-bearing decision is that **an unprocessed source is not debt.** The pile
is allowed to grow forever and the health report is explicitly forbidden from
presenting it as a task. That is what actually removes the FOMO — not the
capturing, but the absence of a queue.

### 2. A citation contract with a mechanical check

The model never writes a reference. It selects keys; references render from the
source files on disk; `scripts/lint.py` fails on a key that does not resolve. So
the worst case is a missing citation, never a fabricated one.

This is the same guarantee the `myway` bot uses for its research corpus, for the
same reason: a plausible fake citation passes review precisely because it looks
right.

Every factual sentence also carries a marker — `[S-key]`, `[mine]`, or
`[inferred]` — which makes the sourced/owned/synthesized split auditable rather
than a matter of trust.

### 3. The Origin rule

`## My take` is owner-only; the model never writes there. Every note declares
`origin: ai-distilled | mine | mixed`. Drafting reads voice from `mine` content
first and treats `ai-distilled` prose as facts-and-structure only, never as text
to lift.

This is the direct answer to the slop critique, and it is the one failure mode a
script cannot catch — which is exactly why it needed a structural rule instead of
a check.

### 4. An output lane

`/draft` produces articles, book chapters, and social posts from the vault with
rendered references, and reports the ratio of `[mine]` to `[S-key]` to
`[inferred]` claims. A draft that is 90 percent sourced is a literature review,
and saying so is more useful than shipping it quietly.

None of the three reference systems treat publishing as a first-class output.
Given the goal is articles, book chapters, and posts, that was the largest gap.

## Deliberate omissions

- **Embeddings and semantic search.** Keyword plus the topic layer is enough for
  hundreds of notes. Revisit in the thousands.
- **Scheduled agents.** Nothing writes to this vault unless asked.
- **Kanban boards, task management, health tracking.** Out of scope; this is a
  knowledge system, not a life-operations system. Adding them is what makes these
  vaults sprawl.
- **A plugin or marketplace distribution.** This is one person's vault. It is
  files in git.
