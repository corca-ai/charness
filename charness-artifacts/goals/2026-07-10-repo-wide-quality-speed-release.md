# Achieve Goal: Repo-wide quality, speed, and v0.64.0 release

Status: active
Created: 2026-07-10
Activation: `/goal @charness-artifacts/goals/2026-07-10-repo-wide-quality-speed-release.md`

This file is the living goal scratchpad. The user's direct instruction to run
the repo-wide sweep and then push/release is the implementation-continuation
activation for this session; the command above is the portable resume form.

## Active Operating Frame

- Current slice: S3 freeze and verify the release bundle.
- Current slice intent: turn the critiqued S1/S2 implementation into a committed,
  fully evidenced release candidate without widening the selected scope.
- Next action: commit the implementation slice, write the final quality record,
  then run the verification lock and release preflight.
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

Improve Charness across the current codebase with evidence-backed code-quality
repairs, real bug fixes, and measurable test/production-path speedups; preserve
or strengthen behavior proof; then publish and independently verify v0.64.0.

## Non-Goals

- Do not turn “repo-wide” into indiscriminate formatting, warning-count gaming,
  baseline widening, or speculative refactors without a measured capability gain.
- Do not weaken correctness, security, mutation, or release gates to make them faster.
- Do not claim production speed from test runtime alone; measure the affected
  operator/CLI/runner path directly.
- Do not add a production LLM/provider runtime: this repo ships a CLI/plugin and
  skills, so production-path work targets installable CLI, plugin, and release flows.
- Do not run Cautilus or other live evaluator spend unless its planner says the
  selected prompt/behavior slice needs it and the ask-before-run boundary is resolved.
- Do not close #421 or any other issue as part of this goal unless the selected
  fix explicitly resolves it through the issue workflow.

## Boundaries

- External side-effect scope: name which phase or bundle any approved
  publish / push / remote-CI / apply applies to. That approval is phase-scoped
  and does not carry forward — after an approved publish/CI/apply lane
  completes, done-early test-only quality continuation is local by default
  (batch remote proof, run CI once over the final bundled state). Per-slice
  remote publication is assumed only when the operator explicitly asks or a
  runtime-affecting slice requires earlier publication.
- The user's message explicitly authorizes the final bundled branch push and
  v0.64.0 publication after local verification and release critique. It does
  not authorize per-slice pushes, unrelated issue closure, or force-push.
- Release scope is one minor bump because the unpushed bundle already contains
  the additive `usage_feedback` operator/data-contract capability; new sweep
  fixes must remain backward compatible.
- Host/environment axes remain real: Claude and Codex plugin surfaces, fresh
  checkout behavior, and the maintainer install refresh are verified separately.
- Work stops before publication if fresh-eye release critique, verification
  lock, credentials, remote ancestry, or distinct-channel public readback fails.

## User Acceptance

- Read the final quality artifact and see concrete before/after measurements,
  named bug fixes, preserved proof, and honest residual Weak/Missing items.
- Run the focused tests/benchmarks and the final verification lock successfully.
- Inspect GitHub and see tag/release v0.64.0 from the pushed main branch.
- Run the documented update path and observe the maintainer installation at
  v0.64.0, with public/fresh-checkout proof recorded through distinct channels.

## Agent Verification Plan

### Low-Cost Checks

- Quality planner primers plus focused runtime, test-economics, source-hygiene,
  CLI, skill-ergonomics, security, duplicate, and dead-code inventories.
- Before/after command timing with repeated samples for every claimed speedup.
- Focused unit/in-process tests for selected bugs and structural seams; ruff,
  py_compile, mirror/surface validators, and changed-line coverage checks.

### High-Confidence Checks

- Bounded fresh-eye plan and implementation critique with distinct code-quality,
  test-economics, production-speed, and release-risk lenses.
- `run_slice_closeout.py --base --verification-lock --produce-mutation-coverage`
  over the final committed mutation set, plus the full read-only quality gate.
- Release helper prepublish checks, fresh-checkout probes, and real-host trigger review.

### External Or Live Proof

- Push the final main bundle and v0.64.0 tag only after local lock proof.
- Publish the GitHub release through the repo-owned helper, verify its public URL
  through a distinct channel, refresh the maintainer installation, and read back
  both remote tag ancestry and installed version.
- No issue-close claim unless a tracked issue is intentionally carried by the release.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| S0 | Inventory repo-wide quality, bug, and speed candidates | Avoid broad cleanup without evidence | Baseline gates, runtime packets, candidate scorecard, critique | completed |
| S1 | Repair usage-feedback review and malformed-history handling | Two reproduced regressions can corrupt counts or crash the writer | Focused delivery+feedback and malformed-history regression tests, mirror parity | completed |
| S2 | Fast-path a healthy bootstrap runtime and overlap independent Markdown checks | Measured CLI and standing-gate costs have behavior-preserving seams | Repeated CLI/Markdown timings, fallback/advisory/failure tests | completed |
| S3 | Freeze and verify the release bundle | Prevent local green from escaping wrong | Fresh-eye critique, verification lock, changed-line coverage | in progress |
| S4 | Bump, push, publish, refresh, and verify v0.64.0 | External boundary comes last | Release artifact, tag/release/public/install readbacks | pending |

## Operator Decision Queue

- Decision: no pending decision at activation; the user authorized the final
  bundled push and minor release, while the release helper's safety gates still
  retain authority to stop publication.
- Owner: operator for any new credential or policy conflict discovered later.
- Why deferred: current `gh` authentication and remote access are available.
- Unblock action: only needed if a later external readback or credential check fails.
- Revisit trigger: release planner/publish helper returns an external-boundary blocker.

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

- Routing: find-skills recommended quality and release for the explicit task; achieve coordinates the long objective, impl owns code/test slices, critique owns fresh-eye risk review, and release owns bump/publish/verification
- Gather: n/a — no external source link is an input; GitHub and public release readbacks are execution evidence, not gathered working context
- Release: pending — bind the v0.64.0 release artifact and public verification at closeout
- Issue closeout: n/a — no tracked issue is claimed resolved by this goal at activation

## Discuss Before Activation

A Before-phase summary of any consequential activation decision — surfaced from
the Non-Goals / Boundaries / Verification / Interview / Critique sections — that
must be resolved before `/goal`. Required only when a trigger fires (live/prod
proof, issue close/split, broad scope, irreversible side effect, or a
proof-level non-claim); replace the `fill` line below, or delete it when none
applies.

- Discuss before activation: resolved — the user explicitly approved a repo-wide implementation continuation followed by push and release; the final bundle is targeted at backward-compatible minor v0.64.0, and publication still waits for critique, locked local proof, remote ancestry, public distinct-channel readback, and install refresh

## Slice Log

- S0 inventory, measured 2026-07-10:
  - standing pytest: 4,398 passed in 28.19s with 16 workers; 8 workers took
    35.43s and 24 workers took 41.90s, so the existing cap remains the honest
    default rather than a tunable-speed cleanup.
  - test economics: 385 Python test files and 144 standing files with nested
    CLI calls; no blanket in-process conversion is selected because host,
    packaging, and real-binary isolation are mixed into that count.
  - Markdown gate: 538 tracked files in 4.6--5.4s; the inline-code advisory is
    ~0.63s and currently serial with MarkdownLint, so overlap is the bounded
    proof-preserving test/gate move. Changed-file caching is not selected
    because no invalidation proof prevents untouched regressions escaping.
  - production CLI: `charness --version` warm median 117--134ms;
    `resolve_repo_python()` costs ~0.5--1.0s per fresh process despite a healthy
    bootstrap launcher, while a direct required-module probe costs ~0.10s.
  - correctness: one delivery plus one linked feedback is reproduced as
    `usage_count=2` with `<missing>` dimensions; one schema-invalid historical
    feedback row raises an uncaught `KeyError` instead of structured rejection.
  - static posture: Ruff, compileall, ShellCheck, high-confidence dead code,
    brittle-source, structural-waste, dual-implementation, CLI-contract, and
    git-aware scan inventories are clean. The `_portable_path` duplicate family
    and narrow E402 suppressions are intentional portable/package boundaries.
- Selected implementation contract:
  - keep deliveries as the usage denominator and evidence/window dimension
    source while joining explicit feedback only onto its linked delivery's
    signal/friction interpretation;
  - schema-validate historical JSONL before semantic feedback reconciliation,
    return structured `invalid_feedback`, and never append after invalid history;
  - prefer a healthy repo bootstrap launcher after one required-module probe,
    fall back to the existing repair bootstrap when absent or unhealthy;
  - run the independent inline-code advisory and blocking MarkdownLint scan in
    parallel while preserving deterministic output order and MarkdownLint exit
    semantics;
  - exact S1 proof: one delivery plus one linked feedback reports
    `usage_count == 1`; first/last seen and product/entry/trigger/outcome
    dimensions come from the delivery; linked feedback contributes only to
    feedback/friction interpretation and never creates `<missing>` dimensions;
  - exact S1 write-safety proof: schema-invalid historical JSONL returns
    structured `invalid_feedback` without traceback or append and remains
    byte-identical after the rejected execution;
  - exact S2 bootstrap proof: healthy launcher performs one required-module
    probe and no repair write; missing/unhealthy launcher delegates to the
    existing `bootstrap_runtime.py` path unchanged; repeated fresh-process
    timings compare the same command before/after;
  - exact S2 Markdown proof: both-pass, advisory-fail/blocking-pass, and
    blocking-fail cases preserve advisory WARN behavior, deterministic output
    order, and MarkdownLint's blocking exit status;
  - defer lazy urllib, changed-file Markdown caching, pytest worker changes,
    broad nested-process consolidation, and concurrent JSONL locking because
    current evidence does not justify their extra release surface.
- S1/S2 implementation and proof, 2026-07-10:
  - feedback review now filters delivery and explicit feedback timestamps
    independently, keeps delivery-only dimensions/evidence, projects linked
    signals onto targets, preserves outcome-only friction, and counts threshold
    episodes uniquely; malformed history is structurally rejected byte-identical;
  - healthy bootstrap resolution validates the same contract shape, minimum
    Python, required modules, and isolated environment in one probe, then falls
    through to the unchanged repair owner for missing, unhealthy, too-old,
    malformed, non-executable, or corrupt launchers;
  - Markdown advisory and MarkdownLint run concurrently with deterministic
    advisory-first output, preserved stderr, and MarkdownLint-owned exit status;
  - combined focused suite: 90 passed; full standing suite after the reviewer
    fixes: 4,413 passed in 28.27s; Ruff, py_compile, ShellCheck, mirror equality,
    repo-copy invariant, diff check, and 648 whole-tree critique records passed;
  - bootstrap fresh-process median: 502.40ms authoritative path versus 102.01ms
    reuse fast path (4.93x); Markdown median: 4.73s baseline versus 4.01s after
    overlap; slow preflight integration call: 5.02s baseline versus 3.96s;
  - plain `version`/exact `--version` is retained as a read-only manifest probe:
    15 fresh-process samples had 112.32ms median versus the recorded 117--134ms
    baseline, but the primary gain is no host-local state creation/rewrite;
    verbose/json/check keep provenance and update-state behavior. Fresh-eye
    decision: `charness-artifacts/critique/2026-07-10-plain-version-readonly-critique.md`;
  - fresh-eye code critique:
    `charness-artifacts/critique/2026-07-10-repo-wide-quality-speed-code-critique.md`;
    its only Act Before Ship finding, launcher `OSError` fallback, is fixed with
    a real subprocess regression.

## Context Sources

- `docs/design-north-star.md` — judgment-first reversible work and distinct-channel release confirmation.
- `charness-artifacts/quality/latest.md` — most recent quality state and active recommendations.
- `charness-artifacts/retro/recent-lessons.md` — reviewer isolation, environment leakage, surface ownership, and release-persistence traps.
- `docs/handoff.md` — current branch/release state and #421 machine-owned boundary.
- `.agents/quality-adapter.yaml` / `.agents/release-adapter.yaml` — gate, runtime, release, fresh-checkout, and install-refresh contracts.
- `charness-artifacts/goals/2026-07-10-outcome-driven-autonomous-improvement.md` — completed additive feedback capability already in the unpushed bundle.

## Interview Decisions

- Mode family: artifact-only vs implementation-continuation. Chosen:
  implementation-continuation because the user said to sweep, fix, push, and release.
- Scope family: warning cleanup vs evidence-ranked repo sweep. Chosen:
  evidence-ranked slices; rejected indiscriminate cleanup because it can game metrics.
- Version family: patch/minor/major. Chosen: minor v0.64.0 because the existing
  unpushed bundle adds an optional operator/data-contract capability; rejected
  patch as under-reporting and major because no compatibility break is intended.
- Production axis: serving-provider runtime vs shipped CLI/plugin/release path.
  Chosen: CLI/plugin/release path; single-point provider benchmarking is inapplicable.
- Host axis: both Claude and Codex installed surfaces remain in scope; neither
  host is promoted to a global default.

## Plan Critique Findings

- Same-agent shaping check: whole-codebase cleanup without ranking is rejected;
  inventories and measured deltas choose the slices.
- Same-agent shaping check: release is one final bundle, never per-slice push.
- Fresh-eye plan critique: satisfied by
  `charness-artifacts/critique/2026-07-10-repo-wide-quality-speed-plan-critique.md`.
  Act Before Ship items F1-F4 are now exact acceptance checks above; bundle
  findings F5-F6 bind the final quality record and shared ownership; F7 is
  explicitly deferred.

## Off-Goal Findings

N/A — inventory has not yet produced off-goal findings.

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
