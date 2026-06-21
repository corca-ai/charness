# Green main + #394 changed-line coverage — critique

Date: 2026-06-21

## Decision Under Review

Item A of the locked next-session sequence: make `main` green and clear the
`#394` mutation regression so the green suite is a trustworthy losslessness
oracle BEFORE any pin/test is deleted in the essence rollout. Three test-only
changes (no production code):

1. `tests/charness_cli/tool_fakes.py` — `make_fake_nose` `--version` bumped
   `0.13.3` → `0.14.0` to match the manifest floor `>=0.14.0` (bumped in
   `edd8bade`); the stale fixture was the standing-red
   (`test_installed_cli_update...::doctor_status == "ok"` saw `version-mismatch`).
2. `tests/test_nose_inprocess_coverage.py` — new
   `test_collect_families_keeps_identityless_families_unkeyed` covering the
   else-branch at `nose_report_lib.py:178` (`unkeyed.append(family)`) — the
   live changed-line-coverage blocking target on #394's latest run (`6791cf4f`).
3. `tests/quality_gates/test_achieve_adapter_policy.py` — 6 assertions pinning
   the `build_items` irreversible-boundary defaults (publish confirmation,
   post-publish verify, draft validation, disposition-review/none-optout floors,
   version) that survived as mutants in #394.

## Failure Angles

- **Masking, not fixing:** bumping the fake nose version hides a real regression
  (the doctor *should* report mismatch) rather than correcting stale fixture data.
- **Grep-bait coverage:** the new nose test names line 178 but does not actually
  execute it, or would still pass if the `unkeyed.append` were deleted.
- **Cosmetic pins:** the achieve assertions read like contract protection but
  assert values that do not come from the mutated `build_items`, or would not
  fail on a flip — pinning without teeth.
- **Goodhart:** chasing every survived mutant (incl. announcement output-format
  plumbing) to 100% instead of the blocking signal + high-value contract gates.

## Counterweight Pass

One bounded fresh-eye reviewer (read-only, shared parent worktree, `git show
HEAD:<path>` for prior versions) was tasked to REFUTE all three claims, reading
the production `nose_report_lib.py` (collect_families / family_identity),
`init_adapter.py build_items`, `doctor_lib.py` status logic, and
`control_plane_lib.py` SpecifierSet comparison directly. Verdict:
`HONEST-AND-FAITHFUL`. It traced (A) `0.13.3 in >=0.14.0` is False → `mismatched`
→ `version-mismatch`, so the bump is mandatory and the only other consumer
(`test_update_output.py:72`) never reads the version; (B) the identity-less
family routes to line 178 and both asserts (`in families`, `len==2`) fail if the
append is dropped; (C) each `build_items` literal is single-sourced and the
`is True` / `== 1` checks fail on any flip, and the gated defaults are genuine
irreversible-boundary contracts.

## Structured Findings

<!-- allowed enums (substitute only these) — bin: act-before-ship | bundle-anyway | over-worry | valid-but-defer; evidence: strong | moderate | weak | contested; action: fix | file-issue | document | defer. action: file-issue also needs a follow-up: (issue URL or 'deferred ' plus a handoff anchor). -->
- F1 | bin: valid-but-defer | evidence: moderate | ref: tests/quality_gates/test_achieve_adapter_policy.py:267 | action: document | note: the reviewer flagged that `disposition_floor: "review-required"` and `default_mode: "audit-only"` string literals in `build_items` stay unpinned by this file (string-replace mutants, not the flagged True/Number survived set). `disposition_floor` is already asserted via the resolver default path (line 43). Out of scope for the blocking-signal + irreversible-boundary-default goal; pinning every string literal is the goodhart move the north star warns against. Recorded in Deliberately Not Doing.
- F2 | bin: over-worry | evidence: strong | ref: skills/public/announcement/scripts/resolve_adapter.py:36 | action: document | note: #394's issue-body sample listed announcement `main` output-format mutants (`required=True`, `sort_keys=True`, `ensure_ascii=False`). These are argparse/JSON-formatting plumbing, not contract gates; killing them is low-value pinning. The blocking signal is changed-line coverage (score already passes 87.3%), so they are advisory. Left unpinned by design.

## Reviewer Tier Evidence

<!-- allowed Host exposure state: pending-parent-spawn | requested_fields_sent | metadata-hidden | host-defaulted | unsupported | applied. Use applied only with Application state: host-confirmed: plus a concrete signal. -->
- Requested tier: standard (one bounded reviewer; test-only, reversible scope, but touching the achieve irreversible-boundary contract).
- Requested spawn fields: model=default (Claude Code host resolution; no override for a single bounded reviewer on test-only work).
- Host exposure state: requested_fields_sent
- Application state: 1 bounded reviewer spawned via the Agent tool in the shared parent worktree, read-only (`git show HEAD:<path>` for prior versions, no index/worktree-mutating git ops); the host does not echo resolved spawn fields, so application is unverified-by-carrier (not claimed host-confirmed).

## Fresh-Eye Satisfaction

parent-delegated. The bounded reviewer returned `HONEST-AND-FAITHFUL` with a
per-claim (A/B/C) ledger and concrete `file:line` fail-on-mutation evidence,
after reading the production code paths end-to-end (not just the diffs).
Deterministic backstop: whole suite green — `tests/quality_gates/` 2283 passed,
broader `tests/` 1189 passed; verification-lock closeout exit 0 (ruff,
python-lengths, attention-state, test-repo-copy, boundary-bypass, standing
pytest read-only, agent-browser orphan guard all PASS); cautilus planner
`next_action: none` / `changed_public_skills: []` (test-only, no skill/prompt
surface — Cautilus correctly NOT run); sync no-op (no mirror drift).

## Deliberately Not Doing

- **Pin the achieve string-literal defaults (F1).** `disposition_floor` /
  `default_mode` are string-replace mutants, not the flagged True/Number set,
  and `disposition_floor` is already asserted via the resolver default. Pinning
  every literal is goodhart, not oracle-strengthening. Left to the surrounding
  suite; flagged here for maintainer eyeball.
- **Kill the announcement output-format mutants (F2).** argparse/JSON plumbing,
  not contract gates; advisory under the passing score. Out of scope for the
  changed-line blocking signal.
- **Run Cautilus.** Planner `next_action: none`; no public skill or prompt
  surface changed. Ask-before-run contract honored by refusing.
