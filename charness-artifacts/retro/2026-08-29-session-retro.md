# Session Retro

Date: 2026-08-29

## Context

The 2026-08-28~29 session executed umbrella #744's step 4 and the
parallel test-corpus track: #748 slice 1 (seven Codex lanes; four Python
repository-boundary owners deleted and replaced by native `repograph`
commands behind one gate-side resolver), #743 resolved and CLOSED
through topology-derived test-role exclusion, #753 driven from
inventory to a blocking ratio gate (operator redirected the recorded
mutation pass to a JTBD audit mid-session), #672 retired, and the next
session designed with the operator (release-first keystone). This retro
exists because the work unit closed and the next session inherits both
its contracts and its traps.

## Window

2026-08-28 09:00 KST session start (post-#746/#747 retro) through
2026-08-29 issue #754 filing. Main moved `e83e71ee9..c1634aedf` plus
the retro-adjacent commits; five full standing batteries ended 78/0.

## Evidence Summary

- `charness-artifacts/design-studies/issue-748/evidence-748.md` —
  lane-by-lane record, real-binary cross-checks, four integration
  catches.
- `charness-artifacts/design-studies/2026-08-28-issue-748-migration-plan.md`
  rev 2 — two-opus-review disposition, slice boundary, deferred work.
- `charness-artifacts/design-studies/issue-753/` — island/orphan
  inventory (zero candidates), 371-file JTBD audit
  (96.5% keep), ratio decomposition table (Python-only denominator was
  the 1.18; executable surface ≈ 1.01), lane briefs.
- GitHub: #743 CLOSED (verified readback), #672 CLOSED
  (retired-subject), #748 slice comment, #754 filed.
- Command evidence quoted in-session: tokei/auto ratio 0.9931
  (145,829 source vs 144,826 test lines), dedup 6.8%→3.8% in
  `tests/quality_gates`, full battery logs. No adapter
  `metrics_commands` exist; no host-log probe was run — efficiency
  claims below are event-based, not token-measured.

## Waste

- **A parent-authored ambiguous brief sentence became a lane defect.**
  The RB brief said plugin-refs scans "outside fences/inline code,
  matching `iter_doc_lines`" — two contradictory clauses; the lane
  implemented inline-code masking and the real-repo subject set went to
  zero. Cost: one diagnosis-and-fix cycle. The parent's real-repo
  comparison (not the lane's tests) caught it.
- **A schema-seam fake pinned payloads but not argv shape.** P5's fake
  classify binary accepted a malformed `--path a b c` invocation, so a
  usage-error (exit 2) degradation shipped past lane tests and surfaced
  only in the parent's live multi-path proof.
- **Bulk `ruff check --fix` over `tests/quality_gates/` stripped a
  support-module re-export** (`seed_commit`), breaking four modules;
  one full-battery cycle to diagnose. The auto-fix was mine, applied
  wholesale to lane B's salvage.
- **Background-wait antipattern, operator-flagged twice.** A watcher
  process idled on P4's wrapper while the candidate commit was already
  inspectable in its worktree; two gitleaks runs scanned gigabytes of
  `native/repograph/target` because they bypassed the gate's
  tracked-population staging, timing out twice before a delta-scoped
  scan found the one finding in seconds.
- **Small unforced errors, each recovered:** popping a foreign stash on
  a clean tree (restored, stash preserved); launching a workflow with a
  placeholder string as `args` (restarted); re-running
  `close-with-comment` to read its output, double-posting the #743
  carrier (duplicate deleted); once misreading a task receipt's
  `after_head` (parent-tree movement) as the candidate sha (cherry-pick
  aborted cleanly).
- **Workflow synthesis truncation:** the JTBD synthesis agent received
  234/371 verdicts because the script sliced the JSON through the
  prompt; the parent re-merged from the journal. Data should have moved
  file-to-file, not through context.
- NOT waste: lane B's timeout salvage (96% of a 90-file refactor
  recovered from the worktree) and the five full batteries — each
  battery caught a real defect class the focused checks missed.

## Critical Decisions

- **Descoping D3/D4 (repo_file_listing, match_surfaces) after the
  contract review** proved consumer repos execute those exported
  helpers and would hard-break before the first artifact release. This
  reshaped the slice and is why the session ended green instead of
  shipping a consumer outage.
- **`test`-only exclusion for #743** (not `generated`): the review
  showed `generated` is surfaces-manifest-configured, so excluding it
  could let a manifest edit invert a publish gate.
- **Seam-first sequencing** (S1 proves the resolver on one gate before
  anything else) — adopted from the scope review; every later lane
  inherited a proven seam.
- **Operator mid-session redirects:** JTBD audit instead of the
  recorded mutation pass (the audit refuted the "prunable meta-layer"
  premise: 96.5% keep), tokei made mandatory on the full surface, both
  #753 lanes run in parallel, ratio gate promoted to blocking after the
  denominator fix. Fixing the metric instead of pruning healthy tests
  was the session's most consequential reframe.
- **Candidate-first integration** (adopted after the operator's
  "stop waiting" correction): integrate from a finished lane worktree
  without waiting for its wrapper; salvage timed-out lanes from their
  worktree instead of re-running.

## Trends vs Last Retro

Against `2026-08-28-umbrella-744-rust-core-session-retro.md`: all four
of its improvements were applied and paid off — per-lane full batteries
(caught four defect classes at integration time instead of one
end-of-session repair pass; last session: 32 late failures), canonical
runners named in briefs, the lane-brief template checked in before the
first lane, and the CI/cargo gap resolved by design (D1 provisioning +
dev-tree resolver). The standing "losing long runs to the timeout" trap
RECURRED in a new costume (lane B timeout, uncommitted work) — now
filed as #754 rather than re-learned. The "premise check" trap held:
the JTBD audit's `delete-code-and-test` candidate was adversarially
re-verified and refuted before any deletion.

## North Star Alignment

Read against `docs/design-north-star.md`: the session's strongest
alignment is **P-channel discipline at boundaries** — every closeout
used a distinct evidence channel (real-binary payloads for #743, set
equality and byte-equal reference kinds for the native owners, backend
readback for issue states), and the parent never treated a lane's green
self-report as integration proof (terminal-trust failure mode avoided
four times over). Deletion-over-layering held: net corpus shrank while
capability grew, and no tombstone gates were added for retired names.
One facet to watch: the blocking ratio gate is a new tooth — it earned
its place only because the denominator now measures the real executable
surface; if the surface definition drifts, the tooth becomes exactly
the bespoke-gate bloat the north star warns about.

## Expert Counterfactuals

- **Engelbart (system-improving-itself):** the session improved H (the
  operator's decisions were load-bearing five times) and LAM (native
  owners, blocking gate) but under-designed T at two joints. The brief
  is a tool artifact — RB's defect shows briefs need a rule: *state
  scan/skip sets by citing the owning source file, never by
  paraphrase*. And the task runner's timeout behavior is part of T:
  #754 exists because the tool discards exactly the state the
  improvement loop needs. Engelbart would have made the WIP-commit
  behavior part of the lane contract before running seven lanes.
- **Gary Klein (recognition-primed decisions / premortem):** the two
  escaped defects (inline-code masking, argv shape) share one shape —
  a plausible-looking artifact accepted without a disconfirming probe.
  A 60-second premortem per lane ("assume this lane's output is subtly
  wrong on the real repo — where?") names the real-repo comparison as
  the first integration step, which is in fact what caught both. The
  lesson is to run the disconfirming probe FIRST at integration, before
  the confirming test suite, not after.

## Next Improvements

- workflow — **candidate-first integration and worktree salvage** are
  now the standing lane policy. Destination: applied — appended to
  `.agents/claude-host.md` lane lessons this session? No: NOT yet
  applied; carried as `repo-local guard: .agents/claude-host.md`
  (one-paragraph addition next session alongside the release).
- workflow — **briefs cite, never paraphrase, an owning source for
  scan/skip/match sets.** Destination: applied —
  `.agents/lane-brief-template.md` gains the rule (next session, same
  edit as above); the RB defect is the triggering instance.
- capability — **seam fakes must reject malformed argv** (strict
  parsers, not payload-only). Applied in-session to both D9 fakes
  (classify, export-safe); the lane-brief template edit above carries
  the rule forward.
- capability — **task-run timeout commits a typed WIP candidate.**
  Structural pattern: long-running child work lost at timeout.
  Triggering instances: lane B here; two 2026-08-15 full-suite losses.
  Destination: issue
  [#754](https://github.com/corca-ai/charness/issues/754) (recurs:
  standing trap, third instance).
- memory — the `ruff --fix` re-export hazard and the `as`-alias
  convention persist via this artifact and the refreshed digest; the
  sibling scan below shows the corpus is otherwise clean today.

## Sibling Search

Transferable pattern: an unused-import auto-fix strips a bare
re-export from a shared support module, breaking its importers.

- same layer: other `tests/**` support modules
  (`support.py`, `seeding_support.py`, `issue_closeout_support.py`,
  `release_publish_fixtures.py`, `dsl.py`, `repo_copy.py`,
  `quality_bootstrap_support.py`, `reviewer_capability_support.py`) |
  decision: diagnostic-only | proof: AST scan for bare unused imports
  found only `from __future__ import annotations` (never stripped);
  `seed_commit` was the sole re-export and now uses the `as` alias.
- abstraction up: production `scripts/*_lib.py` re-exports (e.g.
  `repo_file_listing.py` re-exporting `support_dir`) | decision:
  intentional boundary | proof: production modules are outside the
  bulk-autofix habit that caused the break (the fix was applied only to
  `tests/quality_gates/`), and their re-exports are attribute-used by
  importers, which F401 does not flag.
- specialization down: the four importer test files that broke |
  decision: same waste, fix now | proof: restored via the aliased
  re-export in `issue_closeout_support.py` (`07c7caa7c`); 91 tests
  green.
- mental-model siblings: other "auto-fix erases intent" surfaces —
  `--unsafe-fixes` (never enabled) and formatter-driven edits to
  generated files | decision: diagnostic-only | proof: generated
  surfaces are exporter-owned and gate-checked
  (`validate_packaging_committed`); no autofix path writes them.

## Packet Consumed

n/a (no adapter sections)

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-29-session-retro.md
