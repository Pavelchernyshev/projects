# Setup guide: paste into inbox, wake up to structured notes

A one-time setup, about 30 minutes. After it, your loop is:

> paste something into `inbox/` from any device → forget about it → next morning
> it is filed, summarised, tagged, and linked, with a digest telling you what was
> done and what needs your call.

Read this in Obsidian once the vault is open — it lives at `docs/setup-guide.md`.

---

## First, one correction

**There is nothing to "connect" between Claude and Obsidian.** No login, no
integration, no API key. Your Obsidian account exists only for billing Sync and
Publish; it has no third-party access at all.

Obsidian is a text editor that reads a folder on your disk. Claude is a program
that reads and writes files in that same folder. Neither knows the other exists.
That is the whole design, and it is why nothing here can be taken away from you.

**What actually connects them is git.** GitHub is the meeting point:

```
   your phone / laptop                    GitHub                 Claude
   ┌──────────────────┐                ┌──────────┐         ┌──────────────┐
   │ Obsidian         │  Obsidian Git  │ second-  │  clone  │ daily Routine│
   │ paste to inbox/  │───── push ────>│  brain   │<────────│ /inbox-daily │
   │                  │<──── pull ─────│  (private)│── push ─>│              │
   └──────────────────┘                └──────────┘         └──────────────┘
```

Your paste has to reach GitHub for the Routine to see it. That is what step 4
sets up, and it is the step people skip.

---

## Step 1 — Create the private repo

Go to [github.com/new](https://github.com/new):

- **Name**: `second-brain`
- **Private** — tick this, it is your personal knowledge
- **Do not** tick "Add a README" — the repo must be empty

Click Create. Do nothing else there.

Then tell Claude in this session: **"repo is created"**. The vault gets pushed
to it, already containing your Gabor Maté transcript, the seeded notes, and
every script.

---

## Step 2 — Get the vault onto your laptop

Install [GitHub Desktop](https://desktop.github.com) if you do not already use
git from a terminal. It is the least painful option and it handles the
credentials for you.

- File → Clone repository → `Pavelchernyshev/second-brain`
- Pick a location you will remember. `~/Documents/second-brain` is fine.

If you prefer the terminal:

```bash
cd ~/Documents
git clone https://github.com/Pavelchernyshev/second-brain.git
```

---

## Step 3 — Open it in Obsidian

1. Open Obsidian → **Open folder as vault**
2. Choose the `second-brain` folder you just cloned
3. Trust the vault when asked

It already looks right: the graph is coloured by type, new notes default to
`inbox/`, folders are laid out. Nothing to configure.

Enable these in **Settings → Core plugins** (all built in, no downloads):
Backlinks, Outgoing links, Templates (set folder to `templates`), Tag pane,
Properties view, Daily notes (folder `daily`, format `YYYY-MM-DD`).

---

## Step 4 — The piece that makes it automatic

Your paste must reach GitHub, or the Routine has nothing to read. This plugin
does that.

**Settings → Community plugins → Turn on community plugins → Browse → "Git" →
Install → Enable.**

Then in its settings, set:

| Setting | Value | Why |
|---|---|---|
| Vault backup interval (minutes) | `10` | Auto-commits your pastes |
| Auto push after commit | **on** | Sends them to GitHub |
| Auto pull interval (minutes) | `10` | Brings the Routine's work back |
| Pull updates on startup | **on** | Fresh notes when you open Obsidian |
| Commit message | `vault backup {{date}}` | Anything you like |

That is the loop closed. You paste, it pushes within 10 minutes, the Routine
picks it up on its next run, pushes the result back, and your Obsidian pulls it.

**On phone and tablet:** do not install Git there — it is unreliable on mobile.
Use **Obsidian Sync** (the paid one) between your devices, and let the laptop be
the only machine talking to GitHub. Your laptop needs to be on and Obsidian open
for the push to happen — if it is closed for three days, your pastes wait three
days. That is fine, nothing is lost.

---

## Step 5 — Turn on the daily Routine

Tell Claude: **"set up the daily inbox Routine"**. It gets created against your
new repo, scheduled for whatever time you name (something after you stop reading
for the day works well — 5am means it processes yesterday).

What it does each night, in order:

1. Pulls your latest pastes
2. Files each one into `sources/` with a permanent citation key
3. Writes a **summary**, **key insights**, and **tags** on each
4. Creates notes for ideas that clear the quality bar
5. Writes a **digest** in `daily/YYYY-MM-DD.md`
6. Pushes it all back

**Two things it will never do unattended:** rewrite a note you already have, or
delete anything. When a new source contradicts or should change an existing
note, it writes a proposal into the digest and leaves the note alone. You decide
in the morning. That review gate is deliberate — it is the difference between a
vault that compounds and one that fills with confident mush nobody trusts.

---

## How you actually use it

### Pasting things

Anything goes into `inbox/`. No format required, no naming convention, no
frontmatter. The daily pass works it out.

| What you have | What to do |
|---|---|
| An article | Obsidian **Web Clipper** browser extension → set destination `inbox/` → one click |
| A YouTube talk | Copy the transcript, paste into a new file in `inbox/`, put the URL on the first line |
| A book excerpt | New file in `inbox/`, paste it, first line: `Book Title — Author, p.140` |
| A podcast | Same as YouTube. Timestamps are useful, keep them |
| A thought of your own | New file in `inbox/`, just write it. Or better, put it in today's daily note |
| Something on your phone | Share sheet → Obsidian → append to a file in `inbox/` |

The only thing worth including is **where it came from** — a URL, a book title,
an episode name. That is what makes it citable later. Everything else the daily
pass handles.

### Your morning

Open Obsidian. Today's daily note has the digest:

- **Filed** — what came in
- **Notes created** — what earned a place in the graph
- **Candidates not written** — ideas judged too thin. Skim; if one was worth
  keeping, say so
- **Proposals needing your call** — the only part that needs you

Reply to proposals by asking Claude, e.g. *"do the first proposal"*.

### The one habit worth having

Notes have a `## My take` section. Claude never writes there, ever.

Whatever you put in it becomes the raw material for drafting later — it is how
`/draft` writes in your voice rather than producing a competent summary of the
internet. Two lines of your own opinion on a note is worth more than ten
AI-written notes, and it is the single thing that keeps this vault yours.

---

## When you want something out of it

Open a terminal in the vault folder and run `claude`:

```
/ask what do I have on trauma and childhood?
/draft article "why late people aren't disorganised"
/draft social "one idea from the Gabor Maté episode"
/process S-20260803-therapy-session-dr-gabor-mate  focus on the ADHD part
/lint
```

`/draft` writes with citations that resolve to real files, and tells you how much
of the piece is your thinking versus sourced material. Drafts go in whichever
language your audience speaks; the notes stay English so the graph stays whole.

Before drafting seriously, put two or three things you have published into
`voice/samples/`. Until then, drafting will say the voice is unverified rather
than fake it.

---

## Troubleshooting

**Nothing happened overnight.** Check `inbox/` on GitHub in the browser. If your
file is not there, the Obsidian Git plugin did not push — open Obsidian on the
laptop and wait ten minutes, or hit the command palette → "Git: Commit and push".

**"Merge conflict" in Obsidian Git.** You edited a file on the laptop that the
Routine also changed. Ask Claude to sort it out; do not hand-resolve it.

**The digest says a source was too long to read fully.** It says so honestly
rather than skimming and pretending. Ask Claude to process that one interactively.

**You want to pause the automation.** Say "pause the inbox Routine". Your pastes
keep piling up in `inbox/` harmlessly.

---

## What this costs you

Nothing per day. Pasting is a share-sheet tap or a Web Clipper click.

The pile in `sources/` is allowed to grow without limit and is never a to-do
list. `/lint` reports its size as information, and is explicitly forbidden from
calling it a backlog. Four hundred unprocessed sources and forty good notes is
the system working, not falling behind.
