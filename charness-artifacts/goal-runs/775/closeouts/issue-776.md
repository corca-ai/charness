quality: render the docs-graph phase line from what awiki's exit code means to the gate (#776)

Closes #776

awiki exits 1 on any lint finding, and link_only_lines under the recorded bar
is a finding, so every full lane on this tree printed FAIL [docs-graph-awiki]
beside a docs-graph status: pass. The docs-graph gate is label-only; no
aggregate read that line, only the operator did, as a red. The gate now owns
its terminal lifecycle line: exit 1 renders as OBSERVED with the reason, exit
0 keeps PASS, and a timeout or an unknown exit code keeps the guard's FAIL
beside the gate's NOT-RUN verdict. RUN and HEARTBEAT still stream live.
scripts/core/subprocess_guard.py is untouched.

The addition pushed check_docs_graph.py over the 480-line cap, so the awiki
process contract (argv, timeout, exit codes, lifecycle line, summary and
finding-block parsing) moved to scripts/gates_support/docs_graph_awiki.py;
the gate keeps the metrics, bars, ratchet, and verdict rendering.

Classification: feature
Jtbd: an operator reading a full lane sees a red phase line only when the docs-graph gate's own verdict is red or not-run, so the console and the gate report the same truth.
Boundary: scripts/gates/check_docs_graph.py, the new scripts/gates_support/docs_graph_awiki.py, tests/test_docs_graph_gate.py, and docs/docs-graph-checks.md. What the gate measures, its bars, and its lane are unchanged; subprocess_guard.py is unchanged.
Resolution Brief: charness-artifacts/goals/2026-09-03-verification-shape-alignment.md slice 1 and the #776 Work Item body.
Implementation: run_awiki passes its own stream to run_monitored_phase, forwards RUN and HEARTBEAT lines live, holds the guard's terminal PASS/FAIL line, and prints it or an OBSERVED line from the exit code; the extraction is a cut of the awiki contract with the gate binding _run_awiki by name so verdict tests can still patch the observation out.
Prevention: three seeded tests through a real stub binary on PATH: lint findings under every bar pass with no FAIL line and exactly one terminal line; findings over a bar fail by the named metric with the same neutral line; a timeout and an unknown exit code keep the guard's FAIL line.
Behavior: verified — before: python3 scripts/gates/check_docs_graph.py --repo-root . printed status: pass on stdout and FAIL [docs-graph-awiki] on stderr; after: stdout byte-identical, stderr OBSERVED [docs-graph-awiki]; tests/test_docs_graph_gate.py 56 passed; run_standing_pytest.py 8620 passed with release_only and slow_corpus deselected; ./scripts/run-quality.sh --full --read-only 81 passed, 0 failed; ./scripts/check-docs.sh PASS, all read on the integrated tree at the #777 closeout, which includes this commit; the full lane printed RUN and OBSERVED for docs-graph-awiki and no FAIL line.
Review disposition: critique not required; reversible change local to the gate, proven by seeded lifecycle tests and a byte-identical verdict before and after.
AI-provenance: implemented, probed, and verified by an AI agent (Claude Code) in the Goal Run #775 session.
Goal lineage: Goal Run corca-ai/charness#775; draft sha256 6f2f63ecd8264a4502f7feeb9884a2e2cbb5e3f288be22536fd93a2eed010898; binding sha256 ea389dd26293eb3deff01bf502073c6d242dd84bb3a1df42b245fcac729d46b0; Work Item awiki-phase-echo (#776).
