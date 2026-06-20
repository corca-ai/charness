# Achieve Goal: North-star Phase 4: non-terminality + portability at the remaining irreversible boundaries

Status: active
Created: 2026-06-20
Activation: `/goal @charness-artifacts/goals/2026-06-20-north-star-phase4-boundary-non-terminality.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: **WS-1 (release publish rung-1 + rung-2)** — S0 LOCKED
  (2026-06-20). The concept spec
  `charness-artifacts/spec/2026-06-20-phase4-boundary-non-terminality-concept.md`
  is locked (gating critique PASS-WITH-CONDITIONS, 3 blockers folded §9); it gates
  every impl slice.
- Current slice intent: wire the WS-1 rung-1 per-surface behavioral-verdict
  presence floor + the rung-2 distinct-channel observer onto the release publish
  boundary, **before** `ensure_release_issues_closed`
  (`publish_release_execute.py:187`). Binding non-terminality rule: **F2a** —
  issue-close advances on rung-1 record-presence only; the automated
  distinct-channel confirmation is a recorded observable for the human rung-2
  audit, never an automated proceed-gate. Additive (supplement the line-163
  proxy, do not delete it). This intent spans the WS-1 commits; critique + broad
  proof do not re-fire within it (meaningful-slice-cadence).
- Next action: implement WS-1 per the locked spec §2 + F2a, seeded
  published-release fixture proof, bounded fresh-eye slice critique, then
  `run_slice_closeout.py --skip-broad-pytest`.
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

Extend the validated north-star non-terminality doctrine (equip a judge; teeth
only where a wrong answer escapes; **non-terminal per-unit disposition over
terminal-green**; at irreversible boundaries confirm via a **distinct observer
AND a distinct evidence channel**) to the irreversible boundaries Phase 2 left
untouched — **and** make the one "boundary" charness does **not** own portable
instead of pretending charness owns it. Three workstreams, concept-first, under
the Phase-0 migration discipline:

- **WS-1 — release publish non-terminality.** A real charness-owned irreversible
  boundary that today greens terminally: `publish_release_execute.py:163` sets
  `release_verified = (gh release view returncode == 0)` and gates issue-closeout
  (`ensure_release_issues_closed`) on that single proxy. The pre-publish critique
  gate runs *before* the published state exists; the only post-publish check
  re-reads the **same `gh` channel**. Wire a **rung-1** per-surface
  behavioral-verdict presence floor (refuses silence before issue-closeout, never
  declares completion) + a **rung-2** distinct-channel observer that confirms the
  published release through a channel **distinct from `gh release view`**.

- **WS-2 — Direction-3 (the second #386 consumer).** `issue_tool.py
  verify-closeout` got rung-1 behavioral-verdict + AI-provenance floors in the
  prior goal's S1, but reads **no HOTL ledger disposition**. Add the rung-1 floor
  that **refuses on undispositioned HOTL entries** (a carrier entry present
  without one of the typed HOTL statuses or `local-only-by-contract`). Reuse the
  `proof_mismatch.py` structural template + the HOTL status vocabulary
  (`ledger-and-dispositions.md`). rung-2 honesty stays the resolution critique
  (doctrine already mandates it). Mostly *reuse* of the proven pattern.

- **WS-3 — prod-apply portability deleak (DEEP).** charness owns **no** prod-apply
  boundary — "apply" is a consumer (ceal) concept; charness must not even *know*
  the term. Yet it currently leaks consumer vocabulary into its portable core.
  Make the irreversible-external-write boundary **vocabulary-neutral** and
  **adapter-fillable**: a consumer's apply/deploy/restart plugs into the
  non-terminal seam without charness hardcoding the name. DEEP scope = **Tier 1**
  (remove `ceal-dev`/`ceal` consumer-name leak from portable doctrine/examples) +
  **Tier 2** (rename the core `applied-restarted` closeout-taxonomy token to a
  vocabulary-neutral term with a grandfathered alias; make the
  `goal_artifact_discussion.py` production/irreversible detection vocabulary
  adapter-provided rather than a hardcoded `apply/restart|deploy` English regex;
  rename `Post-Apply Checkpoint Classification`).

**Success = (a) a wrong answer's escape path closes at release publish (rung-1 +
rung-2, no terminal-green gate); (b) `verify-closeout` refuses on undispositioned
HOTL entries; (c) charness no longer hardcodes a consumer's boundary vocabulary —
`apply`/`ceal-dev`/`applied-restarted`/`deploy` leave the portable core and the
boundary becomes an adapter-named, vocabulary-neutral seam, with the locked tests
still green and no guard lost.** "Fewer lines / fewer gates" is NOT the metric (it
is a north-star failure signature).

## Non-Goals

- **Not bulk gate deletion / fewer-gates-as-metric** (north-star failure
  signature). Per-surface migration discipline only.
- **Not an Nth terminal-green gate** (the #386 anti-pattern). Every new rung-1
  floor stays presence/form-only; per-unit *honesty* stays a rung-2
  human-audited distinct-channel observer.
- **Not hardening a charness-owned prod-apply boundary** — charness owns none.
  WS-3 is portability deleak (make the boundary adapter-fillable + neutral), NOT
  boundary-hardening. Treating "apply" as a charness boundary is the error this
  goal corrects.
- **Not the skill-body bloat redesign** (the deferred P3/WS-B body redesign for
  impl/debug/quality/achieve + the ~16 untouched capped bodies) — that is a
  **separate track** (operator-directed 2026-06-20), already captured in the
  overhaul-sweep goal's Operator Decision Queue + retro. WS-1/2/3 will edit the
  specific skill surfaces they touch (release/issue/hotl/achieve), under headroom
  discipline, but do not pursue the broad bloat audit.
- **Not a live GitHub release this run.** Default = implement + seeded proof
  locally; a live release exercising the new WS-1 floors is operator-approved,
  phase-scoped (does not carry forward), and queued in the Operator Decision Queue.
- **Not the separate tracks:** #388 mutation regression, #371 chromium cleanup,
  #392 gather-X — orthogonal, out of scope.

## Boundaries

- **Concept-first (gating).** S0 specs the shared non-terminality contract (WS-1
  rung-1/rung-2 on release publish; WS-2 Direction-3 HOTL floor) **and** the WS-3
  portability-deleak contract (what is renamed vs adapter-provided; the migration
  discipline per surface; the grandfathered-alias shape for the taxonomy rename).
  It is **locked by critique** before any implementation slice.
- **Migration discipline is binding (the Phase-0 hard rule), every surface.**
  Name the failure-mode → land the replacement first → prove it catches a
  *seeded* instance → only then delete the old surface + record a one-line
  rollback ref. Stage surface-by-surface. **Tripwire:** the first lifecycle
  transition that closes on aggregate/proxy proof *after* a slice ships triggers a
  mandatory north-star retro before further rollout.
- **No terminal-green gate (the #386 anti-pattern).** rung-1 refuses
  silence/malformation only; honesty is always the rung-2 distinct-channel
  observer. "All units present ⇒ done" is forbidden.
- **WS-1 distinct-channel (P4).** rung-2 must confirm the published release
  through a channel **distinct from `gh release view`** (the same-proxy re-read
  P4 forbids) — e.g. an HTTP fetch of the published release URL or an install
  probe — or record a typed non-`verified` disposition; never a second `gh
  release view` standing in for confirmation. Reuse the partial implementation in
  `charness-artifacts/spec/release-post-create-verification-suppression.md`.
- **WS-2 adapter-aware.** The HOTL ledger is adapter-owned (path/schema). The
  Direction-3 rung-1 floor reads the **carrier-body** per-issue disposition
  (presence/form), staying adapter-portable; it must not assume a fixed ledger
  file path. It extends the existing `evaluate_behavioral_verdict` family, not a
  new parallel gate where one suffices.
- **WS-3 vocabulary-neutrality is the portability axis.**
  `apply`/`restart`/`deploy`/`applied-restarted`/`ceal-dev` are
  **consumer-axis** values, NOT charness singletons. The deleak must (a) rename
  the core taxonomy token to a vocabulary-neutral term **with a grandfathered
  alias** so existing artifacts/consumers do not break, (b) make the
  discussion-gate detection vocabulary **adapter-provided** (not a hardcoded
  English deploy-word regex), (c) genericize doctrine/examples so a non-ceal
  consumer sees no ceal-specific lane. **Honest contingency:** if S0 finds a
  Tier-2 surface is contract-pinned or the rename is genuinely lossy (the
  template's WS-B failure mode), land what is safe + **defer the rest with cause**
  — forcing a rename to hit a "deleak count" is the line-count failure signature.
  Distinguish a *leak* (consumer vocab in charness core doctrine/taxonomy/gate)
  from a legitimate *adapter example* (`adapter.example.yaml: default_repo: ceal`,
  "e.g. `ceal github`", and the **`slack.ceal-dev` profile-id capability-resolution
  examples** at `docs/runtime-capability-contract.md:117`,
  `docs/capability-resolution.md:140,143` + their tests) that demonstrates the
  seam working as intended — the latter class is **protected, not a target** (S0
  enumerates it so WS-3a does not over-fire). **WS-3a (Tier-1) is the riskier
  deleak**, not Tier-2: the plan critique found Tier-2's `applied-restarted` token
  is *not* contract-pinned (the closeout-delegation gate is resolution-based and
  token-agnostic), so its grandfathered alias is insurance S0 may judge
  unnecessary — while Tier-1 is the slice that can over-fire (strip a protected
  `slack.ceal-dev`) or under-clean (miss the
  `test_goal_artifact_blocked_matrix.py` fixture). Every deleak slice re-syncs the
  `plugins/` mirror (`sync_root_plugin_manifests.py`) before verify — the
  `staged-plugin-mirror-drift` gate fails an unsynced rename.
- **Governing-surface edits** (design-north-star.md, achieve
  lifecycle/goal-artifact references, skill bodies, gate scripts, taxonomy
  tokens) each get a **bounded fresh-eye critique before commit**.
- **External side-effect scope:** WS-1 touches the release-publish path. Default =
  implement + seeded-instance proof **locally**; any **live** release is
  operator-approved and phase-scoped, and that approval does not carry forward.
  Name which phase or bundle any approved publish / push / remote-CI applies to.
  After an approved lane completes, done-early test-only continuation is local by
  default (batch remote proof, run CI once over the final bundled state).

## Discuss before activation

Discuss before activation: RESOLVED — all three consequential defaults (WS-1 live
release proof; WS-3 deep scope touching governing surfaces; the prod-apply +
skill-redesign scope split) were resolved with the operator in the shaping
conversation (2026-06-20). Details below; recorded so a fresh session inherits
the resolution rather than re-litigating it.

- **Live release proof (WS-1) — RESOLVED.** Local implement + seeded-instance
  proof; a live GitHub release exercising the new floors is deferred to the
  Operator Decision Queue, operator-approved + phase-scoped (approval does not
  carry forward). Mirrors the template goal's R2 external-write stance.
- **WS-3 deep scope touches governing surfaces (core taxonomy token + gate
  regex) — RESOLVED.** Operator directed DEEP (Tier 1 + Tier 2). Each
  governing-surface edit gets a bounded fresh-eye critique + the migration
  discipline (grandfathered alias, seeded proof, rollback ref). Honest
  defer-with-cause applies if S0 finds a surface contract-pinned/lossy.
- **Scope of "prod apply" — RESOLVED.** charness owns no prod-apply boundary;
  WS-3 is a portability deleak, not boundary-hardening. The skill-body bloat
  redesign is an explicitly separate track. Phase 4 = WS-1 + WS-2 + WS-3.

## User Acceptance

What the user can do to verify completion directly.

- Read the S0 spec and confirm it embodies the doctrine: no terminal-green gate
  added; rung-1/rung-2 split explicit for WS-1; the WS-3 vocabulary-neutrality +
  grandfathered-alias contract explicit.
- **WS-1:** on a seeded published-release fixture, confirm the publish path now
  records a per-surface behavioral verdict (or a typed non-`verified`
  disposition) **and** a rung-2 confirmation via a channel distinct from `gh
  release view` **before** `ensure_release_issues_closed` proceeds — not a
  returncode-only green.
- **WS-2:** on a seeded carrier with an undispositioned HOTL entry, confirm
  `verify-closeout` **FAILS before `CLOSED` can green**; a typed HOTL disposition
  (or `local-only-by-contract`) PASSES (render-not-declare).
- **WS-3:** `grep -rn "ceal-dev" skills/ scripts/ tests/` returns no
  portable-core doctrine/taxonomy/fixture leak — **only the protected
  `slack.ceal-dev` capability-resolution adapter examples**
  (`docs/runtime-capability-contract.md`, `docs/capability-resolution.md` + their
  tests) remain, deliberately. The core closeout-taxonomy token is
  vocabulary-neutral (with a grandfathered alias if S0 keeps one); the
  `goal_artifact_discussion.py` detection vocabulary is adapter-provided. The
  pinned producer tests (`test_goal_artifact_producers.py`) +
  closeout-delegation tests + `test_goal_artifact_blocked_matrix.py` still pass;
  the plugin mirror is re-synced; no guard lost.
- Gate suite green at the bundle boundary (broad pytest).

## Agent Verification Plan

### Low-Cost Checks

- Commit boundary: `validate_skills`, `check_skill_contracts`, `check_doc_links`,
  `check-markdown`, `ruff`, `check_python_lengths`, the locked floor/closeout
  tests for any touched gate (`test_issue_closeout_verifier.py`, the release
  publish tests, the achieve floor/taxonomy tests), plugin-mirror sync +
  `staged-plugin-mirror-drift`. For the WS-3 token rename additionally: the
  pinned producer tests (`test_goal_artifact_producers.py`) +
  `goal_artifact_closeout_delegation` tests.

### High-Confidence Checks

- Slice boundary: bounded fresh-eye critique per slice; **seeded-instance proof**
  for each migrated floor/surface (the replacement catches the seeded failure
  *before* the old surface is deleted); `run_slice_closeout.py`.

### External Or Live Proof

- Bundle boundary: broad pytest (record the verification lock).
- WS-1 live release proof: only if the operator approves; otherwise record
  `skipped:` and name the un-run proof level honestly (Honest Proof Discipline).

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| S0 | Concept spec + gating critique: lock the shared non-terminality contract (WS-1 rung-1/rung-2 on release publish; WS-2 Direction-3 HOTL floor) + the WS-3 portability-deleak contract (rename-vs-adapter-provide map; grandfathered-alias shape — or straight rename if S0 judges the alias unneeded; per-surface migration discipline; the **complete `ceal-dev` leak inventory incl. the test fixture**; the **protected `slack.ceal-dev` adapter-example set**; the plugin-mirror sync barrier) | concept-first decision; gates every impl slice | spec artifact under `charness-artifacts/spec/` + critique PASS folded | **done** (`spec/2026-06-20-phase4-boundary-non-terminality-concept.md` LOCKED; gating critique PASS-WITH-CONDITIONS, 3 blockers folded §9) |
| WS-1 | Wire rung-1 per-surface behavioral-verdict presence floor + rung-2 distinct-channel observer onto the release publish boundary (before `ensure_release_issues_closed`); reuse the post-create-verification spec | a real charness boundary with confirmed terminal-green (`publish_release_execute.py:163`) | seeded published-release proof + fresh-eye + tests; no terminal-green gate | pending |
| WS-2 | Add the refuse-on-undispositioned-HOTL-entry rung-1 floor to `verify-closeout` (extend `evaluate_behavioral_verdict` family; reuse `proof_mismatch.py` pattern + HOTL status vocab) | the second #386 consumer; rung-1 HOTL floor absent in code | seeded undispositioned-entry proof (FAILS before CLOSED; typed disposition PASSES) + fresh-eye + tests | pending |
| WS-3a | Tier 1 deleak (**the riskier slice**): remove the `ceal-dev` consumer-name leak from portable doctrine/examples (`lifecycle.md:342,353`, `goal-artifact.md:219`, `blocked_matrix.py:7` comment) **and the pinned fixture `test_goal_artifact_blocked_matrix.py:38`**; replace with vocabulary-neutral, adapter-named lane examples; **preserve the protected `slack.ceal-dev` capability-resolution adapter examples**; sync the `plugins/` mirror | clearest portability violation, but over-/under-fire risk | `grep -rn "ceal-dev" skills/ scripts/ tests/` clean except protected sites + doc-link/markdown gates + mirror-drift green + fresh-eye | pending |
| WS-3b | Tier 2 deleak: rename `applied-restarted` taxonomy token → neutral term (S0 decides straight-rename vs grandfathered alias — the gate is token-agnostic, so the alias may be unneeded); genericize `goal_artifact_discussion.py:18,22` detection vocabulary to adapter-provided; rename `Post-Apply Checkpoint Classification`; sync the `plugins/` mirror | the deep portability surgery; migration-disciplined | seeded proof the rename resolves; producer/closeout-delegation/`test_goal_artifact_blocked_matrix` tests green; mirror-drift green; rollback refs; fresh-eye; **defer-with-cause** only if a surface proves genuinely contract-pinned/lossy | pending |
| S4 | Closeout: broad proof, retro, dispositions, honest non-claims, flip to complete | bundle boundary | final verification populated; disposition review (rung 2) | pending |

## Operator Decision Queue

Operator-only decisions surfaced at shaping; none blocks safe local progress.

- Decision: run a **live** GitHub release that exercises the new WS-1 rung-1/rung-2
  floors on a real version.
  - Owner: operator
  - Why deferred: the goal contract scopes WS-1 to local implement + test +
    seeded-instance proof; any live release is operator-approved + phase-scoped
    (approval does not carry forward). Local seeded proof is the closeout default.
  - Unblock action: operator names a target version and approves one live release run.
  - Revisit trigger: the next real `release` cut once the operator approves the
    external write.
- Decision (carried, not owned by this goal): file the **P3 skill-body redesign
  follow-on** (separate track) — already in the overhaul-sweep goal's ODQ + retro.
  - Owner: operator
  - Why deferred: separate track; not this goal's scope.
  - Unblock action: operator approves filing via `issue`, or starts the follow-on goal.
  - Revisit trigger: starting the WS-B body-redesign follow-on.

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
  - `Routing: S0` — `find-skills --recommend-for-task` (concept spec + gating
    critique) → public skills `spec` (author the contract) + `critique` (gating
    critique), with `release`/`hotl` as the WS-1/WS-2 domain skills; `achieve` is
    the goal operator. Recorded read-only.
- **Gather step** — when `## Context Sources` names an external source
  (URL / Slack / Notion / Docs / Drive), add a `Gather:` line here pointing at the
  gathered asset, or write `Gather: n/a — <reason>` when no external context
  applies.
- **Release step** — when this run touches a release surface (a version bump or
  install-manifest edit), add a `Release:` line here pointing at the release
  proof, or write `Release: n/a — <reason>`. (Expected: WS-1 edits the publish
  *code path* but does not cut a release / bump a version — likely a
  `Release: n/a` opt-out at closeout.)
- **Issue closeout step** — when this goal resolves tracked GitHub issues, add
  an `Issue closeout:` line naming the close-intended issue numbers, carrier
  (`direct-commit`, PR body, release commit, or manual fallback), and
  `issue_tool.py validate-closeout-draft` / `verify-closeout` proof. If a
  tracked issue appears in `## Context Sources` as context only, use
  `Issue closeout: n/a — <reason>`.

## Slice Log

- **S0 — concept spec + gating critique (done, 2026-06-20).** Authored
  `charness-artifacts/spec/2026-06-20-phase4-boundary-non-terminality-concept.md`
  from direct code reads of every load-bearing surface (release publish/post-create/
  issue-closeout, `proof_mismatch.py`, HOTL ledger vocab, achieve taxonomy/discussion/
  closeout-delegation, the 4 pinned tests). Locked: the rung-1/rung-2 split per
  workstream (no terminal-green); the **complete leak inventory L1–L6 / protected
  set P1–P5** including **two sites the plan critique missed** —
  **P4** (`test_proof_semantics_adapter.py:244` `ceal-dev` is a *domain-blindness
  guard*, protected) and the **T4/heading pinned tests**
  (`prescribed-skill-closeout-contract.md:227`, `test_workflow_safety_docs.py:14`);
  WS-3b is a **straight rename (no grandfathered alias)** (gate is token-agnostic;
  drift test is membership-based) with neutral token `instance-synced`; WS-3b(b-ii)
  is **Option A** (adapter-provided deploy-vocab with behavior-preserving English
  default). A bounded fresh-eye **gating critique** (read-only, distinct agent
  context, verified against actual code) returned **PASS-WITH-CONDITIONS**; 3
  blockers folded (§9): WS-1 **F2a** presence-only/non-automated-gate + corrected
  rung-2 location (the release critique gate is *pre-publish*, so rung-2 is a
  durable post-publish disposition review); WS-2 `local-only-by-contract` is
  *newly enforced* not pre-existing; `evaluate_source_preservation` is the in-file
  template. Routing: `find-skills` → `spec` (author) + `critique` (gate).

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order. (No external URL/Slack/Notion
source — `Gather: n/a` expected.)

- [design north star](../../docs/design-north-star.md) — the governing doctrine;
  names the irreversible boundary set (issue/PR close, release publish, external
  writes incl. apply-to-prod, deletions) + the distinct-observer/channel P4 rule.
- [north-star overhaul roadmap](../../docs/north-star-overhaul-roadmap.md) Phase 4
  — the plan of record (release publish, prod apply, Direction-3) + the Phase-0
  migration discipline.
- [overhaul-sweep goal](2026-06-20-north-star-overhaul-sweep.md) — the **template**
  + the proven rung-1/rung-2 + floor-grammar pattern (S1 issue closeout, S2
  `goal_artifact_floor_grammar.py`).
- [per-unit-disposition concept spec](../spec/2026-06-20-per-unit-disposition-concept.md)
  — the locked rung-1/rung-2 contract WS-1/WS-2 reuse.
- [**Phase-4 concept spec (S0, LOCKED)**](../spec/2026-06-20-phase4-boundary-non-terminality-concept.md)
  — this goal's locked S0 contract; gates every impl slice (WS-1/WS-2/WS-3a/WS-3b).
- [release-post-create-verification-suppression spec](../spec/release-post-create-verification-suppression.md)
  — the partial WS-1 post-publish verification implementation to extend.
- HOTL [ledger-and-dispositions](../../skills/public/hotl/references/ledger-and-dispositions.md)
  — the typed HOTL status vocabulary WS-2's floor enforces presence of.
- [recent-lessons](../retro/recent-lessons.md) — the pre-cut lossless+contract-safe
  check, bloat-diagnoses-are-hypotheses, and gate-failure-exact-invocation lessons.
- **Session surface maps (folded inline, not checked-in files):** WS-1 terminal-green
  at `skills/public/release/scripts/publish_release_execute.py:163` (issue-closeout
  gates on a single `gh release view` returncode; no distinct-channel post-publish
  observer); prod-apply-not-charness-owned verdict (charness owns only release
  publish + issue/PR close; HOTL is the framework it ships to consumers); Direction-3
  scope (`issue_verify_closeout_body.py:224-258` behavioral-verdict floor exists but
  reads no HOTL disposition; `proof_mismatch.py` is the structural template);
  WS-3 leak grep (Tier 1 `ceal-dev` in `achieve/references/lifecycle.md:342,353` +
  `goal-artifact.md:219` + `goal_artifact_blocked_matrix.py:7`; Tier 2
  `applied-restarted` taxonomy token + `goal_artifact_discussion.py:18,22` regex +
  `Post-Apply Checkpoint Classification`).

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Anti-anchoring axis recorded per value.

- **Prod-apply scope.** Family: (A) harden the apply framework / (B) drop —
  two-boundary scope / (C) keep all three literally. **Chosen: REFRAMED as WS-3
  portability deleak** (operator correction: "apply" is consumer-specific; charness
  must not even know the term — portability). `axis: consumer/host` — the boundary
  vocabulary varies by consumer; it is exactly the portability axis, not a charness
  singleton. Rejected: A imports ceal vocabulary into charness; B leaves the leak in
  place; C — no charness prod-apply surface exists (surface mapping confirmed).
- **WS-3 depth.** Family: shallow (Tier 1 only) vs deep (Tier 1 + Tier 2). **Chosen:
  deep** (operator directed "깊게"). Risk folded: Tier-2 token rename is
  migration-heavy → grandfathered alias + seeded proof + rollback ref + honest
  defer-with-cause baked into Boundaries.
- **Run mode.** Family: artifact-only (shape + stop) vs implementation-continuation.
  **Chosen: artifact-only** (operator "골은 만들고 멈추기"). `/goal` activation is the
  operator's separate action; this draft does not execute slices.
- **Skill-body redesign placement.** Family: in-scope WS / separate track / do it
  first instead. **Chosen: separate track** (operator directed). Consistent with the
  migration discipline (one goal ≠ two big concepts) + the retro caution that bloat
  diagnoses are hypotheses, not mandates to cut.
- **Live release proof (WS-1).** Family: local+seeded vs live-this-run. **Chosen:
  local+seeded**, live deferred to ODQ. `axis: external-write boundary` —
  operator-approved + phase-scoped, does not carry forward.
- **Anti-anchoring axis records:** WS-3 vocabulary = `axis: consumer` (the leak is a
  portability-axis violation); release publish = `single-point: charness's own
  release surface`; HOTL ledger = `axis: adapter` (path/schema adapter-owned →
  WS-2 floor reads the carrier body, not a fixed path).

## Plan Critique Findings

**Bounded fresh-eye PLAN critique — PASS-WITH-CONDITIONS (2026-06-20), folded.**
A different agent context verified the plan's eight load-bearing claims against
the **actual code** (distinct evidence channel, the #386 discipline), then judged
plan soundness adversarially. All eight claims **CONFIRMED** at the cited
file:lines: WS-1 terminal-green (`publish_release_execute.py:163`
`release_verified = returncode == 0`; `:187` issue-closeout gated only on it;
`verify_release_visible` only retries the *same* `gh release view`, no distinct
channel); the partial post-create spec is genuinely extensible; the Direction-3
gap is real (`evaluate_behavioral_verdict` spans exactly 224-258, accepts a HOTL
status as a satisfying *value* but never enforces a typed disposition per HOTL
*entry*); `proof_mismatch.py` is a real reusable template (already folded by both
achieve and issue closeout); the HOTL vocabulary matches; the Tier-1/Tier-2 leak
sites are all present.

The rung-1/rung-2 split is honored throughout (WS-2's floor is genuinely
presence/form-only — refuses a missing line, lets a typed disposition pass, never
classifies honesty). Sequencing S0→WS-1→WS-2→WS-3a→WS-3b→S4 is correct (no
cross-workstream merge hazard: release/issue surfaces don't overlap the achieve
taxonomy/regex surfaces). Migration discipline is correctly method-stated.

**Three blockers folded:**

- **A — WS-3a `ceal-dev` inventory was incomplete.** The pinned test fixture
  `tests/quality_gates/test_goal_artifact_blocked_matrix.py:38` (`_RUNNABLE_LANE
  = "- Lane: ceal-dev apply/restart ..."`) was omitted, and the acceptance grep
  excluded `tests/`. **Folded:** added the fixture to WS-3a's surface list and
  widened the acceptance grep to `skills/ scripts/ tests/`.
- **B — leak-vs-adapter-example boundary under-specified.** `ceal-dev` also
  appears as a **legitimate profile-id adapter example** (`slack.ceal-dev`) at
  `docs/runtime-capability-contract.md:117`, `docs/capability-resolution.md:140,143`,
  and the capability-resolution tests — exactly the protected "adapter example"
  class, not a leak. A naive sweep would over-fire on 6 files the goal never
  classified. **Folded:** S0 must enumerate the protected `slack.ceal-dev`
  capability-resolution sites; WS-3a must not strip them.
- **C — plugin-mirror sync barrier not named in the slices.** Every
  `ceal-dev`/`applied-restarted` source site has a `plugins/charness/...` mirror;
  the `staged-plugin-mirror-drift` gate fails a rename that doesn't re-sync.
  **Folded:** an explicit `sync_root_plugin_manifests.py` step inside WS-3a/WS-3b
  before verify.

**Over-worry raised, deliberately NOT folded (recorded so a fresh session
doesn't re-add rigor):**

- The `applied-restarted` rename is **lower-risk than the goal framed it**: the
  closeout-delegation gate is resolution-based and token-agnostic by design
  (`goal_artifact_closeout_delegation.py:22-23`), and the only drift test asserts
  *membership in lifecycle.md*, not the literal token — **no contract test pins
  it**. The grandfathered-alias machinery is defensible insurance but arguably
  over-engineered; S0 may conclude a straight rename + doc/fixture/mirror update
  suffices. The defer-with-cause hatch is good caution to keep, but Tier-2 is the
  *safer* deleak — **WS-3a (Tier-1), not WS-3b, is the slice most likely to
  over-fire or under-clean.**
- **No missing irreversible boundary.** design-north-star names deletions as
  irreversible, but roadmap Phase 4 deliberately scopes to release publish +
  prod-apply + Direction-3; deletions are out of *this* phase by plan-of-record
  design, not a gap.

**Reviewer provenance:** bounded fresh-eye subagent, read-only inspection
(`git show`/`grep`/`Read`, no worktree mutation), verified against actual code +
ran the leak greps. The **gating concept critique** (S0) is a separate, deeper
pass during activation that locks the spec before any impl.

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

To be populated at closeout with the concrete per-workstream verification
commands (see `## User Acceptance` for the acceptance shape).

## Auto-Retro

Retro dispositions: TODO — disposition every surfaced improvement, or record the explicit no-improvement opt-out
Structural follow-up: TODO — when the retro names a transferable waste item (a `## Sibling Search` trigger), classify its structural destination (`applied: <gate/hook/validator/test/contract change>` / `issue #N (recurs:|novel: <reason>)` / `repo-local guard: <path>` / `none — <reason>`); delete this line when no transferable waste was named
