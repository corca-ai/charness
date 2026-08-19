# Probe Record: scaffold-family-version-refusal

Debt rows 6-10 of slice 5. Five files, one harm shape, and FIVE separately measured
base/head pairs — the shared shape is why they are in one record, not a reason to measure
one and assert four.

Claim: the five artifact scaffolds refuse when the reader honored nothing the adapter
  declared, instead of returning the charness default write target
Claim kind: change
Observable: the `artifact_path` / `write_artifact_path` each scaffold CLI prints, and its
  process exit code, under a repo that declared its own `output_dir`
Source ref: scripts/adapter-consumer-classification.json
Source revision: dd5b6dee9
Source conditions: the adapter's declared version is one this reader does not speak, so
  `adapter["data"]` is the reader's inferred defaults rather than what the repo wrote
Base ref: 0bcb6b227
Head ref: working tree at 0bcb6b227
Base arm: base-observed
Call sites unproven: none — each file holds ONE adapter-payload call site, in
  `payload_for`, and the guard sits above it. CORRECTED after a bounded review: the
  claim first written here, that `payload_for` is the imported symbol in EACH of these
  skills, is false. Only retro and debug have a production importer (`plan_retro_run`,
  `plan_debug_run`); quality, critique and handoff are imported only by tests

## Source text

Verbatim from the manifest at the pinned revision, for the row whose reason is the most
specific of the five.

```
    "skills/public/quality/scripts/scaffold_quality_artifact.py": {
      "verdict": "accepted-risk-unguarded",
      "reason": "payload_for() (line 246-248) does `adapter = load_adapter(repo_root); output_dir = Path(adapter[\"data\"][\"output_dir\"])` with no error/valid check anywhere in the file -- matches the already-known-unguarded classification given for this file."
    },
```

THREE of the other four derive their own finding the same way. Verified verbatim at the
pinned revision rather than characterised: `scaffold_handoff_artifact.py`'s reason names
`payload_for (line 163-177)` and `scripts/scaffold_artifact_lib.py` explicitly, and merely
CITES the pre-listed set as corroboration — an earlier draft of this record called it a
weak source alongside critique, which was an overclaim in the record's own direction and
is corrected here. Exactly ONE row is genuinely non-derived:
`scaffold_critique_artifact.py`'s reason is `"Already reported/known per task background as
unguarded+consequential; not re-derived here"`. For that one the census row is not the
evidence — the measurement below is.

## Stimulus

One temp repo per skill, each declaring its own `output_dir` — a value that differs from
the reader's default, so "honored" and "fell back" are distinguishable. Each real CLI is
run against its own repo.

**WRITTEN OUT PER SKILL after `check_probe_record.py --replay-stimulus` refused the earlier
form.** This block used to be a TEMPLATE over `<skill>`, which reads compactly and is not a
reproduction step: `.agents/<skill>-adapter.yaml` names no resolver, nobody can paste it,
and no checker can replay it. The five documents below are what was actually run. `handoff`
declares `docs/mine` rather than `docs/mine-handoff` because its adapter derives the path
from a directory plus a fixed `handoff.md`.

```
for s in quality retro debug critique handoff; do mkdir -p $D/$s/.agents; done
cat > $D/quality/.agents/quality-adapter.yaml <<'YAML'
version: 9
repo: demo
output_dir: docs/mine-quality
YAML
cat > $D/retro/.agents/retro-adapter.yaml <<'YAML'
version: 9
repo: demo
output_dir: docs/mine-retro
YAML
cat > $D/debug/.agents/debug-adapter.yaml <<'YAML'
version: 9
repo: demo
output_dir: docs/mine-debug
YAML
cat > $D/critique/.agents/critique-adapter.yaml <<'YAML'
version: 9
repo: demo
output_dir: docs/mine-critique
YAML
cat > $D/handoff/.agents/handoff-adapter.yaml <<'YAML'
version: 9
repo: demo
output_dir: docs/mine
YAML
for s in quality retro debug critique handoff; do
  python3 skills/public/$s/scripts/scaffold_${s}_artifact.py --repo-root $D/$s --title probe
done
```

## Base observable

Five runs, five captures, excerpted at the one field this row is about:

```
quality    artifact_path: charness-artifacts/quality/latest.md          exit 0
retro      artifact_path: charness-artifacts/retro/2026-08-19-probe.md  exit 0
debug      artifact_path: charness-artifacts/debug/latest.md            exit 0
critique   artifact_path: charness-artifacts/critique/2026-08-19-probe.md exit 0
handoff    artifact_path: docs/handoff.md                               exit 0
```

Every one is the charness default. Every one of those repos declared something else.

## Head observable

```
`.agents/<skill>-adapter.yaml` declares a `version` this reader does not speak (version must be 1). Nothing the adapter declares is being honored, so this run would fall back to charness defaults rather than to what the repo declared -- refusing instead. Set `version: 1`, or upgrade the reader, then re-run.
exit 1
```

Measured on all five. The five adapter-name lines, which are the part of this arm that a
single generalized run could not produce:

```
`.agents/quality-adapter.yaml` declares a `version` this reader does not speak ...
`.agents/retro-adapter.yaml` declares a `version` this reader does not speak ...
`.agents/debug-adapter.yaml` declares a `version` this reader does not speak ...
`.agents/critique-adapter.yaml` declares a `version` this reader does not speak ...
`.agents/handoff-adapter.yaml` declares a `version` this reader does not speak ...
```

## Polarity controls

- speakable version (`version: 1`), same declared `output_dir` → each returns its own
  path: `docs/mine-quality/latest.md`, `docs/mine-retro/2026-08-19-probe.md`,
  `docs/mine-debug/latest.md`, `docs/mine-critique/2026-08-19-probe.md`,
  `docs/mine/handoff.md`. Exit 0.
- no adapter file at all → each returns its charness default at exit 0. These are opt-in
  surfaces; refusing a repo that declared nothing would break every consumer that never
  wrote an adapter.
- **A control that could not fail, found and re-measured.** The `handoff` stimulus first
  declared `artifact_path: docs/mine/handoff.md`. That resolver ignores the field — it
  builds the path from `output_dir` plus a fixed filename — so the speakable-version
  control ALSO returned `docs/handoff.md` and could not distinguish "honored" from "fell
  back". Both the base and the control were re-run on `output_dir`, which is the field the
  contract reads.

## Non-claims

- **This batch changed two files OUTSIDE its own rows and did not declare it until a
  bounded review found it.** `plan_retro_run` and `plan_debug_run` call the now-guarded
  `payload_for` before building their envelope, so an unhonored declaration produces the
  guard's one-line refusal at exit 1 instead of the full diagnostic plan they used to emit
  (`ok: false`, an `adapter-readiness` fail packet, a `references/adapter-contract.md`
  required read). Measured at `0bcb6b227` and at HEAD. The exit code is unchanged and the
  plan no longer leaks a `write_artifact_path` built from charness defaults, so nothing is
  less safe — but the diagnostic is gone, and whether to restore it for this input class
  is an operator design call staged in the goal's decision queue, not something this batch
  decided. Pinned by
  `tests/quality_gates/test_scaffold_version_refusal.py::test_the_planner_behavior_change_this_slice_caused_is_pinned`.
- **The read-site rationale first written for these rows was REFUTED and is corrected
  above, not deleted.** "A refusal at the entrypoint would cover one caller" is true for
  retro and debug and false for quality, critique and handoff. This slice had already
  struck the same unmeasured harm claim once, for rows 1-5, and re-published it here.
- **Two of the five refuse a PARSER refusal with a raw traceback, not a rendered verdict.**
  `quality` and `critique` reach a resolver that lets the `ValueError` out. They stop the
  run and they do not relocate the artifact, which is this row's claim, but the operator
  sees a stack trace instead of an instruction. That is a real residual, named here rather
  than absorbed; fixing that resolver is a different change than the one these rows make.
- This record establishes FIVE files. It says nothing about the rows that remain; recount
  with `python3 scripts/check_adapter_consumer_classification.py --repo-root .` rather than
  reading a number off this line.
- The claim is about the write TARGET only. Nothing here asserts the scaffolds are correct
  in any other respect, or that the artifacts they produce are well-formed.
- ONE of the five census rows did not derive its own finding: `critique`, whose reason
  says "not re-derived here". The measurement is the evidence for that row. An earlier
  draft of this record said TWO and named `handoff` as the second; checked verbatim at the
  pinned revision, that row does derive its own finding and only cites the pre-listed set
  beside it.
- The base and head observables were captured by running the CLIs, not derived from the
  diff. The record cannot prove that to a reader; a distinct observer re-running the
  stimuli above can.
