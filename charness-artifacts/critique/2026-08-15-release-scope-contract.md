# Critique Review
Date: 2026-08-15

## Decision Under Review

Revision 1 of the 6.0.0 release scope contract
([release scope](../spec/2026-08-15-6-0-0-release-scope.md)) — the owner-approved
wide scope, its S1-S7 sequence, its success criteria and acceptance checks, and
its Fixed Decisions about release notes and the producer-scaffold class.

## Failure Angles

- Implementer misread: an implementer builds S1-S7 from this document and builds
  the wrong thing, either because an instruction's referent is undeterminable or
  because the contract asserts a repo fact that is stale or false.
- Overstated acceptance: the repo's measured failure signature is treating a
  passing gate as completion, and shipping a guard that cannot fail. Attack the
  success criteria and acceptance checks for checks that pass on the current tree
  with no work done, cannot fail by construction, or admit both an outcome and
  its opposite.
- Hidden sequencing: the S1-S7 order claims to be by dependency pressure. Does a
  later slice invalidate or silently redo an earlier one, does a run-late surface
  hide a build-early dependency, and does the two-round review obligation fit.
- Counterweight: separate real blockers from over-worry, and catch angle findings
  that are themselves wrong — over-correcting a contract with unfalsifiable
  checks is a recorded harm here, not a hypothetical one.

## Counterweight Pass

- Six findings were ruled over-worry and deliberately not acted on. The
  distinct-channel check (C4) was factually wrong: `verify-closeout` already
  parses and enforces the `Behavior #N:` grammar with substantive-value floors,
  and demanding a mechanical distinctness arm is the unfalsifiable-guard padding
  the repo already reverted once as F7/F16.
- Ordering #599 before the destructive-defect slice (S10) was ruled a reasoned
  owner decision with no evidence of harm from one slice of delay; the repo
  already has a working interim path for the defect.
- The S6 guard's exposure window (S11) is covered by an existing detective
  control — reviewer boundary snapshot/verify, where a failed verify quarantines
  that review's approvals. S6 upgrades detection to prevention; the interim is
  not unguarded.
- Boundary Ownership recording an assignment with its source while a probe
  question schedules its re-confirmation (S14) is how a contract states a
  live-but-unreconfirmed assignment honestly, not a contradiction.
- A ratchet firing on later slices (S17) is the gate working. Treating it as a
  defect would argue against arming any gate before the last slice, which
  inverts the contract's own derived-surface thesis.
- Two angle sub-claims were refuted on evidence: the `check_docs_graph.py:12-18`
  citation is correct as a docstring rationale reference, and the lint gate scope
  EXCLUDES the plugin mirror, so the 180-finding figure overstates gate-scope work
  rather than understating it.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/publish_release_execute.py:305 | action: fix | note: #608's premise is false — `execute_publish_plan` already stops at `prepared-awaiting-claims-review` and never tags, pushes, or publishes; found independently by three of four reviewers. Contract Problem 2, SC2, AC3, and S1 rebuilt a seam that ships. Recurrence of `premise-not-checked-against-source`.
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/scaffold_artifact_lib.py:167 | action: fix | note: the prescribed generalized date-coherence guard is INERT against #628 (the overwriting artifact carries today's date under today's filename) and would FALSE-REFUSE `debug`, which this line documents as legitimately continuing an open investigation in place. Class scope kept, mechanism replaced with subject identity.
- F3 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/spec/2026-08-15-6-0-0-release-scope.md:194 | action: fix | note: the notes generator and its notes-versus-tree gate are demanded by acceptance checks but built by no slice; S7 used run-only verbs over tools that do not exist. Now owned by S1.
- F4 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/release/2026-08-14-v6.0.0-notes.md:19 | action: fix | note: the specified gate tested only the omission direction, while the failure that shipped twice was an OVER-claim that mentions the surface and produces no omission diff. Both directions now required, with the over-claim case named as the one that must exist.
- F5 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/spec/2026-08-15-6-0-0-release-scope.md:83 | action: fix | note: the authored narrative was exempted from derivation, but the false claims lived in authored prose — so the criterion was asserted over the exact surface that failed. Replaced with a quantifier-containment lint rather than a prose claim-extractor.
- F6 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/spec/2026-08-15-6-0-0-release-scope.md:212 | action: fix | note: a "production caller" criterion was matched only by a direct-call unit test — the #586 shape the same contract schedules S5 to fix, reproduced inside its own acceptance surface.
- F7 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/publish_release_claims_review.py:387 | action: fix | note: the classification ledger was owned by no slice and its natural write time fell inside the window where the claims-review artifact must be the direct child of the prepared record with nothing else riding along.
- F8 | bin: valid-but-defer | evidence: strong | ref: scripts/check_docs_graph.py:248 | action: document | note: adding a metric to the gated set without its `BLOCK_FOR_METRIC`, `_UNREACHABLE_LABEL`, and `_REMEDY` entries degrades the gate to NOT-RUN or crashes uncaught from `main`; S4 is five edits, not one. Recorded in Constraints.
- F9 | bin: valid-but-defer | evidence: strong | ref: tests/test_docs_graph_gate.py:168 | action: document | note: S4 reverses a deliberate pinned scope decision, not an oversight; the contract now names the test and its rationale as things the slice retracts.
- F10 | bin: valid-but-defer | evidence: strong | ref: charness-artifacts/spec/2026-08-15-6-0-0-release-scope.md:185 | action: fix | note: the bar could be declared equal to the measured count, satisfying the criterion with zero work; a ratchet clause now forbids raising it without a recorded decision.
- F11 | bin: valid-but-defer | evidence: strong | ref: skills/public/quality/scripts/inventory_doc_duplicates.py:355 | action: fix | note: the contract's own flag inventory omitted a suppressed `--json-out` — the false-completeness class it exists to eliminate, inside its Problem section.
- F12 | bin: valid-but-defer | evidence: moderate | ref: charness-artifacts/spec/2026-08-15-6-0-0-release-scope.md:66 | action: fix | note: the `link_only_lines` figure was corroborated by nothing checked in and disagreed with three older recorded counts; replaced with the two independent commands that produce it.
- F13 | bin: valid-but-defer | evidence: strong | ref: charness-artifacts/spec/2026-08-15-6-0-0-release-scope.md:68 | action: fix | note: three sequenced slices carried no success criterion and no acceptance check while the contract gates release on "S1-S6 green"; a slice-to-criterion coverage table now closes it.
- F14 | bin: valid-but-defer | evidence: moderate | ref: charness-artifacts/spec/2026-08-15-6-0-0-release-scope.md:161 | action: document | note: the Constraints entry recorded the 180-finding ruff measurement without saying the repairs had already landed, so two reviewers read S1 as arming a red gate; corrected, and both scopes re-measured clean.
- F15 | bin: valid-but-defer | evidence: strong | ref: skills/public/release/references/critique-boundary.md:133 | action: document | note: S7 collapsed two distinct release reviews (the critique gate before bump, the claims round after notes and version exist) into one step; folded into the F1 rewrite.
- F16 | bin: over-worry | evidence: strong | ref: skills/public/issue/scripts/issue_verify_closeout_body.py:66 | action: document | note: the claim that SC8's distinct-channel half is unproven is wrong — `verify-closeout` parses the `Behavior #N:` grammar with substantive-value floors, and the residual is already stated at real size in critique-boundary.md.
- F17 | bin: over-worry | evidence: moderate | ref: charness-artifacts/spec/2026-08-15-6-0-0-release-scope.md:53 | action: document | note: #599-before-#628 was called severity inversion; the sequencing rationale is stated, the defect has a working interim path, and second-guessing it without evidence of harm is the over-correction to resist.
- F18 | bin: over-worry | evidence: strong | ref: skills/shared/scripts/reviewer_boundary_fingerprint.py | action: document | note: S6 landing after the reviewer-heavy slices is not an unguarded window; the snapshot/verify detective control is mandatory today and quarantines approvals on a failed verify.
- F19 | bin: over-worry | evidence: moderate | ref: charness-artifacts/spec/2026-08-15-6-0-0-release-scope.md:232 | action: document | note: Boundary Ownership recording an assignment with its source while a probe schedules re-confirmation is honest contract shape, not a contradiction with the probe question.
- F20 | bin: over-worry | evidence: strong | ref: charness-artifacts/retro/lesson-ledger.json:772 | action: document | note: `bar-recorded-as-prose` was called a non-spec term; it is a real lesson id served to this very session, and citing a recurrence class by name is normal practice here.
- F21 | bin: over-worry | evidence: moderate | ref: scripts/check_docs_graph.py:44 | action: document | note: an armed docs bar firing on later slices is the ratchet working; treating it as unbudgeted cost would argue against arming any gate before the final slice.

## Reviewed Input Identity

<!-- No prepare_packet.py packet was consumed; the reviewed input was the committed contract at 4530857ee, read directly by each reviewer. -->

## Reviewer Tier Evidence

- Requested tier: high-leverage — a task-completing contract governing a release and five proof surfaces.
- Requested spawn fields: typed subagent `bounded-reviewer` (read-only: Read, Grep, Glob), unnamed one-shot spawns, session-inherited model.
- Host exposure state: host-defaulted
- Application state: host-confirmed: four `bounded-reviewer` spawns accepted and returned findings; no per-subagent model or effort control was exposed, so the tier request was not separately honored.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

`parent-delegated` — three angle reviewers and one counterweight reviewer, each
spawned by the parent and completing its assigned lens directly. One angle spawn
terminated early on a host API 500 and was retried unnamed; the retry returned
findings. Boundary integrity was proven around both windows:
`reviewer_boundary_fingerprint` snapshot/verify on `release-scope-2026-08-15-r1`
and `release-scope-2026-08-15-cw`, both returning `verdict: clean` with empty
drift, so no review's approvals are quarantined.

## Boundary Ownership

- Producer: the release scope contract, which produces slice definitions, success criteria, and acceptance checks.
- Consumer: the `impl` slices S1-S7 and the S7 release execution that reads them as its definition of done.
- Owning surface: the spec artifact under `charness-artifacts/spec/`.
- Verdict: owned-correctly
