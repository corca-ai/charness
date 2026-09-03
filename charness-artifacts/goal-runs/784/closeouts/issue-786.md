quality: timeout-bound form check sees a deadline-riding verdict with no time.* call (#786)

Closes #786

The wall-clock form check refuses time.sleep, time.monotonic, and
time.perf_counter in tests/; hosted run 33701977188 failed on a test with none
of them, whose verdict rode on a 0.5 s *_TIMEOUT_SECONDS knob and an assertion
on stdout the child had to print before that deadline. A sibling check,
check_timeout_bound_form.py, now refuses that shape by one closed AST
predicate over a test function: a *_TIMEOUT_SECONDS knob set under 5 s
together with an assert on the child's stdout, stderr, or returncode (or a name
derived from one), or a sub-second communicate/run/wait deadline whose
TimeoutExpired handler asserts; a function on a controlled clock is exempt. Its
docstring names the shapes it cannot see. The census settled every site in
today's tree; the record carries the four kept sites with written reasons and
only shrinks.

Classification: feature
Jtbd: a maintainer cannot land a test whose green depends on a child beating a short deadline, and can read exactly which shapes the gate does not see instead of inferring "none exist" from a green.
Boundary: scripts/gates/check_timeout_bound_form.py (new), charness-artifacts/quality/timeout-bound-baseline.json (new, four kept sites with reasons), tests/quality_gates/test_timeout_bound_form_gate.py (new), the label wiring in .agents/quality-gates.yaml, its test fixture, the repograph label universe fixture, tests/quality_gates/support.py, docs/validator-timing-layers.md, the docs/development.md testing paragraph, charness-artifacts/goal-runs/784/timeout-census.md (the pinned predicate and every disposition), and tests/quality_gates/test_cli_skill_surface_probe_boundary.py, from which test_cli_skill_surface_survives_a_probe_whose_grandchild_holds_the_pipe and its _run_bounded_in_own_session helper are deleted. No test is retried, widened, or deselected; check_wall_clock_form.py and the #358 recovery rule are unchanged.
Resolution Brief: charness-artifacts/goals/2026-09-03-lesson-review-and-775-followups.md slice 2 and the #786 Work Item body.
Implementation: the predicate was written into the census before the gate and extended by one closed rule first, because the pinned form was blind to the hosted shape itself (its assert reads a name two assignments away from result.stdout); transitive name taint within the function closes that. Census of the 12 knob-reading files and every sub-second deadline: four knob-bound sites the gate sees, all certain to fire (the child sleeps 4x to 150x the knob) with the claim on the reporting shape, kept with reasons; two #780 tests exempt on their controlled clock; three blind sites named in the census and docstring; one real-process boundary test deleted because its two claims (holder spawned and line printed before a 0.5 s kill) race the wall clock in the unsafe direction, cannot be forced on a real check process, and are owned non-vacuously by the in-process siblings on a controlled clock.
Prevention: tests/quality_gates/test_timeout_bound_form_gate.py seeds six red shapes (env knob, setenv knob with a derived-payload assert, setattr knob, attribute-assign knob, communicate deadline, run deadline with raise AssertionError), the controlled-clock exemption, eight out-of-rule shapes, the two stated blind shapes pinned as blind, record shrink and raise refusal, a reason required for every recorded site, malformed records, fixture children skipped, the empty-universe refusal, and the live tree against its record.
Behavior: verified — check_timeout_bound_form on the live tree: 635 test files scanned, 4 recorded sites in 4 files, none new; the standing runner and ./scripts/run-quality.sh --full --read-only green on the finished tree (counts in the session record); ./scripts/check-docs.sh PASS; the changed-line gate on this slice's own diff clean.
Review disposition: critique not required; a new standing gate proven by seeded refusals, and a test deletion whose surviving claims are named test by test in the census.
AI-provenance: implemented, censused, and verified by an AI agent (Claude Code) in the Goal Run #784 session.
Goal lineage: Goal Run corca-ai/charness#784; draft sha256 878f74409e4c271d07a87c4bb34108376d10878cfdc476249311ec3671a8a151; binding sha256 9e4650f0f731add79de7a0b68cc3b918ed087e71d7e28f43cb74c0973ddafd82; Work Item timeout-bound-census (#786).
