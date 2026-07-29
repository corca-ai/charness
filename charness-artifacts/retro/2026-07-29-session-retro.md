# Session Retro
Date: 2026-07-29

## Context

A week-audit of the last 161 commits (a 5-lens dynamic workflow, each lens
adversarially challenged) reported that the repo's biggest regression was
operator-facing: five of the last twelve releases published a one-line body, and
one of them was the release whose notes amended an earlier release's wrong
migration instruction. This session closed the recurrence path at the
release-publish boundary. What matters next is that the escape is shut and the
damage is deliberately NOT repaired — the owner declined backfill outright, so
the wrong instruction stands on the public releases permanently.

## Window

`214a1561..f12d78ad` — 4 commits. Two arms added to the release-publish
narrative audit, two dead guards removed, critique re-bound, handoff updated.

## Evidence Summary

- The premise was reproduced, not inherited from the audit: `gh release view`
  body line counts across twelve tags, and `charness-artifacts/release/2026-07-26-v2.11.0-notes.md`
  present in-tree while the published body was 83 bytes.
- Both arms were verified against that live state before any fixture existed.
- `bash scripts/run-quality.sh`: 83 passed / 0 failed, 183s (three full runs).
- `check-changed-line-mutation-coverage`: false-green pre-commit (it warned so
  itself), BLOCKING on three lines post-commit, PASS after their repair.
- Bounded reviews: 2 rounds, 3 reviewers, 220k subagent tokens.
- Reviewer boundary: round 2 `verdict: clean`, drift 0. Round 1 NOT proven —
  see Waste.
- Closeout telemetry: 4 recurring waste items, `over_slice` at 37 occurrences /
  peak run 4 — pre-existing and not attributable to this session.
- Narrative-only on cost: the adapter declares no `metrics_commands`, so no
  token/turn efficiency claim is made here beyond the subagent count above.

## Waste

- **Three defects in this slice were found by RUNNING something, not by reading
  it — and two of them were in my own repairs.** Round 1 found the arm-2 ordering
  bug and the dash-separated naming miss; round 2 found that round 1's own repair
  had pinned the boilerplate URL to GitHub's shape, sending every other host's
  empty body back to `clean` — the exact verdict the five escaped releases got.
  A test fixture then caught the bounded-substring search matching
  `v3-2-1-notes.md` for target `2.1`. Each repair round shipped the class it
  repaired; the discriminator only stopped regressing when it moved from
  boundary-anchored searching to token equality, which has no boundary to get
  wrong. Cost: three extra mutate/sync/verify cycles.
- **I wrote a test asserting exhaustiveness over a directory it never read.** It
  was named `..._matches_every_naming_shape_this_repo_uses` and enumerated four
  hand-sampled shapes; `charness-artifacts/release/` held a fifth
  (dash-separated, used three times). That test is the direct reason the
  false-PASS shipped to round 1 rather than being caught at authoring. It globs
  the live directory now.
- **I ran the changed-line gate before committing, where its verdict is a false
  green, and it told me so in its own warning.** The recent-lessons digest
  already carries "read the `reason`, not the exit code" from the prior session.
  Running it in the wrong order cost one full gate cycle and nearly shipped two
  dead guards.
- **I verified the round-1 reviewer boundary after my own repairs had landed**,
  so the fingerprint could not distinguish reviewer mutation from parent
  mutation. Snapshot was taken correctly; the verify was sequenced wrong. Round 1
  is therefore recorded with the weaker structural claim (the `bounded-reviewer`
  type exposes no write tool) rather than the observation the mechanism exists to
  make. Round 2 was sequenced correctly and came back clean.
- **Four serial validator rejections on the critique artifact** (`bin`,
  `evidence`, `action` enum values, then a stale binding) because I hand-authored
  instead of starting from `scaffold_critique_artifact.py` — which the validator's
  own hint names. Same for the handoff: three trim cycles against the length cap
  and one rejected version literal, all of which `check_doc_authoring_preflight.py`
  reports up front.

## Critical Decisions

- **Scoped the slice to the recurrence path, not the damage.** The owner declined
  backfill; the alternative (writing four release bodies from commit logs, months
  after the fact, with no contemporaneous verification) would have produced
  operator-facing prose with weaker provenance than the silence it replaced.
  Constrains later work: the wrong migration instruction is permanent.
- **Refused to decide what a filename cannot settle.** `v1.2.3-rc1-notes.md` and
  `v1.2.3-public-notes.md` are the same shape after the version. The blocker names
  every candidate and picks none — a forced question, which is what P5 permits,
  rather than the declared answer round 1 caught it handing out.
- **Did not require notes to exist at all.** That is a contract change for
  consuming repos, so the four releases with no draft on disk are still
  publishable. Recorded as a named non-claim in the critique and handoff rather
  than left implied.
- **Removed the dup-ratchet family instead of classifying it.** The audit had just
  measured that gate at 182/182 `intentional` with `fixable_ceiling: 0` — a review
  that only absorbs. `_display_path` genuinely duplicated
  `control_plane_lib._manifest_path_for_payload`, so it defers to the canonical
  `path_portability_lib.repo_relative` via `load_repo_module_from_skill_script`.
  Only the second family (a two-line `if not X: return []` shared by seven
  unrelated functions) was classified, with a reason a reader can check.
- **Deleted the dead guard rather than finding a way to reach it.** `Path.glob`
  swallows the scandir error, so `except OSError` was unreachable and the behavior
  it implied (a handled unreadable directory) was false. The real behavior — silent
  fail-open indistinguishable from "this repo drafts no notes" — is stated as a
  non-claim instead.

## Trends vs Last Retro

- The prior retro's checklist item "guard the irreversible entrypoints, not the
  inner writes" is the same shape as this slice: a form check at an irreversible
  boundary. That lesson transferred and was applied without being re-derived.
- **"A lesson that ships as prose only has not shipped"** recurred, against me.
  "Read the `reason`, not the exit code" is in the digest I read at session start,
  and I still ran the changed-line gate pre-commit. Prose in a digest did not
  change the order I ran commands in; the gate's own inline warning did.
- The prior session's repeat trap `guard-adjacent-to-action` gains a third
  instance: a guard placed where the failure it names cannot occur.

## Expert Counterfactuals

**Engelbart (system-improving-itself; briefed by the planner).** Treat (H + LAM +
T) as one unit — design the tooling alongside the capability. Applied here, the
counterfactual is sharp: **the mechanism that catches dead guards already exists
and is blocking, and I ran it in the order that makes it lie.** Engelbart's move
is not "remember to commit first"; it is to notice that the T-loop has a
false-green window and close it in T, not in memory. The gate already knows it is
in that window — it emits the warning naming the uncommitted pool files. What it
does not do is refuse. A `--refuse-unestablished`-style arm on the pre-commit
invocation would have made the false green unavailable rather than merely
labelled, and this session would have paid one cycle instead of two. The same
reasoning covers the round-1 boundary verify: the fingerprint helper knows when a
verify is being run against a tree the parent has since written to, and could say
`parent-attributed` (it has that verdict) instead of leaving the sequencing to me.

**Ousterhout (deep modules / define errors out of existence).** The naming
discriminator regressed three times because each repair added a boundary rule to a
substring search: dotted-only → dot-or-dash → false match on `v3-2-1`. Ousterhout's
move is to change the representation so the error class cannot be expressed:
compare whole version tokens for equality and there is no boundary to widen. That
is what finally stopped it, and it also retired a pre-existing bug (`v14` matching
every dated filename) that no reviewer had raised. Reaching for it at repair 1
rather than repair 3 would have saved two cycles. Generalizes: **when the second
fix to a matcher is another boundary rule, change what is being compared.**

## Sibling Search

Transferable pattern: *a guard whose test passes for a reason other than the one
it names* — specifically permission-based fail-open tests.

- same layer: `tests/quality_gates/test_current_pointer_writes.py:742`,
  `tests/quality_gates/test_seed_fixture_budget_gate.py:653`,
  `tests/quality_gates/test_helper_provenance_guard.py:561` | decision: intentional
  boundary — no same waste | proof: read all three; each chmods a FILE and then
  READS it, where the permission genuinely raises, unlike a directory `glob` which
  swallows the scandir error. Two also carry a root guard (`os.access` skip,
  `skipif geteuid() == 0`). The repo's existing pattern was correct; this slice's
  test was the deviation, and it now carries the same root guard.
- abstraction up: `check-changed-line-mutation-coverage` | decision: same waste,
  fix now — fixed by removing the guard, not the gate | proof: the gate DID catch
  both dead guards; it is the mechanism for this class and it works. The gap is
  its pre-commit false-green window, which is the Engelbart counterfactual above
  and is now the first `Discuss` bullet in the handoff.
- specialization down: other `except OSError` arms in this slice | decision: same
  waste, fix now | proof: the slice had exactly one; removed. `find_drafted_notes`
  now has no exception handling at all.
- mental-model siblings: `except OSError` around directory iteration elsewhere in
  `scripts/` and `skills/public/` | decision: valid follow-up outside the slice |
  proof: 141 `glob(`/`iterdir()` call sites; only
  `skills/public/quality/scripts/standing_test_economics_lib.py:41` pairs one with
  an OSError guard, and its `iterdir()` is assigned before iteration, so unlike
  `glob` it may genuinely raise — not confirmed either way in this session |
  follow-up: deferred docs/handoff.md `## Discuss` dead-guard bullet

## Next Improvements

- workflow: **commit before reading a changed-line verdict, always.** The gate is
  a false green over uncommitted pool files and says so; the order is not
  optional. Recorded in the handoff `## Current State` so it is a pickup fact, not
  a remembered one.
- workflow: **verify the reviewer boundary at review return, before making any
  repair.** A verify run after parent writes cannot attribute drift, which
  downgrades an otherwise-clean round to a structural claim.
- capability: **make the pre-commit changed-line invocation refuse rather than
  warn**, per the Engelbart counterfactual. The gate already computes the
  uncommitted-pool condition and emits it; converting that to a refusal in the
  pre-commit path removes the false-green window instead of labelling it. Not
  filed as an issue this session — it belongs with D40's owner decisions.
- capability: **start critique and handoff artifacts from their scaffolds.** Four
  serial enum rejections and three length-trim cycles were all pre-announced by
  `scaffold_critique_artifact.py` and `check_doc_authoring_preflight.py`.
- memory: **when the second fix to a matcher is another boundary rule, change what
  is being compared.** Three regressions in one function, ended by moving from
  substring search to token equality.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-07-29-session-retro.md
