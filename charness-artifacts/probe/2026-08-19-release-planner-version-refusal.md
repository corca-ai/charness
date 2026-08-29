# Probe Record: release-planner-version-refusal

The fourth debt row of slice 5, and deliberately the WEAKEST of the four. The planner was
never silent under a refused version — it named the invalid adapter. What it did anyway
was emit a plan whose release identity it had invented.

Claim: `plan_release_run.build_plan` refuses an unspeakable adapter version at its OWN
  read site, rather than inheriting a callee's refusal
Claim kind: change
Observable: the planner's `next_action=` summary line and its process exit code, under a
  repo that DID declare an `output_dir` (the key `release_record_path` is derived from)
Source ref: scripts/adapter-consumer-classification.json
Source revision: dd5b6dee9
Source conditions: the adapter's declared version is one this reader does not speak, so
  `data` is the reader's inferred defaults; one consumer is gated on `adapter["valid"]`
  and three are not
Base ref: dd5b6dee9
Head ref: working tree at f7d3fb70e
Base arm: base-observed
Call sites unproven: none — `build_plan` has no production importer under `scripts/` or
  `skills/`, so the read site and the entrypoint coincide here; the guard is still placed
  at the read site so the row's verdict does not depend on `main()` staying the only
  caller. A round-1 bounded review corrected this line's parenthetical, which said "one
  test module": there are TWO (`test_release_run_planner.py` and this row's own), which changes nothing about the
  load-bearing half and is fixed because a miscount published as a count is this goal's
  own class

## Source text

Verbatim from the manifest at the pinned revision.

```
    "skills/public/release/scripts/plan_release_run.py": {
      "verdict": "accepted-risk-unguarded",
      "reason": "build_plan() does `adapter = load_adapter(repo_root); data = adapter.get(\"data\")` and gates the review payload on validity, but `record_path = _prepared_stop.release_record_path(data)`, `update_blocker = update_instructions_version_blocker(data.get(\"update_instructions\"), ...)`, and `drafted_notes_candidates(repo_root, data, ...)` all read `data` unconditionally, and `release_payload = build_release_payload(repo_root)` is called unconditionally and is itself unguarded (see current_release.py finding)."
    },
```

The source's structural reading is confirmed by measurement below. Two things the source
does NOT say, and this probe does: the base emitted `next_action=repair_adapter`, so the
planner was partially honest and this row is weaker than the three gate rows; and by the
time this row was measured, the `current_release` guard had already made the CLI exit 1 by
inheritance, so the CLI reading alone could not establish the claim.

## Stimulus

A temp repo with a git repository (the planner asks git for the current branch on the arm
that reaches a plan) and an adapter declaring a version this reader refuses beside a real
`output_dir`. The real CLI is run against it.

**CORRECTED after `check_probe_record.py --replay-stimulus`, the detector built for `#674`,
refused this record on its first sweep of the corpus — the FIFTH RECORD in this family
FOUND to have shipped a control that could not fail, and the FIRST to ship one, since this
record predates the other four; the sixth such ARM in all, because the quality record
shipped two; and the only one the review rounds did not find.** The first version of this
block declared `release_record_path: charness-artifacts/release/mine.md`. No ADAPTER
consumer takes that key: both `plan_release_prepared_stop.release_record_path` and
`publish_release_claims_review.release_record_path` DERIVE the path from `output_dir` plus a
fixed filename, precisely so a second copy of the constant cannot drift. Deleting the line
changes nothing the release resolver honors, and neither does varying it.

Both arms were re-run on `output_dir` and both reproduced the observables recorded here,
apart from the temp directory's own name, which differs per run and which the `--detail`
excerpt below embeds. **That makes the declaration one the resolver honors, which is what the detector
checks; it does NOT make the `next_action=` pair discriminating.** Measured at HEAD with
`version: 1`: the dead declaration and the corrected `output_dir` both print
`next_action=sync_release_surface` at exit 0. At the observable this record declares, the
two speakable controls below still cannot tell honored from fell-back — the isolating
control remains the only arm that can fail, and it is what carried this row. The stimulus
repair removes a dead declaration from the published reproduction steps; it does not
upgrade the row's evidence, and saying otherwise would be this record's own class again.

```
git -C $D init -q
mkdir -p $D/.agents
cat > $D/.agents/release-adapter.yaml <<'YAML'
version: 9
output_dir: charness-artifacts/release-mine
YAML
python3 skills/public/release/scripts/plan_release_run.py --repo-root $D
python3 skills/public/release/scripts/plan_release_run.py --repo-root $D --detail
```

## Base observable

```
next_action=repair_adapter: Release adapter is invalid.
exit 0
```

The `--detail` payload at the same base, excerpted at the three fields this row is about:

```
  package_id: probe-prr-oSWDTL
  packaging_manifest_path: /tmp/probe-prr-oSWDTL/packaging/probe-prr-oSWDTL.json
  checked_in_plugin_root: /tmp/probe-prr-oSWDTL/plugins/probe-prr-oSWDTL
```

`probe-prr-oSWDTL` is the temp directory's own name. Neither path exists. `blockers: []`.

## Head observable

```
`.agents/release-adapter.yaml` declares a `version` this reader does not speak (version must be 1). Nothing the adapter declares is being honored, so this run would fall back to charness defaults rather than to what the repo declared -- refusing instead. Set `version: 1`, or upgrade the reader, then re-run.
exit 1
```

## Polarity controls

- speakable but otherwise invalid (`version: 1`, `output_dir: 12345`) →
  `next_action=sync_release_surface`, exit 0. The affordance an operator runs this planner
  for is preserved; only an unspeakable version refuses.
- speakable and well-formed (`version: 1`, `output_dir: charness-artifacts/release-mine`) →
  `next_action=sync_release_surface`, exit 0.
- **The control that could not fail, kept for the trend line.** With the original
  `release_record_path` declaration this pair was WORTHLESS: `next_action=` is identical
  whether the reader honors the declaration or falls back, because no ADAPTER consumer reads
  that key at all. Neither speakable control distinguished anything until the declaration
  moved to `output_dir`. The isolating control below is what carried this row, which is why
  the defect survived every review round — the dead arm was not the load-bearing one.
- **The isolating control, and the one this row actually needs.** The CLI reading above is
  satisfied WITHOUT the guard, because `build_release_payload` (guarded in row 2) is called
  near the top of `build_plan` and its `SystemExit` escapes the surrounding
  `except Exception`. Deleting this file's guard and re-running the suite was measured:
  the two CLI tests still pass and only
  `test_the_refusal_is_this_file_s_own_not_inherited_from_a_callee` fails, with
  `DID NOT RAISE <class 'SystemExit'>`. That test stubs `build_release_payload`,
  `build_review_gate_payload` with a callee that does not
  refuse, and builds its Namespace from the planner's own `parse_args`.

## Non-claims

- **The guard this record measured keyed on ONE door, and a round-1 bounded review found a
  second.** `version: !!int 9` — one token added to this record's own stimulus — makes the
  parser refuse the document, and `simple_skill_adapter_lib` answers that with
  `infer_repo_defaults(...)` plus a `parse_failure_error`, the same "nothing declared is
  honored" state by a different door. At this record's `Head ref` that input still reached
  the base behavior. It is closed in a later commit, by keying
  `adapter_version_verdict` on the CONDITION rather than on one check's wording; the
  base/head pair recorded above is unaffected and was not re-measured for the second door.
- **This row's CLI-level behavior was already fixed by row 2 before this guard existed.**
  What this record establishes is narrower: that the refusal is now a property of this
  file rather than of the order its callees happen to be called in. Reading the exit code
  alone would credit this guard with a flip it did not cause.
- The base was NOT silent. `next_action=repair_adapter: Release adapter is invalid.` is a
  real signal, and this row is weaker than the three gate rows for exactly that reason.
  The defect is the invented identity emitted beside it at exit 0, not an absence of
  warning.
- This record establishes ONE file. It says nothing about the 33 `accepted-risk-unguarded`
  rows that remain.
- `guarded` is a structural claim about the version refusal only. The three unconditional
  `data` reads the source names are now unreachable under an unspeakable version; nothing
  here asserts they are correct under a speakable one.
