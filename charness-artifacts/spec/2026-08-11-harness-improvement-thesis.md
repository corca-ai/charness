# Harness-improvement thesis — what actually carried a lesson, and what blocks autonomy

Date: 2026-08-11. Operator-directed: the thesis had no artifact and was narrowed to two
items before it got one. This is the home for those two, and for nothing else.

The evidence is one headless observation run (`claude -p "handoff"`, Opus 5, isolated
worktree at `369f6d7b`, 82 turns, 7m18s, $5.40; patch preserved at
`../audit/2026-08-11-pickup-deletion-experiment.patch`) plus a direct re-reading of the
digest that run consumed.

## Item 1 — the memory digest is lossy, but not where the run said it was

**The observation run's own conclusion does not survive its own evidence.** It concluded
that "the memory digest is lossy and the handoff plus the spec artifact did the work",
crediting the run's correct consumer-searching behavior (H2) to the handoff's first line
and to the recorded consumer greps. That conclusion is not established, because the
digest carried the same lesson.

Verified rather than assumed:

- `git diff --stat 369f6d7b HEAD -- charness-artifacts/retro/recent-lessons.md` is empty,
  so the digest read here is byte-identical to the one the run read.
- The digest's `## Next-Time Checklist` slot 4 carries, verbatim: *"a removal
  proposal must CARRY its consumer search — the grep and what it returned — so a proposal
  without one is visibly incomplete."* That is precisely the H2 behavior.

So the run's trace **cannot separate the two channels**. Both carried the lesson; the run
observed the behavior once. A claim that one channel did the work needs a run where only
one channel carries it, and no such run exists.

The handoff's Workflow Trigger compounded the error by naming the wrong section: it says
"the digest's **4 trap slots** dropped the two sharpest lessons", but those lessons come
from a retro's `Next Improvements` and route to the CHECKLIST slots, not to
`Repeat Traps`.

### What the digest actually dropped, and the real defect

The 2026-08-11 retro emitted five `Next Improvements`; `LESSON_DIGEST_SLOTS`
(`scripts/recent_lessons_lib.py:42`) allows four. Two survived. The two dropped were:

- *verify a reviewer's factual claim through a channel the reviewer lacked, or label it
  unverified*
- *run the adversarial pass before the operator asks*

**Both dropped lessons were then violated in the very next session.** The 2026-08-11
pickup session forwarded a subagent's history claim ("one committed revision dropped a key
without decrementing the count") into a shipped code comment and a test docstring without
checking it, while holding `git` — the exact first lesson. A bounded reviewer caught it and
demanded the SHA; the claim turned out TRUE (`7a43c8a4` records 151 against 150 keys), so
the cost was a review round, not a falsehood. That is the strongest available evidence that
the selection policy dropped the load-bearing items: recency and recurrence ranked a
content-free line above a lesson that was about to fire.

Because the fourth surviving slot was, verbatim:

```text
- **memory** — This retro plus the recent-lessons digest. (source: ...)
```

A slot spent on a line that instructs nothing. The digest is not merely lossy — it is
lossy while spending scarce capacity on non-lessons.

### The narrow, actionable finding

Two changes are available and they are independent:

1. **Refuse content-free lessons a slot.** A `memory:` disposition whose body names only
   the retro and the digest is bookkeeping, not a lesson. Filtering that class costs one
   predicate in `recent_lessons_lib` and frees a slot in every digest since.
2. **Give a session a way to mark a lesson decisive**, so a lesson that fired can outrank
   recency. Today `advisory recency half-life 45 days plus recurrence boost` is the whole
   policy, and a first-occurrence lesson from the session that just ended competes against
   1,939 candidates on recency alone.

**Non-claim:** nothing here establishes that the handoff channel is better than the digest.
It establishes that the run cannot tell them apart, and that the digest's slot policy spent
one of four slots on nothing.

## Item 2 — autonomy has a precondition, not a harness defect

The headless run could not reach its own stop gate: under `--permission-mode acceptEdits`,
`python3` and most `git` invocations returned "This command requires approval", so it could
not run `sync_root_plugin_manifests.py`, pytest, or the gate. It reported the tree as
inconsistent and unverified, refused to hand-mirror ("unverifiable hand-mirroring is how
drift gets committed"), and named what it still owed.

That behavior is correct and is the finding: **the repo's contract says code written is not
a stop state, and the default permission posture blocks the very commands the contract
requires.** Any autonomous run of this repo hits that wall.

It is a PRECONDITION, not a defect to file: `--dangerously-skip-permissions`, which the
operator already uses interactively, resolves it. The durable content is that a headless
invocation of this repo without that flag cannot produce a proven slice, only an honest
refusal — and that the refusal is the correct outcome, so no repair is owed to the harness.

**Do not file this as an issue.** It was considered and declined on exactly this reasoning.

## What this artifact does not claim

- No A/B run isolating the digest channel from the handoff channel was performed. Item 1's
  conclusion is a refutation of the earlier claim, not a replacement claim.
- The two slot-policy changes in item 1 are proposals; neither is implemented, and neither
  has been measured against the 1,939-candidate index.
- The observation run's patch was produced without a mirror sync, without a test run, and
  without the review the change owed. It is evidence about agent behavior, not a shippable
  change, and the work it sketched was re-done under verification rather than applied.

## References

- [Recent lessons digest](../retro/recent-lessons.md)
- [2026-08-11 session retro](../retro/2026-08-11-session-retro.md)
- [Umbrella class disposition plan](./2026-08-10-umbrella-class-disposition-plan.md)
- [Pickup deletion experiment patch](../audit/2026-08-11-pickup-deletion-experiment.patch)
