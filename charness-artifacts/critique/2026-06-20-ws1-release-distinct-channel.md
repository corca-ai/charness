# WS-1 Critique — Release Publish Non-terminality (rung-1 + rung-2 distinct channel)

Date: 2026-06-20
Slice: WS-1 of `charness-artifacts/goals/2026-06-20-north-star-phase4-boundary-non-terminality.md`
Concept lock: `charness-artifacts/spec/2026-06-20-phase4-boundary-non-terminality-concept.md` §2 + F2a
Scope: governing-surface edit (`release/SKILL.md`, `references/install-surface.md`) + a
release-publish behavior change (new rung-1/rung-2 floor before issue close) +
a public-skill validation review for the changed `release` and `quality` skills.

## What changed

Closed the WS-1 escape: `publish_release_execute.py:163`
`release_verified = (gh release view returncode == 0)` was the **only** post-publish
check gating the irreversible GitHub issue close — a single same-channel proxy
(*P4* re-examination failure). WS-1 adds, before `ensure_release_issues_closed` on
**both** the main and `--resume` publish paths:

- **rung-2 distinct-channel observer** (`confirm_release_via_distinct_channel`):
  confirms the published release through a channel distinct from `gh release view`
  — adapter `post_publish_distinct_channel_probe` shell command, else an HTTP fetch
  of the public release URL — recording a `confirmed` or a typed non-`verified`
  disposition (`not-confirmed`/`blocked-needs-capability`/`skipped`) into
  `payload.distinct_channel_verification` and the release artifact's
  `## Distinct-Channel Verification` section.
- **rung-1 presence floor** (`evaluate_release_distinct_channel`): refuses a
  *silent* close (missing record); a confirmation OR a typed disposition pass
  **equally** (F2a — presence, never an automated `confirmed ⇒ proceed` gate). The
  honesty of the verdict is the human rung-2 disposition review.

## Bounded fresh-eye critique — PASS (folded)

A bounded fresh-eye reviewer (distinct agent context, read-only in the shared
parent worktree) verified every invariant + adversarial angle **against the actual
staged code** (a distinct evidence channel — `git diff --cached` / `Read` /
`git show HEAD:` regression baseline / `git show :plugins/...` mirror fidelity /
independent `grep` of all `ensure_release_issues_closed` callers / read-only
`pytest` 45 passed), not a re-read of the spec. **Verdict: PASS, no blockers.**

CONFIRMED: (A1/F2a) issue-close advances on rung-1 record-**presence** only —
`evaluate_release_distinct_channel(payload)["ok"]` at `publish_release_execute.py:196`
and `publish_release_resume.py:167`, where `["ok"] = isinstance(record, dict) and
bool(status.strip())` — never on `confirmed`; the E2E
`test_publish_release_records_distinct_channel_disposition_and_still_closes` proves
a `not-confirmed` verdict still closes the issue. (A3) the observer structurally
cannot re-read `gh release view` (no `backend`/`run` handle; only `run_shell`/
`http_probe`). (A4) exactly the 2 `ensure_release_issues_closed` callers each carry
the floor; the resume path was a parallel escape now closed and net-strengthened.
Additive: the line-163 proxy + `if not release_verified` guard are byte-identical
to HEAD. The new `skipped` attention-state is declared honestly (recorded,
artifact-rendered, render-not-declare). Seeded tests are non-tautological
(silent ⇒ `SystemExit` before close; disposition ⇒ close proceeds).

Over-worries explicitly dismissed (NOT folded): adding a `release_verified`
hard-fail to the resume path (pre-existing, out of WS-1 scope); a status-whitelist
on the presence floor (would re-create the #386 self-classification green — the
floor MUST stay presence-only); the unused `DISTINCT_CHANNEL_STATUSES` constant
(documents the vocabulary; the floor must not consult it).

## Public-skill validation decision (cautilus `next_action: none`, ask-before-run)

The Cautilus planner reported `run_mode: ask`, `next_action: none` — no live
evaluator run (eval-only/ask-before-run contract). Deterministic validation +
this recorded fresh-eye scenario review own the closeout. The two changed public
skills:

- **release** — a behavior addition (the rung-1/rung-2 floor) internal to the
  publish path; the skill's *consumer contract* (routing prompt → `release` →
  `charness-artifacts/release/latest.md` → maintainer-reviewable) is unchanged.
  Dogfood case refreshed (`reviewed_on` + an observed-evidence line for the floor).
- **quality** — the only touch is a **data declaration** in
  `references/attention-state-visibility.json` (the new `skipped` state); no
  `quality` behavior/contract change. Dogfood case unchanged.

Closeout proceeds with `run_slice_closeout.py --ack-cautilus-skill-review`.

## Non-claims (Honest Proof Discipline)

- **No live GitHub release this run.** Proof is local + seeded fixtures (a fake
  distinct-channel probe + injected HTTP fetcher; zero real network). A live
  release exercising these floors is operator-approved + phase-scoped (the goal's
  Operator Decision Queue); not run here.
- The HTTP-fetch *default* path is unit-proven via an injected fetcher, not
  against a real public release URL (that is the deferred live proof).
