# Quality Review
Date: 2026-07-15
Title: CLI YAML stdout contract

## Scope

Target boundary: root `charness` operational command stdout, its legacy
`--json` compatibility behavior, and the public command guidance that teaches it.

Ambient repo findings: the final read-only gate reported existing Python
length-band warnings only; none are caused by this output-contract slice.

## Current Gates

- Focused root CLI, integration, usage-hook, command-doc, and executable-spec
  checks: 111 passed.
- `./scripts/run-quality.sh --read-only`: passed all configured validation,
  packaging, documentation, compile, and ruff gates.
- `python3 scripts/validate_critique_artifacts.py --repo-root . --paths
  charness-artifacts/critique/2026-07-15-cli-yaml-stdout-contract.md`: passed.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json`, rendered by `scripts/render_runtime_summary.py`; profile `local-linux-x86_64-36cpu`. <!-- reproduction-source -->
- runtime hot spots: final read-only `check-markdown` and `check-secrets` each took 5.4s; these are repository-wide gates rather than a YAML-output regression.
- coverage gate: focused behavior tests passed and the final read-only quality gate passed.
- evaluator depth: deterministic Cautilus registry/proof/diagnostic validators passed; live Cautilus execution remains ask-before-run and was not requested.

## Healthy

- Root handlers now publish JSON-shaped payloads through one YAML emitter, while
  progress remains on stderr and structured failures remain YAML on stdout.
- The parser removes exact legacy `--json` tokens before dispatch; help and
  public root-command guidance no longer advertise the flag.
- Generated CLI reference, Cautilus routing fixture, source docs, tests, and
  checked-in plugin mirrors carry the same root-output contract.

## Weak

- Root `--help` and argparse usage remain human-oriented stdout, outside the
  operational payload boundary; the generated reference states that distinction.

## Missing

- No already-installed executable or open-host-session readback is included in
  this source-checkout proof boundary.

## Deferred

- Private helper scripts keep their explicit JSON protocols because they are
  subprocess boundaries, not root `charness` responses.

## Advisory

- `command: ./scripts/run-quality.sh --read-only` reports ten pre-existing
  Python length-band warnings; no touched file is named by that advisory.
- `artifact: charness-artifacts/critique/2026-07-15-cli-yaml-stdout-contract.md`
  records the fresh-eye distinction between root YAML output and private JSON.
- `artifact: evals/cautilus/scenarios.json` was reviewed against the changed
  critique/hitl/impl/quality/setup/spec guidance: root-command flag removal
  changes neither skill routing nor acceptance evidence, so registry IDs and
  maintained scenarios remain unchanged; no live evaluator run is claimed.

## Delegated Review

- Delegated Review: executed — separate documentation/export and counterweight
  reviewers found no remaining ship blocker; parent fingerprint checks reported
  no worktree or index drift. Slow-gate lenses (fixture-economics,
  parallel-critical-path, duplicated-proof): not re-delegated because this
  slice changes neither gate topology nor runtime recommendations.

## Commands Run

- `python3 scripts/sync_root_plugin_manifests.py --repo-root .`.
- `specdown run -quiet -no-report -jobs 4` and
  `python3 scripts/check_command_docs.py --repo-root .`.
- Focused pytest command over root CLI, usage-hook, integration, and command-doc
  tests (111 passed), plus `ruff check` for touched Python surfaces.
- `python3 scripts/validate_cautilus_scenarios.py --repo-root .`.
- `./scripts/run-quality.sh --read-only`.
- `python3 scripts/run_slice_closeout.py --repo-root . --allow-unmatched
  --verification-lock --produce-mutation-coverage
  --ack-cautilus-skill-review`.

## Recommended Next Quality Moves

- passive released-install readback — capability_needed=operator update confidence; next_center=release workflow; transformation=verify an installed binary after an authorized update; proof_boundary=installed CLI and new host session; enforcement_posture=release-gate because this source slice does not update an installed executable.

## History

- [Previous quality review](history/2026-07-14-open-issue-resolution-proof.md)
