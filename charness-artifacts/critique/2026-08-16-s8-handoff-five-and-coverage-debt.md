# Critique Review
Date: 2026-08-16

## Decision Under Review

Resolving the five handoff items (#632, #618 residual, #528, #634's shell-gate half,
#546's measured half) and paying the aggregate changed-line coverage debt (244 lines
across 69 files) before pushing 51 commits and publishing 6.0.0.

## Failure Angles

- A consumer-facing repair that names a path only the authoring repo has: the exact
  class #632 reports, and the class most likely to recur inside its own fix.
- A documentation placeholder (`<repo-root>/`, `<plugin-dir>/`) inserted into a field
  that is EXECUTED rather than read: `<` and `>` are shell redirections, and the
  adapter runners use `shell=True` or `shlex.split` with no expansion.
- A new blocking gate that manufactures findings on correct prose, making its own
  escape hatch routine.
- Consolidating six hand-copied shell guards into one: a single defect now reaches
  every repo-root gate at once, including the pre-commit and pre-push lanes.
- Coverage written to satisfy a line counter rather than to fail when behavior breaks,
  across 69 files and six concurrent authors.
- A repaired proof surface carrying the class it repaired — the reason this repo's
  contract requires a second review round over the repairs themselves.

## Counterweight Pass

Round 1 (three bounded reviewers, disjoint angles) and round 2 (one bounded reviewer
over the repairs) produced 27 findings. The dispositions that mattered:

REAL, and acted on before shipping. Round 1 found that retargeting instruction sites
to `<repo-root>/` had broken four executed command fields, and that the new blocking
detector arm refused correct consumer-facing prose. Both were net regressions, so the
entire `#634` instruction-site arm was REVERTED rather than patched — a smaller true
claim beats a larger false one. Round 2 then found six defects in round 1's repairs,
including two that were strictly worse than what they replaced: `fnmatch` disagreeing
with `Path.glob` in both directions on one pattern (dropping a root-level gate out of
DISCOVERY, not just miscounting `foreign`), and a `labels_key` pointer that dangled in
the one payload a reviewer reads.

OVER-WORRY, and left alone. Round 2's concern that `runtime_visibility_lib` is an
odd home for a budget helper: it imports nothing from the quality package, so there is
no cycle, and it is the module that already owns "make the population legible".

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/references/coverage_floor_inventory.py | action: fix | note: fnmatch crossed `/` for `*` and demanded a literal `/` for `**/`, so discovery and matching disagreed; replaced by one glob engine used by both
- F2 | bin: act-before-ship | evidence: strong | ref: skills/public/release/references/adapter-contract.md | action: fix | note: a `<repo-root>/` placeholder in a shell=True sync_command parses as a redirection; the whole instruction-site arm was reverted
- F3 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/scripts/runtime_visibility_lib.py | action: fix | note: labels_key named a key bounded_list renames, so the pointer dangled in summary mode; pointer removed
- F4 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/references/coverage_floor_inventory.py | action: fix | note: the no-lefthook SKIP could not tell declared-absent from configured-and-misspelled, turning a broken reference into a green
- F5 | bin: act-before-ship | evidence: strong | ref: scripts/exported-copy-guard.sh | action: fix | note: the CHARNESS_REPO_ROOT refusal keyed on presence, reddening a correct root on `--help`; now refuses only on disagreement, with exit 2
- F6 | bin: act-before-ship | evidence: strong | ref: scripts/lesson_command_citation.py | action: fix | note: repo_carries_index_builder disagreed with the provenance guard about the checked-in export; both predicates now required
- F7 | bin: act-before-ship | evidence: strong | ref: scripts/run_standing_pytest.py | action: fix | note: tests/test_*.py is a flat glob, so tests/coverage_debt would have contributed no coverage to the gate at all
- F8 | bin: act-before-ship | evidence: strong | ref: scripts/inventory_skill_script_references.py | action: fix | note: the new blocking arm refused correct prose naming a consumer's own script; arm reverted rather than narrowed
- F9 | bin: act-before-ship | evidence: moderate | ref: skills/public/handoff/scripts/chunked_routing_cli.py | action: fix | note: a bare JSON scalar bypassed the structural refusal the YAML path applies, so one input had two verdicts
- F10 | bin: act-before-ship | evidence: moderate | ref: scripts/record_usage_feedback.py | action: fix | note: the handler declared four exceptions the loader absorbs and omitted SchemaError, the one that escapes
- F11 | bin: valid-but-defer | evidence: moderate | ref: scripts/export_self_sufficiency_lib.py | action: file-issue | follow-up: deferred docs/handoff.md#next-session | note: the unshipped-path arm counts AST literal nodes, so a subpath written as one literal escapes it
- F12 | bin: over-worry | evidence: weak | ref: skills/public/quality/scripts/runtime_visibility_lib.py | action: defer | note: the helper's home reads oddly by name; there is no cycle and it is the module that owns legibility

## Reviewer Tier Evidence

- Requested tier: n/a
- Requested spawn fields: subagent_type=bounded-reviewer, no host addressing name
- Host exposure state: applied
- Application state: host-confirmed: four bounded-reviewer spawns returned findings inline
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated

## Reviewed Input Identity

<!-- No prepare_packet packet was consumed; reviewers were given explicit file and finding scopes inline. -->

## Boundary Ownership

- Producer: the repo-owned gates and skill references repaired here
- Consumer: a consuming repo reading the installed plugin, and this repo's own standing lane
- Owning surface: skill-packages and repo-python
- Verdict: owned-correctly
