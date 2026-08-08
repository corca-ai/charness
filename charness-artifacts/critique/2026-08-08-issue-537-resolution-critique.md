# Issue #537 resolution critique (delegated)

Classification: bug
Reviewer: delegated bounded reviewer (fresh-eye, read-only envelope: Read/Grep/Glob)
Fresh-eye context: `parent-delegated`
Envelope: bound as expected — no Bash, Edit, Write, or Agent tool exposed to this spawn
Verdict: RESOLVED WITH RESIDUAL RISK — three items did not carry as drafted (F1, F2, F3) plus a
stale durable record (F7); the class RECURRED in the repaired file for three more blocker
classes, one with a strictly worse diagnostic than the one #537 was filed about -> repaired,
restated, and the remainder filed as `#560`

## Boundary Ownership

- Producer of the verdict "is this repo bundle-ready": `scripts/final_bundle_preflight_lib.py`
  `build_plan`. Everything else is a sub-verdict feeding `blockers`.
- Derived verdict: `scripts/closeout_bundle_lib.py` re-publishes the preflight's readiness; the
  closeout surface has NO independent opinion. Consequence, disclosed: every live preflight
  blocker necessarily reddens BOTH readiness tests, so the honest acceptance number is two, not
  one, and the second carries no information the first did not.
- Sub-verdict owners: the mirror verdict is owned by `test_packaging_owner_mirror_is_current`,
  which exists and is correctly named. The critique `current` verdict was owned by NOBODY after
  the first loosening (F2). Surfaces, manifest integrity, and the candidate snapshot have no
  dedicated owner; the preflight is the owner and the readiness tests are its only readers,
  which is defensible.
- Verdict: moved-to-owner — readiness moved to one purpose-built owner per surface, the mirror
  verdict moved to a PRE-EXISTING owner rather than a new one, and no second implementation of
  the readiness rule was created. The residual was that one loosened verdict was moved to an
  owner that did not exist, and that the ready-path shape has no fixture owner.

## Reviewer Tier Evidence

- Requested tier: bounded-reviewer (read-only fresh-eye, `.claude/agents/bounded-reviewer.md`)
- Requested spawn fields: agent_type=bounded-reviewer, model inherited, one-shot spawn with no
  host addressing/team name
- Host exposure state: requested_fields_sent
- Delivery state: findings-received
- Application state: applied as requested; envelope Read/Grep/Glob only and structurally unable
  to write or run `git`. Worktree+index integrity fingerprinted around this window with
  `skills/shared/scripts/reviewer_boundary_fingerprint.py` (window
  `issue537-resolution-critique`, verdict `clean`, no drift), as around both slice rounds
  (`slice4-537-round1` and `slice4-537-round2`, both parent-attributed, no unattributed drift).

## Fresh-Eye Satisfaction

parent-delegated — a separate bounded-reviewer context read the committed tree with no access
to the parent's reasoning or to either slice round. The findings were derived by tracing
`build_plan`'s own control flow rather than by re-checking stated conclusions: F1 came from
asking which OTHER assertion has the same blocked-repo dependency the premise check found for
`planned_commands`; F2 came from grepping the tree for any assertion of `== "current"` rather
than trusting the comment that named its owners; the test arithmetic was recomputed from
`def test_` plus parametrize expansion rather than read off the reported numbers.

## JTBD

An operator running the two bundle gate files needs to learn one of two things: "your
plan-shaping code is broken" or "this repo is not currently bundle-ready, and here is why".
Before #537 the second answer arrived as five instances of the first, each diagnosed by a
truncated `CompletedProcess` repr with an empty custom message, and it went unread for six
commits. The job is not to make the red go away — the issue says so — it is to make the refusal
speak in its own voice, once per surface, carrying `code`/`message`/`remediation`/`subject`.

## Findings

### F1 (BLOCKER as drafted) — the class RECURRED in the repaired file, with a bare `KeyError`

The premise check found that `planned_commands` does not survive a blocked repo, and stopped
there. A second assertion of the same kind remained: `payload["candidate_snapshot"]["head_sha"]`
in the shape test and again in the monkeypatched-branch test. `candidate_snapshot` is `{}`
whenever `base_sha` cannot resolve — a deleted, truncated, untracked, or wrong-shaped manifest —
so subscripting raised a bare `KeyError: 'head_sha'`, naming no code, no subject, no remediation,
and not even a status. That is a WORSE diagnostic than the truncated repr the issue was filed
about.

Reproduced by the parent after the finding: a broken manifest gave 5 failures with 3 misnamed and
two bare `KeyError`s — numerically identical to the profile round 2 measured for the mirror class.
One round fixed `unmatched_surface_path`; round 2 fixed the mirror class; the manifest class was
never measured.

REPAIRED: the shape assertions became `"candidate_snapshot" in payload`, and the verdict moved to
the readiness test. Re-measured: 3 failures, no `KeyError`, cause named.

### F2 (BLOCKER as drafted) — a comment named an owner that does not exist, leaving a verdict unowned

The shape test's comment said `mirror_inventory["status"] == "matched"` and
`critique_inventory[0]["status"] == "current"` "have their own owners —
`test_packaging_owner_mirror_is_current` and the critique-inventory tests below". The first half
was true. The second was not: every critique-inventory test asserts a REFUSAL branch, and an
independent grep found no assertion anywhere that `critique_inventory` yields `status ==
"current"`. Changing that value in the producer would have failed nothing. Before the loosening,
the shape test caught it.

That is a real coverage loss introduced by the round-2 repair, and a checked-in text asserting a
fact the tree refutes — in the file whose subject is honest reporting.

REPAIRED: the readiness test is now that owner and asserts both verdicts explicitly; the comment
names it.

### F3 (BLOCKER as drafted) — "`planned_commands` is EMPTY when blocked" is false, in two comments

Only the CLOSEOUT entry is gated on readiness. Everything else — manifest validation, surface
sync, critique validation, behavior, verify — accumulates unconditionally. Measured by the parent
after the finding: a blocked plan carries 56 planned commands, all with `reason_surface_ids`.

Both conclusions those comments supported survive the correction, so it was a wrong reason for a
right move — except that the `reason_surface_ids` shape assertion had been moved behind the
readiness gate on the false premise, losing it while the repo is blocked.

REPAIRED: both comments restated to "carries no CLOSEOUT command", and that assertion moved back
to the shape test where it holds in either state.

### F4 (residual) — three `status in {"ready", "blocked"}` assertions cannot fail

`closeout_bundle_lib` can produce only those two values, and `build_plan` returns `diagnostic`
only when explicit paths are passed, which neither call site does. Harmless, but they are
placeholders documenting the loosening rather than retained coverage, and the closeout should not
present them as the latter.

### F5 (residual) — the refusal reports itself with class-dependent specificity

`bundle_blocker_report` prints whatever `subject` the blocker carries. For the mirror class the
subject is the ROOT `plugins/charness`; the `differences` list naming the drifted files lives in
the inventory, not the blocker, so the reader learns "something under plugins/charness differs".
And the correctly-named owner test fails as a bare `assert 'needs_sync' == 'matched'` with no
message — so one of the three failures the mirror class produces still has the #537 diagnostic
quality.

### F6 (residual, FILED as `#560`) — the ready path is proven only when the repo is already ready

The ready-path payload and render shape are owned only by tests that require a clean worktree, so
while any blocker is live NOTHING exercises the ready path — the mirror image of this issue. The
owning spec already declared a fixture acceptance check that no test implements. `#560` also
carries the last misnamed failure: a monkeypatch-heavy test that still reads the REAL manifest and
needs a fixture manifest rather than a one-line change.

### F7 (BLOCKER as drafted) — the durable record contradicted itself

At review time the goal artifact's Slice Log ended at the slice-4 PREMISE CHECK with no record of
the build commits, while its Active Operating Frame still read "Current slice: 3 of 9 COMPLETE"
and "Slice 4 is next and has NOT been premise-checked" — refuted forty lines below in the same
file. Third consecutive closeout in this goal whose durable record failed in the ledger.

REPAIRED: the build record was appended and the frame rewritten.

## Q1 — counts checked against the tree

Test arithmetic verified independently: 16 items in the preflight file, 23 in the closeout file
(21 `def test_` plus one 3-way parametrize) = 39, matching `2 failed, 37 passed`; minus the two
new readiness tests = 37, matching the premise check's `5 failed, 32 passed`.

One count was wrong and is restated: the `assert result.returncode == 0, result.stderr` idiom
occurs **913** times in the tree, of which 910 are in tests and three are this goal's own
artifacts and a transcript — not 911. Two of the last three closeouts in this goal were blocked on
exactly this kind of arithmetic, so the number now carries its scope.

"The shape tests no longer assert live-repo verdicts" was FALSE as first written (F1), and
"`planned_commands` is EMPTY when blocked" was FALSE (F3). Both corrected.

## Q3 — acceptance: met for the classes measured, not for all

Of the 22 blocker codes the two surfaces can emit, 15 are reachable by live repo state given the
tests' hardcoded arguments. After the repairs: the surface, manifest-integrity, mirror, artifact,
and critique classes reach only correctly-named tests. What remains is the single monkeypatch test
`#560` carries. The closeout must say "met for the classes measured, and here is the remainder"
rather than "the class is closed".

## Q5 — the process finding was MISDIAGNOSED, and the correction matters

The parent concluded that mutation testing is unreliable against assertions about live repo state,
after mutating a file made the test fail at an EARLIER assertion. The specific observation is
right — editing the source dirties the worktree, which makes the plugin mirror drift, which makes
the plan blocked — but three things make that the wrong lesson.

First, the slice's own new diagnostic already named the confound: the failure printed
`status='blocked'` and `code: needs_sync`. The mistake was not reading WHICH assertion failed,
which is precisely the failure mode #537 is about, committed while fixing #537.

Second, a valid technique was one step away: inject a blocked plan rather than edit the worktree.
The narrow, reusable lesson is that a test whose subject IS the worktree's cleanliness cannot be
mutation-tested by editing the worktree; its discriminating power must be proven by injection.
Generalising further would license skipping mutation proof on exactly the verdict surfaces this
repo requires two review rounds for.

Third, the round-2 finding that prompted it was itself a false positive.
`preflight["status"] == "ready"` was not dead — it is a redundant cross-layer AGREEMENT check,
which is a different and often defensible thing, and applying "derived from the same value"
consistently would delete every such check in the repo. The replacement (the `verification_lock`
command, which comes from the readiness-gated closeout entry) is still better, and worth keeping,
for a different reason than the one first recorded.

## Q7 — Verdict

RESOLVED WITH RESIDUAL RISK.

The fix is the right shape and the premise check is again the strongest part: reproducing exactly,
then refining the issue's own claim — the message was never DELIBERATELY reported, and
`planned_commands` does not survive a blocked repo — is a better outcome than the issue asked for.
`bundle_payload_or_report` and `bundle_blocker_report` each avoid a specific defect: parsing
before the exit-code check, keeping `error` alongside blockers, splitting only the one
comma-joined subject, and refusing to raise from inside a message renderer. Two surfaces own
their readiness question, the gate keeps its teeth, and the issue's explicit warning against
dropping the `ready` assertion is honoured — with one narrow violation, F2, now repaired.

What blocked the close as drafted was the ledger and the durable prose again: a second and third
instance of the very coupling being repaired, a comment naming a nonexistent owner, a false claim
about `planned_commented` emptiness in two places, and a self-contradicting goal frame. All
repaired. The remainder is filed as `#560`, and the closeout claims the classes it measured
rather than the class as a whole.

## Non-claims

No command was executed by this reviewer. `pytest`, `run-quality.sh`, the mutation results, the
dup-ratchet status, the reviewer-boundary fingerprints, and the detached-worktree behavioural run
are taken as reported and are unproven by this review, not disputed — every one is consistent with
the code read, and the 39-item arithmetic independently corroborates the pass/fail totals.
`git show` was unavailable, so nothing about the PRE-fix text of these files is claimed; the five
originally-coupled tests were identified from surviving comments, and F1's `KeyError` scenario is
asserted to be live now rather than to be a regression. F1 through F6 were wrong-by-reading,
traced through `build_plan`'s control flow; the deleted-manifest and malformed-surfaces fan-outs
were not run by this reviewer, though the parent reproduced the first. The 913 count is arithmetic
against the tree at review time. GitHub state for `#537` was not read.
