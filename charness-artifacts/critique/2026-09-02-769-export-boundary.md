# #769 export boundary and gate classification critique

Date: 2026-09-02

## Execution

Fresh-Eye Satisfaction: `parent-delegated`.
Target: `code-critique.md`.

## Decision Under Review

Locking the #769 boundary before its closeout: repo-only quality gates moved
from `scripts/` to the non-exported root `tools/` tree (run as
`python3 -m tools.<name>`), `run-quality.sh` reduced to a thin wrapper over the
declared list `.agents/quality-gates.yaml` executed by `run_quality_engine.py`,
gate scan scopes read from the adapter's `universes:` family, and the quality
skill re-scoped to the consumer definition. Reviewed at main `829d0284b`
(boundary findings applied) and `67ce8ebaa` (runner findings applied).

## Verification Scope Decision

- Claim under test: a clean export carries no `tools/` file and no code that runs a `tools/` module, and a consumer's quality run reaches only gates that check the consumer's own repository.
- Changed surfaces: `tools/**`, `scripts/run-quality.sh`, `scripts/run_quality_engine*.py`, `.agents/quality-gates.yaml`, `scripts/quality_universes_lib.py`, `.agents/quality-adapter.yaml`, `skills/public/quality/**`, `docs/export-boundary.md`; final consumers are the exported plugin (`scripts/export_plugin.py`) and the quality skill's planner.
- Minimum sufficient proof: `python3 -m tools.check_export_self_sufficiency --repo-root .` (blocking on an unguarded executable `tools/` reference in exported code), the export probe (`find <export> -path '*/tools/*'` empty, no moved basename present), `python3 -m tools.check_plugin_import_smoke`, and the planner naming no `ownership: repo-only` row.
- Deliberately omitted checks: the live consumer install on a throwaway repository (owned by #772), the release lane (owned by #772), and the mutation lane (no changed-line proof is claimed here).
- Verifier contract: `scripts/validate_critique_artifacts.py` (unchanged by this slice); the export self-sufficiency gate CHANGED in this slice (its tools-reference arm now blocks on executable spellings) and is therefore suspect until its seeded tests pass, which they do (`tests/quality_gates/test_export_self_sufficiency.py`).
- Failure classification: subject-defect
- Negative control: command: `python3 -m tools.check_export_self_sufficiency --repo-root .` at `e1946ad47` before the guard markers | expected refusal: `status: fail` naming `scripts/check_skill_surface_preflight.py:390` | observed result: `status: fail` with that path in `exported_tools_code_references`; after the `export-guard:` marker `status: pass` | receipt: the gate's YAML payload captured in this session's transcript (`charness-artifacts/goal-runs/765/2026-09-02-session-record.md`)
- Subject identity: sha256:f2a457cd6d58a943ba727a8d70f794b5e2756557d540cb96b8735a1fae3a56a6
- Verifier identity: sha256:bc2de505dc3bddb54516d73467f2ad813dcd568fc4b816a2cdec3586bad019b8
- Input identity: sha256:67629b7b2a65e80d86bd89c56c01f43b7f0da2c1b64caf8019ca78f0f916e6aa
- Failure identity: stable:769-export-boundary-consumer-leak
- Evidence identity: none
- Retry disposition: first-attempt
- Retry key: sha256:ef906893b78821864fd8c8235a03095eaac2a515f5fef2c38a73623fc6a31979

## Reviewed Input Identity

- Packet consumed: charness-artifacts/critique/2026-09-02-769-boundary-v2-packet.json
- Packet path: charness-artifacts/critique/2026-09-02-769-boundary-v2-packet.json
- Packet SHA256: 8813f0f509d4d7042c9933502a5ba2f89cd0fdf02fd14307f93128167951e265
- Identity SHA256: 67629b7b2a65e80d86bd89c56c01f43b7f0da2c1b64caf8019ca78f0f916e6aa

Two bounded read-only reviewers ran in parallel with materially different
angles on the LANDED tree: Gerald Weinberg (producer/consumer boundary of the
`tools/` split) and Michael Jackson (problem framing of the declared runner and
universes). Both delivered findings into the parent context; both reports were
truncated by the host near four thousand characters, so findings after the
eighth (boundary) and sixth (runner) and both `NOT READ` lines are lost and
recorded as a non-claim below. An earlier pair reviewed the lane DESIGN before
any lane ran; that record is
`charness-artifacts/goal-runs/765/briefs/design-critique-769.md` and is not
counted toward this artifact's two-reviewer substrate.

## Reviewer Tier Evidence

- requested tier: `high-leverage`
- requested spawn fields: typed `bounded-reviewer`, session-model inheritance
  (per-host contract; the adapter's Codex-host fields are not applied on this
  Claude host)
- host exposure state: `host-defaulted`
- application state: unverified-by-packet
- Delivery state: `findings-received`
- Worker report: none (typed-subagent path; findings text reached the parent context)
- Worker report identity: none
- Worker report approval: none
- Worker report delivery: findings-received
- Worker report packet identity: 8813f0f509d4d7042c9933502a5ba2f89cd0fdf02fd14307f93128167951e265
- Worker report input identity: 67629b7b2a65e80d86bd89c56c01f43b7f0da2c1b64caf8019ca78f0f916e6aa
- Worker report parent receipt identity: none
- Worker report findings identity: none

## Boundary Ownership

- Producer: `scripts/packaging_lib.py` (`export_plugin_tree`, the allowlist that decides what ships) and `docs/export-boundary.md` (the prose owner of the rule).
- Consumer: the exported plugin's shipped scripts and skills, and the consumer CLI `charness` that spawns `scripts/validate_packaging.py` from the installed checkout.
- Owning surface: `tools/check_export_self_sufficiency.py` with `tools/export_tools_reference_lib.py`.
- Verdict: moved-to-owner

The round-1 boundary put three export-machinery modules and `validate_presets`
into `tools/` because their import closure said so; the consumers (the CLI, the
quality skill's preset reconciliation) proved the closure incomplete because it
ignored spawn and dotted-string edges. The rule now lives in one place: an
exported `.py` or `.sh` that RUNS or IMPORTS a `tools/` module blocks unless the
line carries an `export-guard:` comment naming why it cannot run in a consumer.

## Failure Angles

- Boundary (Weinberg): a shipped consumer entrypoint importing a moved module; the resolver executing a consumer's own `tools/` file; a bare `tools/` directory read as "authoring checkout"; the self-sufficiency arm blind to argv-list and dotted spellings and advisory-only; the shared shim's failure mode when vendored.
- Runner (Jackson): py-compile carrying a second literal glob list; the exported runner dying on a hook file the export does not carry; the exported runner unable to target a consumer at all; the planner's consumer-gate rule derived from a command-path heuristic; undeclared-empty universes passing with a warning where the gate used to refuse.

## Counterweight Pass

Every boundary finding that named a shipped runtime path was reproduced by
reading the cited line and is fixed (`829d0284b`); the two runner findings
that change what a consumer runs or is told to run are fixed (`67ce8ebaa`).
The runner's fourth finding (the exported `run-quality.sh` is charness-only by
construction) is real but is the consumer-run route the issue's Non-claims
leave out ("no redesign of what a consumer quality run proposes"); it is
deferred with a follow-up rather than folded into this closeout. The
undeclared-empty verdict is the U-lane design (a discovered empty is reported,
a declared empty refuses) and stays; the remedy for a consumer is the
`universes:` declaration the skill's bootstrap now shows first.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/scripts/quality_preset_reconciliation.py:21 | action: fix | note: shipped planner path imported tools.validate_presets; validate_presets.py returns to scripts/ (STAY-SHARED), commit plan schedules it by name
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/check-docs.sh:52 | action: fix | note: authoring checkout was keyed on a bare tools/ directory; now tools/__init__.py beside packaging/charness.json, also in check_skill_surface_preflight.py and the shared shim
- F3 | bin: act-before-ship | evidence: strong | ref: tools/export_tools_reference_lib.py | action: fix | note: the arm now matches dotted tools.<module>, tools/<name>.py, and "tools" argv items, skips docstrings, and blocks on unguarded executable references in exported .py/.sh
- F4 | bin: act-before-ship | evidence: strong | ref: tools/check_skill_cut_safety.py | action: fix | note: imported tools.check_skill_contracts at module level while shipping; authoring-only, moved
- F5 | bin: act-before-ship | evidence: strong | ref: skills/shared/scripts/authoring_script_shim.py:47 | action: fix | note: the ancestor walk never executes a consumer's tools/<name> and refuses by name saying the export carries no tools/
- F6 | bin: act-before-ship | evidence: strong | ref: scripts/run_quality_engine_runtime.py:272 | action: fix | note: py-compile carried a second literal glob list without tools/; it now resolves the python_sources universe and refuses a declared-empty one
- F7 | bin: act-before-ship | evidence: strong | ref: scripts/check-python-lint.sh:51 | action: fix | note: unconditional source of .githooks/runtime-env.sh, absent from the export; guarded on the file
- F8 | bin: bundle-anyway | evidence: moderate | ref: skills/public/quality/scripts/quality_declared_gate_source.py:26 | action: fix | note: the planner's consumer rule was a command-path heuristic; rows now carry ownership: repo-only (validate-packaging, validate-packaging-committed, validate-presets, the --require-adoption catalog row) and the planner reads that field first
- F9 | bin: valid-but-defer | evidence: strong | ref: scripts/run-quality.sh:15 | action: file-issue | follow-up: deferred charness-artifacts/goal-runs/765/2026-09-02-session-record.md#next-session-in-order | note: the exported run-quality.sh cannot target a consumer (GATE_ACCEPTS_REPO_ROOT_HATCH=0, package root and package gate list); the consumer route today is the planner over the consumer's own declared list
- F10 | bin: valid-but-defer | evidence: moderate | ref: tests/quality_gates/test_shell_gate_root_resolution.py:400 | action: document | note: the exported-copy test seeds two scripts, not a real export tree; the live install proof in #772 exercises the real shape
- F11 | bin: over-worry | evidence: contested | ref: scripts/check_python_runtime_inheritance.py:144 | action: defer | note: an UNDECLARED empty universe warns and exits 0 by the U-lane contract (discovered empty); a DECLARED empty refuses; the consumer remedy is the universes declaration the skill bootstrap shows first
- F12 | bin: over-worry | evidence: weak | ref: skills/public/quality/scripts/quality_declaration_lifecycle.py:21 | action: defer | note: the resolver's ancestor walk reaching a consumer's tools/ was only reachable through validate_presets, which no longer lives there

## Deliberately Not Doing

- Shipping `run-quality.sh` with a consumer-targeting mode (F9): the issue's Non-claims exclude redesigning the consumer quality run; the exported wrapper refuses by name outside a source checkout, which is honest until the route is designed.
- Re-running the two reviewers on the repaired surface: the repairs are at the cited lines and do not change the reviewed risk's shape; the seeded tests and the blocking gate carry the proof.

## Fresh-Eye Satisfaction

`parent-delegated`: two typed `bounded-reviewer` subagents with disjoint angles delivered findings into the parent context; the parent applied the counterweight pass and the fixes. Non-claim: both reports were truncated by the host after their last listed finding, so any finding past that point and both `NOT READ` lines are unknown.

## Verification

- `python3 -m tools.check_export_self_sufficiency --repo-root .` status pass (blocking arm live, 29 guarded sites annotated)
- export probe: zero `tools/` entries, no moved basename in the export except the shared shim, which refuses by name
- `python3 -m tools.check_plugin_import_smoke --repo-root .` imports every exported module
- `python3 skills/public/quality/scripts/plan_quality_run.py --repo-root .` names no `ownership: repo-only` row
- `./scripts/run-quality.sh` 5 passed; the full standing pytest and the full read-only lane are recorded in the #769 closeout commit
