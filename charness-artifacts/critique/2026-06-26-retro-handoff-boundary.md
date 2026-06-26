# Critique Review
Date: 2026-06-26

## Decision Under Review

Ship the retro/handoff boundary cleanup slice that converts repeated
subprocess-based behavior assertions to in-process `main()` calls.

## Failure Angles

- Test boundary: the conversion could delete the only real CLI proof for
  `refresh_recent_lessons.py`, `persist_retro_artifact.py`, or
  `propose_merges.py`.
- Test isolation: monkeypatching `sys.argv`, `sys.stdin`, and captured output
  could leak process-global state across pytest cases.
- Goal discipline: the new active goal artifact could carry scaffold text or
  missing coordination cues that become a late closeout failure.

## Counterweight Pass

- `refresh_recent_lessons.py` still has a real CLI run in
  `tests/quality_gates/test_retro_lesson_selection_index.py`.
- `persist_retro_artifact.py` still has a real CLI run in
  `tests/quality_gates/test_portable_json_artifacts.py`.
- Handoff parser and installed-layout tests still exercise adjacent CLI
  delivery boundaries; `propose_merges.py` behavior now runs through `main()`
  with stdin, which keeps the pipeline behavior without a subprocess.
- Pytest's `monkeypatch` and `capsys` fixtures scope the process-global changes
  per test; focused pytest confirmed no observed leakage.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_recent_lessons_refresh.py:17 | action: fix | note: direct `main()` runner keeps stdout JSON assertions while eliminating two subprocess launches
- F2 | bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_retro_persistence.py:17 | action: fix | note: direct `main()` runner preserves stdout/stderr assertions for seven persistence cases
- F3 | bin: bundle-anyway | evidence: strong | ref: tests/test_handoff_chunker_parse.py:372 | action: fix | note: merge proposal behavior uses monkeypatched stdin with `main()` while parser CLI smokes remain
- F4 | bin: valid-but-defer | evidence: moderate | ref: tests/quality_gates/test_hitl_report_mode.py | action: defer | note: render_report has many subprocess calls but also unique argparse/CLI proof, so split before conversion
- F5 | bin: valid-but-defer | evidence: moderate | ref: tests/quality_gates/test_record_metric_window.py | action: defer | note: record_metric_window has CLI error-path proof; converting it safely needs a retained boundary smoke first

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: agent_type=explorer, fork_context=false, model inherited/default
- Host exposure state: requested_fields_sent
- Application state: reviewer completed and returned no findings

## Fresh-Eye Satisfaction

parent-delegated: bounded reviewer `019f015c-bba6-79b2-9fa2-43135fc21015`
completed through `multi_agent_v1.spawn_agent`; it found no issues and
confirmed retained CLI proof, no process-global leakage concern, and no obvious
goal-artifact shape failure.
