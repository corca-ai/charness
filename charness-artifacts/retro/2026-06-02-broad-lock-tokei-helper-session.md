# Session Retro: Broad Lock, Tokei Length Gate, Stable Goal Helper

## Mode

session

## Context

This run closed the gap between remembered lessons and executable gates: broad closeout now needs an explicit verification lock, `charness goal check` gives #278 a stable helper surface, and Python file/headroom length checks now use `tokei` code-line counts.

## Evidence Summary

- Goal artifact: `charness-artifacts/goals/2026-06-02-enforce-recent-lessons-broad-gate-lock.md`
- Critique packet: `charness-artifacts/critique/2026-06-02-003849-packet.md`
- Pre-lock closeout: deterministic gates passed with `--skip-broad-pytest` and skipped broad pytest recorded.
- Post-lock closeout: `--verification-lock` run passed, including broad pytest (`2020 passed, 4 skipped`).

## Waste

The costly pattern was not ignorance of the rules; it was relying on read memory instead of an executable refusal point. The same shape appeared twice: `recent-lessons` was read but did not stop pre-lock broad pytest, and `tokei` existed but was not connected to the hard length gate. Both let operator intent degrade into convention.

## Critical Decisions

- Make `run_slice_closeout.py` fail closed before broad pytest unless the caller chooses either pre-lock skip or post-lock verification lock.
- Treat `tokei` as the hard file/headroom measurement source and fail closed rather than falling back to physical `splitlines()` counts.
- Use `charness goal check` as the #278 stable helper surface and resolve relative goal paths against the target repo, not the helper checkout.

## Expert Counterfactuals

- Gary Klein would have asked where the next operator would be forced to notice the risky phase transition. The answer was not `recent-lessons.md`; it had to be the closeout command itself.
- Daniel Kahneman would have separated the remembered label (`tokei`) from the actual measurement implementation. The code path, not the memory, needed to be inspected before trusting the claim.

## Next Improvements

- workflow: treat “we have a tool/lesson” as unproven until the specific hard gate path uses it.
- capability: when a support binary is promoted from advisory evidence to a hard gate dependency, update the integration manifest in the same slice.
- memory: record that closeout evidence should be gathered pre-lock, but final broad proof still needs a concise post-lock evidence append.

## Sibling Search

Transferable pattern scanned: existing advisory/support evidence not wired into the hard gate that operators assume it owns. Siblings checked in this run: `tokei` SLOC inventory vs `check_python_lengths`, stable helper scripts vs plugin-cache paths, and broad pytest lesson vs `run_slice_closeout.py`. The first two were fixed; broad command-shape generalization was classified valid but deferred because the current detector matches the standing closeout command.

## Persisted

yes: `charness-artifacts/retro/2026-06-02-broad-lock-tokei-helper-session.md`
