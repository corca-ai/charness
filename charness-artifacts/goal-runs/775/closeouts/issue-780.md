tests: rewrite the remaining 47 wall-clock sites to forced observations and controlled clocks (#780)

Closes #780

Every remaining entry of the wall-clock census is gone: 47 time.sleep,
time.monotonic and time.perf_counter calls across 14 test files are now a
FIFO the controlled child holds (tests/fifo_witness.py: wait_line replaces
sleep-then-check, wait_eof replaces sleep-then-"the tree is dead"), a
controlled clock in the module under test, a blocking pipe read, or a
deleted elapsed-time assertion whose real claim was already made by a marker.
wall-clock-baseline.json is empty, so the gate rule is now "any call is red".

Classification: feature
Jtbd: a maintainer's green standing lane means the same thing on a loaded hosted runner as on the machine that wrote the test, because no test's claim depends on how fast the scheduler ran it.
Boundary: tests/ only, plus the gate docstring, the docs/development.md paragraph, the quality-gates note, the census header, and the baseline record. scripts/core/subprocess_guard.py is untouched. The probe-boundary tests of check_cli_skill_surface moved to tests/quality_gates/test_cli_skill_surface_probe_boundary.py when the pidfd wait pushed the original past the 800-line cap. Controlled children behind a kill proof now sleep 3600 s so a survivor cannot end EOF by dying of old age.
Resolution Brief: charness-artifacts/goals/2026-09-03-verification-shape-alignment.md slice 5 and the #780 Work Item body.
Implementation: shared witness written by the parent; the 14 files rewritten in parallel on disjoint files by two opus subagents, a Codex lane (task/wall-clock-fifo-four, cherry-picked) and a sonnet dynamic workflow; every diff reviewed in the parent, which caught a fake-clock step that also sized a real select timeout and raised it, and applied the guard subagent's 3600 s finding to the three other kill proofs. Record: charness-artifacts/goal-runs/775/2026-09-03-session-record.md, third session.
Prevention: check_wall_clock_form.py with an empty record refuses the first new call anywhere in tests/ (tests/quality_gates/test_wall_clock_form_gate.py); tests/test_fifo_witness.py pins the witness's own semantics including EOF waiting for an inheriting grandchild.
Behavior: verified — python3 scripts/gates/check_wall_clock_form.py --repo-root . --require-git-file-listing reports 0 recorded sites in 0 files; each rewritten file ran green three times serially and once under xdist; run_standing_pytest.py 8666 passed in 73 s; ./scripts/run-quality.sh --full --read-only 81 passed, 0 failed.
Review disposition: critique not required; reversible test-only change proven by the form gate at zero and the lanes; mutation of _kill_tree to a direct-child kill hangs the two guard tree tests as designed.
AI-provenance: implemented by two Claude subagents, a Codex lane and a Claude workflow, integrated, reviewed and verified by an AI agent (Claude Code) in the Goal Run #775 session.
Goal lineage: Goal Run corca-ai/charness#775; draft sha256 6f2f63ecd8264a4502f7feeb9884a2e2cbb5e3f288be22536fd93a2eed010898; binding sha256 ea389dd26293eb3deff01bf502073c6d242dd84bb3a1df42b245fcac729d46b0; Work Item wall-clock-rewrite-remainder (#780).
