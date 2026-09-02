# Shared rules for the #769 universe-porting lanes (U1, U2, U3)

Read `gh issue view 769`, the table in
`charness-artifacts/quality/2026-09-02-gate-classification-769.md`, and the
per-label blocks for YOUR labels in `charness-artifacts/goal-runs/765/briefs/map-769-conditional.md`
(file:line of each hardcoded universe, today's empty-match behaviour, the
tests that pin it). Lane U0 has landed `scripts/quality_universes_lib.py`
and the `universes:` adapter family (`.agents/quality-adapter.yaml`,
`skills/public/quality/references/adapter-contract.md` `### universes`).
Read that module AS LANDED before porting anything; its `resolve_universe`,
`matching_files`, and `refuse_if_declared_and_empty` are the only scope
readers a ported gate may use.

Outcome for each label in your batch: the gate's scan universe comes from the
adapter through the shared reader; the charness default is the literal it
carried before (now stated once in the universes defaults, not in the gate);
a DECLARED universe that matches nothing refuses with the gate label in the
text; an UNDECLARED universe that matches nothing reports a discovered empty
and does not exit 0 silently (`tests/quality_gates/test_empty_scope_refusals.py:1-15`
states the contract; add your gate to its module list and cases).

Rules:

1. Do not edit `scripts/run-quality.sh` (lane R2 owns it). Where a runner row
   must change (a flag to pass, an inline glob array to replace), write the
   exact replacement row in a `## Runner rows for R2` section of your commit
   body. Do not edit `scripts/quality_adapter_lib.py`,
   `scripts/quality_universes_lib.py`, or `skills/public/quality/scripts/adapter_validators.py`
   except to correct a default that U0 copied wrongly (cite the file:line).
2. A shell gate reads its universe through the module's CLI
   (`python3 scripts/quality_universes_lib.py --repo-root . --key <k> --format lines`);
   it never re-globs a literal.
3. Tests: in-process through `tests/script_loader.py` / `script_main.py`, no
   `subprocess` in a new test; read `docs/development.md` "Verification and
   export" first. For every ported gate add a seeded-consumer case: a tmp repo
   with a `src/`-style layout and an adapter declaring the universe, proving
   the gate scans the declared files; and a declared-but-empty case proving
   the refusal.
4. Tests that pinned the old literal are re-pointed at the universes default,
   not deleted; their assertion keeps its meaning.
5. Regenerate the plugin mirror before any pytest run
   (`python3 scripts/sync_root_plugin_manifests.py --repo-root .`); two
   standing tests byte-compare it.
6. Do not touch `plugins/**` (generated). Do not spawn descendant agents.

Verification before you stop (paste verdicts in the commit body):

```
python3 -m ruff check <touched .py>; python3 -m ruff format --check <touched .py>
python3 <each touched CLI file> --help          # from the repo root; a module that only passes under the pytest loader is the defect class this repo had 39 files of last session
python3 <each ported gate> --repo-root . <its usual flags>
python3 scripts/check_subprocess_form.py --repo-root . --require-git-file-listing
python3 scripts/check_code_lengths.py --repo-root . --require-git-file-listing
python3 scripts/sync_root_plugin_manifests.py --repo-root .
python3 scripts/run_standing_pytest.py --repo-root . --pytest-target tests/quality_gates
./scripts/run-quality.sh
```

Commit in ONE commit, subject given in your lane brief, body listing per
label: old file:line of the literal, the universes key now read, the
empty-match behaviour before and after, and the exact commands with verdicts.
No close keyword. Stop after the commit and report the hash.
