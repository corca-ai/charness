# Achieve Goal: Resolve #354 with updated nose quality scan and public-doc audit

Status: draft
Created: 2026-06-11
Activation: `/goal @charness-artifacts/goals/2026-06-11-354-nose-quality-public-doc-audit.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: before activation.
- Next action: activate with
  `/goal @charness-artifacts/goals/2026-06-11-354-nose-quality-public-doc-audit.md`.
- Verification cadence: cheap deterministic checks at commit boundaries;
  higher-cost or fresh-eye proof at slice boundaries; final broad/live proof at
  closeout.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

Resolve the next Charness maintenance bundle as one auditable goal:

- ensure the latest available `nose` install/update path is in use, then run a
  quality scan with `nose` available;
- audit public docs and reusable public guidance for hard-coupled issue numbers,
  release-specific references, or similar coupling that should not live in
  portable guidance;
- improve the shared bounded subagent reviewer effort policy so routine
  fresh-eye reviews do not silently inherit high effort when a narrow
  medium-effort packet would suffice;
- resolve GitHub issue #354 by starting from the latest issue comments and the
  scheduled mutation run mechanics, not by treating the red run as a flake.

## Non-Goals

- Do not start #184 product metrics ideation in this goal; keep it as a separate
  operator decision after #354 and the quality scan close.
- Do not perform a new release unless the #354 fix or public-doc audit changes
  require it and the operator explicitly approves a release phase.
- Do not close #354 from mutation-score improvement alone; the current blocking
  changed-line coverage signal must be explained or fixed.
- Do not rewrite historical release notes or retro artifacts merely because
  they cite issue numbers; this audit targets reusable public guidance and
  operator-facing docs where coupling would mislead future consumers.
- Do not solve reviewer-effort waste by putting a long rule in `AGENTS.md`;
  prefer the owning shared fresh-eye/critique policy and add only a compact
  pointer from always-loaded instructions if that proves necessary.

## Boundaries

- External side-effect scope: any approved push, remote-CI watch, or release is
  scoped to the phase or bundle that requested it. Approval does not carry
  forward into later done-early quality work.
- Issue closeout scope: #354 is close-intended only after the fix has durable
  proof and the issue workflow validates the carrier. #184 is context only.
- Public-doc audit scope: inspect `skills/public/**`, reusable `docs/**`
  operator guidance, generated public/operator docs, and public-support-facing
  references. Treat `charness-artifacts/**` and historical release records as
  evidence surfaces unless they are linked as reusable guidance.
- `nose` scope: prefer the manifest-supported install/update/doctor path. If the
  latest available `nose` is unavailable on the machine, record the advisory
  state honestly rather than blocking unrelated #354 diagnosis.
- Subagent effort-policy scope: document the default for routine bounded
  reviewer calls in the owning shared fresh-eye/critique reference. If a host
  blocks effort override on full-history forks, prefer a bounded packet with a
  non-forked medium-effort reviewer unless the review genuinely needs full
  inherited context.

## User Acceptance

The user can verify completion directly by checking:

- #354 is closed or has an issue-tool closeout proof showing why it remains
  intentionally open;
- the final report names the `nose` version or advisory-unavailable state used
  for the quality scan;
- the public-doc audit lists concrete files changed or explicitly reports no
  coupling changes needed;
- the final proof distinguishes local deterministic checks, scheduled mutation
  evidence, and any remote/live proof that was or was not run.
- bounded reviewer guidance is updated so routine fresh-eye reviews have an
  explicit medium-effort path, and any high-effort reviewer use has a named
  justification.

## Agent Verification Plan

### Low-Cost Checks

- `git status --short --branch`
- `python3 skills/public/issue/scripts/issue_tool.py read --repo corca-ai/charness --number 354`
- `charness tool doctor nose --json --no-write-locks`
- Public-doc coupling inventory with `rg` over `skills/public`, reusable `docs`,
  and generated public/operator docs for issue-number and release-specific
  references.
- Inspect `skills/shared/references/fresh-eye-subagent-review.md`,
  `skills/public/critique/**`, and `AGENTS.md` only as needed to place reviewer
  effort policy in the right owner.
- Focused tests for the #354 fix path before broader gates.

### High-Confidence Checks

- Reproduce or explain the scheduled mutation changed-line coverage failure from
  run `27332665340` on head `5051119d`, including base/seed/test-selection
  mechanics.
- Run the quality scan with the latest available `nose` surface on PATH, or
  record the `nose` advisory-unavailable disposition and run the non-`nose`
  quality gates that still apply.
- Run the repo closeout gate appropriate to the final changed surfaces; if
  mutation-pool Python files change, include fresh mutation coverage production
  before push.
- Run issue closeout validation for #354's direct-commit or PR carrier before
  claiming the issue is closable.
- Validate any reviewer-effort policy edit with the relevant markdown, skill,
  and artifact checks; do not rely on prose alone if an existing validator owns
  the touched surface.

### External Or Live Proof

- Use the scheduled mutation workflow result after the fix as remote proof when
  a push is approved.
- Complete the remaining v0.41.0 real-host `nose` proof from
  `charness-artifacts/release/latest.md` when practical: doctor before install,
  dry-run install, install/update or record latest available state, verify
  `nose --version`, rerun doctor, run support-sync, and inventory nose clones.
- If a second machine or clean temp-home is unavailable, record that as a
  non-claim instead of presenting maintainer-machine proof as full real-host
  coverage.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Refresh routing and issue context | #354 comments changed the real blocker after v0.41.0 | `find-skills` route, `issue_tool.py read` with comments, summarized base/seed/test-selection facts | planned |
| 2 | Establish latest `nose` quality posture | User explicitly asked for updated `nose` quality scanning | `charness tool doctor nose`, install/update proof or advisory state, `nose --version` when available | planned |
| 3 | Audit public docs for hard coupling | Prevent issue-number/release-specific details from leaking into reusable guidance | Inventory command/output, changed docs or explicit no-change rationale | planned |
| 4 | Improve bounded reviewer effort policy | Current session exposed waste from inherited high effort on a routine review | Shared policy/critique guidance edit, validator proof, and any AGENTS pointer if justified | planned |
| 5 | Diagnose and fix #354 | Current open regression blocks main quality posture | Root-cause note, focused tests, code/doc changes, changed-line coverage proof | planned |
| 6 | Closeout and publish proof | Goal includes tracked issue resolution and optional remote proof | Closeout gate, critique, retro, issue closeout draft/verification, push/CI proof if approved | planned |

## Coordination Cues

Phase-appropriate routing for this run, deferred to `find-skills` (its
recommendation engine) rather than hard-coded here. Fill during the run:

- Routing: pending — ask `find-skills` at activation for the current phase.
- Gather: n/a — no external URL needs to become repo context before activation;
  GitHub issue #354 is read through the issue workflow.
- Release: pending — only required if this goal touches release surfaces or
  consumes remaining v0.41.0 release real-host proof as release closeout.
- Issue closeout: pending — #354 is close-intended; use issue workflow closeout
  validation and verify CLOSED after the carrier lands. #184 is context only.

Discuss before activation: resolved — the operator explicitly requested this
goal artifact now and named the bundle scope: updated `nose` quality scan,
public-doc hard-coupling audit, and #354 fix. Remote push/release approval is
not pre-granted by this draft.

## Slice Log

Not activated yet.

## Context Sources

- [handoff](../../docs/handoff.md) — next-session sequencing and v0.41.0 release
  state.
- [recent lessons](../retro/recent-lessons.md) — do not classify a red mutation
  run as a flake before reading base/seed/selection mechanics.
- [v0.41.0 release record](../release/latest.md) — remaining real-host and
  `nose` proof checklist.
- [fresh-eye subagent review policy](../../skills/shared/references/fresh-eye-subagent-review.md)
  — owner for bounded reviewer spawn/effort guidance.
- GitHub issue #354 — `Mutation test regression on main`, open as of
  2026-06-11; latest issue comment identifies changed-line coverage blockers in
  `skills/public/issue/scripts/issue_read.py` and
  `skills/public/issue/scripts/issue_tool.py`.
- GitHub issue #184 — product metrics ideation, open as context only.

## Interview Decisions

- Mode considered: artifact-only draft vs implementation continuation. Chosen:
  implementation-continuation goal artifact, but inert until `/goal` activation.
  Reason: the operator asked to create an `achieve` goal document for the next
  session, not to execute #354 in this turn.
- Bundle shape considered: split `nose`, public-doc audit, and #354 into
  separate goals vs one bundle. Chosen: one goal with slice boundaries. Reason:
  the operator explicitly tied the three activities together for the next
  session, and #354 validation depends on quality posture.
- `nose` wording considered: hard-code an expected upstream version vs use the
  latest available manifest-supported path. Chosen: latest available path.
  Reason: version availability is machine/upstream dependent; record the
  observed version or advisory state.
- Public-doc audit scope considered: scan all checked-in history/artifacts vs
  reusable public/operator guidance. Chosen: reusable guidance first, historical
  artifacts as evidence unless linked as guidance. Reason: issue numbers are
  legitimate in release/retro evidence but risky in portable docs.
- Issue priority considered: include #184 vs keep separate. Chosen: keep #184
  out of scope. Reason: #184 needs product ideation, while #354 is the active
  main regression.
- Reviewer effort considered: inherit parent model/effort vs explicitly request
  medium for bounded reviewers. Chosen for this goal: use explicit medium effort
  when a subagent reviewer is needed and the host allows it. Reason: the
  operator flagged unintended high-effort reviewer calls as waste.
- Reviewer-effort policy placement considered: add a long rule to `AGENTS.md` vs
  update the shared fresh-eye/critique owner and optionally point from
  `AGENTS.md`. Chosen: shared owner first. Reason: AGENTS should stay short, and
  the durable policy belongs where bounded reviewer mechanics are already
  specified.

## Plan Critique Findings

- Fresh-eye status: not yet run for this draft. At activation, run the required
  slice critique with an explicit medium-effort reviewer request when the host
  permits it.
- Folded concern: `update nose` could be misread as a repo surface edit rather
  than installing/updating the external tool. The plan now says latest available
  install/update path and requires recording the observed version or advisory
  state.
- Folded concern: #354 could be misread as only a mutation-score problem. The
  plan starts from the latest issue comments and the changed-line coverage
  blocker on issue-read files.
- Folded concern: routine bounded reviews can inherit high effort when a
  full-history fork blocks explicit effort overrides. The plan now includes a
  dedicated policy-improvement slice to prefer bounded medium-effort packets
  unless high effort is justified.
- Over-worry: #184 appearing in the open-issue list does not make it part of
  this implementation bundle; it is explicitly context only.

## Off-Goal Findings

None yet; not activated.

## Final Verification

Closeout evidence — replace each `TODO` with a bound path or explicit allowed
skip before completion.

Retro: TODO — create or explicitly skip with an allowed reason before complete
Host log probe: TODO — create or explicitly skip with an allowed reason before complete
Disposition review: TODO — create or explicitly skip only when policy allows before complete

## User Verification Instructions

After activation and completion, review the final report and check:

- the #354 closeout proof and linked workflow result;
- the `nose` version/advisory state recorded in the quality proof;
- the public-doc audit output and any changed files;
- the shared reviewer-effort policy change and proof that it was validated;
- the explicit non-claims for any remote, release, or second-machine proof not
  run.

## Auto-Retro

Retro dispositions: TODO — disposition every surfaced improvement, or record the explicit no-improvement opt-out
Structural follow-up: TODO — when the retro names a transferable waste item (a `## Sibling Search` trigger), classify its structural destination (`applied: <gate/hook/validator/test/contract change>` / `issue #N (recurs:|novel: <reason>)` / `repo-local guard: <path>` / `none — <reason>`); delete this line when no transferable waste was named
