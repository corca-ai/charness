# Code Critique — nose baseline tool_version stamp (issue #391 robustness-gap slice)

- Target reference: `code-critique` (bug-class resolution; recurrence focus)
- Fresh-Eye Satisfaction: parent-delegated (3 angle subagents + 1 counterweight, high-leverage)

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: model=opus (Claude Code host resolution of high-leverage; the critique adapter records the Codex-host mapping model=gpt-5.5, reasoning_effort=medium, service_tier=priority)
- Host exposure state: requested_fields_sent
- Application state: model=opus sent to all 4 bounded subagents (1 causal-review + 3 critique angles/counterweight) via the Agent tool; the host does not echo resolved spawn fields, so application is unverified-by-carrier (not claimed host-confirmed)

## Diff Scope

Both nose code id-set baselines now stamp the producing `nose --version` on
`--write-baseline` (from the same scan that minted the ids) and surface a version-skew
WARNING on read. `nose_report_lib.tool_version_skew` is the shared pure helper;
`nose_baseline_lib` / `dup_ratchet_lib` gained `load_*_tool_version` readers and
stamp-on-build; the advisory (`inventory_nose_clones.py`) and the BLOCKING gate
(`check_dup_ratchet.py`, whose `_code_family_ids`/`_scan_code_family_ids` are now
3-tuples threading the live version) consume it. Additive field, NO `schemaVersion`
bump. Both baselines re-stamped `tool_version: 0.14.0` (525→526, benign reshuffle).
`references/dup-ratchet.md` + tests updated. A causal review preceded design.

## Angles

- **Correctness + regression risk:** 3-tuple threading completeness; back-compat of
  the additive field; the #394 changed-line in-process-coverage trap; skew semantics.
- **Behavior + contract + scope:** warn-vs-degrade for the BLOCKING gate; operator
  legibility of the skew message under a hard-block; honesty of deferring the
  doc-signature baseline; doc/code agreement.
- **Counterweight:** is the stamp gold-plating; should the 3 version-readers be
  de-duped; are the ~15 tests over-pinned; is warn-not-degrade an over/under-build.

## Findings → Counterweight four-bin triage

**Act Before Ship:**
- None. All three reviewers returned SHIP with no blockers and no gating should-fixes.

**Bundle Anyway (applied):**
- None outstanding — the design already carried the items a bundle pass would add
  (stamp-from-same-scan comment, additive-no-bump justification, skew message
  appended after the hard-block so both signals show).

**Over-Worry (no change — counterweight rejected):**
- De-dup the 3 version-readers into one helper — REJECTED: they read 3 different
  sources (disk path, in-memory dict, injected JSON string) and live in
  independently-portable skill packages that deliberately clone their baseline I/O;
  extraction would manufacture the cross-package coupling the repo intentionally avoids.
- Trim the ~15 tests — REJECTED: honest branch coverage the #394 changed-line gate
  requires; the string assertions pin the load-bearing operator instruction
  ("re-baseline"), not incidental phrasing.
- Inflate warn-not-degrade into a configurable skew policy / auto-degrade — REJECTED:
  degrading a blocking gate on skew would silently let real new duplication through;
  warn-on-the-verdict is the conservative irreversible-boundary-respecting choice.
  Behavior verified: the gate keeps `status: hard-block` and appends the skew WARNING.

**Valid but Defer:** see Deliberately Not Doing.

## Deliberately Not Doing

- **Precise the injected-path comment.** The `check_dup_ratchet.py` comment "the stamp
  can never disagree with the ids it labels" is exactly true for the live-scan path and
  for a real injected inventory (one scan produces both version and ids); only a
  hand-crafted/stale test fixture could mismatch them. Making the comment precise means
  editing a scanned clone-member file, which rotates `family_id`s and forces ANOTHER
  full re-baseline cycle — disproportionate to a test-seam NIT (the batching-waste the
  implementation-discipline lesson guards). Left as-is.
- **Spell out the consumer-on-different-version recovery loop in the doc.** Structurally
  bounded already: baselines are charness-internal and seeded per-repo, NOT shipped to
  consumers, and `integrations/tools/nose.json` pins a single `>= 0.14.0` floor; the
  skew WARNING is itself the recovery affordance. Inferable from "explains a block";
  not worth a doc edit (also a scanned-file-adjacent reference churn cost).
- **A `--write-baseline` that refuses to stamp a version mismatching the ids.** Only
  reachable via a deliberately-malformed injected test payload; no real operator path
  hits it.

## Next Move

Verify (structural sweep + focused proof + changed-pool mutation coverage), commit
direct-to-default. Do NOT auto-close #391: the extraction-candidate follow-ups (the
3 cross-dir families) remain its open scope. Comment on #391 that the baseline
robustness gap is resolved with the commit ref; leave the issue open.
