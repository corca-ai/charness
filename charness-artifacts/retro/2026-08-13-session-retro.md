# Session Retro
Date: 2026-08-13
Goal: charness-artifacts/goals/2026-08-12-resolve-open-quality-and-trust-backlog.md

## Context

This session reconciled the fixed 22-issue cohort without converting an OPEN
tracker state into a completion claim. It repaired #607's conservative static
subprocess-settlement inventory, recorded #527 as an operator-owned product
decision rather than inventing its lock/docs design, and made the execution
ledger, goal, and handoff agree on the final frozen reconciliation.

The trustworthy evidence is the committed local proof, the two-round bounded
reviews for #607, and GitHub issue/comment readback. The 22 carriers were
checked by asking each issue reader for its comment URLs; a browser comment URL
fragment was not treated as a REST comment identifier. No push, release,
remote CI, issue close, or hosted behavior proof occurred.

## Window

`022c09a9..7f9733ed`, including #607's implementation and the frozen cohort
reconciliation. The branch remains ahead of `origin/main`; all 22 cohort issues
remain OPEN by design pending the goal's final closeout conditions.

## Evidence Summary

- `1570ba32` adds the #607 settlement inventory and focused regressions;
  `tests/quality_gates/test_standing_test_economics.py`,
  `test_subprocess_settlement_inventory.py`, and `test_quality_skill_docs.py`
  passed (45 tests).
- `charness-artifacts/critique/2026-08-13-issue-607-subprocess-settlement-inventory-resolution.md`
  binds the two bounded review rounds. R1 caught no-timeout/mixed-stream
  false-greens; R2 caught dynamic-timeout false-greens. The last R2 repair is
  recorded accepted-unreviewed under the two-round cap, not silently approved.
- `charness-artifacts/issue/2026-08-13-issue-527-brief.md` and its GitHub
  carrier keep #527 OPEN until an operator chooses the product boundary.
- `charness-artifacts/goals/2026-08-12-open-backlog-execution-ledger.md` has
  22 rows. Live reconciliation found 22 matching OPEN tracker issues, 22
  matching carrier comment URLs, and neither a ledger-only nor tracker-only
  issue number.
- `mine_closeout_telemetry.py --detail` read 1,652 historical records through
  2026-08-12. Its recurring slow-gate/over-slice signals are local-machine
  history, not evidence for this session or a safe budget change; #503 already
  owns their remeasurement boundary.

## Waste

The initial reconciliation probe used a GitHub browser comment URL's visible
fragment as though it were the REST comment id. It returned 404, but no absence
claim was made; the method was corrected immediately to issue-reader comment
URL matching. This was small, reversible rework caused by confusing two
identity channels, not a tracker defect.

#607's R1/R2 repair cycles were not avoidable waste: the first draft would have
said finite/bounded where a process may wait forever or capture an unbounded
stream. The reviews found the exact false-greens before shipment. The planning
lesson is narrower: generate the final critique packet after the final repair,
not before it, so review identity and repaired code do not require extra packet
turns.

The telemetry miner still reports recurring full-pytest, release-bundle,
read-only-pytest, and over-slice cost. This is a standing gate-baseline cost,
not a reason to weaken proof: #503 records the quality/achieve owner split and
requires a matched remeasurement before changing execution or budgets.

## Critical Decisions

1. **Keep #527 as `unproven-defer`.** Product-lock, docs lifecycle, and working
   criteria were not specified. A decision brief and OPEN carrier preserve the
   question without fabricating a feature.
2. **Treat #607's static signals as conservative facts, not runtime truth.** A
   literal finite timeout is the only finite lifecycle claim; dynamic/absent
   values and process-tree ownership remain unknown. This constrained the code
   and prevented an attractive but false completeness claim.
3. **Freeze the cohort by reconciliation, not closure.** Every row has local
   proof, split, or tracker-visible defer, while GitHub stays the source of
   truth for OPEN state. This makes the release decision inspectable without
   laundering unresolved product premises into “done.”

## Trends vs Last Retro

The prior durable retro says the existing #503 telemetry cluster must not be
filed again; the current miner reports the same class and remains bounded by
the same owner. The stronger current improvement is claim discipline: this
session's #527 premise was explicitly deferred, while #607's later repair is
explicitly accepted-unreviewed rather than described as a completed second
review.

## North Star Alignment

**P4/P5 held.** #607 crossed an irreversible proof-surface boundary only with
independent bounded readers, and GitHub carrier presence was verified through
the issue reader rather than inferred from local files. Both channels caught or
could falsify an author claim.

**P1 held for #527.** The evidence did not establish a concrete defect with a
safe implementation choice, so the work stopped at a named operator decision.

**Mis-applied method corrected:** the first 404 reconciliation probe confused
URL display identity with REST identity. The result was treated as a failed
method, not an evidence verdict, then replaced with the appropriate reader.

**Failure signature avoided:** “local green becomes terminal trust.” Focused
tests and carriers establish local/tracker facts only; they do not establish a
push, release, hosted behavior, or cohort closure.

## Expert Counterfactuals

**Douglas Engelbart — design Tool, Language, and Method together.** The
settlement scan's first contract could have named literal-timeout, output-stream,
and ownership uncertainty as a small table before implementation. That would
have aligned the static tool with the conservative language and reduced the R1
repair surface; the separate reviewer remains necessary for adversarial cases.

**Falsification-first operator lens.** A carrier URL is a web-facing locator,
not automatically an API primary key. The first reconciliation command should
ask whether the identifier type matches the reader's contract before interpreting
its response. This changes the next move from “retry a 404” to “select the
evidence channel that owns the fact.”

## Sibling Search

- same layer: `skills/public/issue/scripts/issue_tool.py read` comment URL
  output | decision: same waste, fix now | proof: the final 22-row reconciliation
  used it to verify every exact carrier URL after the REST-id probe failed.
- abstraction up: `scripts/prepare_packet.py` identity binding | decision:
  intentional boundary | proof: packets bind a particular reviewed state; a
  repair necessarily needs a new packet rather than mutating an old identity.
- specialization down: `skills/public/quality/scripts/surface_marker_lib.py`
  timeout/output classifiers | decision: same waste, fix now | proof: #607 now
  tests no timeout, dynamic timeout, and mixed DEVNULL/PIPE streams.
- mental-model siblings: `charness-artifacts/quality/2026-08-05-issue-503-runtime-budget.md`
  | decision: intentional boundary | proof: the same historical telemetry class
  already has named quality/achieve owners and a matched-measurement condition.

Structural-follow-up destination: applied: #607 focused tests and the frozen
reconciliation method; none — #503 already owns the telemetry remeasurement.

## Next Improvements

- **workflow**: Before interpreting an external-read failure, check that the
  supplied identifier belongs to that API/read channel. Keep a failed probe as
  method evidence, never as absence evidence. (recurrence-class: evidence-channel-identity)
- **capability**: For conservative static inventories, write the known/unknown
  signal matrix before implementation and keep dynamic values unknown unless a
  direct parser proves them. (recurrence-class: conservative-static-verdicts)
- **memory**: Keep the goal, execution ledger, handoff, this retro, and #527's
  decision brief as the release-boundary record; #503 remains the owner of the
  historical runtime-cost question. (recurrence-class: premises-not-debt)

## Packet Consumed

- `charness-artifacts/retro/2026-08-12-180732-packet.md`
- `charness-artifacts/retro/2026-08-13-090345-packet.md`

## Continuation: Issue #615 Focused Verdict Repair

### Context and Evidence

The late-arrival #615 slice repaired a focused changed-line coverage wrapper
that widened the standing test population with `--include-release-only`, even
though the broad mutation campaign deliberately excludes that marker. The
authoritative wrapper now executes the nonempty command owned by the command
suggester, the checked-in plugin export is byte-identical, and a real
release-only child sentinel proves that focused execution cannot silently add
the marker again.

The strongest behavioral evidence is the isolated historical-range replay in
`charness-artifacts/debug/2026-08-13-issue-615-focused-changed-line-false-clean.md`:
the repaired wrapper exits 1 and reports exactly lines 116, 117, 132, 133, and
134 as missing for base `d0c33e6b4a653bd758f5e5910c115819dd0333b4`.
Focused verification passed 132 tests. Two bounded critique rounds read the
repair; round 2 caught the stale plugin export before closeout. These are local
facts only: no push, hosted CI, GitHub closure, or installed-consumer readback
occurred.

### Waste and Critical Decisions

The packet/critique binding was regenerated several times because exact
historical evidence and its declared digest continued changing after a packet
identity had been minted. This repeats the recent lesson that evidence identity
must be frozen after all source, export, and receipt synchronization, not while
review findings can still mutate the bundle. The independent review itself was
not waste: it found the installed-plugin false-clean path that same-agent source
inspection had missed.

The decisions that constrained the outcome were: keep broad marker policy as
the population owner; consume the suggester-owned command rather than build a
second command in the wrapper; preserve the exact historical command and
dirty-worktree nonclaim; and stop at a local direct-commit carrier without
turning `Closes #615` into a publication claim.

### North Star and Expert Counterfactual

The irreversible proof-surface boundary used a different observer and evidence
channel: round 2 inspected the exported plugin, while the historical-range
runtime replay falsified the old clean verdict. This is the north-star behavior
the slice needed; source parity tests alone would not have exposed the stale
export at the moment it existed.

Douglas Engelbart's system-improving lens would treat packet generation,
derived-surface sync, and critique binding as one Tool/Language/Method unit.
The changed next move is a declared freeze stage — mutate, sync every export and
receipt, validate, then mint the packet once — with a binder that rejects a
critique record whose declared packet digest is no longer current. That makes
the workflow enforce the lesson instead of relying on reviewers to remember it.

### Trends and Next Improvements

The 1,689-record local telemetry read still shows the same recurring broad-gate
and over-slice classes already owned by #503; occurrence is a cost signal, not
permission to weaken this slice's proof, and it says nothing about other repos.

- **workflow**: freeze source, generated export, exact runtime receipt, and
  critique text before minting the final review packet.
- **capability**: make critique binding validation reject a stale declared
  packet SHA/identity before review closeout, rather than discovering it during
  repeated readbacks.
- **memory**: retain the exact historical command, coverage fingerprint, five
  missing lines, and hosted/public nonclaims in the debug record.

The sibling at the abstraction layer remains `scripts/prepare_packet.py`'s
intentional immutable identity boundary. The improvement is sequencing and a
stale-binding validator around that boundary; no new tracker item is filed in
this slice because the existing recent lesson already names the recurrence and
the current repair demonstrates the required sequence.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-13-session-retro.md
