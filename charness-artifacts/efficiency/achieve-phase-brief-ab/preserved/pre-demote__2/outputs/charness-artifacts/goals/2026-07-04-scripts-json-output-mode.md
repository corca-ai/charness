# Achieve Goal: Consistent --json output mode across repo scripts via shared helper

Status: draft
Created: 2026-07-04
Activation: `/goal @charness-artifacts/goals/2026-07-04-scripts-json-output-mode.md`
Timebox: none — no operator work budget supplied; slices are individually shippable so any stop point is safe
Activation time: unset — filled when the active run starts
Closeout reserve: final slice reserved for full-suite proof, retro, and closeout (no wall-clock budget to slice)
Done-early policy: continue_next_improvement

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: real draft/backlog awaiting activation.
- Current slice intent: real draft/backlog awaiting activation; reshape before
  activating if the acceptance boundary has changed. Once active, this names
  the reviewable-intent unit in progress and the commits it spans; critique
  and broad proof do not re-fire within one unchanged intent — update it when
  the intent changes, not per commit (meaningful-slice-cadence).
- Next action: activate with `/goal @charness-artifacts/goals/2026-07-04-scripts-json-output-mode.md` after confirming the draft is
  still intended.
- Verification cadence: cheap deterministic checks at commit boundaries;
  higher-cost or fresh-eye proof at slice boundaries; final broad/live proof at
  closeout.
- Gate cadence: pre-lock slices use `run_slice_closeout.py --skip-broad-pytest`;
  final/bundle proof records the verification lock and uses `--verification-lock`.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Operator Decision Queue`, `## Final Verification`,
  and `## Auto-Retro`.

## Goal

Every Python CLI entrypoint under `scripts/` (argparse-based; 148 measured on
2026-07-04) offers a consistent `--json` output mode that emits its result
payload through one shared repo helper, and the contract is enforced by tests
so new scripts cannot regress it.

- Outcome capability: an operator or downstream tool can run any repo script
  entrypoint with `--json` and get a machine-parseable payload with one shared
  serialization contract (`ensure_ascii=False`, `indent=2`, `sort_keys=True`,
  trailing newline). Note: this is the TARGET contract, not the dominant
  existing idiom — critique measured `sort_keys=True` in only 23 of the 73
  existing `--json` argparse scripts, so convergence reorders keys for the
  insertion-order majority (see the payload-equality boundary).
- Failed capability today: 75 of 148 entrypoints have no `--json` at all, and
  the 73 that do each hand-roll `json.dumps` with divergent kwargs (~45 of 155
  call sites use `sort_keys`), so serialization drift between scripts is
  unguarded.
- Deliverables: (1) shared helper module `scripts/json_output_lib.py` (emit
  function + standard `--json` argparse registrar), (2) unit tests for the
  helper, (3) an enforcement test that enumerates argparse entrypoints and
  ratchets missing-`--json` / non-helper emitters down to zero, (4) migration
  of all entrypoints onto the helper in bounded batches.
- Proof cost: cheap — every check is repo-local (pytest + smoke-invoking
  scripts with `--json` and `json.loads`-parsing stdout). No live/provider
  proof exists or is claimed for this goal.
- Test-duplication pressure: enforcement is ONE enumerator/ratchet test plus
  parameterized smoke coverage, not a hand-written test per script; helper unit
  tests stay in one module. Per-slice `--test-pressure` samples watch this.
  Critique caveat: the changed-line mutation-coverage gate
  (`scripts/run-quality.sh` -> `check_changed_line_mutation_coverage.py`;
  `scripts/*.py` is the core-python mutation pool) means every migrated
  script's emit path must execute under pytest — so "parameterized" still
  requires a per-script invocation recipe (safe args/env/tmp fixtures) via the
  repo's in-process convention (`tests/script_main.py:run_loaded_script_main`).
  Keep recipes as a data table/fixture registry, not per-script test functions,
  and expect fixture-heavy batches to shrink below the ~15 estimate.
- Critique plan: fresh-eye plan critique before activation (bounded reviewer,
  recorded in Plan Critique Findings); fresh-eye slice critique with the
  standard slice packet at slice boundaries (helper design slice and each
  migration bundle), commit-level checks stay mechanical.
- Stop conditions: flip to `blocked` if the enforcement contract conflicts with
  an existing repo gate in a way not resolvable locally, or a migration batch
  cannot preserve an existing consumer's payload; `No safe next slice:` if
  remaining scripts all require payload-semantics decisions the operator must
  make.
- Reporting expectations: slice log per batch with script counts
  (migrated/remaining), ratchet baseline value at each commit, final report
  separating self-verification from user verification.

## Non-Goals

- Shell scripts (`scripts/*.sh`) — different language surface; a follow-up
  issue may be filed but they are out of this goal.
- Library modules without a CLI entrypoint (`*_lib.py` files with no argparse
  main path).
- Changing the human-readable (non-`--json`) default output of any script.
- Changing the payload *schema* of the 73 scripts that already emit JSON;
  convergence is emitter-mechanics only (shared helper call), payload keys and
  values stay as they are (key ORDER may change — see the payload-equality
  boundary). Any script whose payload must semantically change is out of scope
  and gets an issue instead.
- A new CLI framework or `create-cli`-style command-surface redesign; this goal
  standardizes output plumbing only.
- Rewriting `docs/generated/cli-reference.md` by hand — it regenerates via its
  owning script if the gates require it.

## Boundaries

- External side-effect scope: name which phase or bundle any approved
  publish / push / remote-CI / apply applies to. That approval is phase-scoped
  and does not carry forward — after an approved publish/CI/apply lane
  completes, done-early test-only quality continuation is local by default
  (batch remote proof, run CI once over the final bundled state). Per-slice
  remote publication is assumed only when the operator explicitly asks or a
  runtime-affecting slice requires earlier publication.
- This goal is fully repo-local: no push, release, or remote-CI lane is
  requested or approved. Commits land locally per repo commit discipline.
- Backward compatibility is a hard line, defined as PARSED-OBJECT EQUALITY,
  not byte equality: existing `--json` flags keep their semantics (including
  the default-true variants — the registrar is never force-applied over an
  existing flag), and for every converged script `json.loads(before) ==
  json.loads(after)` on the same input. Byte-level output MAY change (key
  reordering from `sort_keys=True`) because only ~23/73 existing emitters sort
  keys; for any consumer that reads the output textually (string-pinning
  tests, line parsers found by consumer grep), prove that consumer green or
  exclude that script with a recorded reason.
- Migration batches stay bounded (~10–20 scripts per slice, shrinking when
  invocation recipes are fixture-heavy) so each slice is reviewable and any
  stop point leaves the ratchet green.
- Scripts that cannot be safely smoke-run get an explicit allowlist entry with
  a recorded reason instead of a fake recipe; `run_cautilus_eval.py` is
  contractually ask-before-run and is allowlisted from smoke invocation from
  the start (its `--json` wiring is still migrated; proof is unit-level).
- Mirror and export safety: every `scripts/*.py` edit regenerates the
  `plugins/charness/scripts/` mirror (`sync_root_plugin_manifests.py`; gated
  by `check_staged_mirror_drift.py`) and both are staged together. The new
  helper is itself exported, so consumers import it via the repo pattern
  (`runtime_bootstrap.import_repo_module`) so it resolves in dev and exported
  plugin trees alike (`check_export_safe_imports.py` gates this). The slice-2
  enumerator scopes to repo `scripts/` only, never the mirror, or every count
  doubles.
- `mutate -> sync -> verify` order per repo phase rules; generated surfaces
  (e.g. CLI reference) sync via their owning scripts before validators run.
- Consumers first: before changing any script that other scripts, tests, hooks,
  or skills invoke with `--json`, grep for its invocations and keep them green.

## User Acceptance

- Pick any Python entrypoint in `scripts/` (e.g.
  `python3 scripts/check_doc_links.py --json`) and get valid JSON on stdout
  (`... --json | python3 -m json.tool` succeeds).
- Run the enforcement test (final name recorded in the Slice Log, under
  `tests/`) and see it pass with a zero-missing baseline.
- `grep -l argparse scripts/*.py | xargs grep -L -- '--json'` returns empty
  (modulo any explicitly allowlisted exclusions recorded in the artifact).

## Agent Verification Plan

### Low-Cost Checks

- Unit tests for `scripts/json_output_lib.py` (encoding args, trailing
  newline, sort order, non-ASCII passthrough, stream override).
- Per-migrated-script smoke: invoke with `--json` on a cheap/no-op input and
  `json.loads` the stdout; parameterized, not hand-written per script.
- Payload-equality check for already-JSON scripts: capture payload
  before/after the helper migration on the same input (reusing that script's
  invocation recipe) and assert `json.loads` equality; consumer grep for
  textual readers of that output.
- Ratchet/enforcement test run at every commit boundary.

### High-Confidence Checks

- Full repo pytest suite at slice boundaries.
- Repo commit gates as configured (changed-line mutation coverage, duplicate-
  pressure gates, `run_slice_closeout.py` cadence per the Operating Frame).
- Fresh-eye slice critique on the helper-design slice and each migration
  bundle.

### External Or Live Proof

- None planned and none claimed: the goal surface is repo-local script
  behavior. There is no provider/live lane; closeout will state this
  explicitly as a non-claim rather than implying live proof.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Ship `scripts/json_output_lib.py` (export-safe emit + argparse registrar) with unit tests, mirror-synced | Everything else depends on the helper contract | helper module + green unit tests; `check_export_safe_imports.py` green | pending |
| 2 | Enforcement/ratchet test enumerating repo-`scripts/` argparse entrypoints (mirror excluded); baseline = 75 missing + 73 non-helper emitters, re-measured at slice time | Locks the floor before migration so progress can never silently regress | new test green with recorded baseline file/count | pending |
| 3 | Invocation-recipe registry (data table: safe args/env/fixtures per script, plus not-smoke-runnable allowlist with reasons) seeded for the first migration batch | Mutation-coverage gate makes recipes the real unit of migration cost; pricing them early keeps later batch estimates honest | registry consumed by parameterized smoke via `tests/script_main.py` convention | pending |
| 4..N | Migrate missing-`--json` entrypoints in bounded batches (~10–15/slice, smaller when fixture-heavy), ratchet down each slice | Largest gap first: 75 scripts have no machine output at all | ratchet count drops per slice; parameterized smoke + changed-line mutation gate green | pending |
| N+1..M | Converge the 73 existing `--json` scripts onto the helper, parsed-object-equality-checked with consumer grep | Consistency half of the goal; mechanical except where key order is textually consumed | ratchet non-helper count reaches 0; `json.loads`-equality checks green | pending |
| final | Flip ratchet to zero-tolerance, full suite + closeout (retro, dispositions, final report) | Proves the contract is enforced, not just achieved | enforcement test green with empty baseline; closeout artifacts | pending |

## Operator Decision Queue

Record decisions, confirmations, credential actions, manual proof steps, and
external-boundary approvals discovered during the run when they do not block
safe local progress. Use `none — <reason>` when the queue is empty at closeout.

Queue item form:

- Decision: operator-only decision or confirmation needed
- Owner: operator or named human owner
- Why deferred: why the run did not stop immediately
- Unblock action: exact action or answer needed
- Revisit trigger: event, date, or proof boundary that reopens this

## Coordination Cues

Phase-appropriate routing for this run, deferred to `find-skills` (its
`--recommend-for-task` / `--recommendation-role --next-skill-id` recommendation
engine) — never a hard-coded phase-to-skill list here. `achieve` owns this slot
and the floors below; `find-skills` owns *which* skill answers a boundary. Fill
during the run:

- **Routing** — ask `find-skills` to recommend the skill for the current phase or
  boundary, and record the route it returns. At completion, recorded
  implementation / debug / quality / issue work needs this `Routing:` evidence
  or a `Routing: n/a — <reason>` opt-out.
- **Gather step** — when `## Context Sources` names an external source
  (URL / Slack / Notion / Docs / Drive), add a `Gather:` line here pointing at the
  gathered asset, or write `Gather: n/a — <reason>` when no external context
  applies.
- **Release step** — when this run touches a release surface (a version bump or
  install-manifest edit), add a `Release:` line here pointing at the release
  proof, or write `Release: n/a — <reason>`.
- **Issue closeout step** — when this goal resolves tracked GitHub issues, add
  an `Issue closeout:` line naming the close-intended issue numbers, carrier
  (`direct-commit`, PR body, release commit, or manual fallback), and
  `issue_tool.py validate-closeout-draft` / `verify-closeout` proof. If a
  tracked issue appears in `## Context Sources` as context only, use
  `Issue closeout: n/a — <reason>`.

Routing step line — record it on ONE physical line so the floor reads the whole
value (a soft-wrapped value is tolerated now, but one line is clearest). Copy the
form below and replace `<skill>` with the find-skills-recommended skill; the
placeholder is intentionally non-satisfying (the Gather / Release / Issue
closeout floors are presence-only, so no stub is seeded for them — add their line
per the bullets above when that boundary is crossed):

- `Routing: find-skills -> achieve — Before-phase goal shaping (task-text probe on 2026-07-04 returned no support-skill match; achieve owns the goal artifact, impl/quality expected downstream per fresh probes at those boundaries)`

## Discuss Before Activation

A Before-phase summary of any consequential activation decision — surfaced from
the Non-Goals / Boundaries / Verification / Interview / Critique sections — that
must be resolved before `/goal`. Required only when a trigger fires (live/prod
proof, issue close/split, broad scope, irreversible side effect, or a
proof-level non-claim); replace the `fill` line below, or delete it when none
applies.

- Discuss before activation: resolved — two consequential defaults, both
  settled with stated defaults the operator confirms by reviewing this draft
  before `/goal` (reshape via `/achieve @` if either default is wrong).
  (1) Broad scope: "모든 repo 스크립트" resolves to the 148 Python argparse
  entrypoints in `scripts/` (75 additions + 73 emitter convergences); shell
  scripts and CLI-less libs are excluded as Non-Goals, and the run is
  ratchet-guarded bounded batches so every stop point is safe.
  (2) Output-compatibility semantics (surfaced by plan critique): the target
  contract includes `sort_keys=True` but only 23/73 existing emitters sort
  keys, so "one shared contract" and "byte-stable existing output" cannot both
  hold. Settled as parsed-object equality (`json.loads` before == after) as
  the hard line, key ordering allowed to change, with a consumer grep + green
  proof (or recorded exclusion) for any textual consumer of a converged
  script's output. The rejected alternatives were per-script kwargs (defeats
  the consistency goal) and byte-for-byte freeze (blocks convergence for the
  insertion-order majority).
  No live-proof, issue-close, or irreversible-side-effect trigger applies —
  the goal is fully repo-local and reversible.

## Slice Log

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

- Operator request (2026-07-04, Korean prose): "모든 repo 스크립트에 일관된
  --json 출력 모드를 공유 헬퍼와 테스트로 추가하는 목표를 잡아줘" — shape the
  goal; artifact-only, no execution requested.
- Surface measurement (2026-07-04, repo greps; corrected by plan critique):
  286 entries in `scripts/`; 148 files with argparse; 75 argparse files
  lacking `--json`; 73 argparse files with ad hoc `--json` (an initial count
  of 78 included non-argparse files). Emit kwargs diverge: across ~155
  `json.dumps` call sites, ~102 use `indent=2`, ~91 `ensure_ascii=False`, only
  ~45 `sort_keys=True` (23 of the 73 `--json` scripts). Target-idiom examples:
  `scripts/check_boundary_bypass_ratchet.py:39`,
  `scripts/check_cli_skill_surface.py:262`, `scripts/check_github_actions.py:28`.
- Ratchet precedent: `scripts/check_boundary_bypass_ratchet.py` +
  `scripts/boundary-bypass-baseline.json` — the existing repo pattern for
  baseline-and-shrink enforcement this goal's slice 2 mirrors.
- `docs/conventions/implementation-discipline.md` and
  `docs/conventions/operating-contract.md` — sync/verify order and closeout
  discipline governing every slice.
- Gather: n/a — no external URL/source; all context is repo-local.

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

- Artifact-only vs implementation-continuation: chose artifact-only. The prose
  "목표를 잡아줘" (set the goal) is an explicit Before-phase ask; a strong
  default settles it without an interview round, and execution stays gated
  behind `/goal`.
- Scope of "모든 repo 스크립트": options were (a) literally everything in
  `scripts/` incl. shell, (b) Python argparse CLI entrypoints, (c) only the 75
  currently missing `--json`. Chose (b): shell scripts are a different
  serialization surface (rejected a — cost/heterogeneity), and consistency via
  a shared helper is the stated point of the request, which (c) would miss by
  leaving 73 hand-rolled emitters diverging (rejected c — fails "일관된").
- Helper shape: options were a new `scripts/json_output_lib.py`, extending an
  existing lib, or a decorator/framework. Chose a new small `_lib` module per
  repo naming convention (`check_python_filenames.py` governs), exposing an
  emit function plus an argparse `--json` registrar; rejected framework-scale
  designs as `create-cli` territory and out of proportion.
- Enforcement style: big-bang test (fails until all 148 migrated) vs
  baseline-ratchet. Chose ratchet, mirroring the repo's boundary-bypass
  precedent: keeps every intermediate commit green and makes partial progress
  durable; big-bang would force one unreviewable mega-slice.
- Payload compatibility: initially chose byte-stability for the 73 existing
  scripts; plan critique showed that conflicts with the shared contract (key
  ordering differs for 50/73), so the boundary was revised to parsed-object
  equality plus consumer-grep proof for textual readers. Still rejected
  "improve payloads while touching them" because unknown downstream consumers
  (tests, hooks, skills) parse those payloads.
- Timebox: none supplied; recorded `Timebox: none` with per-slice safety
  instead of inventing a budget.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

Provenance: bounded fresh-eye subagent (general-purpose, read-only in the
shared worktree), 2026-07-04, pre-activation plan critique of this draft.

Blockers folded:

1. "Dominant idiom" premise false — `sort_keys=True` is a 23/73 minority, so
   byte-stable output and one shared contract were mutually unsatisfiable.
   Folded: boundary redefined to parsed-object equality + consumer-grep proof;
   added as Discuss Before Activation item (2).
2. Changed-line mutation-coverage gate turns "parameterized smoke" into a
   per-script invocation-recipe cost (via `tests/script_main.py`
   `run_loaded_script_main` convention), with side-effectful and
   ask-before-run scripts needing allowlisting. Folded: new slice 3 (recipe
   registry), batch sizes revised downward, `run_cautilus_eval.py` allowlisted
   from smoke from the start, test-duplication note expanded.
3. Plugin mirror + export safety unnamed: every `scripts/*.py` edit must sync
   `plugins/charness/scripts/` (`sync_root_plugin_manifests.py`,
   `check_staged_mirror_drift.py`); the helper must be export-safe
   (`runtime_bootstrap.import_repo_module`, `check_export_safe_imports.py`);
   the enumerator must exclude the mirror or counts double. Folded into
   Boundaries and slices 1–2.
4. Arithmetic drift: 75+78≠148; the correct existing-`--json` argparse count
   is 73. Folded: all counts corrected; slice 2 re-measures at slice time
   rather than trusting shaping-time numbers.

Over-worry raised, not folded (no artifact change needed):

5. Duplicate-pressure ratchet — a 1–2 line registrar call per script is below
   clone-detection granularity and the migration is net dedup.
6. Test-file length cap (800 lines) — avoided trivially by keeping recipes in
   a data module/fixture file; noted, no plan restructure.
7. Variant `--json` semantics (default-true flags) and CLI-reference coupling —
   already covered by the "flags keep their semantics" boundary and the
   Non-Goals regeneration line; `render_cli_reference.py` only touches
   charness-dispatched commands.

## Off-Goal Findings

Issues or deferred findings discovered during the run.

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>`. The complete gate rejects a literal
`TODO` / `<path>` / `TBD` until you do.

Retro: TODO — create or explicitly skip with an allowed reason before complete
Host log probe: TODO — create or explicitly skip with an allowed reason before complete
Disposition review: TODO — create or explicitly skip only when policy allows before complete

## User Verification Instructions

## Auto-Retro

Retro dispositions: TODO — disposition every surfaced improvement, or record the explicit no-improvement opt-out
Structural follow-up: TODO — when the retro names a transferable waste item (a `## Sibling Search` trigger), classify its structural destination (`applied: <gate/hook/validator/test/contract change>` / `issue #N (recurs:|novel: <reason>)` / `repo-local guard: <path>` / `none — <reason>`); delete this line when no transferable waste was named
