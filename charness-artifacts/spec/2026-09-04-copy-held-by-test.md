# Copy-held-by-test: restated identity

Date: 2026-09-04
Status: first slice landed 2026-09-04. Remaining: deferred D47 essay, proof-semantics-adapter stale path list, more closed-decision bodies, authoring-preflight still over budget on teaching not identity.
Owner: documentation principles + the mechanisms table in `docs/development.md`

## Diagnosis

A rule is held by a mechanism or it is prose. After the mechanism exists, restating its identity in docs is waste. The expensive form of that waste is a **copy held by a test**: the doc recopies enums, field grammars, numeric defaults, or exit tables the code already refuses, and when the copy would drift, a test is added to keep the copy honest.

That test is not protection. It is proof the copy should not exist.

The smoking gun is `tests/test_authoring_preflight_reference.py::test_authoring_preflight_lists_current_attention_vocabulary`. It imports `ATTENTION_TERMS` from `tools/validate_attention_state_visibility.py` and requires every term to appear as `` `{term}` `` in `docs/authoring-preflight.md`. The 2026-06-05 goal named this as a feature: "the doc is the single human-facing copy, the test enforces alignment." Alignment of a copy is the class. The terms already live in the validator; the gate already refuses undeclared uses.

A sibling that is *not* this class, and must not be deleted with it:

- Pointer liveness: a test that the doc names a runnable script (`check_skill_surface_preflight.py` exists). That binds a name to an affordance.
- Typed command surface: `check_documented_command_flags.py` / `check_documented_subcommands.py` against `--help`. Operators must type those.
- Describe/verify identity: `describe_closeout_draft_shape.py` rendering live verifier constants, with a test that describe matches verify. The describe script *is* the mechanism; docs that recopy its grammar are the copy.

## Inventory (2026-09-04, six read-only lanes)

Approximate words that can go without hiding a typed command or an exception the code does not name. Overlap (the same enum dumped in three places) is not subtracted; treat the numbers as ranking, not a budget.

### Copy-held-by-test (must die first)

| Site | Copy | Holding test | Cut |
| --- | --- | --- | --- |
| `docs/authoring-preflight.md` banned-term list | `ATTENTION_TERMS` | `test_authoring_preflight_lists_current_attention_vocabulary` | delete list + that test; keep token-shaped teaching + pointer |

No other test iterates a production constant into a `docs/` or `skills/**/*.md` file. Recurrence for this instance is held by `test_authoring_preflight_does_not_recopy_attention_terms`.

### Ranked dumps (code already holds identity; no sync test)

| ~Words | Path | Mechanism | KEEP |
| ---: | --- | --- | --- |
| 2100 | `skills/public/issue/references/closeout-discipline.md` field grammars | `describe_closeout_draft_shape.py`, verify/validate | P4 necessary≠sufficient; typed describe/validate/verify commands |
| 1800 | `skills/public/critique/references/prepare-packet.md` schema/identity | `prepare_packet.py`, identity modules | when-to-run; `--commit`/`--range` |
| 1100–3000 | `skills/public/quality/references/adapter-contract.md` defaults/exits/rule-ids | `quality_policy_defaults.py`, gate `--help` | field *purpose*; `--suggest-budgets` / `--advisory` cues |
| 1200–1500 | `docs/goal-lifecycle.md` binding/observation/close steps | `goal_binding.py`, achieve/issue scripts | Design Center + Authority By Phase |
| 1000–1600 | `docs/deferred-decisions.md` closed D1–D4/D6 bodies | `docs/host-packaging.md`, packaging manifest | Decision/reopen one-liner + link |
| 850 | `skills/public/release/references/critique-boundary.md` claims JSON | `claims_review_schema.py` + scaffold | claims≠critique; planner scaffold |
| 760+660 | web-fetch `routing-table` + `runtime-contract` | `route_public_fetch_routes.py`, classifier | Scope Rule / Acquisition Invariant |
| 650 | `docs/control-plane.md` SoT + per-command encyclopedia | `support_sync_lib.py`, doctor, `cli-reference` | Goals/Non-Goals + one typed line |
| 550 | `docs/agent-task-runs.md` Run field encyclopedia | `task_run_contract.py` and siblings | typed `task run`/`status` |
| 400 | `docs/authoring-preflight.md` 160/4 and dual-inventory numbers | `MAX_CORE_NONEMPTY_LINES`, `CORE_NONEMPTY_HEADROOM_BUFFER` | diverge warning; typed preflight commands |
| 350 | `docs/operator-acceptance.md` Acceptance bullets | host-packaging / CLI / control-plane | short run list |
| 330 | `integrations/{tools,locks}/README.md` field inventories | `*.schema.json` | SoT sentence + do-not-hand-edit |
| 320 | `.agents/claude-host.md` Lane-orchestration lessons | `docs/parallel-execution.md` | host model/idle-reviewer policy |
| ~remaining | README install inventory, AGENTS Documentation restatement, worktree dependency-reuse/exit/doctor table, export-boundary basename loop, operating-contract generated-surfaces restatement, artifact-policy naming enum, issue-backend payload encyclopedia, quality SKILL planner roster, bootstrap-resolution refusal statuses, announcement verification flags, fresh-eye Result Delivery dumps | owning scripts as named in the 2026-09-04 explore reports | typed commands; unlabeled-feature `cleanup --yes`; P4 principles |

JSON registries `docs/public-skill-validation.json` and `docs/public-skill-dogfood.json` are hand SoT, not copies. `docs/cli-reference.md` is generated from `--help`.

## Plan

Execute in this order. Each slice deletes copies and their sync tests if any; it does not add a page.

1. **Standing rule.** Name the class in `docs/documentation-principles.md`. Point the mechanisms table at the anti-copy test and the `--help` flag/subcommand checks.
2. **Kill the smoking gun.** Remove the banned-term list from `docs/authoring-preflight.md`. Replace `test_authoring_preflight_lists_current_attention_vocabulary` with a test that refuses that list form. Keep pointer-liveness tests.
3. **Preflight numbers.** Point `160`/`4` at `MAX_CORE_NONEMPTY_LINES` / `CORE_NONEMPTY_HEADROOM_BUFFER`. Keep the dual-counter diverge warning (preflight vs inventory is an exception the two modules actually hold separately).
4. **`docs/` dumps.** control-plane, agent-task-runs, worktree-prepare (keep unlabeled-feature exception), export-boundary, operating-contract generated surfaces, artifact-policy naming, parallel-execution token rules, goal-lifecycle, deferred-decisions closed packaging bodies, host-packaging inventories, operator-acceptance, README/AGENTS restatements. Shrink `docs-length-baseline.json` only downward.
5. **Skill dumps.** issue closeout grammars → describe script; critique prepare-packet schema; quality adapter-contract literals; release claims JSON; issue-backend payloads. Run `check_skill_cut_safety` before each SKILL.md cut.
6. **Support / shared / host notes.** web-fetch route inventories; bootstrap-resolution refusal encyclopedia; claude-host parallel restatement. Keep host-specific routing that is not in `docs/`.

Stop condition: no test greps a doc for a production constant; ranked dumps above are pointers plus typed commands; length baseline has dropped for every over-budget page this work shortened.

## Non-claims

This record does not claim a general form gate over every "docs mention a number the code also has." Counts in a dated artifact are history. Generated `cli-reference.md` is the `--help` contract. A principle plus a worked example (token-shaped matching) is not a copy of `ATTENTION_TERMS`.
