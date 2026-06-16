# HOTL Proof Packet: Open issue HOTL closeout

Status: active-audit; proof incomplete
Created: 2026-06-16
Last audited: 2026-06-16
Goal: `charness-artifacts/goals/2026-06-16-open-issue-hotl-closeout.md`

## Loop Inventory

- Surface class: mixed local guard / repo artifact / GitHub issue state /
  external runtime lifecycle.
- Related issues: #378, #377, #376, #375, #371.
- Applied/live state at shaping: no active-run mutation had been executed.
- Applied/live state at latest audit: no issue-closeout mutation has been
  executed by this packet audit; all issue readbacks below were read-only.
- Local implementation state: #375 has a local implementation slice in progress;
  no GitHub closeout carrier has been published.
- Adapter state: no HOTL adapter is present; live proof commands are
  undeclared.
- Issue backend: `issue_tool.py preflight --repo-root . --json` selected the
  authenticated `gh` backend.
- GitHub source-of-truth readback on 2026-06-16: #378, #377, #376, #375, and
  #371 all remained `OPEN`; per-issue reads returned `comments_read: true`.

## Success Criteria

- Every shaped issue (#378, #377, #376, #375, #371) is verified `CLOSED`
  through GitHub readback after the implementation carrier lands.
- Any GitHub issue closure carries before/after provider readback.
- #371 closeout is acceptable from the Charness side if local mitigation and
  ownership transfer are proven, upstream lifecycle ownership is linked, and the
  closeout explicitly does not claim invocation-bound teardown was fixed.
- #371 upstream lifecycle proof is verified only if invocation-end process-tree
  teardown and `agent-browser-chrome-*` profile-dir cleanup are proven for
  normal completion, cancellation, provider failure, and timeout.

## Pre-Roundtrip Failure Checks

- Confirm `issue_tool.py preflight --repo-root . --json` selects an
  authenticated GitHub backend.
- Refresh `gh issue list --repo corca-ai/charness --state open --limit 50`.
- Read each issue with comments before design.
- Run `hotl` adapter resolution. If no adapter declares live proof commands,
  record any live-provider proof need as a residual disposition unless the
  active run first adds a repo-owned proof command and tests it.
- Validate issue closeout carrier drafts before publishing close keywords.

## Feasibility

- #378: feasible through local quality advisory implementation plus tests and
  GitHub closeout readback.
- #377: feasible through repo-wide artifact/current-pointer audit, resolver or
  instruction changes, validators where justified, and GitHub closeout readback.
- #376: feasible through skill-contract updates plus at least one cross-skill
  audit and tests/validators that prove the visible re-judgment surface.
- #375: feasible through `achieve` adapter/scaffold changes and tests proving
  idempotent draft-frame customization.
- #371: feasible as Charness-local closeout if the active run records verified
  mitigation/readback plus residual upstream issue disposition. The local issue
  can close without upstream lifecycle verification, as long as the closeout
  explicitly does not claim that upstream teardown was fixed.

## Human Intervention

- Before any push, release, or manual issue close, name the phase-scoped carrier
  and obtain or record the operator-approved path.
- If #371 proof depends on a real provider cancellation/failure/timeout event,
  record the exact action packet and readback target before executing it.

## Non-Claims

- Local deterministic tests do not prove live provider lifecycle behavior for
  #371.
- A direct cleanup command or doctor result proves post-hoc mitigation only, not
  invocation-bound teardown.
- Closing #371 locally does not prove upstream `agent-browser` has fixed its
  daemon/profile lifecycle.
- A closed GitHub issue proves tracker state only; it does not by itself prove
  release availability or consumer update.
- This audit does not prove any implementation acceptance for #378, #377, #376,
  or #375; it only proves the GitHub issue state and comments were read.
- This audit does not claim #371 is closeable today. The latest #371 comments
  state that it should remain open unless controlled invocation-end lifecycle
  proof exists, which is stricter than the goal's draft local-close path.

## Read-Only Issue Audit

| Issue | GitHub state | Comments read | Current proof state | Evidence |
| --- | --- | --- | --- | --- |
| #378 | `OPEN` | yes | not verified; implementation/carrier missing | Issue readback says the advisory inventory is still requested; no closeout carrier or closed-state proof exists. |
| #377 | `OPEN` | yes | not verified; implementation/carrier missing | Issue readback says the current-pointer audit/tightening remains open; no closeout carrier or closed-state proof exists. |
| #376 | `OPEN` | yes | not verified; implementation/carrier missing | Issue readback says deterministic-helper re-judgment guidance remains open; no closeout carrier or closed-state proof exists. |
| #375 | `OPEN` | yes | local implementation proof present; carrier missing | Achieve scaffold now accepts adapter-controlled draft Active Operating Frame lines for new artifacts, refuses invalid scaffold adapter config on create, and preserves existing-artifact status-only idempotence. GitHub closeout carrier and closed-state proof still do not exist. |
| #371 | `OPEN` | yes | `issue` disposition candidate | Latest comments preserve the upstream lifecycle proof boundary: local repair mitigation shipped, but invocation-bound process/profile teardown remains unproven. |

## Staleness Findings

- `docs/handoff.md` now reports the repository at `origin/main` after the
  v0.50.2 release, while this goal artifact still carries older draft-time
  branch-state language. Treat the Git refs and GitHub issue readback as newer
  authority.
- The goal artifact's #371 closure allowance is stale against the issue's own
  latest comments unless the active run either obtains controlled lifecycle
  proof or records a new operator decision that explicitly supersedes the
  current open-issue disposition.
- No `charness-artifacts/hotl/latest.md` ledger exists yet, so this proof packet
  is the current durable HOTL state for the loop until a ledger/current pointer
  is added.

## Ledger Draft

| Issue | Initial HOTL status | Required proof or disposition |
| --- | --- | --- |
| #378 | planned | Local advisory implementation proof plus GitHub before/after closeout readback |
| #377 | planned | Audit/change proof plus GitHub before/after closeout readback |
| #376 | planned | Re-judgment contract proof plus GitHub before/after closeout readback |
| #375 | planned | Adapter-controlled scaffold proof plus GitHub before/after closeout readback |
| #371 | planned close | Verify Charness mitigation/ownership closeout; disposition upstream lifecycle residual as `issue` with upstream tracker and non-claim; verify local GitHub issue closed |

## Local Proof: #375

- Classification: feature.
- Boundary: add adapter-controlled draft Active Operating Frame scaffold lines to
  `achieve`; do not alter existing goal artifacts or close GitHub issues.
- Changed surfaces: `skills/public/achieve/scripts/goal_artifact_scaffold.py`,
  `goal_artifact_lib.py`, `achieve_adapter_policy.py`,
  `goal_artifact_template.md`, `init_adapter.py`, `adapter.example.yaml`,
  `references/adapter-contract.md`, `docs/public-skill-dogfood.json`, mirrored
  `plugins/charness/skills/achieve/*`, and focused tests under
  `tests/quality_gates/`.
- Fresh-eye critique: `charness-artifacts/critique/2026-06-16-issue-375-achieve-scaffold-adapter.md`.
- Prepared critique packet:
  `charness-artifacts/critique/2026-06-16-004228-packet.md`.
- Public-skill dogfood/scenario review: `suggest_public_skill_dogfood.py`
  reported the existing `achieve` case as `hitl-recommended`; decision recorded
  in the critique artifact is to update the explicit dogfood case and not
  require a maintained evaluator scenario by default for this slice.
- Targeted proof: `python3 -m pytest -q
  tests/quality_gates/test_goal_artifact_lib.py
  tests/quality_gates/test_goal_artifact_scaffold.py
  tests/quality_gates/test_achieve_adapter_policy.py
  tests/quality_gates/test_goal_artifact_producers.py` -> 66 passed.
- Broad local proof: `python3 scripts/run_standing_pytest.py --repo-root .
  --mode read-only` -> 3160 passed in 21.67s.
- Additional validators passed: packaging validation, skill validation, public
  skill validation/dogfood, docs/markdown/secrets checks, Cautilus provenance
  validation, Ruff, py_compile, Python length check, attention-state visibility,
  boundary-bypass ratchet, and gitignore scan hygiene.
- Slice closeout: `run_slice_closeout.py --verification-lock
  --refresh-broad-pytest-proof --produce-mutation-coverage
  --mutation-coverage-command <focused achieve scaffold pytest>
  --ack-cautilus-skill-review` completed, including focused mutation coverage
  production for the new scaffold helper.
- Non-claim: this local proof does not close #375. Final issue closeout still
  requires a carrier with close keywords or approved fallback and GitHub
  `CLOSED` readback.

## Next Action

- Do not close or comment on the issues from this audit alone.
- If another agent is implementing the open-issue queue, use this packet as the
  current HOTL readback baseline and require before/after GitHub state proof for
  any later closeout carrier.
- Before any #371 close attempt, reconcile the stale goal wording with the live
  issue comments; without controlled lifecycle proof, keep #371 as `issue`
  disposition rather than `verified`.
