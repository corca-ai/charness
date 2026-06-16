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
- Local implementation state: #375, #378, #377, and #376 have local implementation
  proof; no GitHub closeout carrier has been published.
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
- This audit does not prove GitHub closeout acceptance for #378, #377, #376, or
  #375; local implementation proof exists only where explicitly recorded below.
- This audit does not claim #371 is closeable today. The latest #371 comments
  state that it should remain open unless controlled invocation-end lifecycle
  proof exists, which is stricter than the goal's draft local-close path.

## Read-Only Issue Audit

| Issue | GitHub state | Comments read | Current proof state | Evidence |
| --- | --- | --- | --- | --- |
| #378 | `OPEN` | yes | local implementation proof present; carrier missing | Quality now includes an advisory structural-waste inventory for duplicate broad collection and broad AST scanner candidates. GitHub closeout carrier and closed-state proof still do not exist. |
| #377 | `OPEN` | yes | local implementation proof present; carrier missing | Artifact resolver payloads now expose `artifact_path`, repo-wide current-pointer layout inventory reports adapter class/write-path/symlink metadata, and policy/quality guidance points agents toward resolved write paths and dated records for long evidence. GitHub closeout carrier and closed-state proof still do not exist. |
| #376 | `OPEN` | yes | local implementation proof present; carrier missing | Handoff chunked routing now requires agentic package `judgment_summary` fields and carries them into operator-facing package candidates. GitHub closeout carrier and closed-state proof still do not exist. |
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

## Local Proof: #377

- Classification: feature.
- Boundary: make current-pointer handling auditable and harder to misread
  across skills; do not convert every `latest.md` to a symlink, add a new
  blocking floor, or close GitHub issues.
- Changed surfaces: `scripts/inventory_current_pointer_layouts.py`,
  `scripts/resolve_artifact_path.py`,
  `skills/public/quality/scripts/resolve_quality_artifact.py`,
  `docs/artifact-policy.md`,
  `skills/public/quality/references/bootstrap-escalations.md`, mirrored
  `plugins/charness/*`, and focused artifact naming tests.
- Resolver output proof: generic and quality-specific resolvers now include
  `artifact_path` alongside `current_artifact_path`, `write_artifact_path`,
  `write_artifact_role`, and symlink metadata.
- Layout audit proof: `python3 scripts/inventory_current_pointer_layouts.py
  --repo-root . --json` reported 20 public skills plus the `cautilus` artifact
  family: 5 adapter-unmanaged workflows, 5 missing current pointers, 9 regular
  current pointers, 1 rolling file, and 1 symlink current pointer (`debug`),
  with per-skill/family source, `artifact_path`, `write_artifact_path`, and
  symlink metadata where available.
- Fresh-eye critique: `charness-artifacts/critique/2026-06-16-issue-377-current-pointer-audit.md`.
- Targeted proof: `python3 -m pytest -q
  tests/quality_gates/test_artifact_naming.py
  tests/quality_gates/test_current_pointer_writes.py` -> 38 passed.
- Additional focused validators passed:
  `check_current_pointer_writes.py --require-empty`,
  `validate_current_pointer_freshness.py`, `validate_packaging.py`,
  `validate_packaging_committed.py`, `check_doc_links.py`,
  `check-markdown.sh`, `validate_skills.py`, Ruff on changed Python files, and
  Python length headroom for the changed scripts.
- Public-skill dogfood review:
  `python3 scripts/suggest_public_skill_dogfood.py --repo-root .
  --skill-id quality --json` reported the existing quality consumer contract as
  `hitl-recommended`; no maintained evaluator scenario was required by default
  for this deterministic resolver/inventory guidance slice.
- Slice closeout: `python3 scripts/run_slice_closeout.py --repo-root .
  --verification-lock --refresh-broad-pytest-proof
  --produce-mutation-coverage --mutation-coverage-command "python3 -m pytest -q
  tests/quality_gates/test_artifact_naming.py
  tests/quality_gates/test_current_pointer_writes.py"
  --ack-cautilus-skill-review` completed, including broad standing pytest and
  focused mutation coverage producer.
- Non-claim: this local proof does not close #377. Final issue closeout still
  requires a carrier with close keywords or approved fallback and GitHub
  `CLOSED` readback.

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
  tests/quality_gates/test_goal_artifact_producers.py` -> 68 passed.
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

## Local Proof: #378

- Classification: feature.
- Boundary: add a `quality` advisory inventory for duplicate broad
  discovery/collection and broad AST scanner prefilter waste; do not create a
  blocking gate and do not close GitHub issues.
- Changed surfaces: `skills/public/quality/scripts/inventory_structural_waste.py`,
  `structural_waste_lib.py`, `skills/public/quality/SKILL.md`,
  `references/inventory-dispatch.md`,
  `references/inventory-consumer-fields.json`,
  `.agents/inference-interpretation-surfaces.json`,
  `docs/public-skill-dogfood.json`, mirrored
  `plugins/charness/skills/quality/*`, and focused quality-gate tests.
- Fresh-eye critique:
  `charness-artifacts/critique/2026-06-16-issue-378-quality-structural-waste.md`.
- Public-skill dogfood/scenario review: `suggest_public_skill_dogfood.py`
  reported the existing `quality` case as `hitl-recommended`; the checked-in
  dogfood case was updated with #378 observed evidence. `validate_cautilus_proof.py`
  reported `next_action: none` for live Cautilus execution because the repo
  requires an explicit log-backed behavior proof request.
- Local live inventory: `python3
  skills/public/quality/scripts/inventory_structural_waste.py --repo-root .
  --json` reported zero duplicate-discovery candidates and one advisory
  broad-scanner candidate (`scripts/check_test_repo_copy_invariants.py:103`),
  with an interpretation section that keeps the result advisory.
- Targeted proof: `python3 -m pytest -q
  tests/quality_gates/test_structural_waste_inventory.py
  tests/quality_gates/test_inference_interpretation_meta_validator.py
  tests/quality_gates/test_quality_skill_docs.py
  tests/quality_gates/test_inventory_consumption.py` -> 56 passed.
- Additional focused validators passed: `validate_inference_interpretation.py
  --require-git-file-listing`, inventory declaration coverage/declaration drift,
  `validate_public_skill_dogfood.py`, `validate_skills.py`,
  `validate_packaging.py`, `validate_packaging_committed.py`, doc links,
  command docs, markdown, secrets, py_compile, Ruff, and gitignore scan
  hygiene.
- Non-claim: this local proof does not close #378. Final issue closeout still
  requires a carrier with close keywords or approved fallback and GitHub
  `CLOSED` readback.

## Local Proof: #376

- Classification: feature.
- Boundary: make deterministic helper outputs visibly subordinate to agent
  judgment for the handoff chunker package stage; record a cross-skill audit;
  do not claim exhaustive helper-surface coverage and do not close GitHub
  issues.
- Changed surfaces: `skills/public/handoff/scripts/chunked_routing_agentic.py`,
  `chunked_routing_agentic_policy.py`,
  `chunked_routing_agentic_validation.py`, `chunked_routing_types.py`,
  `prepare_ranker_packet.py`, `draft_goal_from_chunk.py`,
  `references/chunked-routing.md`, `docs/handoff-chunked-routing.md`,
  `docs/public-skill-dogfood.json`, mirrored
  `plugins/charness/skills/handoff/*`, and focused handoff tests.
- Cross-skill audit:
  `charness-artifacts/audit/2026-06-16-helper-output-rejudgment.md`.
- Fresh-eye critique:
  `charness-artifacts/critique/2026-06-16-issue-376-helper-rejudgment.md`.
- Public-skill dogfood/scenario review: `suggest_public_skill_dogfood.py`
  reported `handoff` as `evaluator-required`; the checked-in dogfood case was
  updated with #376 observed evidence. `evals/cautilus/scenarios.json` still
  maps `handoff` to `handoff-adapter-bootstrap`; no registry mutation was made
  because this slice changes deterministic package-synthesis schema, not
  routing/bootstrap behavior, and no log-backed behavior proof was requested.
- Targeted proof: `python3 -m pytest -q
  tests/test_handoff_chunker_agentic_packages.py
  tests/test_handoff_chunker_end_to_end.py
  tests/test_handoff_chunker_cli_contract.py
  tests/test_handoff_chunker_ranker_packet.py
  tests/test_handoff_chunker_auto_draft.py
  tests/quality_gates/test_goal_artifact_producers.py` -> 66 passed.
- Additional focused validators passed: `validate_public_skill_dogfood.py`,
  packaging validation, skill validation, public-skill validation, doc links,
  markdown, py_compile, and Ruff.
- Non-claim: this local proof does not close #376. Final issue closeout still
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
