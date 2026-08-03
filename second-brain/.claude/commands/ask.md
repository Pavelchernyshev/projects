---
description: Answer a question from the vault, grounded, with citation keys.
argument-hint: <question>
---

Answer from the vault: $ARGUMENTS

Retrieval, not generation. The value here is that the answer is *yours* — drawn
from what you have actually read and thought, not from the model's general
knowledge.

## Procedure

1. **Read `index.md` first.** The catalog is cheaper and more reliable than
   grepping blind.
2. **Then search exhaustively.** Grep `notes/`, `topics/`, `sources/`, and
   `daily/` for the question's terms *and their synonyms*. Enumerate matches;
   do not sample. Under-reporting is the failure mode here — an answer that
   misses the one note that mattered is worse than no answer, because it looks
   complete.
3. **Read the matches fully** before answering.
4. **Answer with markers.** Every factual sentence carries `[S-key]`, `[mine]`,
   or `[inferred]`, and every vault note referenced is a `[[wikilink]]`.
5. **Separate vault from world.** If the vault does not cover part of the
   question and you answer it from general knowledge, put that in a clearly
   labelled `## Outside the vault` section at the end. Never let general
   knowledge blend into the grounded part — that is exactly the contamination
   this vault exists to prevent.
6. **Say what is missing.** If the vault is thin on the question, name what
   would need capturing to answer it properly.

## Cross-domain synthesis

The highest-value use of this command is a problem, not a lookup: "I need to
decide X" or "how should I approach Y". For those, deliberately pull from
*different* topics. A negotiation problem may be best answered by something
filed under biology. Nobody naturally thinks across ten domains at once; the
vault does, and this is where that pays off.

When doing this, mark the cross-domain leaps `[inferred]` — they are your
synthesis, not anyone's claim.

## Offer to file

If the answer took real work and would be worth having again, offer once to save
it as a note in `notes/concepts/` with `origin: ai-distilled`. Ask; do not
assume. Answers that get auto-filed are how a vault fills with material nobody
chose to keep.
