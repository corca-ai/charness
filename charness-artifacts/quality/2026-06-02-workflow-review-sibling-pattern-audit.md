# Workflow Review Sibling-Pattern Audit
Date: 2026-06-02

## Scope

Audit for sibling patterns behind the recent workflow-boundary fixes without
turning issue-specific wording into another source guard. The scan classified
candidates by interface shape:

- cross-skill or installed-bundle source resolution
- diagnostic, readiness, or status propagation from producer to final consumer
- placeholder/readiness gates
- release, issue, and goal closeout disposition carriers
- source-guard or phrase-detector coupling

This is a static repo-local audit. It does not claim live host, GitHub, release,
or installed-machine proof.

## Scan Method

- Ran `find-skills` read-only bootstrap, then `quality` inventories for public
  specs, adapter/gate design, skill ergonomics, and brittle source guards.
- Used grep only as a candidate generator. Dispositions below rely on owning
  validators, references, and inventory outputs rather than exact issue-number
  or phrase hits.
- Treated "expression difference" as evidence only when a phrase detector
  changes a hard pass/fail outcome. Advisory review queues and bounded
  recommendations are not blockers by themselves.

## Scanned Surfaces

- `skills/public/debug/` and `skills/public/issue/`: invariant-first review,
  sibling-search, causal-review, debug artifact scaffold/validator.
- `skills/public/achieve/` and tests: pursue-readiness, discussion-readiness,
  coordination floors, closeout evidence, disposition review evidence.
- `skills/public/find-skills/`, `skills/public/setup/`, and setup inspection:
  routing discovery, compact AGENTS routing, source-guard scan roots, setup
  recommendation queues.
- `skills/public/release/`, `skills/public/issue/`, and shared closeout docs:
  close keyword, critique, carrier, and backend-state verification.
- `scripts/` quality inventories and validators: adapter/gate design,
  brittle source guards, current-pointer scan, changed surfaces, quality
  artifact validation, critique artifact validation.

## Findings And Dispositions

| ID | Interface Shape | Evidence | Disposition |
| --- | --- | --- | --- |
| F1 | Phrase detectors near policy gates | `inventory_adapter_gate_design.py` reported `script.brittle_review_phrase_detector` for `scripts/setup_agent_docs_lib.py` and `scripts/setup_artifact_policy_lib.py`, both `NON_AUTOMATABLE`; `adapter-gate-review.md` says brittle phrase matching should stay advisory unless a sharper invariant appears. Setup inspection can surface `needs_normalization`, but `inspect_repo.py` exits 0 and emits JSON recommendation state. | rejected for code change: do not promote this to a hard gate. Owner: `quality` adapter/gate review. Rationale: this is a real coupling smell, but the current consumer makes it visible advisory/recommendation state, not a hidden source guard that blocks closeout. |
| F2 | Fixed source-guard rows over prose | `inventory_brittle_source_guards.py --json` found `source_guard_count=0`, `fragile_count=0`, `warnings=[]` over bounded roots `AGENTS.md`, `README.md`, `docs`, and `specs`. Public-spec inventory also found `source_guard_row_count=0`. | rejected for code change: no live brittle source guard to fix in this slice. Owner: `quality` source-guard inventory. Reopen if a new fixed row appears or a hard gate starts reading prose-only phrasing. |
| F3 | Source-guard scanner generalization | `docs/deferred-decisions.md` D19 already defers adapter-resolved current-pointer taint analysis until a second bypassing sibling appears; current helper adoption is the chosen boundary. | deferred-with-owner: owner `scripts/check_current_pointer_writes.py` / `scripts/current_pointer_writer_lib.py`; reopen trigger is D19's second adapter-resolved bypass condition. No new issue filed because the existing deferral is explicit and scoped. |
| F4 | Placeholder/readiness gates | Achieve readiness now separates structural placeholders from consequential activation discussion via `pursue_ready`, `discussion_ready`, and `placeholder_count`; focused tests cover custom routing and discussion readiness. | applied: prior slices already encoded the invariant. No new code; this audit records that the sibling class is covered by structured fields, not by comparing prose variants. |
| F5 | Issue/release/goal closeout disposition | Issue closeout verifies carrier text, close keywords, classification ledger, critique line for bug-class work, and backend state when final; achieve coordination floors now include `Issue closeout:`. | applied: #277 and Slice 1 closed the sibling class for the known carrier path. Non-claim: non-`gh` issue backend live proof remains unproven, already recorded in `docs/handoff.md`. |
| F6 | Diagnostic/status propagation bugs | Debug artifacts now require `## Invariant Proof` with producer proof, final-consumer proof, interface-shape sibling scan, and non-claims; issue causal review cites the same substrate. | applied: Slice 3 owns this class. No broader rewrite because the shared invariant is review-level guidance plus artifact schema, not a framework coupling all skills. |
| F7 | Cross-skill installed/source resolution | Skill ergonomics inventory reported zero heuristic findings across 23 public/support skills, while still requiring prose review; find-skills records canonical paths and referenced paths, and packaging/mirror drift is owned by changed-surface and packaging validators. | rejected for broad rewrite: no evidence justifies a shared dependency-injection layer. Owner: `find-skills`, packaging validators, and skill ergonomics inventory. |
| F8 | Recommendation queues becoming hidden gates | Setup inspection emits typed recommendations with `priority`, `confidence`, `enforcement_tier`, and acknowledgement metadata; tests cover acknowledgement scoping and compact routing acceptance/rejection. Current policy keeps contextual recommendations out of hard gates unless the expected response is clear and false positives are rare. | rejected for code change: leave as structured advisory unless a specific recommendation has low-noise failure semantics. Owner: `setup` inspection and `quality` adapter/gate review. Future consumer drift is the risk to watch: if another command starts treating `needs_normalization`, `review_required`, or `brittle_hard_gate_smell` as a hard failure, reopen this disposition. |

## Disposition Summary

- applied: F4, F5, F6
- rejected: F1, F2, F7, F8
- deferred-with-owner: F3
- issue: none filed; every candidate had an applied, rejected, or existing
  deferred owner. Filing a new issue would duplicate D19 or create process
  churn without a new invariant.

## Non-Claims

- This audit does not prove every historical artifact is migrated.
- This audit does not prove non-`gh` issue backend closeout live behavior.
- This audit does not prove installed plugin/cache propagation beyond existing
  packaging and changed-surface validators.
- This audit does not claim wording differences are harmless everywhere; it
  only rejects treating phrase difference as a hard-failure invariant without a
  structural consumer boundary.
- This audit does not claim F1/F8 have no coupling. It claims the coupling is
  currently advisory by enforcement tier and consumer behavior.

## Commands Run

- `python3 skills/public/find-skills/scripts/list_capabilities.py --repo-root . --read-only`
- `python3 skills/public/achieve/scripts/check_goal_artifact.py --repo-root . --goal-path charness-artifacts/goals/2026-06-02-workflow-review-efficiency-and-generalization.md --pursue-ready`
- `python3 skills/public/quality/scripts/resolve_quality_artifact.py --repo-root . --intent current`
- `python3 skills/public/quality/scripts/inventory_public_spec_quality.py --repo-root . --json`
- `python3 skills/public/quality/scripts/inventory_adapter_gate_design.py --repo-root .`
- `python3 skills/public/quality/scripts/inventory_skill_ergonomics.py --repo-root . --json`
- `python3 skills/public/quality/scripts/inventory_brittle_source_guards.py --repo-root . --json`
- `python3 scripts/check_changed_surfaces.py --repo-root .`
- `rg` scans over source-resolution, diagnostic/status, readiness/placeholder,
  closeout/disposition, and source-guard/phrase-detector candidate terms.

## Next Gate

Run a bounded fresh-eye critique on this audit, specifically asking whether any
rejection hides a real hard-gate coupling, whether F3 needs a new tracked issue
instead of the existing deferral, and whether "expression difference" has been
underweighted or overweighted.
