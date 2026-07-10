# Fresh-Eye Resolution Critique — #428 Reviewer Boundary Enforcement

Date: 2026-07-10
Issue: [#428](https://github.com/corca-ai/charness/issues/428)
Fix commit: `5d894aa1` (critique-driven follow-up `8145629a`)
Goal: `charness-artifacts/goals/2026-07-10-428-reviewer-boundary-enforcement-release.md`
Fresh-Eye Satisfaction: parent-delegated

## Reviewer Tier Evidence

- Requested tier: high-leverage (issue-closeout depth)
- Requested spawn fields: subagent_type=bounded-reviewer, model inherited
  from the parent session (no override)
- Host exposure state: host-defaulted
- Application state: not-confirmed — the spawn was accepted, but the probe
  showed the envelope's tool restriction did not bind mid-session (spawn
  metadata echoed the spawn name as agentType), so the reviewer's read-only
  conduct was proven by the rail-1 fingerprint (verify clean, drift empty)
  plus a transcript tool-use audit, not self-report.

## Decision Under Review

Whether resolving #428 with the shipped two-rail enforcement (portable
worktree+index fingerprint; Claude host read-only reviewer envelope) prevents
the recorded violation class from recurring, and whether closing the issue in
the pending release-bundle carrier is honest.

## Recurrence Walkthrough

- Violations 1 and 3 (staged+committed content; no-write-brief doc edit):
  prevented where the envelope binds; detected everywhere by rail-1 drift with
  concrete paths, provided the parent runs snapshot/verify. Closed.
- Violation 2 (undelegated child spawn): rail 1 cannot see a zero-footprint
  spawn; prevention rests entirely on rail 2, whose live binding is unproven
  this session (mid-session probe: `TOOL-EXECUTED`). Any write the child makes
  is still caught by rail 1, so silent closeout-commit corruption stays
  covered even here.

## Verdict

CLOSE-WITH-EDITS. The capability is shipped and rail 1 is live-proven; the
close comment must carry per-acceptance-line honesty:

1. Lines 3-4 met and live-proven (drift JSON; fingerprint dogfooded around
   this critique itself).
2. Line 1 detection met and proven; the literal "cannot" prevention rests on
   the rail-2 envelope, deferred to a fresh-session binding proof.
3. Line 2 (spawn denied) rests entirely on the unproven envelope; no automated
   spawn-denial regression exists.
4. Line 5 scoped: the 12 regression tests cover the git-state violation class;
   the undelegated-spawn sub-class relies on rail 2.

## Findings And Dispositions

- BLOCKER (honest-close): close comment must map the rail-2 non-claim to
  acceptance lines 1-2 and scope line 5 — applied in the closeout carrier
  draft.
- SHOULD-FIX: fresh-session envelope-binding proof + spawn-denial regression —
  tracked issue [#430](https://github.com/corca-ai/charness/issues/430).
- SHOULD-FIX: rail-1 invocation not wired at the reviewer-spawn step of
  quality/release/issue/critique SKILL.md (portable installs lose the
  AGENTS.md bullet) — tracked issue
  [#431](https://github.com/corca-ai/charness/issues/431).
- NIT: after a quarantine, re-run verify to full-clean (drift list is
  fail-closed, not exhaustive) — applied to the Enforcement section in
  `8145629a`.

## Boundary Ownership

- Verdict: escalated-to-issue-spec

The enforcement mechanism is owned correctly by the producer surfaces (the
shared reference's Enforcement section and `skills/shared/scripts/`), but the
consumer surfaces that spawn reviewers (quality/release/issue/critique
SKILL.md) do not yet invoke rail 1 at their spawn steps; that
producer/consumer seam is escalated as tracked issue
[#431](https://github.com/corca-ai/charness/issues/431) rather than patched
ad hoc inside this closeout.

## Non-Claims

- No claim that rail 2 binds on this host mid-session; the probe showed it did
  not, and fresh-session proof is deferred (#430).
- No claim of Codex-host enforcement: `.claude/agents/` is Claude-host-local
  and unpackaged; rail 1 is the floor elsewhere.
- Gitignored paths are outside fingerprint scope by design; a writing reviewer
  on an envelope-less host could tamper the default snapshot — pass `--out`
  outside the reviewer-reachable tree when that matters.
