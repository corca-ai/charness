# Achieve Goal: Autonomous structural quality bundle: shim drift gate, doc-coupling gate, contract fixture, nose-as-structural-signal

Status: active
Created: 2026-06-12
Activation: `/goal @charness-artifacts/goals/2026-06-12-autonomous-structural-quality-bundle.md`
Timebox: 8h
Activation time: 2026-06-12T21:42:32+09:00
Closeout reserve: 90m
Done-early policy: continue_next_improvement

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: 1 — bootstrap-shim consistency gate.
- Proof base for closeout: `c1f7b581` (HEAD == origin/main at activation).
- Next action: implement `scripts/check_bootstrap_shim_consistency.py` with
  `--fix`, normalize the 3 wrapped variants, wire into run-quality.sh, test,
  sync mirror, commit.
- Slice queue after current: 2 doc-coupling gate -> 3 nose structural-signal
  contract -> 4 contract fixture -> 5 closeout (critique BEFORE coverage
  producer; single handoff write; no push).
- Verification cadence: cheap deterministic checks at commit boundaries;
  higher-cost or fresh-eye proof at slice boundaries; final broad/live proof at
  closeout.
- Gate cadence: pre-lock slices use `run_slice_closeout.py --skip-broad-pytest`;
  final/bundle proof records the verification lock and uses `--verification-lock`.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

Operator-approved autonomous improvement bundle (8h timebox): make bootstrap-shim consistency machine-owned, turn the public-doc hard-coupling policy into a deterministic advisory gate, introduce a log-backed contract-effectiveness cautilus fixture behind the planner fence, and upgrade the quality skill so nose clone advisories are consumed as structural-improvement signals rather than a dup-line reduction target; fold handoff hygiene (stale items, second-machine proof removal) into closeout.

## Non-Goals

- Do not centralize the `_load_skill_runtime_bootstrap` shim into a shared
  import: the per-file copy is required by the portability doctrine in
  `skills/shared/references/bootstrap-resolution.md` (plugin-cache, split-tree,
  and operator-shell execution contexts). This goal machine-owns the copies'
  consistency; it does not remove the copies.
- Do not run a live `cautilus evaluate` this session: the planner reports
  `next_action: none` / `must_ask_before_running: true` and the operator's
  request did not name a failing-log path. The new fixture ships with
  deterministic schema validation only; live execution stays behind the
  existing planner fence and is an explicit non-claim.
- Do not turn the public-doc coupling gate into a blocking gate or extend it
  over `charness-artifacts/**`, `docs/handoff.md`, standing docs already owned
  by `check_standing_doc_provenance.py`, or intentional tracking ledgers;
  historical provenance stays legitimate where it lives today.
- Do not make dup-line reduction a target anywhere: the nose slice changes how
  advisories are *interpreted* (structural signal taxonomy), not a numeric
  goal. No clone refactor beyond the shim-consistency gate itself is bundled.
- Do not push to `origin/main` or cut a release: the operator is asleep and
  push approval was not pre-granted. Local commits only; push/release is a
  wake-up decision.
- Do not start #184 product-metrics ideation; it remains a separate operator
  session.
- Do not rewrite `docs/handoff.md` mid-session; stale-item fixes (completed
  06-11 goal listed as draft, second-machine proof carryover removal approved
  by the operator) fold into the single closeout write.

## Boundaries

- External side-effect scope: none granted. All work lands as local commits on
  `main`; no push, release, or remote-CI lane is approved for any phase of
  this goal.
- Shim gate scope: files defining `_load_skill_runtime_bootstrap` under
  `skills/`, `scripts/`, and the root `skill_runtime_bootstrap.py` source
  tree; the `plugins/` mirror stays owned by the existing tree-copy sync and
  mirror-drift gates. Gate must offer `--fix` and be wired into
  `run-quality.sh`.
- Doc-coupling gate scope: exported reusable guidance only —
  `skills/public/**/*.md`, `skills/shared/references/**/*.md`,
  `skills/support/**/*.md`, `docs/generated/**/*.md` — surfaces that are clean
  today after the 06-11 audit, so the gate starts at a zero-finding baseline.
  Advisory (exit 0) by design, consistent with `check_symbol_residue.py`.
- Nose-signal scope: the owning quality-skill advisory-interpretation surface
  and, if needed, `inventory_nose_clones.py` output notes. SKILL.md headroom
  checked with `check_skill_surface_preflight.py` before adding prose.
- Fixture scope: one new `evals/cautilus/*.fixture.json` derived from
  retro-documented real contract violations (counterweight-miss,
  same-agent-substitution lineage), auto-discovered by
  `validate-cautilus-scenarios`; registry/dogfood entries only if validators
  require them.
- Handoff scope: single closeout write; remove the second-machine/temp-home
  proof carryover (operator: stabilized, automation previously cost too much —
  remove rather than automate), retire the stale 06-11 re-scope item with
  evidence, resolve Discuss item 1 via the slice-2 policy, keep Discuss item 2
  untouched.
- Subagent reviews run in the shared parent worktree, read-only, medium effort
  for routine bounded packets per
  `skills/shared/references/fresh-eye-subagent-review.md`.

## User Acceptance

The user can verify completion directly by checking:

- `./scripts/run-quality.sh` passes and includes two new gates
  (`check-bootstrap-shim-consistency`, `check-public-doc-coupling`); breaking
  a shim copy or adding `(#999)` to an exported reference makes the
  respective gate report it.
- The quality skill's advisory-interpretation surface tells a consumer what
  *structural* action each clone-family class maps to, and explicitly forbids
  treating `total_dup_lines` as a reduction KPI.
- `evals/cautilus/` contains the contract-effectiveness fixture, named from
  real retro records, and `validate-cautilus-scenarios` passes; the final
  report states plainly that no live cautilus run happened and why.
- `docs/handoff.md` no longer carries the second-machine proof item or the
  stale 06-11 re-scope item, and Discuss item 1 is resolved with the codified
  policy.
- Every slice has a commit on `main` (local), and nothing was pushed.

## Agent Verification Plan

### Low-Cost Checks

- `git status --short --branch` at each boundary; per-slice focused pytest for
  new gate scripts (`tests/quality_gates/`).
- New gate self-tests: run each new check against a deliberately broken
  temp-tree sample (drifted shim copy; injected `(#999)` ref) and confirm
  detection plus `--fix` round-trip for the shim gate.
- `python3 scripts/check_skill_surface_preflight.py` before skill prose edits;
  `check_python_lengths.py --headroom` before extending existing scripts.
- `python3 scripts/sync_root_plugin_manifests.py --repo-root .` after any
  exported-surface edit, before validators (mutate -> sync -> verify).

### High-Confidence Checks

- `run_slice_closeout.py --skip-broad-pytest` pre-lock rehearsal at slice
  boundaries spanning generated surfaces or validator families.
- Bounded fresh-eye slice critique (medium effort) per substantial slice, with
  the packet shape from the operating contract; counterweight pass included.
- Final bundle: `run_slice_closeout.py --verification-lock
  --produce-mutation-coverage` (Python mutation-pool files change in slices 1
  and 2), full `./scripts/run-quality.sh` green.
- `plan_cautilus_proof.py` re-consult after fixture/prompt-affecting changes;
  obey whatever the planner then requires (e.g., scenario registry review).

### External Or Live Proof

- None planned: no push, no release, no live cautilus run. Each is recorded as
  an explicit non-claim with its wake-up follow-up named in the final report.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Bootstrap-shim consistency gate (`--fix`, run-quality wiring, tests) | 73 hand-maintained byte-identical copies have no content-level guard; divergence is silent today | Gate script + tests, broken-copy detection demo, gates green | planned |
| 2 | Public-doc hard-coupling advisory gate + codified policy line | Locks in the 06-11 audit cleanup and resolves handoff Discuss item 1 with a validator instead of prose | Gate script + tests, zero-finding baseline run, policy doctrine in owning doc | planned |
| 3 | Quality-skill nose-as-structural-signal contract | Operator explicitly asked: advisories must drive structural responses, not dup-line reduction | Updated advisory-interpretation surface, skill validators green, plugin mirror synced | planned |
| 4 | Contract-effectiveness cautilus fixture (log-backed, deterministically validated) | Contract effectiveness has no eval surface; real retro violations provide honest log-backed derivation | New fixture file, `validate-cautilus-scenarios` green, explicit live-run non-claim | planned |
| 5 | Closeout: handoff single write, critique, retro, verification lock | Contract-mandated closeout; folds operator-approved handoff hygiene | Handoff diff, critique + retro artifacts, `--verification-lock` proof, commits | planned |

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

Discuss before activation: resolved — the operator approved the bundle scope
in two explicit messages this session (improvement items 2/3/4, the added
nose-as-structural-signal skill request, and second-machine carryover removal)
and granted an 8h active-execution window while asleep. Consequential defaults
taken without a live operator: no push/release (kept local, named as wake-up
decisions), no live cautilus run (planner fence honored; fixture ships
deterministically validated), advisory-not-blocking posture for the new
doc-coupling gate.

## Slice Log

### Slice 1: Activation

- Objective: Activate the operator-approved 8h bundle after plan critique folded six blockers
- Why this approach:
- Commits:
- What changed:
- Alternatives rejected:
- Targeted verification: check_goal_artifact.py --pursue-ready reported pursue_ready: true; proof base c1f7b581 recorded; plan reviewer a507372a97726c30d verdict REVISE folded
- Test duplication pressure:
- Critique:
- Off-goal findings:
- Lessons carried forward:
- Metrics:

### Slice 2: Bootstrap-shim consistency gate

- Objective: Machine-own the 74-copy bootstrap shim's byte-consistency: new blocking gate scripts/check_bootstrap_shim_consistency.py with --fix, normalized the 3 wrapped variants (check_changed_line_coverage, check_standing_doc_provenance, normalize_host_docs), wired check-bootstrap-shim-consistency into run-quality.sh, mirror re-synced. Portability classification: gate stays host-local (canonical block is charness-specific authoring state); the generalizable lesson (consistency-gate response to intentional-duplication advisories) is absorbed into the quality skill in slice 3
- Why this approach:
- Commits:
- What changed:
- Alternatives rejected:
- Targeted verification: 5 new tests pass (drift detect, fix round-trip, nested unfixable, prefix-collision exclusion); gate reports 74/74 canonical on the real tree; ruff, attention-state, packaging, length headroom green; fixed scripts py_compile and run
- Test duplication pressure: 5 new subprocess-style gate tests in tests/quality_gates/, consistent with sibling gate test shape; no duplicate fixture infra added
- Critique:
- Off-goal findings:
- Lessons carried forward:
- Metrics:

### Slice 3: Public-doc hard-coupling advisory gate

- Objective: Lock in the 06-11 audit cleanup with a validator: new advisory scripts/check_public_doc_coupling.py reuses the canonical ISSUE_ANCHOR_RE/is_allowed_issue_anchor_context rule for the unowned exported surfaces (skills/shared/references, docs/generated) and adds a charness self-version-pin arm over all exported guidance (v0.x family + charness <semver>; external tool pins out of pattern). Codified the exported-reusable-guidance class in docs/conventions/provenance-placement.md, which resolves handoff Discuss item 1 at closeout. Portability classification: gate is host-local today (zero-baseline assertion is charness state); the placement policy itself is the portable artifact via provenance-placement.md and the existing standing-doc-provenance quality capability
- Why this approach:
- Commits:
- What changed:
- Alternatives rejected:
- Targeted verification: 6 new tests pass incl. real-repo zero-baseline assertion and external-version negative cases; gate clean on real tree; ruff, doc-links, markdown, attention-state green; mirror synced
- Test duplication pressure: 6 subprocess-style gate tests; reuses canonical regex from skill_text_quality_lib rather than forking the rule
- Critique:
- Off-goal findings:
- Lessons carried forward:
- Metrics:

### Slice 4: Nose advisories as structural signals

- Objective: Upgrade the quality skill's clone-advisory consumer contract: new Clone Families As Structural Signals section in references/inventory-dispatch.md maps each reviewed family to one structural response (machine-owned consistency / owned extraction / generated-surface ownership / design review), forbids total_dup_lines as a reduction target or cross-scanner-version trend, and requires per-family dispositions in the quality artifact; inventory_nose_clones.py notes now carry the same two consumer rules. Slice 1's shim gate is the live exemplar of the intentional-duplication response
- Why this approach:
- Commits:
- What changed:
- Alternatives rejected:
- Targeted verification: 8 nose-advisory tests pass; skill-surface preflight --run-checks all PASS (skills, ergonomics, ownership overlap, attention-state, doc links, markdown); live inventory run renders the new notes (nose 0.7.0, 20 families); prose-pin clean; mirror synced
- Test duplication pressure: no new tests; existing nose-advisory suite covers notes payload shape
- Critique:
- Off-goal findings:
- Lessons carried forward:
- Metrics:

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

- Operator conversation 2026-06-12 (this session): approved improvement ideas
  2/3/4 from the autonomous-improvement proposal, added the
  nose-as-structural-signal skill request, approved removing the
  second-machine proof carryover ("예전에 문제 됐고 이제는 안정화되어서 아예
  빼도 됩니다 ... 자동화 했다가 시간과 비용 너무 많이 들었던 것"), granted an
  8h timebox.
- [docs/handoff.md](../../docs/handoff.md) — v0.42.0 verified state; stale
  re-scope item for the completed 06-11 goal; Discuss items.
- [2026-06-11 goal](2026-06-11-354-nose-quality-public-doc-audit.md) —
  `Status: complete` since commit `b6bbf6f7`; its slice 3/4 already did the
  bounded public-doc audit and reviewer-effort policy, which re-scopes this
  goal's doc-coupling slice to gate-and-policy rather than re-audit.
- [quality latest](../quality/latest.md) — nose 0.7.0 baseline, clone-family
  interpretation (intentional bootstrap fence, #11/#12 candidates), 74-gate
  surface.
- [recent lessons](../retro/recent-lessons.md) — counterweight-miss and
  proof-base traps that seed the contract-effectiveness fixture.
- [skills/shared/references/bootstrap-resolution.md](../../skills/shared/references/bootstrap-resolution.md)
  — why the shim must stay per-file (constrains slice 1 to consistency, not
  centralization).
- [skills/public/quality/references/cautilus-on-demand.md](../../skills/public/quality/references/cautilus-on-demand.md)
  and `evals/README.md` — eval-only fence, log-backed fixture doctrine,
  planner-consult contract (constrains slice 4).

## Interview Decisions

- Execution mode considered: artifact-only draft vs shape-then-pursue in this
  session. Chosen: shape-then-pursue. Reason: the operator said "설계, 실행
  적극적으로 해서 골 만들어봐요" and then granted "최대 8시간" — an explicit
  standing activation request; pausing for a second activation message would
  block on a sleeping operator.
- Shim approach considered: (a) centralize via shared import, (b) code
  generator that stamps shims, (c) consistency gate over hand-maintained
  copies with `--fix`. Chosen: (c). Reason: (a) violates the portability
  doctrine; (b) adds a generator surface for a 5-line block whose only real
  risk is divergence; (c) is the smallest validator that makes the nose fence
  mechanically true.
- Doc-coupling gate posture considered: blocking vs advisory; scan all docs vs
  exported-reusable-only. Chosen: advisory, exported-reusable-only with a
  zero-finding baseline. Reason: standing docs and ledgers are already owned
  by `check_standing_doc_provenance.py` and intentional allowlists; a blocking
  gate over interpretive surfaces invites false-positive churn.
- Cautilus slice considered: (a) run live eval with a self-authored
  justification log, (b) author fixture + deterministic validation only,
  (c) skip entirely. Chosen: (b). Reason: (a) would satisfy the wrapper's
  letter while violating the planner contract (`next_action: none`, operator
  named no failing-log); (c) drops an operator-approved item. (b) ships value
  that the next legitimate log-backed request can execute.
- Nose-signal placement considered: new reference vs extending the existing
  advisory-interpretation owner vs CLAUDE.md prose. Chosen: the owning
  quality-skill surface (exact file resolved in-slice), never CLAUDE.md.
  Reason: portable skill metadata owns routing detail; always-loaded prose is
  the wrong layer.
- Second-machine proof item considered: automate vs keep carrying vs remove.
  Chosen: remove from handoff. Reason: operator explicitly said prior
  automation cost too much and the path has stabilized; carrying a dead proof
  item is handoff noise.
- Push policy considered: treat the 8h grant as push approval vs local-only.
  Chosen: local-only. Reason: pushes are outward-facing; prior goals in this
  repo treated push as explicitly granted per phase, and the operator is
  asleep — the wake-up report names push as the follow-up decision.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

- Fresh-eye status: executed before any mutation — one parent-delegated
  bounded plan reviewer (read-only shared worktree, agent
  `a507372a97726c30d`), verdict REVISE with six foldable blockers, all folded
  below; its over-worry triage is recorded here and the full
  counterweight-paired critique still runs at the slice-5 bundle boundary.
- Folded B1: the shim population is NOT clean today — 71 byte-identical
  one-liner copies plus 3 semantically-identical wrapped variants
  (`check_changed_line_coverage.py`, `check_standing_doc_provenance.py`,
  `normalize_host_docs.py`). Slice 1 scopes by the exact predicate
  `def _load_skill_runtime_bootstrap(` (excluding root
  `skill_runtime_bootstrap.py`'s `_load_skill_runtime_bootstrap_module` and
  test-file name references), adopts the 71-copy majority one-liner as
  canonical (lint-safe: ruff ignores E501), runs `--fix` on the 3 variants,
  re-syncs the mirror, and commits normalization together with the gate.
- Folded B2: issue-anchor scanning over `skills/public|support` is already
  owned blocking by `skill_text_quality_lib.py` (`ISSUE_ANCHOR_RE` +
  `is_allowed_issue_anchor_context`) via `validate_skill_ergonomics`. The new
  gate reuses that canonical regex/skip logic and covers only the unowned
  surfaces: `skills/shared/references/**` and `docs/generated/**`; it must not
  re-judge surfaces the ergonomics sweep owns.
- Folded B3: a naive version-pin arm breaks the zero-baseline claim —
  deliberate external-tool versions exist (`cautilus 0.15.4` in
  cautilus-on-demand.md, create-cli case studies). The pin arm targets
  charness self-version references only (and proves a zero-finding run before
  run-quality wiring); external tool versions are out of pattern, not
  allowlisted one-by-one.
- Folded B4: `skills/public/quality/SKILL.md` is at its exact 200/200 cap.
  Slice 3 lands in the existing advisory-interpretation owner
  `skills/public/quality/references/inventory-dispatch.md` with zero net-new
  SKILL.md lines; no new reference file.
- Folded B5: second-machine retirement also needs a disposition line in
  `charness-artifacts/release/latest.md` (its line ~91 regenerates the item at
  next release closeout otherwise); mid-run check whether
  `skills/public/release/scripts/check_real_host_proof.py` mechanically
  enforces the arm and needs a policy edit vs a disposition.
- Folded B6: proof base recorded now — `c1f7b581` (HEAD == origin/main, clean
  tree except this goal file) is the closeout `--base` for this goal; slice 5
  ordering is explicit: fresh-eye bundle critique BEFORE the locked
  `--produce-mutation-coverage` producer run.
- Over-worry (raised, not folded): shim gate vs nose advisory conflict
  (complementary — fence becomes machine-owned); mirror-drift gate conflict
  (ordering already handles it); fixture wiring breakage (glob auto-discovery
  validates schema only; no scenarios.json/adapter entry required); doc
  anchors as false positives (current numeric scan is zero in scope);
  handoff-retirement legitimacy (06-11 goal verifiably complete at
  `b6bbf6f7`).
- Mid-run checks scheduled: `check_real_host_proof.py` enforcement shape;
  deliberate placement of the two new gate scripts (`scripts/` vs
  `skills/public/quality/scripts/` — changes which validators/dogfood
  obligations fire); regenerate gate-count-bearing surfaces after wiring;
  cautilus adapter pattern classification of the new fixture matches the
  planner re-consult; re-verify the shim count (74 observed vs 73 claimed)
  when building the gate inventory.

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
