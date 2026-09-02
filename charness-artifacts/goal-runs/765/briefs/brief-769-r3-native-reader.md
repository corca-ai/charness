# Lane brief R3: the native extractor reads the declared gate list (#769, Goal Run #765)

Read `charness-artifacts/goal-runs/765/briefs/map-769-runner.md` section 3a
(the Rust extractor at `native/repograph/src/graph_carriers.rs:22-32, :92,
:565-646, :1076-1150` and the fixture
`native/repograph/fixtures/carriers/expected/quality_label_universe.yaml`
asserted at `:1345-1373`) and section 7b (the row schema). Lane R1 is
landing `.agents/quality-gates.yaml` in that schema (also restated in
`charness-artifacts/goal-runs/765/briefs/brief-769-r1-gate-list.md`, Design
item 1) with `scripts/quality_gates_extract.py` that emits it from the shell
file; if R1 is not on your base, generate the YAML yourself with the same
extraction the Python `scripts/quality_label_universe.py` regexes do and
keep it under `tests/` as a fixture only.

Outcome: the repograph carrier extractor reads gate labels and commands from
`.agents/quality-gates.yaml` when it exists and falls back to the shell
parse when it does not; the two agree on this repo (a test proves the
symmetric difference is empty); the captured fixture is regenerated from the
data file; `check-export-safe-imports` and `check-plugin-dir-references`
(the two native gates) keep passing.

Rules: block-style YAML only (the repo's loaders do not parse inline
arrays); no new crate unless `Cargo.lock` under `native/repograph` already
resolves it offline (say which); `./scripts/check-rust.sh` is the gate;
tests in `native/repograph/tests/` for the reader plus one Python test under
`tests/quality_gates/` proving fixture parity in-process. Do not edit
`scripts/run-quality.sh`, `scripts/quality_label_universe.py`, or anything
outside `native/`, `tests/quality_gates/`, and (only if needed for the
fixture) `.agents/quality-gates.yaml`. Do not spawn descendant agents.

Verification before you stop:

```
./scripts/check-rust.sh
python3 scripts/native_gate_lib.py --repo-root . export-safe      # read the real subcommand names first
python3 scripts/native_gate_lib.py --repo-root . plugin-refs
python3 scripts/sync_root_plugin_manifests.py --repo-root .
python3 scripts/run_standing_pytest.py --repo-root . --pytest-target tests/quality_gates
./scripts/run-quality.sh
```

Commit in ONE commit with subject
`repograph: read the declared gate list for the quality label universe carrier (#769 R3 lane candidate)`
and a body with the exact commands and verdicts. No close keyword. Stop
after the commit and report the hash.
