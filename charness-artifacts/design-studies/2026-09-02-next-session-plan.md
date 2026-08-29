# Next-session plan: consumer-facing defects first, then the surfaces that let them sit

> Written at the close of the 2026-08-29 session, with the operator.
> Supersedes `2026-09-01-next-session-plan.md`, whose Step 1, Step 3, and every
> deferred handoff it inherited are now closed.

## Read this FIRST, and read the files, not this summary

This plan cites inputs. **Open them before planning.** The single largest waste of
the last session was re-deriving measurements, decisions, and a fully-diagnosed
follow-up that a prior retro already held, because the plan named its inputs in
prose and prose citation is not a mechanism. If you find yourself measuring
something, grep the retro corpus for it first.

Required opens, in this order:

1. `charness-artifacts/retro/purpose-and-the-unread-input.md` — the last session's
   retro. Its `Waste`, `Sibling Search`, and `Next Improvements` are this plan's
   backing.
2. `charness-artifacts/retro/2026-08-29-detector-blind-class.md` — the retro
   BEFORE that. Read it too: last session skipped it and paid for it.
3. `docs/design-north-star.md` — specifically the `Purpose` section, which is new.
   Every item below is ranked by it.
4. `charness-artifacts/retro/recent-lessons.md` — but know its limit: it sources
   24 of 419 corpus files and did NOT pick up the retro written minutes before
   this plan. Do not treat it as the corpus.

The ranking rule, from the north star's Purpose: **charness exists to reduce
rework in the repositories that CONSUME it.** A defect a consumer hits outranks a
defect this checkout hits, however green this checkout measures.

## Step 0 — FIRST: compress `AGENTS.md` to ceal level, then gate it

Highest priority in this session. Do it before the issues below.

`AGENTS.md` is 48 lines / ~2.6 KB. `../ceal/AGENTS.md` is 23 lines / 1.3 KB and
`../craken-agents/AGENTS.md` is 20 lines / 1.1 KB. The file's own second sentence
says *"Keep this file short: it routes to the document that owns the question; it
is not a second operating manual"*, and its `## Make changes` section is exactly
that second manual — worktree policy, lane selection, parallel shape, and
canonical-surface rules, ~20 lines of it, in the file that forbids them. ceal
states the same principle as a rule: *"`AGENTS.md` is the first-read router; host
mechanics belong in the linked host adapter."*

Two parts, both required:

1. **Compress to ceal level.** Target 20–23 lines. `## Make changes` moves to the
   owner pages it already links (`.agents/codex-host.md`, `.agents/claude-host.md`,
   `docs/development.md`, `docs/operating-contract.md`) — MOVE the content, do not
   delete it, and check each destination already covers it before dropping a line.
   `## Repository map` largely duplicates `docs/index.md`; keep only what the
   index cannot carry.
2. **Wire a pre-commit gate.** A staged change to `AGENTS.md` (and its `CLAUDE.md`
   symlink) is REFUSED and requires the operator's explicit approval to proceed.
   ceal has the rule in `docs/agent-operating-rules.md` and never mechanized it —
   *"this is a workflow boundary, not a size ratchet or approval-receipt gate"* —
   and the rule alone did not hold: this file was edited twice without approval in
   the session that wrote this plan, and only the operator caught it.
   `.githooks/pre-commit` is the home; the repo's existing escape idiom is an
   env-var bypass (`CHARNESS_ALLOW_STAGED_REVERSION`,
   `CHARNESS_ALLOW_PARTIAL_STAGE`, `CHARNESS_ALLOW_FOREIGN_HELPER`), so follow it
   rather than inventing a receipt format. The point of the refusal is that an
   agent must STOP and ask; make the message say that.

Nothing today enforces either half: no gate bounds this file's size, and none
guards its modification. A search of current `scripts/`, `.githooks/`, and the
four recent "simplification" commits found no such guard present or deleted.

## Step 1 — The consumer-facing open issues

These are ranked above everything else because a consumer meets them. Check each
against code before believing its text; two of last session's severity readings
changed on contact.

- **#755 — reviewer capability non-claim digest invalidates delivery.** Filed
  from Ceal against 8.0.0: every reviewer returned substantive bounded-review
  JSON and delivery was rejected anyway, because model-authored
  `capability_non_claims` provenance had to match a launch envelope exactly. This
  is the consumer-facing shape of the class the last session spent itself on — a
  mechanism refusing on a question the worker was never able to answer. Highest
  rank: it blocks a paying path end-to-end, three times, on a canonical mode with
  no customization.
- **#750 — retro adapter cannot opt out of the recent-lessons projection.**
  `resolve_adapter.py:62` fills the default unconditionally, so a consumer repo
  cannot decline a surface it does not want. Small, and consumer-facing.
- **#731 — bounded-review friction; partial worker progress is not first-class.**
  Related to #755 in surface and in feel. Read them together before designing
  either.

## Step 2 — Read the inventory this session produced, then disposition it

`skills/public/quality/scripts/inventory_empty_scope_honesty.py --summary` reports
per detector what it says when it establishes nothing. Today: 129 detectors, 42
refuse, 48 are honest in prose only, 2 carry a machine-readable marker, 13 assert
success over a scope they never established, 16 could not be probed.

**The deliverable of Step 2 is a disposition of those 13**, not a new gate. For
each: is this the sanctioned discovered-empty pass, or the defect? The repo already
forbids this exact shape on one gate (`check_code_lengths`'s named arm) and
permits it on that same gate's discovered arm, so the answer is per-detector
judgment, not a sweep.

An inventory nobody reads is the cost the Purpose clause names. If Step 2 does not
happen, delete the inventory rather than keep it.

## Step 3 — The prose-honesty gate, per the operator's design

`check_regenerable_facts` is configured for `docs/**`, exempts nothing relevant,
runs clean, and misses. Its detector is *digit + space + an enumerated noun*.
Measured against five real phrasings from `docs/design-north-star.md`: one hit,
four misses — spelled-out numerals, unit suffixes (`17.6K lines`), hyphenated
compounds (`5.8K-test suite`), and nouns outside the list all pass.

The operator's design, to be built rather than re-litigated:

> The detector is heuristic. Accept false negatives. Surface it as a **pre-commit
> ADVISORY** on changes to `AGENTS.md`, `README.md`, and `docs/**/*.md`, and let
> an agent judge the flagged text against the warning's own stated rule, rather
> than widening the regex.

Do not widen the noun list. That is the enumeration this repo's own P3 rejects,
inside the gate that enforces prose honesty, on the page where P3 is written.

## Step 4 — Two carry-forward surfaces that failed while being used

Both found while persisting the last retro. Both are small and both cost real
work when they fire.

- **The retro scaffold and the persist helper disagree about the path.** The
  scaffold checks a DATED artifact path; the helper writes an UNDATED one. The
  scaffold reported the target empty, the helper overwrote a tracked retro from
  another session, and only a `git status` read caught it. One subject key, two
  paths.
- **The lesson memory loop is built in three parts and only one is wired.** The
  operator's design: a session START reads the ledger, every RETRO evaluates and
  updates it, and a QUALITY run promotes/retires. The spec is
  `charness-artifacts/spec/2026-08-13-lesson-evaluation-observability-contract.md`
  (Status: completed), whose entities are `lesson session`, `emission receipt`,
  `retro disposition`, and `continuity report`. Measured state:
  - **(1) session start — command EXISTS and works, wiring was missing.**
    `render_lesson_selection_preview.py --seed <id>` reads the *validated* ledger
    and selects 43 eligible lessons into recency / value / uncertainty buckets
    with each lesson's source artifact named. `AGENTS.md` pointed at
    `recent-lessons.md` instead. Wired in the session that wrote this plan; the
    remaining two are open.
  - **(2) retro evaluates and updates — MISSING.** The retro skill never writes
    the ledger and never records the spec's `retro disposition` line, and nothing
    asks it to. Ledger holds 43 lessons against a 419-artifact corpus.
  - **(3) quality promotes/retires — MISSING, and partly deleted.** No
    promote/retire concept exists in the quality skill, and ledger schema v8
    (`5a8b6baca`, *"Remove lesson lifecycle state and quality-run writes"*,
    2026-08-27) removed the lifecycle state together with the spec's
    session-emission snapshots and session-bound scoring. **The operator's
    reading is that this removal was a misread of an instruction to delete
    `recent-lessons.md`, not the lifecycle.** Read `5a8b6baca` before designing;
    restore from it if that reading holds.
  - **The Markdown projection was supposed to be migrated INTO the ledger and was
    not.** Both surfaces are live. #750 is the consumer-facing half: Ceal makes
    its ledger the sole lesson surface and cannot switch the projection off.
    Design #750 and this together — the question is which surface a reader is
    owed, not how to make the projection rank better.
- **`persist_retro_artifact.py` writes a lesson selection index that the repo's
  own checker then rejects.** After persisting a retro, the ledger preview refused
  with *"does not match what this repo's own code produces"*; rebuilding with
  `build_retro_lesson_selection_index.py --write` added 49 lines. Two writers, one
  artifact — the same shape as the scaffold/persist path mismatch above.
- **`validate_integrations.py` does not refuse a lock whose manifest is gone.**
  `integrations/locks/cautilus.json` survived the cautilus removal pointing at a <!-- reproduction-source -->
  deleted `integrations/tools/cautilus.json`; the validator reported 14 lock files
  validated and exited 0. Locks are gitignored local state, so this is not shipped
  drift — but it is a detector passing over a question it never asked, which is
  the class Step 2 dispositions.

## Step 5 — The release, if the above leaves room

8.0.0 remains prepared and unpushed; the hole the last plan named before it
(`_publish_and_finalize`) is closed — the closeout tail is now covered through the
path a release actually takes. 100+ commits are unpushed. This is deliberately
LAST: none of it is consumer-facing until it ships, and shipping it on top of
#755 would ship a known blocked review path.

## Deliberately not in this session

- **#748 / #749 / #744, the Rust migration.** The advantageous conversions are
  done; four Python owners deleted. The three that remain are Python for recorded
  reasons — consumer contract, measured-slower, and an acceptance bullet that
  requires Python. Do not reopen without a NEW measurement.
- **#753.** Untouched last session and not consumer-facing.
- **Arming anything built last session.** The Rust changed-line floor and the
  empty-scope inventory both ship unarmed on purpose. Arming is its own decision
  with its own evidence; the ratio-cap entry in the corpus is what happens
  otherwise.

## Working shape

- Consumer-facing repairs go to Codex lanes; the parent owns design, integration,
  and final verification.
- **Build `--scope` from a real search, not `ls <dir> | grep`.** Two of three
  lanes last session returned `invalid` because a needed test file lived in a
  subdirectory the scope never listed.
- **Run the FULL standing lane, including `--include-release-only`, before
  calling a production-surface change done.** It caught three violations last
  session that focused runs did not: a cross-module private import, a polyglot
  constant needing a boundary marker, and a skill-ownership overlap.
- Any proposal containing "faster / smaller / cheaper" carries its measurement in
  the same message.
- Before optimising a mechanism, ask what it is FOR. That question has been the
  operator's intervention in each of the last two sessions.
- `plugins/` is untracked. The mirror is regenerated by `charness init`/`update`
  and by the release version bump — NOT by pre-push. Regenerate derived surfaces
  after the last source edit:
  `python3 scripts/sync_root_plugin_manifests.py --repo-root .` and
  `./charness catalog refresh --repo-root .`.
