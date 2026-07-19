# Fake Git Proxy Speed Retro
Date: 2026-07-19

## Mode

session

## Context

The standing suite's slowest family repeatedly started a Python fake-Git process before real Git. The slice replaced that test-only layer with a Bash proxy, then repaired semantic and surface-ownership gaps found by fresh-eye review.

## Evidence Summary

- The exact serial command for 41 release-resilience tests fell from 51.41s to 30.38s on this host; the final seven-file release packet passed 102 tests in 6.16s under the canonical xdist runner.
- Direct proxy tests cover C0/Unicode JSON argv, element-wise fault matching, log-derived push counts, and after-mode real-Git failure normalization.
- Closeout initially rejected the new shell fixture as unmatched; the final surface routes `tests/*.sh` through shell lint and standing pytest, and a direct discovery test proves the nested fixture reaches ShellCheck.
- Packet Consumed: charness-artifacts/retro/2026-07-19-003309-packet.md

## Waste

The avoidable rework was optimizing the process shape before writing the fake-Git compatibility envelope. That let argv-boundary collapse, partial JSON escaping, and sidecar state reach review. A second assumption mapped the new file to `check-shell.sh` without checking that the command actually discovered test fixtures. Both were caught before broad proof, but the method should have started from exact inputs, state, outputs, and validator consumption.

## Critical Decisions

- Keep real Git and temporary remotes; remove only the redundant Python proxy startup.
- Define fixture compatibility by decoded argv, fault-injection semantics, and fresh ephemeral logs, not retired JSON whitespace or traceback text.
- Treat surface routing as a producer/consumer contract: selecting a validator is insufficient unless that validator reads the changed file.

## Expert Counterfactuals

- Douglas Engelbart's `(H + LAM + T)` lens would specify the proxy envelope and its verification tool together: argv/state/exit semantics plus the exact lint discovery path. That would have made both review repairs first-pass implementation constraints.
- A performance-engineering lens would profile the repeated process chain, remove one startup layer, and benchmark the identical selection before considering test deletion or weaker release proof—the sequence this slice ultimately followed.

## Sibling Search

- same layer: Python fake-CLI fixtures such as `release_publish_fake_gh.py` | decision: diagnostic-only | proof: source scan found another proxy, but this slice has no isolated timing evidence that it dominates a standing critical path
- abstraction up: `.agents/surfaces.json` validator routing | decision: same waste, fix now | proof: `tests/*.sh` now selects shell lint and a direct test proves the lint command consumes a nested fixture
- specialization down: fake-Git fault modes | decision: same waste, fix now | proof: direct regressions pin argv boundaries, JSON controls, log-derived counts, and after-mode failure
- mental-model siblings: shell fixture discovery | decision: same waste, fix now | proof: root and plugin `check-shell.sh` now conditionally scan the tests tree and focused discovery tests pass

## Next Improvements

- workflow: write the compatibility envelope before replacing a repeated boundary process, then benchmark identical work.
- capability: for new surface patterns, test both route selection and validator consumption of a representative file.
- memory: preserve “remove redundant startup, not proof” and “planned validation is not consumed validation” as reusable speed rules.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-07-19-fake-git-proxy-speed-retro.md
