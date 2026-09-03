tests: census every wall-clock site in tests/, refuse a new one, and make the #764 baseline failures deterministic (#779)

Closes #779

Six scheduled mutation runs failed in their coverage baseline before any mutant
ran (#764). Read from the latest run's log rather than the issue's name list,
the five failures were two wall-clock claims and three verification-shape
leaks: the CLI skill surface drain tests required one escaped grandchild per
probe attempt and an elapsed time under fifteen seconds, both of which a loaded
runner breaks; the markdown preview tests built an "isolated" PATH from the
interpreter's directory, which locally also holds git and script and on the
hosted runner holds neither; and the issue source capture CLI bound its gh
runner as a definition-time default, so the test's patch never reached it and
the locally authenticated gh answered instead. The CI-shape baseline on this
tree also caught a checkout copy racing a sibling worker's cargo build.

The census records 96 wall-clock sites in tests/ (51 in rewrite scope) in
charness-artifacts/goal-runs/775/wall-clock-census.md. check_wall_clock_form.py
refuses a new time.sleep, time.monotonic, or time.perf_counter call in tests/
and holds the recorded sites (47 after this commit, in 14 files) to a per-file
count that only shrinks; the remainder is #780.

Classification: feature
Jtbd: a maintainer can read the hosted mutation sampler's baseline as a statement about the tree, because no test in it claims a wall-clock outcome and a new one is refused before it lands.
Boundary: scripts/gates/check_wall_clock_form.py with its baseline record, test, and registration (.agents/quality-gates.yaml, the fixture copy, tests/quality_gates/support.py, the repograph label fixture, the consumer-validator catalog, docs/validator-timing-layers.md); tests/quality_gates/test_cli_skill_surface.py, tests/test_markdown_preview_support.py, tests/test_issue_source_capture.py, scripts/issue/capture_issue_source.py (runner resolved at call time), tests/charness_cli/test_codex_cache_refresh.py (path-anchored checkout copy); docs/development.md. No retry, tolerance widening, or deselection anywhere; the sampler and the #358 recovery rule are untouched. #764 stays open for the recovery observer.
Resolution Brief: charness-artifacts/goals/2026-09-03-verification-shape-alignment.md slice 4a and the #779 Work Item body.
Implementation: the drain tests keep `assert escaped_pids` as the precondition that makes the deadline load-bearing and drop the per-attempt equality and the elapsed bound, since `_run_bounded_in_own_session` is the bound and `result is not None` is the claim; `_isolated_path` names git and script explicitly; `run_capture` resolves `runner` from the module global at call time and the test patches the module under test; the checkout copy uses `repo_copy_ignore_for`, which keeps only the built repograph binary under target/.
Prevention: test_wall_clock_form_gate.py seeds a sleep, a monotonic deadline, an imported sleep, and a perf_counter call and each turns the gate red; a sleep inside a seeded child string, a time.time() age, and a fixtures/ child stay green; the writer refuses to raise a count; the live-repo test asserts nothing above the record. The issue source test now passes with a fake gh on PATH that exits 4, which the old test could not.
Behavior: verified — CI-shape baseline (fresh clone, mirror materialised, node_modules/.bin on PATH, CHARNESS_REQUIRE_MARKDOWNLINT=1, the sampler's own command) before: 1 failed, 8619 passed (the checkout-copy race); after: 0 failed, 8631 passed in the sampler's coverage baseline (the sampler was still post-processing coverage at commit time; its coverage-baseline pytest is the step that failed in every #764 run and it passed); python3 scripts/gates/check_wall_clock_form.py --repo-root . --require-git-file-listing validates 624 test files with 47 recorded sites and none new; tests/test_issue_source_capture.py, tests/test_markdown_preview_support.py, and tests/quality_gates/test_cli_skill_surface.py 84 passed with a fake gh exiting 4 first on PATH; run_standing_pytest.py 8631 passed with release_only and slow_corpus deselected; ./scripts/run-quality.sh --full --read-only 82 passed, 0 failed; ./scripts/check-docs.sh PASS. The hosted run on the pushed tree is read in integrated-closeout (#782).
Review disposition: critique not required; test rewrites proven by seeded refusals and the CI-shape baseline before and after, with the operator's 2026-09-03 rule (rewrite or delete, never retry, widen, or deselect) applied per site.
AI-provenance: implemented, probed, and verified by an AI agent (Claude Code) in the Goal Run #775 session.
Goal lineage: Goal Run corca-ai/charness#775; draft sha256 6f2f63ecd8264a4502f7feeb9884a2e2cbb5e3f288be22536fd93a2eed010898; binding sha256 ea389dd26293eb3deff01bf502073c6d242dd84bb3a1df42b245fcac729d46b0; Work Item wall-clock-census-and-764 (#779).
