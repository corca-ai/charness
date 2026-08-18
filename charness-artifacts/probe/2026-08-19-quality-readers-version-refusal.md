# Probe Record: quality-readers-version-refusal

Debt rows 14-18 of slice 5. Three of these five do not degrade their answer under an
unhonored declaration — they emit ADVISORY-SHAPED FINDINGS asserting the repo configured
nothing, on the surface that decides whether a gate's cost is visible at all.

Claim: the five quality-skill readers refuse when the adapter declares a `version` this
  reader cannot speak, instead of reporting the opposite of what the repo declared
Claim kind: change
Observable: each CLI's own first lines — the probe roster, the resolved `artifact_path`,
  the runtime-budget findings, the visibility verdict, the cost-ranked gate count — and
  its process exit code
Source ref: scripts/adapter-consumer-classification.json
Source revision: dd5b6dee9
Source conditions: the adapter's declared version is one this reader does not speak, so
  `adapter["data"]` is the reader's inferred defaults rather than what the repo wrote
Base ref: 00c50ed3f
Head ref: working tree at 00c50ed3f
Base arm: base-observed
Call sites unproven: none — four of the five hold ONE point where the payload enters,
  and the guard sits above it. For `check_runtime_budget`, `render_runtime_summary` and
  `inventory_ci_recoverable_gates` that point is where `load_adapter` is HANDED to
  `runtime_budget_lib`, not a payload read of their own; `check_runtime_budget` holds TWO such points and both are guarded

## Source text

Verbatim from the manifest at the pinned revision.

```
    "skills/public/quality/scripts/check_runtime_budget.py": {
      "verdict": "accepted-risk-unguarded",
      "reason": "L95/L113 pass `load_adapter` into runtime_budget_lib; main() branches only on `profile_config_errors`, never on the adapter's own `errors`. On a refused version the declared `runtime_budgets` ceiling is absent and the run reports nothing to check. Same root cause as the runtime_budget_lib row."
    },
```

The source names the injection seam and the missing `errors` branch. It does NOT name the
INVERSION — that the run does not merely report "nothing to check" but affirmatively
states the adapter "has no effective runtime budget" and "has no startup_probes" over a
repo that declared both. That is this probe's own measurement.

## Stimulus

One temp repo declaring an output directory, a startup probe and a runtime budget, in the
shapes the contract actually reads.

```
mkdir -p $D/.agents
cat > $D/.agents/quality-adapter.yaml <<'YAML'
version: 9
repo: demo
output_dir: docs/mine-q
startup_probes:
  - label: probe-one
    command:
      - python3
      - "-c"
      - "pass"
    class: standing
    startup_mode: warm
    surface: direct
runtime_budgets:
  pytest: 70000
YAML
for f in measure_startup_probes resolve_quality_artifact check_runtime_budget \
         render_runtime_summary inventory_ci_recoverable_gates; do
  python3 skills/public/quality/scripts/$f.py --repo-root $D
done
```

## Base observable

```
measure_startup_probes          No startup probes matched the selected class.
resolve_quality_artifact        artifact_path: charness-artifacts/quality/latest.md
check_runtime_budget            WEAK runtime_visibility_missing_budgets: quality adapter has
                                no effective runtime budget for the selected profile
                                WEAK runtime_visibility_missing_startup_probes: quality
                                adapter has no startup_probes
render_runtime_summary          runtime visibility: weak due to
                                `runtime_visibility_missing_budgets`,
                                `runtime_visibility_missing_startup_probes`
inventory_ci_recoverable_gates  0 cost-ranked gate(s) ... no cost-ranked standing gates:
                                configure `runtime_budgets`
```

All exit 0. The last one is the sharpest reading: it instructs the operator to configure
the thing the operator configured.

## Head observable

```
`.agents/quality-adapter.yaml` declares a `version` this reader does not speak (version must be 1). Nothing the adapter declares is being honored, so this run would fall back to charness defaults rather than to what the repo declared -- refusing instead. Set `version: 1`, or upgrade the reader, then re-run.
exit 1
```

Measured on all five, in the working tree that became `724fe8a55`. The `Head ref`
above names the parent because that is the tree the base arm was captured against;
the head arm is the same content, uncommitted at capture time.

## Polarity controls

- speakable version (`version: 1`), same declarations → each reports the declaration:
  `OK             probe-one: latest 16ms, median 16ms (standing, warm, direct)`;
  `artifact_path: docs/mine-q/latest.md`; `WARN pytest: no sample yet (budget 70000ms)`;
  `runtime visibility: configured.`; `1 cost-ranked gate(s) ... keep-local pytest`.
  All exit 0.
- no adapter file at all → each exits 0. The `missing_budgets` /
  `missing_startup_probes` advisories are the CORRECT answer for a repo that declared
  nothing; they are only wrong over a repo that declared.
- **A CONTROL THAT COULD NOT FAIL, found TWICE in this one record, and the second time
  by a bounded review reading the published stimulus rather than the fixture.** The first
  correction fixed `id` -> `label` and added `class`/`startup_mode`/`surface`, and left
  `command: [python3, "-c", "pass"]` — a FLOW SEQUENCE. This repo parses its own adapters
  with `adapter_lib`, not PyYAML, and `_mapping_value` dispatches only on `""`, `"[]"`,
  `"{}"` and block scalars; anything else becomes a plain string. So
  `adapter_validators.startup_probes` dropped the probe and the speakable-version arm of
  the PUBLISHED stimulus reproduced the base observable byte-for-byte for
  `measure_startup_probes`, and `weak due to runtime_visibility_missing_startup_probes`
  for `render_runtime_summary`. Reproduced before fixing. The test fixture always used
  the block form and was right; the record and the test disagreed and only the test was
  correct, which is the sharper lesson: the section offered for INDEPENDENT REPLAY is the
  one that was wrong.
- **The earlier control-that-could-not-fail, kept for the trend line.** The first stimulus declared `startup_probes: [{id, command: <string>}]` and a
  bare `runtime_budgets` label, shapes this contract does not honor. The speakable-version
  control therefore produced the SAME output as the refused one for
  `measure_startup_probes` and `check_runtime_budget`, so their "flip" was unproven. Both
  the base and the control were re-run on the shapes `adapter_validators.startup_probes`
  and `runtime_profile_lib` actually read.

## Non-claims

- **THE CLAIM IS NARROWER THAN "the reader honored nothing the repo declared", and it is
  written that way after a bounded review measured why.** These guards ask
  `adapter_version_verdict.declarations_unhonored`, which is `version_refused or
  parse_refused` — and BOTH read `errors`. Quality's resolver calls
  `adapter_lib.load_yaml_file`, which DISCARDS the uninterpreted-line sink that
  `load_yaml_file_report` returns. So a THIRD state exists that no predicate over `errors`
  can see. Measured at `5ecf7575f` with the guard installed:

  ```
  version: 1
    output_dir: docs/mine-q
  ```

  One stray indent. `_parse_block` drops the line, `errors: []`, `valid: True`, and
  `resolve_quality_artifact` emits `artifact_path: charness-artifacts/quality/latest.md`
  at exit 0 — the base observable above, at HEAD. Swept across all sixteen public
  resolvers: the SAME SIX that raise on a parser refusal (achieve, announcement,
  create-skill, critique, narrative, quality) also drop silently; the other ten report.
  Filed on [#673](https://github.com/corca-ai/charness/issues/673). It is a resolver gap,
  not a guard-placement error in these five, and it is named here rather than left to make
  the claim read wider than it is.
- **The two libraries these rows read through are NOT paid down and are not credited.**
  `runtime_budget_lib.evaluate` and `runtime_budget_sizing_lib.suggest_budgets` take their
  loader INJECTED, so they cannot know which adapter they are reading or refuse for it.
  That seam is deliberate. The guard therefore lives in each caller, and those two rows
  stay `accepted-risk-unguarded` rather than being credited with a property their callers
  supply — a caller that forgets is unguarded again, and nothing structural stops that.
- **The parser door refuses with a raw TRACEBACK for this whole family.**
  `quality_adapter_lib` calls `load_yaml_file` with no handler, unlike
  `simple_skill_adapter_lib`, so `version: !!int 9` raises rather than resolving to the
  rendered refusal. It stops and reports nothing inverted, which is this row's claim; the
  stack trace is the same residual the scaffold rows already record, not a new one.
- This record establishes FIVE files. Recount the rest with
  `python3 scripts/check_adapter_consumer_classification.py --repo-root .`.
- The base and head observables were captured by running the CLIs against a base with the
  guards reverted, not derived from the diff. A distinct observer re-running the stimulus
  above can check that; the record cannot prove it.
