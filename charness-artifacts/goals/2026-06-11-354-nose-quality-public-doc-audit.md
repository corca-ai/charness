# Achieve Goal: Resolve #354 with updated nose quality scan and public-doc audit

Status: complete
Created: 2026-06-11
Activation: `/goal @charness-artifacts/goals/2026-06-11-354-nose-quality-public-doc-audit.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: complete locally — closeout proof is recorded and the
  direct-commit carrier is committed.
- Next action: push/watch CI only if explicitly approved. Remote issue closure
  remains a non-claim until push/CI is approved and executed.
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
| 1 | Refresh routing and issue context | #354 comments changed the real blocker after v0.41.0 | `find-skills` route, `issue_tool.py read` with comments, summarized base/seed/test-selection facts | complete |
| 2 | Establish latest `nose` quality posture | User explicitly asked for updated `nose` quality scanning | `charness tool doctor nose`, install/update proof or advisory state, `nose --version` when available | complete |
| 3 | Audit public docs for hard coupling | Prevent issue-number/release-specific details from leaking into reusable guidance | Inventory command/output, changed docs or explicit no-change rationale | complete |
| 4 | Improve bounded reviewer effort policy | Current session exposed waste from inherited high effort on a routine review | Shared policy/critique guidance edit, validator proof, and any AGENTS pointer if justified | complete |
| 5 | Diagnose and fix #354 | Current open regression blocks main quality posture | Root-cause note, focused tests, code/doc changes, changed-line coverage proof | complete |
| 6 | Closeout and publish proof | Goal includes tracked issue resolution and optional remote proof | Closeout gate, critique, retro, issue closeout draft/verification, push/CI proof if approved | complete |

## Coordination Cues

Phase-appropriate routing for this run, deferred to `find-skills` (its
recommendation engine) rather than hard-coded here. Fill during the run:

- Routing: find-skills routed debug-shaped root-cause work through issue and quality for this slice; critique and retro handled closeout review.
- Gather: n/a — no external URL needs to become repo context before activation;
  GitHub issue #354 is read through the issue workflow.
- Release: pending — only required if this goal touches release surfaces or
  consumes remaining v0.41.0 release real-host proof as release closeout.
- Issue closeout: pending — #354 is close-intended; use issue workflow closeout
  validation and verify CLOSED after the carrier lands. #184 is context only.
- Issue closeout result: direct-commit carrier is committed and locally verified;
  remote CLOSED verification is intentionally pending push/CI approval.

Discuss before activation: resolved — the operator explicitly requested this
goal artifact now and named the bundle scope: updated `nose` quality scan,
public-doc hard-coupling audit, and #354 fix. Remote push/release approval is
not pre-granted by this draft.

## Slice Log

### 2026-06-11 18:32 KST — Activation

- Routing: `find-skills` session-start route selected `quality` for the active
  goal and surfaced the `nose` validation integration as repair-needed on this
  machine.
- Activation proof: `check_goal_artifact.py --pursue-ready --goal-path
  charness-artifacts/goals/2026-06-11-354-nose-quality-public-doc-audit.md`
  reported `pursue_ready: true`.
- Working tree: `main...origin/main [ahead 1]` with no uncommitted changes
  before activation edit.
- Next evidence target: GitHub issue #354 with comments plus scheduled mutation
  run mechanics; avoid classifying the red run before reading the selection
  mechanism.

### 2026-06-11 18:58 KST — #354 Issue And Mutation Evidence

- Issue read: `issue_tool.py read --repo corca-ai/charness --number 354`
  returned `comments_read: true`, `state: OPEN`, `comment_count: 2`.
- Latest blocker: scheduled run `27332665340` on head
  `5051119dd3196bcbd7bf36db4c6a1494aeec73d4` over base
  `a7d50604347cbff5d00d45602baacf92e0f7c6d3`; raw artifact
  `/tmp/charness-354-mutation-report.zip` showed changed-line blockers for
  `skills/public/issue/scripts/issue_read.py` and
  `skills/public/issue/scripts/issue_tool.py`.
- Root cause: tests that passed a fake-tool `PATH` made the shared
  `tests/quality_gates/support.py::run_script` choose `python3` from PATH on
  CI instead of the coverage-instrumented current interpreter, so subprocess
  coverage was lost while the tests still passed.
- Fresh-eye causal review: executed (`parent-delegated`, subagent
  `019eb622-c19b-7dc3-a3af-f292f43754a4`); reviewer confirmed the root cause
  and recommended the narrow `sys.executable` helper fix, with broader helper
  scans treated as adjacent follow-up risk rather than #354 scope.
- Proof: focused pytest passed (`60 passed in 103.54s`), and
  `check_changed_line_mutation_coverage.py` over the same base/head with the
  faithful coverage artifact reported `blocking: []`.

### 2026-06-11 19:05 KST — `nose` 0.6 Quality Posture

- Latest upstream release: `v0.6.0`, observed locally as `nose 0.6.0`;
  `doctor.py --tool-id nose` initially failed because the integration
  healthcheck expected old help text.
- Fix: updated `integrations/tools/nose.json` and exported plugin mirror to
  accept the current `nose scan --help` surface, and updated
  `inventory_nose_clones.py` to call `nose scan ... --min-size 24` instead of
  removed legacy flags.
- Proof: `doctor.py --tool-id nose` now reports `doctor_status: ok`, and both
  source and plugin `inventory_nose_clones.py --json` runs succeed with
  `tool_version: 0.6.0`, `family_count: 20`, `total_dup_lines: 3124`.
- Advisory interpretation: top families are mostly intentional
  per-skill/portable bootstrap duplication; no refactor was bundled from the
  advisory scan in this slice.

### 2026-06-11 19:12 KST — Public-Doc Coupling And Reviewer Effort

- Audit result: historical issue references in design docs, dogfood evidence,
  and current handoff/release artifacts remain provenance, not reusable
  guidance. Edited exported reusable guidance only.
- Changed files: `skills/shared/references/fresh-eye-subagent-review.md`,
  `skills/public/critique/adapter.example.yaml`,
  `skills/public/critique/references/adapter-contract.md`,
  `skills/public/critique/references/rename-critique.md`,
  `skills/public/release/references/install-surface.md`, and
  `skills/public/release/references/closeout-critique-gate.md`, plus plugin
  mirrors.
- Reviewer policy: added a portable `medium` reviewer tier for routine bounded
  fresh-eye reviews and reserved `high-leverage` for issue/release/quality
  closeout, deployment-confidence, or explicitly justified high-risk packets.
- Coupling cleanup: removed the stale `#258`, `v0.5.0`,
  `v0.27.0/v0.28.0`, and dated-release-critique example anchors from exported
  reusable guidance.
- Proof so far: `validate_integrations.py`, `validate_skills.py`,
  `validate_packaging.py`, and skill script `py_compile` passed after plugin
  sync.

### 2026-06-11 19:45 KST — Critique And Closeout Carrier

- Critique packet:
  `charness-artifacts/critique/2026-06-11-101503-packet.md`.
- Fresh-eye code critique: three parent-delegated bounded reviewers covered
  problem framing, root-cause diagnosis, and operational closeout risk; no
  `Act Before Ship` blockers were found.
- Folded critique findings: added deterministic fake-nose assertions for
  `--min-size 24` and absence of removed legacy flags, and updated the fake nose
  fixture to report `nose 0.6.0` consistently with its help surface.
- Counterweight: parent-delegated counterweight confirmed the folded items were
  sufficient; the remaining `tests/control_plane/support.py` `python3` helper is
  valid but deferred because it is outside #354's failing quality-gate path.
- Issue carrier:
  `charness-artifacts/issue/2026-06-11-issue-354-closeout-commit-message.md`;
  `issue_tool.py validate-closeout-draft --repo corca-ai/charness --number 354
  --classification bug --carrier direct-commit --commit-message-file ...`
  returned `status: draft_verified`, `publication_status:
  ready_to_commit_push`.
- Resolution critique:
  `charness-artifacts/critique/2026-06-11-issue-354-mutation-coverage-resolution.md`
  binds to #354 and validates through the issue tool.
- Non-claim: #354 remains open remotely until the direct commit is pushed and
  the scheduled mutation/CI proof runs; this session has not been granted remote
  push approval.

### 2026-06-11 20:05 KST — Validation Snapshot

- Focused tests after #354/nose edits passed: issue-read, issue-skill,
  nose-advisory, tool lifecycle/install/update tests.
- Broad standing pytest passed before the final critique-driven test hardening:
  `2799 passed, 4 skipped, 26 deselected`.
- Post-hardening focused pytest passed: `27 passed in 101.15s`.
- Deterministic validators passed locally: integration manifests, skills,
  packaging, critique artifacts, public-skill validation and dogfood,
  inference-interpretation, markdown links, command docs, markdown lint, secret
  scan, Cautilus proof validator, skill ownership overlap, skill ergonomics,
  packaging committed, Python length gate (warn-band advisories only), attention
  state visibility, test-repo copy invariants, boundary bypass ratchet, ruff,
  gitignore-scan hygiene, support sync dry-run, and tool update dry-run.
- `nose` proof: observed `nose 0.6.0`, latest upstream `v0.6.0` published
  2026-06-11T07:25:19Z; doctor is healthy; source and plugin nose inventory
  scripts both report `family_count: 20`, `total_dup_lines: 3124`.

### 2026-06-11 20:24 KST — Scenario Review And Verification Lock

- Public-skill scenario review: `plan_cautilus_proof.py --repo-root . --json`
  reported `next_action: none` and `run_mode: ask`; no Cautilus eval was run.
  The required HITL scenario-review decisions for `critique`, `quality`, and
  `release` were recorded in `docs/public-skill-dogfood.json`, and
  `validate_public_skill_dogfood.py` passed.
- Retro and disposition: persisted
  `charness-artifacts/retro/2026-06-11-354-nose-quality-public-doc-audit.md`,
  host probe
  `charness-artifacts/probe/2026-06-11-354-nose-quality-public-doc-audit-host-log.json`,
  and disposition review
  `charness-artifacts/critique/2026-06-11-354-nose-quality-public-doc-audit-disposition-review.md`.
- Pre-lock closeout: `run_slice_closeout.py --skip-broad-pytest
  --ack-cautilus-skill-review` completed.
- Final lock: `run_slice_closeout.py --verification-lock
  --produce-mutation-coverage --ack-cautilus-skill-review` completed. Broad
  non-release pytest passed under coverage, and `reports/mutation/test-coverage.json`
  plus `.fingerprint` were produced for the pre-push changed-line gate.
- Changed-line coverage consumer: `check_changed_line_mutation_coverage.py
  --reuse-coverage --coverage-json reports/mutation/test-coverage.json` returned
  `blocking: []` and noted that without a base SHA the workflow-dispatch-shaped
  check is non-blocking by construction. The stronger #354-specific base/head
  rerun from the scheduled-run evidence remains the causal proof for the issue.

### 2026-06-11 20:36 KST — Local Commit Carrier

- Commit: `b6bbf6f7 Fix mutation changed-line subprocess coverage`.
- Post-commit verifier: `issue_tool.py verify-closeout --repo corca-ai/charness
  --number 354 --classification bug --carrier direct-commit --commit-ref
  b6bbf6f7 --repo-root .` returned `status: carrier_verified`.
- Remote state check after the local commit still showed #354 `OPEN`, which is
  expected because the branch was not pushed; the goal's acceptance path is the
  issue-tool closeout proof plus explicit remote non-claim.

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

Retro: charness-artifacts/retro/2026-06-11-354-nose-quality-public-doc-audit.md
Host log probe: charness-artifacts/probe/2026-06-11-354-nose-quality-public-doc-audit-host-log.json
Disposition review: charness-artifacts/critique/2026-06-11-354-nose-quality-public-doc-audit-disposition-review.md
- Issue closeout draft:
  charness-artifacts/issue/2026-06-11-issue-354-closeout-commit-message.md
  validated with `status: draft_verified`; after commit, `verify-closeout`
  returned `status: carrier_verified` for `b6bbf6f7`.
- Remote issue state: #354 remains open until the direct commit is pushed and
  the remote close/CI proof is verified. This is an explicit non-claim, not an
  omission.
- Verification lock:
  `run_slice_closeout.py --verification-lock --produce-mutation-coverage
  --ack-cautilus-skill-review` completed, including broad non-release pytest and
  mutation coverage freshness production.

## User Verification Instructions

After activation and completion, review the final report and check:

- the #354 closeout proof and linked workflow result;
- the `nose` version/advisory state recorded in the quality proof;
- the public-doc audit output and any changed files;
- the shared reviewer-effort policy change and proof that it was validated;
- the explicit non-claims for any remote, release, or second-machine proof not
  run.

## Auto-Retro

Retro dispositions: none — the session retro names no actionable Next
Improvements; the existing issue validator caught closeout-shape mistakes before
commit, fresh-eye critique caught the nose fake-boundary gap before ship, and
the only residual sibling risk is documented as out-of-scope in the #354
resolution critique.
Structural follow-up: none — the retro's Sibling Search says no transferable
waste pattern is proposed; the deferred control-plane helper note is an
out-of-scope code-family risk, not a structural workflow destination for this
goal.
