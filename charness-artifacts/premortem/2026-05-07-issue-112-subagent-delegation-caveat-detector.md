# Premortem: Issue #112 init-repo Weakening-Caveat Detector

Date: 2026-05-07

## Decision

Close GitHub issue #112 by extending `init-repo`'s AGENTS.md inspector with a
section-scoped negative-pattern advisory that catches caveat wording which
weakens the standing subagent delegation contract before any concrete spawn
failure.

- add `FRESH_EYE_DELEGATION_CAVEAT_PATTERNS` (closed enumeration of 4
  case-insensitive substrings) and `_extract_section` helper to
  `scripts/init_repo_agent_docs_lib.py`
- run pattern detection only against the body of `## Subagent Delegation`
  (heading match is case-insensitive on the stripped line; body ends at the
  next `## ` heading or EOF) so caveat phrases that legitimately appear in
  `Phase Rules`, `Policy Index`, or other sections do not produce false
  positives
- emit a new finding `fresh_eye_delegation_caveat_weakens_contract` registered
  in `FINDING_RECOMMENDATION_PRIORITIES` with priority `advisory`, surfaced as
  a recommendation but not a hard failure (matches the issue's "recommendation
  or finding, not necessarily a hard failure" guidance)
- expose detected patterns at
  `agent_docs.normalization.fresh_eye_review.weakening_caveats_detected[]`
- update `skills/public/init-repo/references/agent-docs-policy.md` `Rule`
  section to enumerate the 4 patterns operators must avoid, and add a top-level
  bullet describing the new advisory finding so the inspector signal lines up
  with written policy
- add three regression tests in
  `tests/quality_gates/test_init_repo_inspect_policy.py`:
  caveat inside section emits the finding at advisory priority, mixed-case
  heading still extracts the section, caveat phrase outside the section does
  not emit
- re-sync the plugin mirror via `scripts/sync_root_plugin_manifests.py` so
  `plugins/charness/scripts/...` and `plugins/charness/skills/init-repo/...`
  stay in sync with canonical sources

## Likely Misread

A future operator could read the new advisory as a hard "this AGENTS.md is
broken" gate, but the recommendation entry carries `priority: advisory` and
the inspector still returns a non-zero exit only via existing mechanisms.
Status remains `needs_normalization` for any finding regardless of priority,
so operators reading status alone cannot distinguish advisory from
review_required without inspecting `recommendations[].priority`. This is a
known soft signal rather than a hard failure, and matches existing inspector
behavior for advisory-priority findings.

## Counterweight Triage

Act Before Ship:

- Use case-insensitive equality on the stripped heading line in
  `_extract_section` so the gate (lowercased substring) and extraction stay
  consistent. Without this fix, `## Subagent delegation` (lowercase 'd') flips
  the gate to True but extraction returns empty body, silently skipping the
  caveat scan. Added a mixed-case heading regression test.
- Lock the close keyword to the final-token form (`Closes #112`) on its own
  trailing clause so GitHub auto-close fires; recent retro lessons explicitly
  flag the multi-issue commit-message trap.

Bundle Anyway:

- Sync the plugin mirror with `python3 scripts/sync_root_plugin_manifests.py`
  immediately after canonical edits so the verify phase sees identical
  canonical and plugin payloads.
- Run the full `tests/quality_gates` suite plus `validate_skills.py` and
  `check_doc_links.py` to catch payload-shape break in adjacent inspector
  tests.
- Verify against a `crill`-shaped weakened AGENTS.md fixture (the exact
  caveat wording cited in issue #112 body) so the prevention is observed
  rather than asserted.

Over-Worry:

- Fenced-code blocks containing `## ` inside the Subagent Delegation section
  could cause `_extract_section` to truncate early. Realistic occurrence in
  `AGENTS.md` is near zero; markdown AST parsing for an advisory-priority
  4-pattern check is over-engineering.
- BOM or CRLF whitespace edge cases at the heading. `splitlines()` and
  `.strip()` handle the realistic shapes; the BOM case shares the same fix as
  the case-mismatch concern.
- Self-trip via overlap with `FRESH_EYE_REQUIRED_SNIPPETS`. Substring overlap
  was checked manually: none of the 4 caveat patterns is contained in any
  positive snippet, and none of the positive snippets is contained in a
  caveat pattern.
- `higher-priority host` colliding with affirmative wording like "If a
  higher-priority host actually blocks `spawn_agent`, report it." The
  canonical Charness AGENTS.md and reference doc do not use that exact
  phrasing. At advisory severity, the rare false positive is cheap operator
  noise; dropping the most diagnostic part of the crill caveat would weaken
  detection more than it would help.

Valid but Defer:

- Paraphrase escapes of the closed enumeration (e.g. `"obey that stricter
  rule"`, `"after the user authorizes subagents"`, `"another explicit user
  delegation"`). Adding broader substrings now risks false positives in
  retrospective prose; expanding to regex or fuzzy matching at the inspector
  layer is exactly the over-engineering the contract warns against. Add
  literal patterns when a real-world miss is observed, not speculatively.
- Grading `normalization.status` by the highest finding priority so operators
  can tell advisory from review_required without inspecting recommendation
  entries individually. Useful future refinement, not load-bearing now.

## Deliberately Not Doing

- A regex / fuzzy-match layer on caveat detection. Closed substring is the
  conservative move for an advisory-priority inspector; expansion happens
  when a real regression slips through.
- A markdown AST parser for `_extract_section`. Line-based section walking is
  honest about the actual shape of `AGENTS.md` files this repo and adjacent
  Charness-managed repos write.
- Re-grading `normalization.status` to reflect highest priority. Tracked for
  future enhancement; out of scope for issue #112.

## Fresh-Eye Satisfaction

parent-delegated. Three angle bounded subagents (false-positive scoping,
pattern coverage, contract integrity) plus one counterweight subagent ran in
parallel before closeout; their findings are encoded in the triage above.

## Next Move

Closeout: stage canonical and synced mirror changes plus tests and policy
reference, ensure the commit message ends with `Closes #112` as the final
trailing token, push, and confirm GitHub auto-close fires.
