perf: scope focused mutation coverage export

Closes #505

Classification: deferred-work

JTBD: Make the local mutation/quality-gate runtime actionable without weakening
changed-line coverage, failure visibility, boundary contracts, or the existing
proof floor.

Boundary: The local focused changed-line coverage producer/export and its
consumer-facing JSON artifact. Broad closeout coverage, test selection, consumer
verdict logic, and remote/public proof are outside this slice.

Resolution brief: inline (no pause) — in scope was one measured, proof-preserving
runtime improvement on the owned focused producer path; out of scope were floor
weakening, test-pattern pruning, broad CLI harness changes, and Cautilus.

Root cause: the focused producer ran the right mapped tests but exported coverage
JSON for the entire repository. The changed-line consumer only reads mapped changed
files, so repository-wide JSON serialization was structural runtime waste.

Implementation: pass the mapped changed mutation-pool paths to coverage JSON export
as one comma-separated `--include` argument. Preserve the unfiltered broad producer,
write the freshness marker only after successful export, keep unmapped files partial/
unproven, and add one-path, multi-path, and producer-boundary regression tests. Sync
the checked-in plugin mirror.

Prevention: keep selector ownership (what runs), producer ownership (how coverage is
collected/exported), and consumer ownership (the verdict) separate; require a matched
export timing/size observation before any future test-scope or proof-floor change.

Critique #505: charness-artifacts/critique/2026-08-06-issue-505-focused-export-resolution-critique.md

Behavior #505: local-only-by-contract — `python3 scripts/prepush_focused_changed_line_coverage.py --repo-root . --base-sha origin/main --json` returned `0`, reported `clean`, and analyzed `4/4` changed pool files after the implementation commit. This is a distinct producer/consumer roundtrip channel from the focused pytest regression suite. Remote CI and installed-host behavior remain unproven.

Fresh-Eye Satisfaction: parent-delegated high-leverage review ran in two named
rounds; the first found and the second verified the repaired multi-path export seam.
Both reviewer boundary fingerprints were clean.

AI-provenance: implementation and closeout text were authored with Codex; the
delegated reviewer findings are recorded in the linked critique artifact.
