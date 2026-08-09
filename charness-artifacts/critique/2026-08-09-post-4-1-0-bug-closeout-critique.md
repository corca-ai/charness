# Post-v4.1.0 bug closeout critique: #573, #563, #570, #549, #545

Date: 2026-08-09
Classification: bug
Fresh-eye satisfaction: parent-delegated
Verdict: all five CLOSABLE, each with a named residual carried into the close rather than smoothed away.

## Decision Under Review

Whether five bug-class issues repaired inside the v4.1.0 delta are closable now
that v4.1.0 is published (tag `v4.1.0`, commit `cd7ab479`). Each was judged by a
bounded read-only fresh-eye subagent instructed to REFUSE the close.
`reviewer_boundary_fingerprint.py` verified `clean` around the review window.

## Failure Angles

- A repair that makes a defect HONEST (reports it) rather than FIXED (refuses it),
  closed as if fixed.
- A repair proven only by its own commit body or by the issue's CLOSED state.
- A repair that landed in the source tree but not the `plugins/charness/**` mirror
  that consumers actually run.
- A closeout that claims more than the code does, because the release note already
  generalized past it.

## Per-issue findings

### #573 — killed mutation sweep leaves the tree MUTATED

CLOSABLE. The reviewer traced the mechanism rather than trusting the commit:
`mutate_and_restore.py:355` writes a write-ahead journal via `mutation_recovery.begin()`
BEFORE the first mutated byte, into `.git/charness-mutation-recovery` — deliberately
outside `git status`, which is exactly the discrimination #573 said was missing (the
residue was invisible for ~40 minutes because `M` already meant live work). Three
independent readers refuse with exit 2: `.githooks/pre-commit:7`,
`scripts/run-quality.sh:69`, and the sweep's own `assert_clear()` at
`mutate_and_restore.py:397`. SIGKILL is correctly NOT claimed to be caught —
`termination_handlers` traps only SIGINT/SIGTERM (`mutation_recovery.py:307`); the
untrappable case is handled by journal-plus-recovery-on-next-invocation.
`recover()` also stops the orphaned child process group and refuses to overwrite
bytes the sweep does not own.

Non-blocking residuals recorded: `--check-recovery` names the record path but not the
target file, which is the last inch of #573's "which `M` is residue?" pain; consumer
tests cover one predicate branch each.

### #563 — title-slug gate reported clean over a scope that excluded the drift

CLOSABLE. Retirement is real on every armed path (`run-quality.sh`, `.githooks/pre-push`,
`staged_commit_gate_plan.py`, `catalog.yaml`, `.agents/quality-adapter.yaml` all
return no hits; pinned by `tests/quality_gates/test_title_slug_retirement_compatibility.py:76-82`),
and the retained deprecated direct-call default now includes the excluded root
(`scripts/check_title_slug_drift.py:79-83`), pinned through the default path by
`test_deprecated_title_slug_default_scope_includes_goal_records`. The replacement is
reachable, not promised: `skills/public/critique/references/rename-critique.md:83-88`
with an explicit anti-aggregate rule.

Residual carried into the close: the 5 findings the issue measured are now judged by
nothing standing — the coherence lens fires only on rename-heavy critique. That is a
recorded disposition, not an oversight, and #563 asked for an honest gate rather than
for those files to be renamed. Also, the deprecated command's own pass line still
prints a count without naming its population (`check_title_slug_drift.py:186`) — a
weakened instance of the class the issue filed, surviving on an unwired advisory
surface slated for removal at the next major.

### #570 — handoff planner briefs the surface the run must not write

CLOSABLE, with the halves stated separately because only one was repaired by the
commit. Half one is fixed: `HANDOFF_AUTHORING_ACTIONS` (`plan_handoff_run.py:201`)
no longer contains `run_chunked_routing`, so no `--as-surface handoff` is emitted for
it. Half two — "briefs NOTHING for the surface it creates" — was discharged by a read
that ALREADY existed (`INTENT_REFERENCE_READS["chunked_routing"]` forces
`references/chunked-routing.md`, which names the goal drafter, the artifact path, and
the never-rewrite-handoff prohibition), not by this commit. Claiming the commit fixed
both halves would be false.

Residuals recorded: `_gate_packets` is still unconditional on intent, so a
chunked-routing plan ships handoff-scoped gate evidence and no `check_goal_artifact`
packet — the issue's own complaint shape surviving one field over; and
`plan_handoff_run.py:220` resolves the length surface by filename sniff rather than
from the adapter, so a consumer whose adapter names the artifact something else gets
an authoring action briefed with the length rule silently absent.

### #549 — gate-failure survival: three layers, one built

CLOSABLE. Layer 1's "exactly one script does it" count is still literally true, and
the reviewer judged it the wrong measure: the other eight `scripts/*.sh` are CHILDREN
invoked by `run-quality.sh`, whose `:553-560` copies each failing child's full log
into the durable directory, so one aggregator covers all of them. Layer 2 now has an
executable reader (`setup_hook_failure_visibility_lib.py:230`, wired at
`setup_inspect_lib.py:196` in both trees) that emits concrete per-command gaps,
suppresses fd analysis rather than guessing when complex shell constructs are
present, and — critically — never renders a pass: the clean path is
`live-verification-required` with explicit `non_claims`. Layer 3 ships to consumers
in two mirrored references a plugin install physically delivers.

Residuals recorded: layer 3 reaches consumers only through the Lefthook route (the
consumer ROOT-DOC templates carry no such rule), so a Husky or CI-only consumer
receives it from no shipped surface. And a genuinely new defect the reviewer found
which #549 never named — `.githooks/pre-push:8,19` runs two validators OUTSIDE the
durable-log aggregator, and this repo has no `lefthook.yml`, so the reader it authored
can never inspect its own authoring repo. That is filed as follow-up work, not folded
into this close.

### #545 — private provider media URLs published as GitHub evidence

CLOSABLE, with a mandatory scope correction. `issue_create.py:165-172` REFUSES before
the command is even built, and the test asserts the backend call-counter file was
never created — "before the write", not merely "before returning". The refusal is
backend-agnostic by construction, so it covers host-mediated backends too. Six
parametrized refusal cases cover inline, quoted/bare `<img>`, full/collapsed/shortcut
reference forms, with allow-cases for fenced code and for plain provenance links.

The correction that MUST travel with the close: the recognizer is
slack-host-only (`issue_create.py:100-106`), not a general private-media rule — a
private Notion, Drive, Figma, or even `*.slack-edge.com` URL is not caught. And there
is no executable "durable evidence" gate; the only condition is the absence of that
one markup-plus-host pair. The v4.1.0 release note's "provider-private ... unless it
has durable evidence" is one generalization wider than the code, and the closeout must
not repeat it. Residual recorded: `issue_close.py` publishes closeout comments through
`--body-file` with no media check at all, which is the sibling external-write path.

## Counterweight Pass

Real blockers found: none for these five. The reviewers' strongest refusals were
scope-and-claim problems, not correctness problems — the code does what the issues
asked; the risk is a closeout that says more than the code. That risk is answered by
carrying each correction into the carrier body rather than by holding the issues open.

The one finding that WOULD have been a blocker if folded in — `.githooks/pre-push`
violating the hook-failure contract it exports — is a different, narrower defect than
#549 filed, and is recorded for filing instead of silently absorbed.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/release/2026-08-09-v4.1.0-notes.md | action: document | note: the #545 release-note wording generalizes past a slack-host-only recognizer; the closeout must state the narrower truth
- F2 | bin: valid-but-defer | evidence: strong | ref: .githooks/pre-push:8 | action: file-issue | note: two validators run outside the durable-failure-log aggregator and this repo has no lefthook.yml, so its own hook-visibility reader cannot inspect it | follow-up: deferred docs/handoff.md#next-session
- F3 | bin: valid-but-defer | evidence: moderate | ref: skills/public/issue/scripts/issue_close.py | action: file-issue | note: the closeout-comment write path has no private-media check, unlike the create path | follow-up: deferred docs/handoff.md#next-session
- F4 | bin: over-worry | evidence: moderate | ref: scripts/check_title_slug_drift.py:186 | action: defer | note: a deprecated, unwired advisory surface still prints a count without its population; removal is reserved for the next major

## Reviewer Tier Evidence

- Requested tier: `bounded-reviewer` (the repo's typed read-only subagent).
- Requested spawn fields: `subagent_type: bounded-reviewer`, prompt, synchronous
  return; deliberately no host addressing/team `name`.
- Host exposure state: host-defaulted
- Application state: n/a — no per-subagent model or effort override was requested.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated

## Boundary Ownership

- Producer: the repaired gates, readers, and refusals in the v4.1.0 delta.
- Consumer: a consuming repo running the shipped surfaces, and a future reader of
  these five issues who will treat CLOSED as "the reported behavior no longer happens".
- Owning surface: each repaired surface owns its own verdict; the closeout carrier
  owns the claim about it.
- Verdict: owned-correctly

## Non-Claims

- Mirror parity was established by reading both trees and by the repo's export-drift
  gates, not by a byte diff in this session.
- #545 is closed for the create path and the Slack host family only.
- #549 is closed for the three layers as filed; the pre-push aggregator gap and the
  Husky/CI-only export gap are follow-up work, unfixed.
- #563's measured five findings remain unjudged by any standing gate.
