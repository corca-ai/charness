# README Proof Ledger

This ledger maps reader-facing README and operator claims to the proof layer
that currently owns them. It is not a second test runner. It is the current
claim-by-claim index that says what must be trusted, what is already checked,
and what still needs stronger proof.

## Terms

- Claim: a reader-facing promise in README or operator docs.
- Acceptance criterion: the behavior that would make the claim true enough for
  an operator to rely on it.
- Proof owner: the layer that can prove or falsify the claim. Owners are
  deterministic, Cautilus, HITL/operator, or deferred.
- Evidence: a concrete repo path, checked artifact, command, or review record.
- Freshness rule: the change that requires the evidence to be refreshed.

`cautilus claim discover` produces `cautilus.claim_proof_plan.v1`. That packet
is a proof plan, not a verdict that the claims are true. Its job is to discover
candidate claims and recommend a proof layer. The repo still needs deterministic
gates, evaluator runs, or human/operator evidence to satisfy those claims.

## Direction

The target is a single Specdown report that lets a reader inspect the current
contract and see proof for each acceptance criterion. The report should include:

- this ledger, or a generated successor with the same claim-to-proof shape;
- deterministic executable checks for local scripts, docs, and CLI behavior;
- historical Cautilus behavioral proof at
  [`charness-artifacts/cautilus/latest.md`](../charness-artifacts/cautilus/latest.md);
- future Cautilus claim-discovery and claim-validation outputs after the repo
  adapter is deliberately re-enabled and those packets become stable checked
  artifacts.

While the root Cautilus adapter is `disabled`, do not run claim discovery or
evaluation commands. After the adapter is deliberately re-enabled, use the
normal distributed binary surface; if that is not available yet, the historical
implementation-checkout command shape was:

```bash
../cautilus/bin/cautilus claim discover \
  --repo-root . \
  --source README.md \
  --source docs/operator-acceptance.md \
  --output /tmp/charness-readme-claims.json
../cautilus/bin/cautilus claim validate \
  --claims /tmp/charness-readme-claims.json \
  --output /tmp/charness-readme-claims-validation.json
```

The current validation report checks packet shape and evidence references. It
does not search for evidence or decide that the product claim is satisfied.

## Claim Ledger

| ID | Source | Claim / acceptance criterion | Proof owner | Current evidence | Freshness rule | Status | Gap / next proof |
| --- | --- | --- | --- | --- | --- | --- | --- |
| README-BOOTSTRAP | [README.md](../README.md) Quick Start | Python 3 plus [init.sh](../init.sh) installs the managed `charness` CLI and host plugin bundle. | Deterministic plus HITL/operator | [init.sh](../init.sh), [charness](../charness), [packaging/bootstrap-python.json](../packaging/bootstrap-python.json), [packaging/bootstrap-requirements.txt](../packaging/bootstrap-requirements.txt), [scripts/validate_packaging.py](../scripts/validate_packaging.py), [scripts/validate_packaging_committed.py](../scripts/validate_packaging_committed.py), [tests/charness_cli/test_managed_install.py](../tests/charness_cli/test_managed_install.py) | Refresh when install script, bootstrap manifests, host plugin layout, or packaging validators change. | Partial | Local bootstrap shape is checked; real host install success still needs operator or CI environment proof. |
| README-INIT-ROUTE | [README.md](../README.md) Quick Start | "Use charness to initialize this repo" should route to `charness:setup` and update [AGENTS.md](../AGENTS.md) plus related settings through ordinary diffs. | Cautilus plus deterministic | [skills/public/setup/SKILL.md](../skills/public/setup/SKILL.md), [skills/public/setup/references/](../skills/public/setup/references/), [tests/quality_gates/test_setup_inspect_policy.py](../tests/quality_gates/test_setup_inspect_policy.py), [evals/cautilus/whole-repo-routing.fixture.json](../evals/cautilus/whole-repo-routing.fixture.json), [charness-artifacts/cautilus/latest.md](../charness-artifacts/cautilus/latest.md) | Refresh when README wording, setup skill metadata, init references, or routing fixtures change. | Partial | Add a README-specific Cautilus fixture for the exact Quick Start prompt. |
| README-NORMAL-PROMPTS | [README.md](../README.md) Quick Start and How You Use It | After initialization, users can prompt normally; `charness` supplies routing context without requiring skill names each time. | Cautilus | [evals/cautilus/whole-repo-routing.fixture.json](../evals/cautilus/whole-repo-routing.fixture.json), [.agents/cautilus-adapter.yaml](../.agents/cautilus-adapter.yaml), [charness-artifacts/cautilus/latest.md](../charness-artifacts/cautilus/latest.md) | Refresh when AGENTS startup guidance, skill descriptions, adapter routing policy, or README prompt guidance changes. | Partial | Add a Cautilus fixture for normal prompts without explicit skill names. |
| README-CLI-STATE | [README.md](../README.md) Quick Start | `charness --help`, `charness doctor`, and `charness update` let humans and agents inspect local harness state instead of guessing. | Deterministic plus Specdown | [docs/cli-reference.md](./cli-reference.md), [.agents/command-docs.yaml](../.agents/command-docs.yaml), [scripts/render_cli_reference.py](../scripts/render_cli_reference.py), [tests/quality_gates/test_command_docs_gate.py](../tests/quality_gates/test_command_docs_gate.py), [specs/tool-doctor.spec.md](../specs/tool-doctor.spec.md) | Refresh when CLI commands, generated reference ownership, doctor output, or command-doc gates change. | Partial | Existing checks prove command surface and doctor behavior, not every semantic workflow claim behind update. |
| README-UPDATE-ALL | [README.md](../README.md) Quick Start | `charness update all` refreshes tracked external tools and bundled support skills. | Deterministic plus HITL/operator | [scripts/update_tools.py](../scripts/update_tools.py), [scripts/sync_support.py](../scripts/sync_support.py), [docs/development.md](./development.md), [docs/cli-reference.md](./cli-reference.md), [tests/charness_cli/test_update_output.py](../tests/charness_cli/test_update_output.py), [tests/control_plane/test_sync_support.py](../tests/control_plane/test_sync_support.py) | Refresh when update manifests, support-skill sync policy, CLI wiring, or host packaging changes. | Partial | Dry-run and local helpers are checked; real external tool freshness remains operator or CI proof. |
| README-WORKFLOW-ROUTES | [README.md](../README.md) How You Use It | Common project and existing-repo prompts route to the intended public workflow skills. | Cautilus plus human-auditable docs | [skills/public/](../skills/public/), [charness-artifacts/find-skills/latest.md](../charness-artifacts/find-skills/latest.md), [evals/cautilus/whole-repo-routing.fixture.json](../evals/cautilus/whole-repo-routing.fixture.json), [charness-artifacts/cautilus/latest.md](../charness-artifacts/cautilus/latest.md) | Refresh when README route examples, public skill descriptions, find-skills output, or routing eval fixtures change. | Partial | Expand Cautilus fixtures from whole-repo routing into README entrypoint claims. |
| README-QUALITY | [README.md](../README.md) How You Use It | `quality` covers missing gates, brittle tests, duplicate code, security risks, documentation drift, skill/script ergonomics, tool health, and runtime cost. | Deterministic plus delegated review | [skills/public/quality/SKILL.md](../skills/public/quality/SKILL.md), [.agents/quality-adapter.yaml](../.agents/quality-adapter.yaml), [scripts/run-quality.sh](../scripts/run-quality.sh), [charness-artifacts/quality/latest.md](../charness-artifacts/quality/latest.md), quality inventory scripts, runtime-budget checks | Refresh when quality adapter commands, review scope, runtime budgets, or quality artifact schema change. | Proved for current repo posture | Keep the ledger current when quality adds or removes review lenses. |
| README-CAUTILUS | [README.md](../README.md) How You Use It | Prompt- or behavior-affecting changes can use Cautilus evaluator-backed scenario review when installed and configured. | Cautilus plus Specdown | [.agents/cautilus-adapter.yaml](../.agents/cautilus-adapter.yaml), [evals/cautilus/whole-repo-routing.fixture.json](../evals/cautilus/whole-repo-routing.fixture.json), [charness-artifacts/cautilus/latest.md](../charness-artifacts/cautilus/latest.md), [specs/on-demand-validation.spec.md](../specs/on-demand-validation.spec.md) | Refresh when adapter run mode, eval fixtures, Cautilus artifact shape, or Specdown viewer changes. | Eval-only, ask mode | Per corca-ai/cautilus#32, only `cautilus eval test` and `cautilus eval evaluate` are supported; claim discovery, optimize, review-learning, and `eval live` remain under contract rewrite and stay opt-out for this repo. |
| README-PUBLIC-SUPPORT | [README.md](../README.md) Core Concepts | Public skills name user intent while support skills hide tool-specific detail. | Deterministic plus human-auditable docs | [docs/support-skill-policy.md](./support-skill-policy.md), [docs/capability-resolution.md](./capability-resolution.md), [skills/public/](../skills/public/), support-skill manifests, public-skill validation tests | Refresh when public/support boundaries, skill metadata, or capability-resolution policy changes. | Partial | Current proof is mostly structural and reviewable; add a lower-noise boundary validator before hard-gating wording. |
| README-CONTEXT-FLOW | [README.md](../README.md) Core Concepts and How You Use It | Handoffs, retros, and artifacts preserve decisions so future agents can resume. | Deterministic plus human-auditable artifacts | [docs/handoff.md](./handoff.md), [skills/public/handoff/SKILL.md](../skills/public/handoff/SKILL.md), [skills/public/retro/SKILL.md](../skills/public/retro/SKILL.md), [charness-artifacts/retro/recent-lessons.md](../charness-artifacts/retro/recent-lessons.md), [scripts/validate_handoff_artifact.py](../scripts/validate_handoff_artifact.py), current-pointer freshness validation | Refresh when handoff/retro skill contracts, artifact policy, or current-pointer validators change. | Partial | Structural freshness is checked; quality of resumed judgment remains review-driven. |

## Cautilus Integration Plan

Use Cautilus discovery as the bridge from entrypoint prose to executable proof,
not as the final proof by itself.

1. After the root adapter is re-enabled, run `cautilus claim discover` over [README.md](../README.md) and
   [docs/operator-acceptance.md](./operator-acceptance.md) to produce a
   source-ref-backed proof plan.
2. Review the candidate claims and merge or split them into stable acceptance
   criteria like the rows above.
3. Attach direct evidence references with path, kind, commit or content hash,
   and the supported claim IDs when a claim is satisfied.
4. Run `cautilus claim validate` to validate the packet and evidence refs.
5. Surface the ledger, validation report, and
   [charness-artifacts/cautilus/latest.md](../charness-artifacts/cautilus/latest.md)
   through Specdown so the report shows both claims and proof.

This keeps the proof direction honest: Cautilus can discover and validate proof
plans, deterministic gates can prove repeatable local behavior, and HITL or
operator evidence remains explicit where the repo cannot prove real-world host
state alone.
