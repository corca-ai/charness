# Lane brief S: re-scope the quality skill and adapter to the consumer definition (#769, Goal Run #765)

Read `gh issue view 769` (Owned scope fourth bullet, Non-claims) and the
table in `charness-artifacts/quality/2026-09-02-gate-classification-769.md`
(its `ship` rows and the paragraph "Running count of conditional `ship`
rows"). On your base, lanes U0 to U3, R1 to R3, and T1 to T2 have landed:
`universes:` in the adapter, the declared gate list, the thin runner, and
`tools/`. Read `skills/public/quality/SKILL.md`, `.agents/quality-adapter.yaml`,
`skills/public/quality/adapter.example.yaml`,
`skills/public/quality/references/adapter-contract.md`,
`skills/public/quality/references/catalog.yaml`,
`skills/public/quality/references/consumer-validator-catalog.yaml`, and
`docs/export-boundary.md` AS LANDED.

Outcome: a consumer reading the quality skill sees only what checks their
repo's health; the skill's prose, catalogs, and example adapter name no gate
that lives in `tools/`; this repo's adapter declares its own universes and
nothing a consumer would have to copy; the planner
(`skills/public/quality/scripts/plan_quality_run.py`) proposes gates from
the declared list rows marked `ship`.

Design:

1. `SKILL.md` (keep under the skill ergonomics rules `validate-skill-ergonomics`
   enforces; no dated incidents, no issue anchors): "Consumer-repo health"
   becomes the centre; the bootstrap block adds one line showing
   `universes:` as the first thing a consumer declares; a short "What this
   skill does not run" list names the repo-only classes (packaging, export,
   skill contracts, presets, profiles, integrations, this repo's pointer
   freshness) as living in the authoring repo's `tools/`.
2. `adapter.example.yaml`: a `src/`-layout consumer with `universes:` filled
   in; every key that only charness needs is gone from the example (keep it
   in `.agents/quality-adapter.yaml`).
3. `catalog.yaml` and `consumer-validator-catalog.yaml`: remove or re-tag
   entries for moved gates; `check_consumer_validator_catalog.py` must stay
   green with `--require-adoption` for the `tools` row and without it for
   the `ship` row.
4. `plan_quality_run.py` reads `.agents/quality-gates.yaml` rows with
   `lane != tools` when the file exists; a consumer without the file keeps
   today's discovery.
5. `README.md` skill list entry for quality and `docs/index.md` link to
   `docs/export-boundary.md` if T1 did not add it.

Scope: the files named, `skills/public/quality/scripts/plan_quality_run.py`
and its tests, `tests/quality_gates/test_quality_skill_docs.py` and the
catalog tests. Do not touch `plugins/**`. Do not spawn descendant agents.

Verification before you stop:

```
python3 scripts/validate_skill_ergonomics.py --repo-root .
python3 -m tools.validate_skills --repo-root .
python3 -m tools.validate_quality_reference_catalog --repo-root .
python3 scripts/check_consumer_validator_catalog.py --repo-root . ; python3 scripts/check_consumer_validator_catalog.py --repo-root . --require-adoption
python3 skills/public/quality/scripts/plan_quality_run.py --repo-root .
python3 scripts/sync_root_plugin_manifests.py --repo-root .
python3 scripts/run_standing_pytest.py --repo-root . --pytest-target tests/quality_gates
./scripts/run-quality.sh --full --read-only
./scripts/check-docs.sh
```

Commit in ONE commit with subject
`quality: re-scope the skill, example adapter, catalogs, and planner to the consumer definition (#769 S lane candidate)`.
No close keyword. Stop after the commit and report the hash.
