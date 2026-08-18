# Probe Record: handoff-hitl-version-refusal

Debt rows 11-13 of slice 5. The harm here is sharper than a relocated write target: one of
these READS the file it resolves and reports counts from it, so an unhonored declaration
produces a confident, well-formed answer about a document the repo does not use.

Claim: `parse_handoff_entries`, `plan_handoff_run` and `sync_review_artifact` refuse when
  the reader honored nothing the adapter declared, instead of resolving a charness default
  path and acting on it
Claim kind: change
Observable: the `handoff_path` / `artifact_path` each CLI prints, its process exit code,
  and — for the writer — whether a file appears at the default location
Source ref: scripts/adapter-consumer-classification.json
Source revision: dd5b6dee9
Source conditions: the adapter's declared version is one this reader does not speak, so
  the resolved payload is the reader's inferred defaults
Base ref: 97dfc881a
Head ref: working tree at 97dfc881a
Base arm: base-observed
Call sites unproven: none — each file holds ONE adapter-payload call site reached from
  its own entrypoint, and the guard sits above it. `parse_handoff_entries` additionally
  has an EXPLICIT-PATH arm that never asks the adapter; the guard is placed after it, and
  a test asserts that arm still works under a refused version

## Source text

Verbatim from the manifest at the pinned revision, for the row this record's sharpest
reading belongs to.

```
    "skills/public/handoff/scripts/plan_handoff_run.py": {
      "verdict": "accepted-risk-unguarded",
      "reason": "_artifact_summary (line 156-157) and _resolved_max_content_lines (line 100-117) act on adapter[\"artifact_path\"]/adapter[\"data\"] unconditionally; the errors check at line 279 only adds an advisory reference read and echoes errors in the output envelope (line 397-403), it never gates the artifact_path or next_action that get built from the defaulted data."
    },
```

The source makes the distinction this record's second measurement rests on: this file
ALREADY read `errors`, and it did not help. That is not a claim this probe adds — it is
the row's own, and it was confirmed by running the CLI, which reported the wrong path at
exit 0 with the error channel available to it the whole time.

## Stimulus

One temp repo declaring `output_dir: docs/mine` for handoff and `docs/mine-hitl` for
HITL, with a handoff at BOTH the declared and the default location carrying different
bodies — so "read the declared file" and "read ours" are distinguishable in the parsed
output, not only in the path.

```
mkdir -p $D/.agents $D/docs/mine $D/.charness/hitl/runtime/s1
cat > $D/.agents/handoff-adapter.yaml <<'YAML'
version: 9
repo: demo
output_dir: docs/mine
YAML
cat > $D/.agents/hitl-adapter.yaml <<'YAML'
version: 9
repo: demo
output_dir: docs/mine-hitl
YAML
printf '# Handoff\n\n## Next Session\n\n1. the declared one\n' > $D/docs/mine/handoff.md
printf '# Handoff\n\n## Next Session\n\n1. the charness default one\n' > $D/docs/handoff.md
printf 'session_id: s1\nstatus: in_progress\n' > $D/.charness/hitl/runtime/s1/state.yaml

python3 skills/public/handoff/scripts/parse_handoff_entries.py --repo-root $D
python3 skills/public/handoff/scripts/plan_handoff_run.py --repo-root $D
python3 skills/public/hitl/scripts/sync_review_artifact.py --repo-root $D --session-id s1
```

## Base observable

```
parse_handoff_entries   ok: true
                        handoff_path: /tmp/probe-b3-RuiuDO/docs/handoff.md
                        entry_count: 1
                        exit 0

plan_handoff_run          artifact_path: docs/handoff.md
                          exit 0

sync_review_artifact    status: synced
                        artifact_path: charness-artifacts/hitl/latest.md
                        errors: []
                        exit 0
```

The first is the one to read closely: `ok: true`, a real `entry_count`, and `errors: []`
on the third — three well-formed answers, all about the wrong file.

## Head observable

```
`.agents/handoff-adapter.yaml` declares a `version` this reader does not speak (version must be 1). Nothing the adapter declares is being honored, so this run would fall back to charness defaults rather than to what the repo declared -- refusing instead. Set `version: 1`, or upgrade the reader, then re-run.
exit 1
```

Measured on all three, with `hitl-adapter.yaml` named in the third. The HITL writer leaves
no file at the default location.

## Polarity controls

- speakable version (`version: 1`), same declarations → `handoff_path:
  <repo>/docs/mine/handoff.md`, `artifact_path: docs/mine/handoff.md`, `artifact_path:
  docs/mine-hitl/latest.md`. All exit 0.
- no adapter file at all → each returns its charness default at exit 0. These are opt-in
  surfaces.
- **the explicit-path arm**, `parse_handoff_entries.py <path>` under `version: 9` → exit
  0, `handoff_path` as given. A caller that named the file is not asking the adapter
  anything FOR THE PATH IT PARSES, and the guard is placed after that arm so it stays
  that way. A bounded review narrowed that sentence: `<path> --with-issues` DOES reach the
  handoff adapter, through `chunked_routing_issue_source.build_issue_entries` and its
  `issue_source:` block. That path is safe today because the helper checks
  `adapter.get("valid") is False` and returns `enabled: False`, so no charness default is
  acted on — but the safety is the helper's, not this exemption's, and no test covers
  `<path> --with-issues` under `version: 9`.

## Non-claims

- This record establishes THREE files. It says nothing about the rows that remain;
  recount with `python3 scripts/check_adapter_consumer_classification.py --repo-root .`.
- **A fourth row was attempted in this batch and DROPPED without a verdict.**
  `scripts/risk_interrupt_lib.py` was measured and its harm did NOT reproduce: base and
  control both returned the declared `docs/mine-debug/latest.md`. Reading the code
  explains why and makes the row bigger, not smaller — `_load_debug_adapter` falls back to
  a RAW LINE SCAN of `.agents/debug-adapter.yaml` when the debug skill's resolver is not
  present, and that fallback reads `output_dir:` with no version check at all. So the row
  carries a `no-version-validation` class its census entry did not name, and reproducing
  the resolver arm needs a repo that ships the skill tree. It stays UNPAID rather than
  being classified on an argument. A bounded review then pointed out that recording the
  second class ONLY here left the manifest — the surface the gate reads — saying half of
  it, so the row is now a multi-class entry carrying both verdicts with the measurement
  above as the second one's evidence.
- The claim is about path resolution only. Nothing here asserts these readers are correct
  in any other respect.
- The base and head observables were captured by running the CLIs, not derived from the
  diff. A distinct observer re-running the stimulus above can check that; the record
  cannot prove it.
