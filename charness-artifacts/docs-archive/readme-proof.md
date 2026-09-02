# README Proof Ledger

> Status: retired 2026-09-02
> No successor; dated record.

This ledger maps reader-facing README and operator claims to the proof layer
that currently owns them. It is not a second test runner. It is the current
claim-by-claim index that says what must be trusted, what is already checked,
and what still needs stronger proof.

## Terms

- Claim: a reader-facing promise in README or operator docs.
- Acceptance criterion: the behavior that would make the claim true enough for
  an operator to rely on it.
- Proof owner: the layer that can prove or falsify the claim. Owners are
  deterministic, delegated review, HITL/operator, or deferred.
- Evidence: a concrete repo path, checked artifact, command, or review record.
- Freshness rule: the change that requires the evidence to be refreshed.

## Direction

The target is a single Specdown report that lets a reader inspect the current
contract and see proof for each acceptance criterion. The report should include:

- this ledger, or a generated successor with the same claim-to-proof shape;
- deterministic executable checks for local scripts, docs, and CLI behavior;
- explicit reviewer or operator evidence when a claim is semantic or host-bound.

The ledger indexes evidence; it does not search for evidence or decide that a
product claim is satisfied on its own.

## Claim Ledger

| ID | Source | Claim / acceptance criterion | Proof owner | Current evidence | Freshness rule | Status | Gap / next proof |
| --- | --- | --- | --- | --- | --- | --- | --- |
| README-BOOTSTRAP | [README.md](../../README.md) Quick Start | Python 3 plus [init.sh](../../init.sh) installs the managed `charness` CLI and host plugin bundle. | Deterministic plus HITL/operator | [init.sh](../../init.sh), [charness](../../charness), [packaging/bootstrap-python.json](../../packaging/bootstrap-python.json), [packaging/bootstrap-requirements.txt](../../packaging/bootstrap-requirements.txt), [scripts/validate_packaging.py](../../scripts/validate_packaging.py), [scripts/validate_packaging_committed.py](../../scripts/validate_packaging_committed.py), [tests/charness_cli/test_managed_install.py](../../tests/charness_cli/test_managed_install.py) | Refresh when install script, bootstrap manifests, host plugin layout, or packaging validators change. | Partial | Local bootstrap shape is checked; real host install success still needs operator or CI environment proof. |
| README-INIT-ROUTE | [README.md](../../README.md) Quick Start | "Use charness to initialize this repo" should route to `charness:setup` and update [AGENTS.md](../../AGENTS.md) plus related settings through ordinary diffs. | Deterministic plus delegated review | [skills/public/setup/SKILL.md](../../skills/public/setup/SKILL.md), [skills/public/setup/references/](../../skills/public/setup/references/), [tests/quality_gates/test_setup_inspect_policy.py](../../tests/quality_gates/test_setup_inspect_policy.py) | Refresh when README wording, setup skill metadata, init references, or routing fixtures change. | Partial | Add focused operator evidence for the exact Quick Start prompt when the route changes. |
| README-NORMAL-PROMPTS | [README.md](../../README.md) Quick Start and Workflow Routes | After initialization, users can prompt normally; `charness` supplies routing context without requiring skill names each time. | Delegated review plus human-auditable docs | [AGENTS.md](../../AGENTS.md), [docs/index.md](../../docs/index.md), [skills/public/](../../skills/public/) | Refresh when AGENTS startup guidance, skill descriptions, or README prompt guidance changes. | Partial | Review the normal-prompt route when startup guidance or skill triggers change. |
| README-CLI-STATE | [README.md](../../README.md) Quick Start | `charness --help`, `charness doctor`, and `charness update` let humans and agents inspect local harness state instead of guessing. | Deterministic plus Specdown | [docs/cli-reference.md](../../docs/cli-reference.md), [.agents/command-docs.yaml](../../.agents/command-docs.yaml), [scripts/render_cli_reference.py](../../scripts/render_cli_reference.py), [tests/quality_gates/test_command_docs_gate.py](../../tests/quality_gates/test_command_docs_gate.py), [specs/tool-doctor.spec.md](../../specs/tool-doctor.spec.md) | Refresh when CLI commands, generated reference ownership, doctor output, or command-doc gates change. | Partial | Existing checks prove command surface and doctor behavior, not every semantic workflow claim behind update. |
| README-UPDATE-ALL | [README.md](../../README.md) Quick Start | `charness update all` refreshes tracked external tools and bundled support skills. | Deterministic plus HITL/operator | [scripts/update_tools.py](../../scripts/update_tools.py), [scripts/sync_support.py](../../scripts/sync_support.py), [docs/development.md](../../docs/development.md), [docs/cli-reference.md](../../docs/cli-reference.md), [tests/charness_cli/test_update_output.py](../../tests/charness_cli/test_update_output.py), [tests/control_plane/test_sync_support.py](../../tests/control_plane/test_sync_support.py) | Refresh when update manifests, support-skill sync policy, CLI wiring, or host packaging changes. | Partial | Dry-run and local helpers are checked; real external tool freshness remains operator or CI proof. |
| README-WORKFLOW-ROUTES | [README.md](../../README.md) Workflow Routes and [docs/workflow-routes.md](../../docs/workflow-routes.md) | Common project and existing-repo prompts route to the intended public workflow skills. | Deterministic plus human-auditable docs | [skills/public/](../../skills/public/), [charness-artifacts/capability-catalog/latest.md](../../charness-artifacts/capability-catalog/latest.md) | Refresh when README route examples, public skill descriptions, or capability catalog output change. | Partial | Keep route examples and the capability catalog aligned; use focused review for semantic routing changes. |
| README-ACHIEVE-GOALS | [README.md](../../README.md) Workflow Routes and [docs/workflow-routes.md](../../docs/workflow-routes.md) | Long-running or autonomous objectives use `achieve` to shape and freeze a Goal Draft, bind it to a provider-backed Goal Run, and resume with the exact `/goal #N` objective while the parent cursor carries the next-child decision. | Deterministic plus human-auditable docs | [skills/public/achieve/SKILL.md](../../skills/public/achieve/SKILL.md), [skills/public/achieve/references/lifecycle.md](../../skills/public/achieve/references/lifecycle.md), [skills/public/achieve/references/coordination.md](../../skills/public/achieve/references/coordination.md), [scripts/goal_lineage.py](../../scripts/goal_lineage.py), [skills/public/achieve/scripts/goal_run_pickup.py](../../skills/public/achieve/scripts/goal_run_pickup.py) | Refresh when achieve lifecycle wording, Goal Draft/Binding schema, Goal Run provider contract, or README long-goal route wording changes. | Partial | Add clean-consumer and live establishment proof for the exact issue-number route. |
| README-QUALITY | [README.md](../../README.md) Workflow Routes | `quality` covers missing gates, brittle tests, duplicate code, security risks, documentation drift, skill/script ergonomics, tool health, and runtime cost. | Deterministic plus delegated review | [skills/public/quality/SKILL.md](../../skills/public/quality/SKILL.md), [.agents/quality-adapter.yaml](../../.agents/quality-adapter.yaml), [scripts/run-quality.sh](../../scripts/run-quality.sh), [charness-artifacts/quality/latest.md](../../charness-artifacts/quality/latest.md), [quality inventory scripts](../../skills/public/quality/scripts/), [runtime-budget checker](../../skills/public/quality/scripts/check_runtime_budget.py) | Refresh when quality adapter commands, review scope, runtime budgets, or quality artifact schema change. | Proved for current repo posture | Keep the ledger current when quality adds or removes review lenses. |
| README-PUBLIC-SUPPORT | [README.md](../../README.md) Core Concepts | Public skills name user intent while support skills hide tool-specific detail. | Deterministic plus human-auditable docs | [docs/support-skill-policy.md](../../docs/support-skill-policy.md), [docs/capability-resolution.md](../../docs/capability-resolution.md), [skills/public/](../../skills/public/), [support-skill manifests](../../skills/support/), [public-skill validation tests](../../tests/quality_gates/test_skill_validation.py) | Refresh when public/support boundaries, skill metadata, or capability-resolution policy changes. | Partial | Current proof is mostly structural and reviewable; add a lower-noise boundary validator before hard-gating wording. |
| README-CONTEXT-FLOW | [README.md](../../README.md) Core Concepts and Workflow Routes | Goal Run parent/cursor state, retros, and artifacts preserve decisions so future agents can resume. | Deterministic plus human-auditable artifacts | [docs/goal-lifecycle.md](../../docs/goal-lifecycle.md), [skills/public/achieve/SKILL.md](../../skills/public/achieve/SKILL.md), [skills/public/retro/SKILL.md](../../skills/public/retro/SKILL.md), [charness-artifacts/retro/recent-lessons.md](../../charness-artifacts/retro/recent-lessons.md), [current-pointer freshness validation](../../scripts/validate_current_pointer_freshness.py) | Refresh when achieve/retro contracts, artifact policy, or current-pointer validators change. | Partial | Structural freshness is checked; quality of resumed judgment remains review-driven. |

## Review Rule

Update this ledger when a claim's source or proof owner changes. Use the
smallest deterministic check for local behavior and explicit reviewer or
operator evidence for semantic or host-bound behavior. Do not add a
Charness-specific evaluator artifact solely to make a row appear complete.
