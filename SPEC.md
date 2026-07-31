# MyWay — product spec

Written alongside the MVP in this repo. Records the decisions that are already
implemented and the open questions that need a human answer.

## 1. What this is

An interview-driven coach in Telegram that gets a person to name what they are
avoiding, then points at exactly one thing to fix — with the research behind that
direction visible and checkable.

The wedge is not "AI life coach". It is **refusal to give you five things**, plus
**receipts**. Both are product constraints enforced in code, not tone-of-voice
guidance:

| Promise | How it is enforced |
|---|---|
| One thing to fix | `focus_domain` is a single enum in the verdict schema; other domains go to `not_now` |
| Brutally honest | Prompt forbids validation openings; `honest_read` must name what the user talked around |
| Extremely clear | Action must be an if-then with a named obstacle and a countable measure |
| Actually scientific | Model returns citation ids only; references render from our YAML |

## 2. The five domains

Time, social, mental, physical, financial — following Sahil Bloom's
*The 5 Types of Wealth* (2025). The taxonomy is his; the evidence attached to each
domain is ours and lives in `src/myway/science/corpus/`.

Behaviour-change evidence sits outside the five as `cross_cutting`, always in
scope, because every verdict ends in a plan.

## 3. Conversation design

```
/begin → OPENING → PULSE → PROBE ⟳(3–6) → VERDICT → COMMIT → closed
```

**OPENING.** One question: *what do you keep meaning to deal with and keep not
dealing with?* Deliberately not a menu. Answers under 15 characters are rejected —
the interview is worthless on "dunno".

**PULSE.** Five inline-keyboard taps, 1–5. Cheap, fast, and gives a numeric
baseline the model can be wrong about out loud ("you rated money 4 but described
three months of dread"). The pulse orders which domains' evidence enters the
verdict prompt; it does not decide the focus.

**PROBE.** The model sees the transcript and decides: ask again, or stop. It is
told to go after specific instances rather than generalisations, and after what
the person is avoiding rather than what they elaborate on comfortably. Bounded
3–6, capped in both the engine and the bot loop.

**VERDICT.** One domain — chosen for being *upstream*, not lowest-scoring. Names
what they talked around in their own words. Defers the rest explicitly, which is
part of the help. One to three citations.

**COMMIT.** They accept or push back. Both are recorded; a decline with a reason
is more useful signal than a hollow yes.

## 4. Model configuration

| | Verdict | Probe |
|---|---|---|
| Model | `claude-opus-5` | `claude-opus-5` |
| Effort | `high` | `low` |
| Max tokens | 8000 | 2000 |
| Output | Strict JSON schema | Strict JSON schema |

Thinking is on by default on Opus 5 and left there. The system prompt is
byte-stable across every call and cached, so after the first request of a session
the identity and evidence rules are close to free.

Prompt choices worth preserving (they counter documented Opus 5 defaults):

- Explicit conciseness instruction — the model is verbose by default, and `effort`
  does not reliably shorten visible output.
- Explicit scope discipline — it expands task scope otherwise.
- **No** "double-check your work" instruction — it self-verifies without being
  asked, and adding one causes over-verification.

## 5. The citation guarantee

The single most important design decision in the product.

The model never emits a reference. It picks ids from a supplied list; the
application renders authors, year, journal, and DOI from YAML it controls. An
invented id fails lookup, is logged at ERROR, and is dropped.

Consequences, accepted deliberately:

- Coverage is bounded by the corpus. If nothing supports a point, the model is
  told to change the point or drop the citation.
- Growing coverage is manual editorial work, not a retrieval improvement.
- In exchange, "this is scientific" is a checkable claim rather than a vibe, and
  `/sources` lets any user audit it.

**`verified: false` on all 28 entries is a launch blocker.** The flag means no
human has confirmed our summary fairly states what the paper found. DOI
resolution is automated (`scripts/verify_corpus.py --resolve-doi`); fair-summary
review is not.

## 6. Safety

Layered, and none of the layers is sufficient alone:

1. **Pre-model keyword screen** (`safety.py`), bilingual, on every user message.
   Match → session closed, emergency signpost, no API call. Tuned to over-trigger.
2. **Model escalation flag** in the verdict schema for clinical-shaped pictures
   that no keyword catches. Rendered before the plan, not instead of it.
3. **Standing disclaimers** — the greeting says it is not a therapist; `/about`
   states that effects are population-level and mostly small to moderate.
4. **`/forget`** deletes everything for one user, immediately.

Open question for a human: whether jurisdiction-specific regional helpline numbers
should replace the generic 112 / findahelpline.com signpost. Doing that properly
means knowing the user's country, which means asking for it.

## 7. Data

SQLite, four tables: `users`, `sessions`, `turns`, plus commitments stored as JSON
on the session. State is persisted per turn, so a restart mid-interview resumes
rather than losing answers.

Transcripts are personal and sometimes distressing. Current posture: stored
unencrypted on the host, deletable with `/forget`, never sent anywhere except
Anthropic for inference. Before any real launch, decide on at-rest encryption and
a retention window.

Voice defaults to local transcription for the same reason — audio of someone
describing their worst month should not reach an extra vendor by default.

## 8. Cost model

Rough per completed interview at Opus 5 rates ($5/$25 per MTok), assuming a
~2.5k-token cached system prompt:

| | Calls | Input | Output | Est. |
|---|---|---|---|---|
| Probe | 4–7 | mostly cached | ~200 tok | ~$0.03 |
| Verdict | 1 | ~4k (evidence + transcript) | ~1.5k | ~$0.06 |
| **Total** | | | | **~$0.10** |

Local Whisper adds compute but no marginal API cost. So a free tier of a few
interviews per user is viable; a subscription is priced against perceived value,
not cost.

## 9. Roadmap

**Before launch**
- Verify all 28 citations (DOI + fair-summary review), flip `verified: true`
- Confirm the real product name; set `PRODUCT_NAME`
- Native-speaker pass on the Russian copy — it is fluent but unreviewed
- Decide retention and at-rest encryption

**Next**
- The check-in loop. Copy already promises it, `past_commitments()` and PTB's
  `JobQueue` are in place, the job is not written. Monitoring progress has good
  evidence behind it (`change.harkin2016`) so this is not just retention theatre.
- An eval set: 20–30 realistic transcripts, scored on whether the verdict names
  the right upstream domain and whether the action is genuinely small. Without
  this, prompt changes are guesswork.
- Corpus expansion, editorially, with `verified: true` from the start.

**Later**
- Embedding-based citation selection once the corpus outgrows the prompt
- Postgres + webhooks for multi-instance
- Repeat-session memory: the second interview should know what the first one said

## 10. Open questions for a human

1. **Product name.** "my boot, my way" came through a voice transcript garbled.
2. **Brutality calibration.** The prompt currently forbids validation openings and
   requires naming the avoided thing. Whether that lands as *honest* or as
   *unpleasant* is an empirical question about real users, not a prompt question.
3. **Russian as the primary market?** Both languages work; if RU is primary, the
   corpus should probably include Russian-language research, and the escalation
   copy should point at Russian services.
4. **Is one interview a product, or is the check-in loop the product?** The
   current build treats the interview as the deliverable. If retention is the
   business, the loop is not a nice-to-have and should be built next.
