# Probe Record: release-planner-version-refusal

The fourth debt row of slice 5, and deliberately the WEAKEST of the four. The planner was
never silent under a refused version — it named the invalid adapter. What it did anyway
was emit a plan whose release identity it had invented.

Claim: `plan_release_run.build_plan` refuses an unspeakable adapter version at its OWN
  read site, rather than inheriting a callee's refusal
Claim kind: change
Observable: the planner's `next_action=` summary line and its process exit code, under a
  repo that DID declare `release_record_path` and a real-host trigger glob
Source ref: scripts/adapter-consumer-classification.json
Source revision: dd5b6dee9
Source conditions: the adapter's declared version is one this reader does not speak, so
  `data` is the reader's inferred defaults; two consumers are gated on `adapter["valid"]`
  and three are not
Base ref: dd5b6dee9
Head ref: working tree at f7d3fb70e
Base arm: base-observed
Call sites unproven: none — `build_plan` has no production importer (`grep` over
  `scripts/`, `skills/` and `tests/` finds only its own `main()` and one test module), so
  the read site and the entrypoint coincide here; the guard is still placed at the read
  site so the row's verdict does not depend on `main()` staying the only caller

## Source text

Verbatim from the manifest at the pinned revision.

```
    "skills/public/release/scripts/plan_release_run.py": {
      "verdict": "accepted-risk-unguarded",
      "reason": "build_plan() (line 179-236) does `adapter = load_adapter(repo_root); data = adapter.get(\"data\")` and gates only two consumers on validity -- `real_host_payload` (line 213) and `review_payload` (line 234) are each behind `if adapter.get(\"valid\"):` -- but `record_path = _prepared_stop.release_record_path(data)` (line 236), `update_blocker = update_instructions_version_blocker(data.get(\"update_instructions\"), ...)` (line 205-209), and `drafted_notes_candidates(repo_root, data, ...)` (line 251-254) all read `data` unconditionally, and `release_payload = build_release_payload(repo_root)` (line 186, i.e. current_release.build_payload) is called unconditionally and is itself unguarded (see current_release.py finding)."
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
`release_record_path` and a real trigger glob. The real CLI is run against it.

```
git -C $D init -q
mkdir -p $D/.agents
cat > $D/.agents/release-adapter.yaml <<'YAML'
version: 9
release_record_path: charness-artifacts/release/mine.md
real_host_required_path_globs:
  - "src/**"
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

- speakable but otherwise invalid (`version: 1`, `release_record_path: 12345`) →
  `next_action=sync_release_surface`, exit 0. The affordance an operator runs this planner
  for is preserved; only an unspeakable version refuses.
- speakable and well-formed → `next_action=sync_release_surface`, exit 0.
- **The isolating control, and the one this row actually needs.** The CLI reading above is
  satisfied WITHOUT the guard, because `build_release_payload` (guarded in row 2) is called
  near the top of `build_plan` and its `SystemExit` escapes the surrounding
  `except Exception`. Deleting this file's guard and re-running the suite was measured:
  the two CLI tests still pass and only
  `test_the_refusal_is_this_file_s_own_not_inherited_from_a_callee` fails, with
  `DID NOT RAISE <class 'SystemExit'>`. That test stubs `build_release_payload`,
  `build_real_host_payload` and `build_review_gate_payload` with callees that do not
  refuse, and builds its Namespace from the planner's own `parse_args`.

## Non-claims

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
