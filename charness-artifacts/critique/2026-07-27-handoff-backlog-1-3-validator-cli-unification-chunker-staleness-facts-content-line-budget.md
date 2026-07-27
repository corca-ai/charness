# Handoff backlog 1-3: validator CLI unification, chunker staleness facts, content-line budget
Date: 2026-07-27

## Decision Under Review

Three operator-scheduled backlog items landed together: (1) D28's A+B+C — flip
debug/critique to one-pass default, make `--fail-fast` the only control, and
single-source every changed-path validator's `main()`; (2) #459 — report per-entry
resolvable-ness facts in chunked routing; (3) re-base the handoff size budget on
CONTENT lines at 58.

## Failure Angles

- **Silent behavior change under a "unification" banner.** Item 1 deletes two
  hand-written `main()`s. Anything the old ones did that the shared runner does
  not is a regression the diff makes look like cleanup.
- **A staleness fact that manufactures false comfort.** Item 2's whole value is
  telling an agent a backlog line is stale. An empty `closed_issues` list means
  "open" and "never asked" identically; a reader takes the comfortable reading.
- **A staleness fact that manufactures a false verdict.** The mirror risk: a
  live issue reported closed makes the chunker deprioritize real work.
- **A raised cap sold as a re-base.** Item 3 could be a budget increase wearing
  a measurement story.

## Counterweight Pass

Two bounded fresh-eye reviewers (distinct lenses: validator correctness /
behavior-change honesty, and staleness false-comfort) returned nine findings.
Six were real and are fixed below. Three were correctly bounded as non-blockers:
`--report-all` plus `--fail-fast` together resolving to fail-fast is exactly
"ignored"; `from_dict`'s `int()` coercion turns a malformed index into a shaped
error rather than a traceback; and the `run.selected_paths` fallback branch is
unread by its only caller.

The cap re-base is a re-base, not an increase: 13 of the 14 handoffs committed
before it pinned at 69-70 against a raw cap of 70, and those files carried ~50
content lines. 58 grants ~8 real lines while removing a structural penalty that
charged the same for a reference link as for a paragraph.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/artifact_validator.py:457 | action: fix | note: critique's factory resolved the cross-surface probe even with zero artifacts; an unresolvable base sha raises SurfaceError (not ValidationError), turning a silent pass into a crash. Fixed: the runner skips the factory on an empty set.
- F2 | bin: act-before-ship | evidence: strong | ref: skills/public/handoff/scripts/chunked_routing_staleness.py:227 | action: fix | note: the open set was read back off a SECOND module instance (skill loaders do not cache), so reuse was dead and every cited issue cost a provider call. Fixed: threaded explicitly from the CLI; verified same-object check fails, and the live `--with-issues` run is 0.9s.
- F3 | bin: act-before-ship | evidence: strong | ref: skills/public/handoff/scripts/chunked_routing_agentic.py:143 | action: fix | note: the checked/not-checked flags stopped at stage 1, so the packet the agent reads asserted a clean bill of health for a check that could not have run. Fixed: `staleness` forwarded through propose_merges into the packet, with a pipeline test.
- F4 | bin: act-before-ship | evidence: strong | ref: skills/public/handoff/scripts/chunked_routing_staleness.py:108 | action: fix | note: closed was a deny-list, so GitLab `opened` / Linear `started` / Jira `In Progress` would be reported CLOSED — a live issue called stale. Fixed: explicit CLOSED_STATES allow-list; unrecognized is UNKNOWN.
- F5 | bin: act-before-ship | evidence: strong | ref: skills/public/handoff/scripts/chunked_routing_staleness.py:180 | action: fix | note: 19-of-20 failed lookups plus one CLOSED reported as a clean check. Fixed: per-entry `unresolved_issues` plus `unresolved_issue_count`, so a PARTIAL check is legible as partial.
- F6 | bin: act-before-ship | evidence: moderate | ref: scripts/validate_debug_artifact.py:437 | action: fix | note: a wrong `--repo-root` now emitted "start from the owning scaffold" — advice to author a stub when the fix is a path. Fixed: the two non-violation exits print and exit 1 without the hint.
- F7 | bin: act-before-ship | evidence: moderate | ref: docs/deferred-decisions.md:253 | action: fix | note: D28 claimed "all five changed-path validators" route through the shared runner; it is four (quality and handoff are adapter-scoped and keep their own `main()`). Fixed.
- F8 | bin: bundle-anyway | evidence: moderate | ref: scripts/artifact_validator.py | action: fix | note: `selected_artifact_paths` lost its last caller, and leaving the pre-unification resolver exported is the one remaining affordance for forking `main()` again — exactly what C exists to prevent. Deleted in the same slice.
- F9 | bin: valid-but-defer | evidence: moderate | ref: skills/public/handoff/scripts/chunked_routing_auto_draft.py:99 | action: defer | note: the auto-draft renders a known-missing path as "In scope:" with no marker. Real, but it is a goal-artifact rendering concern rather than a fact-production one, and #459's scope is producing the facts. Follow-up: deferred docs/handoff.md `## Next Session`.
- F10 | bin: over-worry | evidence: weak | ref: skills/public/handoff/scripts/chunked_routing_staleness.py:61 | action: defer | note: an out-of-tree citation is skipped without a per-entry record. The reviewer is right that this is the same "empty means two things" shape, but the population is near-empty and adding a fourth fact field to guard it would cost more legibility than it buys.

## Reviewer Tier Evidence

- Requested tier: bounded read-only fresh-eye reviewer, two distinct lenses.
- Requested spawn fields: `subagent_type: bounded-reviewer`, no host addressing name (per the repo's named-spawn rule), session-model inheritance.
- Host exposure state: applied
- Application state: host-confirmed: both spawns returned findings inline in the Agent tool result, each reporting `envelope-bound` (Read/Grep/Glob only; no Bash/Edit/Write/Agent).
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated; two reviewers completed their assigned lenses and their
findings are dispositioned as F1-F10 above.

## Reviewed Input Identity

<!-- No prepare-packet consumed; the reviewers were briefed against the live worktree diff. -->

## Boundary Ownership

- Producer: `scripts/artifact_validator.py` for the shared validator CLI contract; `skills/public/handoff/scripts/chunked_routing_staleness.py` for resolvable-ness facts; `skills/public/handoff/scripts/handoff_content_budget.py` for the canonical sections and content-line rule.
- Consumer: the six artifact validators and `run-quality.sh`; the chunk-proposal packet the ranking agent reads; `validate_handoff_artifact.py`, `plan_handoff_run.py`, and `check_doc_authoring_preflight.py`.
- Owning surface: repo validator scripts for item 1; the portable handoff skill package for items 2 and 3.
- Verdict: owned-correctly
