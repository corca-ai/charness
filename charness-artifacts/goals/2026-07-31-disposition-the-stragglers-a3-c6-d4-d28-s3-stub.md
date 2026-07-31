# Achieve Goal: Disposition the stragglers — A3, C6, D4, D28, sibling-scan Tier 2 D, S3's stub half

Status: complete
Created: 2026-07-31
Activation: `/goal @charness-artifacts/goals/2026-07-31-disposition-the-stragglers-a3-c6-d4-d28-s3-stub.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

Mode: **implementation-continuation** (assumed, not asked). The originating
request was "리포 자율 개선 해봅시다" and the operator then selected this chunk from
the handoff chunker's ranked list; both read as "run it", not "draft it".

## Active Operating Frame

- Current disposition: **complete.** All five slices landed, closeout verified,
  retro persisted, disposition review folded.
- Current slice: none — the run is closed.
- Next action: none for this goal. The one live operator decision is in
  `## Operator Decision Queue`; the two structural follow-ups are on the handoff.
- Verification cadence: cheap deterministic gates at each commit boundary
  (`check_doc_authoring_preflight.py` read for findings, the touched validator's
  own tests); `scripts/run-quality.sh` once at the bundle boundary;
  `prepush_focused_changed_line_coverage.py` with `--base-sha <pre-slice-1 sha>`
  and `--refuse-unestablished`; then the locked slice closeout with
  mutation-coverage production, before closeout.
- Slice review packet: per slice — intent, changed files with owning/generated
  surfaces, the assertions that pinned today's behavior, expected invariants,
  tests, non-claims, out-of-scope lines, and questions.
- History boundary: keep this frame current during the active run; move
  completed detail to `## Slice Log`, `## Operator Decision Queue`,
  `## Final Verification`, and `## Auto-Retro`.

## Goal

Take every un-dispositioned straggler on the backlog and move it to a state a
future session can act on without re-deriving it: either a repair with a
regression test, or a recorded disposition carrying the evidence that justifies
it. The rows are A3's three residuals, C6's committed-range half, D4's
released-vs-pushed half, the D28 remainder, sibling-scan Tier 2 D, and S3's
xfail-pinned stub half.

**What the plan critique changed about that list.** Two of the six are not work:
sibling-scan Tier 2 D already shipped on 2026-07-20, and D4's remaining question
is an operator credentials decision the hunt already measured live. What is left
is three repairs (A3 residual 1, S3's stub half, C6's caller-side scope), one
promoted tool fix found live this session, and a bookkeeping pass.

**A disposition is a first-class outcome here** — with a floor. A row whose right
answer is "not now, and here is the evidence" closes as a disposition. But at
least one row must end repaired with a revert-checked regression test, or the
goal is incomplete; without that line a run that changes zero lines of code would
satisfy every other criterion.

**Source handoff entry #4: Un-dispositioned:**

> A3 PARTIAL (needs a live staged/revert probe — the
> [A3 staged-scope critique](../critique/2026-07-27-a3-staged-scope.md) F8/F9),
> C6, D4, D28 remainder, sibling-scan Tier 2 D;
> [D39/D41](../../docs/deferred-decisions.md) deferred, S3's stub half pinned as
> an xfail.

## Non-Goals

- Not a release: no plugin version bump, no publish, no tag, no push.
- Not a re-audit. Rows outside the six named here are not re-read, and the
  hunt's E-cluster (handoff entry 2) and S11's second channel (entry 3) stay out
  even where the defect shape rhymes.
- D39 and D41 stay deferred; this goal does not reopen them.
- No repair may widen into a redesign of the surface it lands in. Each row gets
  the smallest change that makes the wrong verdict fail, or no change and a
  disposition.
- No live cautilus run, no mutation lane, no CI dispatch.
- Not a fix for S110 (the freshness row opened today) — it is a new `LEAD`, not a
  straggler.

## Boundaries

- In scope, one surface family per row (re-locate by symbol; line numbers are the
  owning record's, as-of its date):
  - **A3 residual 1 — "scheduled is not judged".** Surface:
    `scripts/staged_commit_gate_plan.py` (+ `staged_commit_gate_plan_helpers.py`)
    and the `.githooks/pre-commit` rendering path. The repair is to make the
    **scope each scheduled gate actually inspects** legible next to its verdict,
    so `git rm --cached docs/x.md` no longer prints a bare `ok` over gates that
    walked the worktree instead of the index. **Explicitly NOT** converting the
    scheduled gates from worktree readers to index readers: the owning critique
    already declined that as "a change to every gate rather than to the plan"
    ([A3 staged-scope critique](../critique/2026-07-27-a3-staged-scope.md),
    `## Deliberately Not Doing`), and this goal's no-redesign fence keeps that
    decision. Consumers of the planner besides the hook —
    `run_slice_closeout.py --predict-commit` and the structural sweep — are in
    scope for not-breaking, not for change.
  - **A3 residuals 2 and 3 — status only, no probe.** Residual 2 (`git revert` and
    auto-merge never reach the hook) was already probed and recorded in the hunt
    with `core.hooksPath` set; re-probing it would re-derive a written measurement.
    Residual 3 (A5/A6 inside the floor) closed on 2026-07-30. Both get a Status
    line, not a slice.
  - **S3 stub half.** Surface: the accept path of
    `scripts/check_prescribed_skill_executed_lib.py` (see its
    "NOT a size floor, deliberately" comment). The pin is
    `tests/quality_gates/test_prescribed_skill_executed.py`
    `test_s3_residual_a_stub_that_cites_its_context_is_not_refused`, marked
    `xfail(strict=False)`. **Removing that marker is part of the repair**, not a
    consequence of it.
  - **C6.** The committed-range read is in `scripts/boundary_probe_lib.py`
    (`resolve_hit` -> `collect_changed_paths_for_ref`), reached through
    `scripts/critique_enforcement_scope.py` `resolve_cross_surface_scope`;
    `scripts/validate_critique_artifacts.py` only calls into them, and
    `scripts/run-quality.sh` is the caller that supplies scope. The audit names
    the validator and `run-quality.sh` together, and the plan follows the code.
    `boundary_probe_lib.resolve_hit` has a **second consumer** (the impl
    stop-gate hook) — in scope for not-breaking, not for change.
  - **D4 — decision, not repair.** Surface:
    `skills/public/release/scripts/publish_release_post_create.py`
    (`_http_release_probe` / `confirm_release_via_distinct_channel`). The hunt
    already measured the defect **live**: a pushed tag with no release returns
    200 with the tag present 23 times and the same `Release <tag>` title, and the
    one channel that discriminates (unauthenticated REST) answered 403 and "is
    not a dependable default". A local-server fixture cannot produce evidence
    stronger than that live measurement, so this row becomes an Operator Decision
    Queue item, not a slice.
  - **D28 remainder — trigger check only.** `emit_payload_main` in
    `scripts/scaffold_artifact_lib.py` still has no `--write`, and the fill-guard
    arm needs observed n-fold rework evidence. Read the trigger, record the
    verdict, do not reopen.
  - **sibling-scan Tier 2 D — ALREADY CLOSED; record sync only.** Repaired in
    commit `48b51a39` (2026-07-20) with the finding id in the code comment and
    three regression tests including a discriminating control. The only artifact
    left is the stale "Remaining: decide on Tier 2 (D)" line in the sibling-scan
    record. Verified independently by the parent and by two bounded reviewers.
  - **The handoff chunker's path-resolution defect — promoted from Off-Goal.**
    `skills/public/handoff/scripts/chunked_routing_staleness.py` `missing_paths`
    resolves cited paths against the repo root, so a correct dot-slash link in
    `docs/handoff.md` is reported missing and `draft_goal_from_chunk.py` can stamp
    a live citation `MISSING`. Observed live this session; it hits every future
    goal draft.
- Also in scope: the regression test for each repair, and any generated/mirror
  surface the changed files feed.
- **Mirror sync is a named step, not a note.** The chunker fix and any
  release-surface edit are public-skill exports: run
  `python3 scripts/sync_root_plugin_manifests.py` (and the skill mirror sync the
  repo's implementation-discipline names) BEFORE validators, and stage
  `plugins/ .claude-plugin/ .agents/plugins/` in the same commit —
  `check_staged_mirror_drift.py` enforces this at pre-commit.
- Out of scope as an editing target: `plugins/` copies. Mutate canonical source
  and sync.
- **Live git probes run in an isolated worktree (`charness worktree create`) or a
  throwaway clone, never against this worktree's index.** Running `git rm --cached`
  or `git revert` here would stage a reversion into the closeout commit (#258).
- **Round-2 bounded review is owed by whichever slices SHIP changed verdict
  logic on a proof surface — currently A3, S3, and C6.** The trigger is what the
  surface decides, not that its file was touched. The A3 planner decides which
  gates run and whether a commit is refused, so it owes the round; D4 and D28 now
  ship no code, so they owe nothing. Cap is two rounds; round-2 repairs are
  recorded as accepted-unreviewed. A first round that produces no repairs
  discharges the obligation. Ordering is fixed: round 1 -> repairs -> round 2 ->
  repairs -> mutation-coverage producer, so the producer is not paid for twice.
- **Every bounded review is bracketed by
  `skills/shared/scripts/reviewer_boundary_fingerprint.py` snapshot/verify**, with
  parent writes declared via `--parent-path` / `--parent-staged`. This run
  interleaves clone-based probes, mirror syncs, and reviewer rounds, which is the
  highest-risk shape for unattributable drift; a failed verify quarantines that
  review's approvals.
- **A new blocking floor requires a recorded Floor-Addition Restraint call.**
  Slice 2 (S3) is a third attempt at a floor and slice 3 (C6) may add a refusal
  condition. Run the three-question checklist and record the call as a
  `Floor-Addition Restraint:` line or a site comment; the two withdrawn byte
  floors are the recurrence evidence the checklist asks for, cited under the rule
  rather than instead of it.
- **Portability classification is a closeout checkpoint.** Each shipped repair
  gets a `host-local` vs `skill-capability` call, because contract-shaped repairs
  are inheritable policy and defect-repair framing is exactly what keeps that call
  out of view.
- **The assertions that pin today's behavior, listed now, before the slice plan**
  (the shaping-time rule, not a during-run one):
  - A3: `tests/quality_gates/test_staged_commit_gate_plan.py` (56 tests) pins the
    plan's gate scheduling; `tests/quality_gates/test_new_proof_surface_advisory.py`,
    `test_slice_closeout_decaying_habit_advisory.py`,
    `test_slice_closeout_close_keyword_advisory.py`, and
    `tests/test_doc_authoring_preflight.py` also read the planner. A repair that
    adds a per-gate scope field must keep all of them green.
  - S3: `tests/quality_gates/test_prescribed_skill_executed.py` (31 tests) — this
    is the "34 existing tests" surface that defeated the universal byte floor.
    Any shape floor must be measured against these first, not after.
  - C6: `tests/test_boundary_probe.py`, `tests/test_critique_artifact_validation.py`,
    `tests/test_validate_critique_artifacts_dates.py`. (The release-publish
    critique-artifact tests pin D4's surface, which ships no code this run.)
- **No repair may turn an ordinary run red.** A silently weakened assertion is the
  escape `docs/conventions/operating-contract.md` names; a re-pinned assertion is
  named in the slice review packet.
- Reproduction first. A row whose wrong output cannot be reproduced does not get a
  fix — it gets a recorded disposition saying so.
- Stop conditions: (1) a row's reproduction fails -> re-disposition, do not fix;
  (2) a repair would need a change larger than its row -> record the question in
  the Operator Decision Queue and move on; (3) any probe that would touch a live
  external boundary (a real release page, a real push) stops for operator
  approval.

## User Acceptance

The operator can open this artifact after the run and, for each row, read one
line saying either "repaired, and here is the test that fails when the fix is
reverted" or "not repaired, and here is the evidence plus the reason". No row is
left un-dispositioned.

Concretely:

- Each row appears in `## Slice Log` with one of three outcomes: repaired,
  disposition recorded, or refuted.
- **At least one row ends `repaired` with a revert-checked regression test, or
  this goal is incomplete.** Recorded because the plan legitimately treats
  dispositions as success, and without this line a run that changes zero lines of
  code and writes six paragraphs would satisfy every other criterion.
- Every repaired row names a regression test and the check showing that test
  fails against the pre-fix code. For S3 specifically the check is only
  meaningful after the `xfail` marker is removed: with `strict=False` a reverted
  fix yields XFAIL and the suite stays green in both states, so the marker's
  removal is part of the repair.
- Every disposition names the evidence that justifies stopping — a probe
  transcript, a measured refusal count, a checked-in prior measurement, or a
  scope statement — not an assertion that it seemed hard.
- One critique artifact per slice, recording both review rounds (or
  `Critique: blocked <host-signal>` if the bounded path is host-blocked).
- The owning records — the hunt, the sweep, the sibling-scan backlog, and
  `docs/deferred-decisions.md` — are updated so their Status columns match this
  goal's outcomes.

## Agent Verification Plan

Low-cost, at every commit boundary:

- `python3 scripts/check_doc_authoring_preflight.py --path <changed md>` for every
  changed markdown surface, **read for findings, not for exit code**: the preflight
  exits 1 on advisory `pathy` backticked refs for essentially every checked-in
  artifact, including `docs/handoff.md` and the prior goal. Its markdownlint,
  wrapped-inline-code, and broken-relative-link findings are the signal.
- The touched module's own test file, run directly.
- **`scripts/check_doc_links.py` does NOT cover `charness-artifacts/`.** Its
  `DOC_GLOBS` is README/AGENTS/docs/presets/profiles/skills only, with no path
  override, so running it proves nothing about the audit records this goal must
  update. The preflight's `doc-links` findings on an explicit `--path` are the
  only link channel that reaches an artifact; a green `check_doc_links` over this
  goal's changes is a non-claim.
- `python3 scripts/validate_handoff_artifact.py --repo-root .` if the handoff is
  touched at closeout.

Slice-boundary:

- The full test module for the changed surface plus the pinning assertions listed
  in Boundaries.
- For each repair, the revert check: apply the fix's inverse, confirm the new test
  fails, restore.

Bundle boundary, before closeout:

- `bash scripts/run-quality.sh` (or the documented substitute if a lane is
  unavailable — record which).
- `prepush_focused_changed_line_coverage.py` with `--repo-root .`,
  `--base-sha <sha before slice 1's first commit>`, and
  **`--refuse-unestablished`** — the source copy, never `plugins/`. Without that
  flag an unestablished run stays non-blocking and merely loud, so the closeout
  evidence could be green over a run that established nothing. The default
  merge-base is right only while the commits are unpushed and vacuous after, so
  the explicit `--base-sha` is required.
- `run_slice_closeout.py` with `--produce-mutation-coverage` at the final
  `--verification-lock`. `scripts/**` and `skills/public/*/scripts/**` are both
  eligible mutation pools and this goal edits both, so the closeout producer is
  the broad proof; the pre-push changed-line lane does not substitute for it.

High-confidence / high-cost proof, and what is NOT run:

- A3's residual-1 repair is exercised by **live git shapes** (staged deletion,
  `git rm --cached`, a detected rename) in an isolated worktree or throwaway
  clone. That proves the planner's behavior on that clone's shapes, never this
  host's installed `core.hooksPath` behavior.
- **D4 is not probed at all this run.** The hunt already measured it live; the
  remaining question is credentials/availability and belongs to the operator.
- **A green changed-line coverage result over an empty or near-empty changed set
  is a non-claim.** If the bundle lands as mostly markdown, the changed-line gate
  has an empty denominator — the exact class this backlog hunts — and the closeout
  says so rather than citing the green.
- No mutation lane beyond the closeout producer, no cautilus run, no CI dispatch.

## Discuss before activation

RESOLVED 2026-07-31. Each item below was decided by the shaping session against
the three bounded plan reviews and surfaced in the transcript before activation
was offered; the operator may overturn any of them at activation. They are
recorded here so `--pursue-ready` does not clear until they have been seen.

- **The plan shrank from six slices to three repairs plus bookkeeping.** Two
  reviewers independently found that sibling-scan Tier 2 D already shipped on
  2026-07-20, and that D4's remaining question is a credentials decision the hunt
  already measured live. Both were re-verified by the parent against the tree.
  The operator selected a six-row chunk; what is actually left is smaller, and
  the difference is recorded rather than padded.
- **A3's repair is deliberately narrower than the defect.** The owning critique
  declined converting scheduled gates to index readers. This goal makes the
  scope-vs-verdict mismatch legible instead of fixing it, which retires the
  "legible assurance over an uninspected scope" class without the every-gate
  change. That is a smaller claim than "A3 closed", and the record will say so.
- **S3's third attempt may fail like the first two.** If a per-kind shape floor
  cannot clear the 31 pinning tests, the correct outcome is to leave the xfail in
  place and record what the attempt ruled out — not to ship a floor that passes by
  being weak.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | A3 residual 1 — RE-SCOPED by its own reproduction: repair the untrack blindness in `check_staged_worktree_consistency` rather than annotate the planner | The only row here whose wrong verdict escapes on every commit; the probe showed the assurance is refusable, not merely illegible | Reproduced with a discriminating control; predicate replaced; 34 tests green, 13 red against the pre-slice gate; 199 planner-family tests green | **repaired** |
| 2 | S3 stub half — closed, but NOT with the per-kind shape check planned: a markdown-shape floor was measured and rejected (22 real artifacts have no headings), and the rule that worked is "evidence must say more than the identity it was checked against" | The pin is checked in and two prior attempts bound the design space; success flips a test green | Measurement scripted and recorded; floor 8 below both measured minima (337 markdown / 530 JSON probe); xfail replaced by real refusal assertions; the motivating case refused at the issue-close gate | **repaired** |
| 3 | C6: opt-in `--include-worktree` that unions rather than replaces | `--changed-path` was already a first-class input and `overrides` fires only on evaluated+hit, so widening is strictly stricter — a bounded, testable question, not a redesign | Blindness reproduced with a control; false-refusal cost measured at 11 of 965 artifacts; second consumer unbroken; the scope report now names which scope and which path produced the verdict | **repaired** |
| 4 | Chunker path resolution: base follows the citation style, resolved lexically | Hits every future goal draft, was observed live this session, and is the same wrong-base class this backlog hunts | `missing_path_count` 1 -> 0 on the repo's own handoff; 9 tests, all red against the pre-slice parser; mirrors synced | **repaired** |
| 5 | Record sync and queue: sibling-scan Tier 2 D -> CLOSED, D28 trigger -> not fired, D4 -> operator decision, hunt/sweep statuses matched | Bookkeeping is what makes the next session's backlog true; today's run found an 11-day-stale row | Every touched record's Status matches this run; D4 queued with the distinct-channel constraint stated; the armed coverage gate's 9 uncovered lines closed; S111-S113 opened for this run's own off-goal findings | **done** |

## Operator Decision Queue

Operator-only decisions surfaced by this run. Seeded empty; the During loop
appends. Use `none — <reason>` at closeout if nothing was surfaced.

Queue item form:

- Decision: operator-only decision or confirmation needed
- Owner: operator or named human owner
- Why deferred: why the run did not stop immediately
- Unblock action: exact action or answer needed
- Revisit trigger: event, date, or proof boundary that reopens this

Queue:

- Decision: does the release distinct-channel probe get an authenticated channel,
  or is the tag-vs-release ambiguity accepted as rendered by `does_not_establish`?
  This is audit row D4's whole remainder. The hunt already measured it LIVE: a
  pushed tag with no release returns HTTP 200 with the tag present 23 times, and
  both that page and a real release page title themselves `Release <tag>`. The
  channel that discriminates — the unauthenticated REST API — answered 403 and is
  not a dependable default.
  - Owner: repo owner.
  - Why deferred: it is a credentials/availability question, not agent work. A
    local-server fixture cannot produce evidence stronger than a live measurement
    of the real surface, so building one would be theater.
  - Unblock action: decide authenticate-vs-accept. If authenticate, it wants its
    own slice and a decision about where the token lives for a consuming repo.
    The option a reader thinks of first — reuse the `gh` credential the publish
    flow already holds — is excluded on purpose: the whole point of this probe is
    to be a DISTINCT channel from the one that created the release, so an
    authenticated same-provider check would confirm the release against itself.
    Any answer has to clear that, which is what makes it a decision rather than a
    task.
  - Revisit trigger: the next release whose publish is confirmed by that probe, or
    any consuming repo that asks what `confirmed` means at that boundary.
**Withdrawn from this queue on the disposition review's finding, and correctly:**
"should the A3 residual be closed structurally" was filed here as an operator
decision, and it is not one — this run already answered it (slice 1 closed the
reachable escape) and nothing in it needs information only the repo owner holds.
It is a next-goal candidate, carried on the handoff rather than blocked on a
human. Recorded rather than deleted, because a queue that quietly absorbs
agent-decidable work is how a decision stops being anyone's.

## Public-Skill Validation Decision

Three public skills changed semantically: `handoff` (citation canonicalization),
`achieve` and `issue` (a new refusal category on their closeout wrappers).
`plan_cautilus_proof.py --detail` over the committed range reports
`status: not-required`, `run_mode: ask`, and
`scenario_registry_review_required: true`.

**Decision: deterministic validation owns these changes; no live cautilus run.**

- **No `cautilus evaluate` was run**, and none is claimed. The planner itself says
  the proof is not required, the repo contract is ask-before-run, and this goal's
  Non-Goals forbid it. Recorded as a decision, not skipped silently.
- **Scenario registry, reviewed:** the three consumer prompts in the dogfood
  matrix are `handoff` pickup routing, `achieve` goal shaping, and `issue`
  filing/resolution through `gh`. None of them exercises the changed behavior:
  the chunker's path canonicalization is below the pickup prompt, and the stub
  floor fires only on evidence a scenario would have to deliberately stub. So the
  maintained coverage does not need to change for these edits — and that is a
  statement about these edits, not a claim that the scenarios cover them.
- **Consumer-visible risk, stated plainly:** all three changes make a gate
  STRICTER. A consuming repo whose closeout previously passed with a stub-shaped
  evidence file, or whose critique carried a bare `single-surface` verdict while
  its worktree touched a cross-surface path, will now be refused. That is the
  intent, and it is the same migration shape the 3.0.1 notes carried. It is not
  in a release this session — no version bump, no publish — so the note belongs to
  whoever cuts the next one.
- **Dogfood contract:** not re-frozen. `docs/public-skill-dogfood.json` describes
  the consumer PROMPT and expected routing, neither of which these edits change.
  Freezing it would record a contract change that did not happen.

## Slice Log

### Slice 1 — A3 residual 1: scheduled is not judged

- Objective: Close the shape where every worktree-walking pre-commit gate prints PASS over content the commit removes from the tree. Planned as a legibility change to the gate PLANNER; the reproduction found a repairable hole in check_staged_worktree_consistency instead, so the slice repaired that and left the planner untouched.
- Why this approach: The planned repair (annotate each scheduled gate with the scope it inspects) would have made a false assurance readable. The probe showed the assurance is refusable: the gate whose stated question is 'does this path appear on BOTH sides' was structurally blind to the untrack shape, because removing a path from the index removes its index ENTRY and the worktree-vs-index diff can no longer name it. Repairing the predicate beats annotating around it, and it stays inside the critique's 'not converting scheduled gates to index readers' fence.
- Commits: `a4925516`
- What changed: scripts/check_staged_worktree_consistency.py (canonical) + plugins/charness/scripts/ mirror (synced, sha256-identical); tests/quality_gates/test_check_staged_worktree_consistency.py (+16 tests, 18 -> 34)
- Alternatives rejected: Annotating the planner's output with a per-gate inspected-scope field: rejected once the hole turned out to be repairable — a legible false assurance is still a false assurance. Converting the scheduled gates to index readers: out of bounds, declined by the owning critique as 'a change to every gate rather than to the plan'.
- Targeted verification: REPRODUCED in an isolated clone with NO bypass set: git rm --cached docs/handoff.md + an on-disk edit cleared check_staged_reversion AND check_staged_worktree_consistency, then check_doc_links / check-markdown / check_title_slug_drift / validate_current_pointer_freshness all printed PASS and the commit landed, deleting the file. DISCRIMINATING CONTROL: with the worktree made to match the committed tree, check_doc_links FAILS (AGENTS.md: broken relative link ./docs/handoff.md) — so the green was over a tree that is not what got committed. REPAIRED: predicate is now staged(--no-renames) - ls-files(--full-name), filtered by on-disk presence. 34 tests green; 13 of them fail against the pre-slice gate; reverting only --no-renames fails exactly the rename test, reverting only the case fold fails exactly the fail-open test. Planner-family suites 199 green. ruff clean.
- Test duplication pressure: 16 tests added to one existing module, all against the same gate; no new test file, no fixture duplication — each new test constructs its own git state through the module's existing _repo/_git helpers. Two tests execute the offered remedies rather than string-matching them, which is what caught a remedy that exits 128.
- Critique artifact: [slice 1 critique](../critique/2026-08-01-slice-1-a3-residual-1.md)
- Critique: Two rounds, bounded read-only reviewers, each bracketed by reviewer_boundary_fingerprint snapshot/verify — both windows verified clean. Round 1 (2 reviewers): 3 BLOCKERs, all parent-confirmed by command — rename detection collapses D+A into R so --diff-filter=D missed the move-and-recreate shape; the offered `git rm <path>` exits 128 on a path with no index entry; the legitimate untrack workflow had no correct offered move. Plus the Floor-Addition Restraint record manufactured a recurrence count where the honest statement is that it promotes A3-critique F8's documented deferral. Round 2 (read the repairs): 1 BLOCKER — the case-only-rename exemption folded over the whole tracked set, so untracking Foo.md escaped whenever an unrelated foo.md was tracked; a fail-open in the repaired predicate, in the class the slice closes. Parent reproduced it before fixing. Also: --no-renames was on the staged read only, so an intent-to-add rename (what git add -p creates) resurfaced the ORIGINAL shape-1 defect; ls-files is cwd-scoped where diff --cached is repo-wide; and three tests proved less than their docstrings claimed. All folded. Round-2 repairs are accepted-unreviewed under the two-round cap.
- Off-goal findings: The pre-commit hook on this session's own first commit scheduled check_doc_links and printed PASS over a commit that was entirely under charness-artifacts/, which check_doc_links' DOC_GLOBS excludes — the same 'green over an uninspected scope' class, at glob granularity rather than index granularity. Not repaired here: each gate owns its own denominator, which the A3 critique fenced out.
- Lessons carried forward: The reproduction is what re-scoped the slice: the planned repair was designed against the audit's prose, and the prose described a shape that a later fix had already made unreachable by its stated route. Probing first turned a legibility patch into a refusable hole. Second: my repair introduced a status-letter allowlist four lines below the file's own comment arguing that a status-letter allowlist is the wrong shape for this gate — the round that read the repair is what caught it, for the fourth measured slice running.
- Metrics: not recorded per slice. The goal carried no `Host metric window:` line, so any per-slice token or duration number would be a proxy; the run-level host log probe is cited in `## Final Verification` instead.

### Slice 2 — S3's stub half

- Objective: Close the stub half of sweep row S3: a four-byte file whose whole content is its own citation satisfied the mandatory closeout-critique gate, because the only content test was st_size == 0 and the file bound by content.
- Why this approach: Not the byte floor S3 asked for, and not either of the two that were withdrawn. The precise defect is narrower than 'the file is small': the content IS the token. So the rule is that evidence must say something BEYOND the identity it was checked against. Measured before it was written, which is what both withdrawn attempts skipped.
- Commits: `eedb7ec6`
- What changed: scripts/check_prescribed_skill_executed_lib.py (the floor + residual_tokens); skills/public/issue/scripts/issue_resolution_critique.py and skills/public/achieve/scripts/goal_artifact_closeout_evidence.py (wired); skills/public/achieve/scripts/check_goal_artifact.py, skills/public/achieve/scripts/describe_goal_closeout_shape.py, scripts/check_issue_closeout_commit_msg.py (renderers taught the new category); scripts/measure_evidence_residual.py (new, the measurement as a script); charness-artifacts/probe/2026-08-01-evidence-residual-floor.json (its recorded run); docs/prescribed-skill-closeout-contract.md; tests (+7 in the gate's own module, 4 degenerate fixtures rewritten in 3 files); plugins/ mirrors synced
- Alternatives rejected: A per-kind markdown SHAPE check (require headings): measured and REJECTED — 22 of 2168 real artifacts have no headings, all of them commit-message drafts, so it sits above how this repo writes its own evidence, which is the shape that withdrew the last attempt. A third byte floor: rejected, coarse in the direction that matters. Copying the floor into each wrapper: rejected — that is the mistake evidence_binds_to_context already made once, and residual_tokens keeps it at the choke point.
- Targeted verification: Measured first, by a checked-in script (scripts/measure_evidence_residual.py, run recorded at charness-artifacts/probe/2026-08-01-evidence-residual-floor.json): the stub's residual is 0; markdown artifacts floor at 337 over 2168 files; real JSON host-log probes at 530 over 83. The floor sits at 8, below every measured minimum. The gate's own module went 31 -> 43 tests, 4 of which fail against the pre-slice library. Live corpus check: a real checked-in critique scores 5951 against a floor of 8. The motivating case executed end to end at the gate it lives on — a 4-byte '#466' file is refused by the issue-close gate and a real critique still closes the issue. Consumer suites 705 green; full suite run separately.
- Test duplication pressure: 7 tests added to the gate's own module; no new test file. Four EXISTING fixtures in three other files were rewritten because they were degenerate (12-byte shapes like {"goal":"g"}); git diff confirms no assertion moved, only fixture content and comments. Two of those rewrites shipped malformed JSON in the first cut and were fixed after round 2 caught it.
- Critique artifact: [slice 2 critique](../critique/2026-08-01-slice-2-s3-stub-half.md)
- Critique: Two rounds, bounded read-only reviewers, both windows fingerprinted. ROUND 1 BLOCKER, parent-confirmed by running it: the floor was in the library and did not reach the gate that motivated it — issue_resolution_critique and goal_artifact_closeout_evidence bind OUT-OF-BAND and pass no tokens, so a 4-byte '#466' file still closed issue #466 with the floor shipped. Also: the floor at 20 cleared a real fixture by 2 characters, and the corpus measurement covered markdown only while the gate is generic over kinds. ROUND 2 BLOCKER, parent-confirmed: the new stub_evidence refusal category had no renderer in three consumer surfaces, so a stub-only refusal printed a prefix with an empty tail — and each of those files carries a comment saying that exact no-diagnosis defect was already repaired there once for other categories. Round 2 also found the code and the doc contradicting each other about whether the JSON kind was measured, two fixture rewrites emitting invalid JSON, a test whose name asserted an invariant the repair had deleted, and that the measurement numbers were reproducible from nothing. Every one folded; the measurement is now a checked-in script. Round-2 repairs are accepted-unreviewed under the two-round cap.
- Off-goal findings: Running two pytest suites concurrently produced 17 false failures and 21 errors in shared-state tests — the same flake class sibling-scan Tier 2 D fixed for concurrent SessionStart hooks, one level up. Not repaired; the clean serial run is 6388 passed.
- Lessons carried forward: Measuring before writing is what separated this attempt from the two that were withdrawn — and the withdrawal reasoning itself was a mis-measurement: 34 failing TEST FIXTURES were read as evidence about how the repo writes EVIDENCE, when the artifacts start at 427 bytes. Second: both rounds found the same shape of miss — the repair was correct where I was looking and absent where the thing is actually used (round 1: the wrapper that never passed tokens; round 2: the renderers that never learned the category).
- Metrics: not recorded per slice. The goal carried no `Host metric window:` line, so any per-slice token or duration number would be a proxy; the run-level host log probe is cited in `## Final Verification` instead.

### Slice 3 — C6: the probe read the committed range only

- Objective: Make the critique cross-surface probe judge the change under review.
  Verify precedes commit, so the slice under critique is in the worktree and
  structurally invisible to a committed range.
- Why this approach: Not the contract change the hunt implied. `--changed-path`
  was already a first-class input and `resolve_changed_paths` already had a
  worktree fallback; the blindness was manufactured entirely by the caller passing
  only `--changed-ref`. An opt-in `--include-worktree` that UNIONS rather than
  replaces keeps `--changed-path`'s documented precedence and the second consumer
  (the `prove` stop-gate) untouched.
- What changed: `scripts/boundary_probe_lib.py`,
  `scripts/critique_enforcement_scope.py`,
  `scripts/validate_critique_artifacts.py`, `scripts/run-quality.sh`,
  `scripts/check_artifact_surface_preflight.py` (comment and recorded residual
  only); `tests/test_boundary_probe.py`,
  `tests/test_validate_critique_artifacts_dates.py` (+4 tests); `plugins/`
  mirrors synced.
- Alternatives rejected: making `--changed-path` union by default — it has
  documented wins-over semantics and a second consumer. Giving the commit-boundary
  preflight the same flag — TRIED and REVERTED on measurement: it refused a
  critique artifact written for an earlier change, because that arm targets the
  artifact the author holds while the tooth judges the current worktree.
- Verification: REPRODUCED on the live repo — one worktree-only edit to a
  configured `scripts/*_lib.py` glob with an empty committed range gave
  `state=evaluated hit=False overrides=False` from the range, and
  `hit=True overrides=True` from the same tree's worktree paths. The 5b tooth was armed
  or disarmed by which question was asked, not by the code. FALSE-REFUSAL COST
  MEASURED before shipping: 11 of 965 checked-in critique artifacts carry a bare
  `single-surface` verdict past the grandfather cutoff, and widening can only make
  the gate stricter, because `overrides` fires solely on `evaluated AND hit`. Four
  tests added, all red against the pre-slice library; 366 boundary/critique/
  preflight tests green.
- Test duplication pressure: 4 tests across two existing modules, no new file. Two
  of them pin STATES rather than values, which is what this module exists to
  distinguish.
- Critique artifact: [slice 3 critique](../critique/2026-08-01-slice-3-c6-worktree-scope.md)
- Critique: two rounds, both fingerprint-verified clean.
  - Round 1, no blocker, six should-fixes. The flag made `not-established`
    structurally unreachable, so an empty ref plus a clean tree reported
    `evaluated (no match)` over ZERO paths — the empty-scope class this backlog
    hunts, introduced by my own repair. The parent found and confirmed it
    independently before the review returned; the state is now decided by the
    RESOLVED path list rather than by which flags were passed. Round 1 also caught
    that the slice RELOCATED the same-tree-two-questions divergence to the
    commit-boundary preflight instead of closing it.
  - Round 2, no blocker, six more. The run-quality comment "fix" had ADDED a
    second comment five lines below the stale one, leaving the file
    self-contradictory — the class the repair was fixing. The `not-established`
    note still stated a cause that had become false. `matched_path` was scored
    against a different adapter read than the `hit` it explains, which could
    render a match on `None`. And the residual comment's story was wrong: a
    genuinely months-old artifact CANNOT be refused, because the override is
    date-grandfathered at 2026-07-06, so the reachable case is narrower than I
    wrote. All folded; round-2 repairs are accepted-unreviewed under the two-round
    cap.
- Off-goal findings: `resolve_hit` re-reads the adapter through its own
  module-level binding while `resolve_cross_surface_scope` reads the adapter
  handed to it — two adapter reads on one decision. Pre-existing and not worsened;
  the matched-path repair now consumes the read `resolve_hit` actually used.
- Lessons: the reproduction re-sized the row again — the hunt called C6 a contract
  change and the code already had every piece, with one caller argument as the
  whole defect. And now three for three: the round that reads the repairs caught
  something the repair itself introduced. This time it was my comment repair
  contradicting the comment it was repairing.

### Slice 4 — the handoff chunker resolved cited paths against the wrong base

- Objective: resolve a cited path against the directory of the artifact that
  cites it, instead of stripping `./` and `../` prefixes and testing the result
  against the repo root.
- Why this approach: prefix-stripping is not canonicalization. From `docs/`,
  `../charness-artifacts/x.md` stripped to the right answer by coincidence
  (`docs/..` IS the root) and `./deferred-decisions.md` stripped to a path that
  does not exist. A check run against the wrong base, reporting its miss as a
  fact — the same class the rest of this goal repairs, inside the tool that
  selects the work.
- What changed: `skills/public/handoff/scripts/chunked_routing_parser.py`
  (`_normalize_path`, `_resolve_lexically`, `_with_token_slash`,
  `_strip_relative_prefixes`, and a new `path_root` parameter),
  `skills/public/handoff/scripts/parse_handoff_entries.py`
  (`_path_root_for_citations`, and staleness now takes the citation root);
  `tests/test_handoff_chunker_parse.py` (+9 tests); `plugins/` mirrors synced.
- Alternatives rejected: resolving EVERYTHING against the artifact directory —
  tried first, and the repo's own CLI test caught it: a bare
  `charness-artifacts/goals/x.md` became `docs/charness-artifacts/goals/x.md` and
  the completed-goal filter stopped firing. Reusing the live-filter root as the
  citation root — tried, and it made a checked-in fixture snapshot inherit this
  repo, so live goal-status filters judged the snapshot against today's artifacts
  and dropped an entry.
- Verification: reproduced on the repo's own handoff — `missing_paths` returned
  a live file as stale and `missing_path_count` was 1 with zero stale citations;
  it is 0 now, and `deferred-decisions.md` resolves to `docs/deferred-decisions.md`.
  The `--handoff-path` form from another cwd now resolves AND reports missing
  paths. 9 tests added; all fail against the pre-slice parser. 681
  handoff/chunker/achieve tests green.
- Test duplication pressure: 9 tests in one existing module, no new file. Three
  of them exist because a reviewer showed an earlier test proved less than its
  docstring claimed, which is its own kind of duplication debt.
- Critique artifact: [slice 4 critique](../critique/2026-08-01-slice-4-chunker-path-resolution.md)
- Critique: two rounds, both fingerprint-verified clean.
  - Round 1, one blocker: a directory token lost its trailing slash under the new
    resolution, so `integrations/tools` (handoff side) stopped intersecting
    `integrations/tools/` (issue side) in the merger's exact-string boundary-token
    intersection — a merge that fired before silently stopped firing, in the very
    invocation the slice enables. Also: `.resolve()` followed symlinks, and this
    repo checks in current pointers (`charness-artifacts/quality/latest.md` and
    `CLAUDE.md` are symlinks), so a cited pointer was rewritten to its frozen
    dated target; the cross-style fallback could launder a stale citation into a
    different existing file; an out-of-repo citation could be pulled back inside;
    and the escape test did not test escape.
  - Round 2, no blocker: the blocker's repair had re-created the same divergence
    with the BASE diverging instead of the slash — a bare `conventions/x.md`
    became `docs/conventions/x.md` on the handoff side while the issue side kept
    the bare form. And an anchor-only link (`[rule](#skill-routing)`) normalized
    to the artifact DIRECTORY, so the drafter rendered `In scope: docs` — a goal
    claiming a whole top-level directory from a link that cites nothing. Both are
    the wrong-base class, running through the new base. Also caught: the rewritten
    escape test still shipped a claim it could not establish, the
    directory-slash test never reached the branch it named, and the citation-root
    docstring contradicted the code beside it. All folded; round-2 repairs are
    accepted-unreviewed under the two-round cap.
- Off-goal findings: none new.
- Lessons: four for four now — the round that reads the repairs caught something
  the repair itself introduced, every slice this session. Slice 4 went further:
  round 1's repair created round 2's blocker, and round 1's OTHER repair created
  the fixture regression that the repo's own test caught before any reviewer saw
  it. The cheapest guard remains running the existing suite against the repair
  before believing it.

### Slice 5 — record sync, and the closeout gates

- Objective: make every owning record's Status match what slices 1-4 actually did,
  check D28's reopen trigger rather than assume it, and queue D4 as the operator
  decision it is.
- Why this approach: bookkeeping is what makes the next session's backlog true.
  This run started by finding an 11-day-stale row that cost a reproduction attempt,
  so leaving the same debt behind would be the session's own lesson unlearned.
- What changed: the sibling-scan record (Tier 2 D marked CLOSED with its commit and
  the eleven-day gap named), the hunt (A3 residual 1 narrowed, C6 FIXED, D4
  dispositioned to an operator decision), the sweep (S3 CLOSED with the measurement
  cited), `docs/deferred-decisions.md` (D28's trigger checked and recorded unfired),
  and the goal's own Operator Decision Queue. Plus the coverage work below.
- Alternatives rejected: leaving the records and describing the outcomes only here.
  A goal artifact is not where a future session looks for a row's status.
- Verification: full suite 6403 passed. The armed changed-line gate
  (`--base-sha <pre-slice-1> --refuse-unestablished`, the source copy) found NINE
  uncovered changed lines across five files — every one of them this session's own
  code — and they are now covered; `blocking_targets` is empty. It also reported
  `scripts/measure_evidence_residual.py` as mapped to no test, which is the
  measurement script slice 2's whole claim rests on, so it got its own module
  including a test that RE-RUNS the recorded probe artifact against today's tree.
  D28's trigger was read, not assumed: `emit_payload_main` still has no `--write`.
- Test duplication pressure: one new test module for the measurement script, plus
  nine coverage tests spread across four existing modules. The new module is
  justified by the script being new; the rest went where their subject lives.
- Critique artifact: [slice 5 critique](../critique/2026-08-01-slice-5-record-sync-and-closeout.md)
- Critique: no separate round. This slice ships record edits plus tests for code
  that has already had two review rounds each; the rounds that mattered are logged
  under slices 1-4. Recorded as a deliberate omission rather than an oversight.
- Off-goal findings: a defensive `return None` in `_path_root_for_citations` was
  unreachable — `live is None` implies an explicit path exists — and the coverage
  gate is what surfaced it. Removed rather than test-covered: a branch that cannot
  fire reads as a backstop and is not one.
- Lessons: the armed changed-line gate earned its keep for the second session
  running, and it earned it on MY code, not inherited code. Running it before
  believing a slice is done is cheaper than any review round.

## Context Sources

- Selected by handoff chunked routing on 2026-07-31 from
  [docs/handoff.md](../../docs/handoff.md) `## Next Session` entry 4, ranked 4 of
  5 and chosen by the operator over the ranker's recommendation.
- [2026-07-27 evidence-surface bug hunt](../audit/2026-07-27-evidence-surface-bug-hunt.md)
  — owns A3, C6, D4 and the class taxonomy (a)-(h).
- [2026-07-28 evidence-surface triage sweep](../audit/2026-07-28-evidence-surface-triage-sweep.md)
  — owns S3 and its `## 2026-07-31 closeout non-claims`.
- [2026-07-20 abstracted-pattern sibling scan](../audit/2026-07-20-abstracted-pattern-sibling-scan.md)
  — owns Tier 2 D.
- [A3 staged-scope critique](../critique/2026-07-27-a3-staged-scope.md) — F8/F9
  are the named residuals this goal probes.
- [deferred decisions](../../docs/deferred-decisions.md) — D28's reopen trigger,
  and D39/D41 which stay deferred.
- [recent lessons](../retro/recent-lessons.md) — read before changing any repo
  operating contract or proof surface.

## Interview Decisions

- **Mode: implementation-continuation.** Family considered: artifact-only draft
  vs implementation-continuation. Chosen because the operator's opening request
  was an autonomous-improvement instruction and the chunk selection followed a
  ranked list, which is a "run this one" signal. Rejected artifact-only: it would
  strand a draft the operator asked to have executed.
  `single-point: mode is a per-invocation intent, not a system axis.`
- **Chunk: un-dispositioned rows, over the ranker's recommendation.** Family
  considered: all five ranked chunks. The operator chose rank 4 over rank 2
  (S11's second channel). Recorded because the ranking reasoning is still on file
  and a later session should not read the choice as the ranker's output.
  `single-point: an operator override of a proposal, not a configurable value.`
- **Sandboxed probes over live ones.** Family considered: live repo index / live
  release surface / throwaway clone + local server. Chose the sandbox because the
  live variants are exactly the irreversible-boundary and index-corruption
  failures this repo's contracts exist to prevent. Rejected live probing: its
  extra proof does not pay for a corrupted closeout commit.
  Anti-anchoring: `axis: host` — hook installation and the `core.hooksPath`
  setting vary by host, which is itself why a clone-scoped probe cannot claim
  installed-host behavior.
- **Disposition counts as success, with a floor.** Family considered:
  repair-only criterion, disposition-friendly criterion, or disposition-friendly
  plus a minimum. Chose the third after the counterweight review showed the
  second admits a run that changes zero lines of code and still passes every
  criterion. A repair-only criterion is still rejected: it is precisely the
  pressure that produced S3's two withdrawn floors.
  `single-point: a success definition for this goal.`
- **Plan size: three repairs plus bookkeeping, not six slices.** Family
  considered: the six-row chunk as selected, a five-slice plan, or a cut plan.
  Cut after two reviewers independently showed one row had already shipped and
  another's remaining question was an operator credentials decision. The operator
  selected a six-row chunk; recording that what remains is smaller is more useful
  than padding the plan to match the selection.
  `single-point: a sizing call for this goal, re-decided against evidence.`

## Plan Critique Findings

Three bounded read-only reviewers (`bounded-reviewer`, spawned unnamed, shared
parent worktree) read the draft on 2026-07-31 at distinct angles:
scope-and-reproducibility, repo-contract conflict, and counterweight/over-worry.
Parent bracketed the round with
`skills/shared/scripts/reviewer_boundary_fingerprint.py` snapshot/verify; verify
returned `verdict: clean` with empty drift, so all three reviews are admissible.
The parent independently re-verified every blocker against the tree before
folding — no finding below rests on a reviewer's reading alone.

**Blockers, folded:**

- **Slice 2's defect already shipped.** Two reviewers found it independently and
  the parent confirmed: `tests/test_usage_episodes_host_hooks.py` carries the
  fence with the finding id in its comment plus three regression tests, landed in
  `48b51a39` on 2026-07-20. The plan had called it "the cheapest real repair in
  the set" — the one row it counted on as a repair. Folded: the row became a
  record sync, and the plan's shape claim was rewritten rather than preserved.
- **`check_doc_links.py` does not scan `charness-artifacts/`.** Its `DOC_GLOBS`
  covers README/AGENTS/docs/presets/profiles/skills with no path override, so the
  plan's stated link evidence for the audit records was a verdict over a scope it
  never establishes — the class this goal hunts, inside its own verification plan.
  Folded into `## Agent Verification Plan` as an explicit non-claim.
- **The round-2 trigger set was close to inverted.** The draft named S3/C6/D4 —
  the three rows most likely to ship no code — and omitted A3, whose planner
  decides which gates run and whether a commit is refused. Folded: the trigger is
  now "whichever slices SHIP changed verdict logic", currently A3/S3/C6.
- **The mutation-coverage producer and the locked closeout were absent.** Both
  `scripts/**` and `skills/public/*/scripts/**` are eligible mutation pools and
  this goal edits both; the pre-push changed-line lane does not substitute for the
  closeout producer. Folded, with the fixed
  round-1 -> repairs -> round-2 -> repairs -> producer ordering.

**Also folded:** the `xfail(strict=False)` discrimination gap (a reverted fix
yields XFAIL, so the revert check proves nothing until the marker is removed, and
"strict-passing" is not a pytest state); C6's real surface is
`scripts/boundary_probe_lib.py` with a second consumer, not the validator;
`--refuse-unestablished` on the changed-line gate; the reviewer-boundary
fingerprint rail; Floor-Addition Restraint records; portability classification;
one critique artifact per slice; the shaping-time pinning-assertion list; and the
acceptance line requiring at least one revert-checked repair.

**Raised and NOT folded, deliberately:**

- **"Cut D4's slice to a queue item" — folded; "cut A3's probe" — not.** The
  counterweight reviewer argued A3's residuals are decidable by reading. Residuals
  2 and 3 are, and were demoted to status lines. Residual 1's repair changes what
  the hook prints on a real staged deletion, and that is worth executing rather
  than reasoning about.
- **"Six slices will half-finish"** — accepted as the diagnosis, and the plan was
  cut to three repairs plus bookkeeping. The reviewer's stronger form ("ship only
  A3 residual 1") is not adopted: slices 2-4 are each independently small, and
  slice 4 was promoted precisely because it is cheap and hits every future draft.
- **Over-worry confirmed in the plan's favor:** the round-2 obligation carries its
  own discharge clause and costs nothing when a row ends as a disposition, and the
  throwaway-clone rule is one command against a failure (#258) that corrupts the
  closeout commit. Neither was cut.
- **A note for the next session, not this one:** the evaluated / empty /
  not-configured scope concept now has two independent implementations in tree
  (`critique_enforcement_scope.CrossSurfaceScope` and D7's `evaluation_scope`).
  The unify-on-second-occurrence rule means the next row in that family should
  unify rather than add a third. None of this goal's rows is in that family.

## Coordination Cues

- Routing: `achieve` — selected from installed skill metadata as the owner of a
  multi-slice goal lifecycle, after `handoff` chunked routing produced the
  skeleton. Within it, repairs routed to `impl`/`prove`, the plan pass and all ten
  per-slice rounds to `critique`, the closeout review to `critique` as a
  disposition reviewer, and the quality phase to `quality` (dup-ratchet triage and
  classification, the armed changed-line gate, the locked closeout producer).
- Gather: n/a — no external source; every input is a checked-in repo artifact.
- Release: n/a — Non-Goals forbid a version bump, tag, or publish.
- Issue closeout: n/a — no tracked issue; the repo's open-issue backlog is empty
  as of 2026-07-31.

## Off-Goal Findings

- **The handoff chunker resolves cited paths against the repo root, not against
  the citing artifact's directory.** `docs/handoff.md` cites the deferred-decisions doc with a
  dot-slash relative link, which is correct from `docs/`;
  `chunked_routing_staleness.missing_paths` normalizes it to
  `deferred-decisions.md`, tests it against the repo root, and reports it as a
  missing path. `staleness.missing_path_count` was 1 on a handoff with zero stale
  citations. Because `draft_goal_from_chunk.py` renders a `MISSING` marker from
  that fact and refuses to put such a path in Boundaries, a live citation can be
  stamped stale in a drafted goal. Same class as the surfaces this backlog
  hunts: the check ran against the wrong base and reported its miss as a fact.
  Observed live this session. **Promoted to slice 4** on the counterweight
  reviewer's finding that it is the best operator-value-per-minute item on the
  page, so it is no longer off-goal.
- **`draft_goal_from_chunk.py` validates with `check_goal` but not with the doc
  authoring preflight.** Its output for this chunk carried four markdownlint
  findings (H1 trailing punctuation from a sentence-shaped objective, three
  `MD027` blockquote indents copied verbatim from the handoff's list
  continuation) and two broken relative links: the handoff's link targets are
  written relative to `docs/`, and the drafter copies them verbatim into
  `charness-artifacts/goals/`, where the same text resolves to nothing. Fixed by
  hand in this file; the drafter still emits them. Stays off-goal: it shares
  slice 4's file family, so fold it there only if it is free, otherwise leave it
  recorded.

## Final Verification

Retro: charness-artifacts/retro/2026-08-01-session-retro.md
Host log probe: charness-artifacts/probe/2026-08-01-disposition-the-stragglers-a3-c6-d4-d28-s3-stub-host-log.json
Disposition review: charness-artifacts/critique/2026-08-01-disposition-the-stragglers-a3-c6-d4-d28-s3-stub-disposition-review.md

Every row reached a state a future session can act on. What each one is, and what
it is NOT:

- **A3 residual 1 — repaired, narrowed.** Reproduced with a discriminating control
  in an isolated clone, no bypass set. NOT closed: the broader residual stands and
  the hunt row stays `PARTIAL` — a scheduled gate can still walk the worktree over
  a scope the commit changes, and the only structural closure is running those
  gates against a materialized index tree.
- **A3 residuals 2 and 3 — status only.** Re-read, not re-probed. Residual 2's
  measurement was already in the record; A5/A6 closed 2026-07-30. A6 was then
  reopened and re-closed by slice 1, and now says so in its own row.
- **S3 stub half — repaired.** The checked-in xfail is gone, replaced by refusal
  assertions. NOT closed: a few characters of filler still passes. This refuses a
  stub, not a lie.
- **C6 — repaired, narrowed.** The row reads `FIXED (narrowed)`, not `FIXED`. The
  flag is opt-in and the commit-boundary arms deliberately do not pass it, so the
  two surfaces still disagree on a worktree slice; the residual is in the code as
  `CROSS_SURFACE_RESIDUAL`.
- **sibling-scan Tier 2 D — already closed; record synced.** No code changed.
- **D28 — trigger read, stays deferred.** `emit_payload_main` still has no
  `--write`.
- **D4 — dispositioned to an operator decision.** No code changed and none is
  claimed; the measurement is inherited from the hunt's live run and disclosed as
  inherited.
- **Chunker path resolution — repaired.** Promoted in from off-goal.

Acceptance line satisfied: four rows ended `repaired` with revert-checked
regression tests, not one.

Executed proof:

- Full suite: **6403 passed**, serial.
- The locked slice closeout, run with `--base` so it covers the committed bundle
  rather than the worktree, with mutation-coverage production and the
  public-skill review acknowledged: **completed, 0 FAIL**.
- Armed changed-line coverage over the committed range
  (`--base-sha cb35991e --refuse-unestablished`, source copy): **clean**. It first
  found NINE uncovered changed lines across five files, all of them this session's
  own code, and one changed pool file mapped to no test at all; both are closed.
- `check_dup_ratchet --summary`: **0 new code families** after two real
  extractions and five recorded classifications.
- Ten bounded review rounds across five slices, each bracketed by
  `reviewer_boundary_fingerprint.py`; every window verified `clean` or
  `parent-attributed` with zero undeclared drift. One critique artifact per slice.
- `plan_cautilus_proof.py`: `status: not-required`, `run_mode: ask`.

Non-claims:

- **No live cautilus run.** None was required and none was requested.
- **No CI dispatch, no push, no release.** Nothing here is proven on a remote.
- **No mutation SCORE claim.** The closeout produced mutation coverage; it did not
  run a mutation campaign, and no score is cited.
- **D4 is not re-measured.** Its live evidence predates this session.
- **The A3 probes prove the clone's behavior, not this host's installed hook.**
- **Per-slice token and duration numbers are not recorded.** The goal carried no
  `Host metric window:` line, so the host log probe's `goal_metric_window` is
  `absent` and any per-slice figure would be a proxy.

## User Verification Instructions

1. `git log --oneline cb35991e..HEAD` — six commits, one per slice plus the shape.
2. Re-run the measurement slice 2's floor rests on:
   `python3 scripts/measure_evidence_residual.py --repo-root .` — it should exit 0
   and report the floor below both measured minima.
3. Re-run the gate that found this session's own uncovered lines —
   `prepush_focused_changed_line_coverage.py` with `--repo-root .`,
   `--base-sha cb35991e`, and `--refuse-unestablished`. It reports `clean`.
4. Reproduce slice 1's defect against the PRE-slice gate if you want the control:
   in a throwaway clone at `a4925516~1`, `git rm --cached docs/handoff.md`, edit
   the on-disk copy, and commit — it lands, deleting the file, with every doc gate
   green. At `a4925516` it is refused.
5. The two queued decisions are in `## Operator Decision Queue`: the release
   probe's authentication question, and nothing else — the second item was
   withdrawn as agent-decidable and is recorded as withdrawn.

## Auto-Retro

- applied: `scripts/measure_evidence_residual.py` plus its recorded run and its
  own test module — the "a threshold defended by prose gets withdrawn, a
  threshold defended by a script survives" lesson, made executable rather than
  written down.
- applied: `stub_evidence` rendered in all three consumer surfaces
  (`check_goal_artifact`, `describe_goal_closeout_shape`,
  `check_issue_closeout_commit_msg`), and `_refusal_bits` extracted so adding the
  NEXT refusal category is one line rather than a new unrendered branch.
- applied: S111-S113 opened in the sweep for this run's own off-goal findings,
  rather than leaving them in a goal artifact about to be closed.
- out-of-scope: a refusal-category renderer gate (a detector for "a bucket feeds
  `ok` but appears in no message builder") — the retro's Portable Candidate says
  it needs one more independent instance before it earns a checkable form.
  Carried on the handoff, not filed: this repo's open-issue backlog is empty by
  policy and its follow-ups live in docs.
- out-of-scope: the measurement-as-script sweep over the remaining prose
  thresholds (`MIN_SKIP_DETAIL_LENGTH`, the dup-ratchet baselines, the coverage
  floors). Named in the retro's Sibling Search as a follow-up outside this slice.
