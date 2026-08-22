# Achieve Goal: Make claims review converge, then ship the 6.3.0 bundle

Status: complete
Created: 2026-08-22
Activation: `/goal @charness-artifacts/goals/2026-08-22-claims-review-convergence-then-ship-6-3-0.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: real draft/backlog awaiting activation.
- Current slice intent: real draft/backlog awaiting activation; reshape before
  activating if the acceptance boundary has changed. Once active, this names
  the reviewable-intent unit in progress and the commits it spans; critique
  and broad proof do not re-fire within one unchanged intent — update it when
  the intent changes, not per commit (meaningful-slice-cadence).
- Next action: activate with `/goal @charness-artifacts/goals/2026-08-22-claims-review-convergence-then-ship-6-3-0.md` after confirming the draft is
  still intended.
- Verification cadence: cheap deterministic checks at commit boundaries;
  higher-cost or fresh-eye proof at slice boundaries; final broad/live proof at
  closeout.
- Gate cadence: pre-lock slices use `run_slice_closeout.py --skip-broad-pytest`;
  final/bundle proof records the verification lock and uses `--verification-lock`.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Operator Decision Queue`, `## Final Verification`,
  and `## Auto-Retro`.

## Goal

Make the claims-review loop converge, then publish the 6.3.0 bundle that four
rounds proved was code-clean and could not ship.

This goal exists because its predecessor
(`charness-artifacts/goals/2026-08-22-proof-cost-portability-and-the-cadence-contract.md`)
landed slices C, B and A and then could not publish them. Four claims rounds all
returned `unproven`. Not one blocker was in the shipped code: every round
confirmed the quality-status owner mechanism, all five version surfaces, and
every derived figure. Every blocker was prose ABOUT the review, in artifacts
that ship inside the bundle being reviewed.

That is a loop with no fixed point, filed as #701. Repairing a finding changes
the bundle, which changes the record and the counts, which requires new prose
that nothing has reviewed. The predecessor's own durable claims record — added
to satisfy a round-3 finding — landed inside the prepared commit and made a
`pass` structurally unpublishable, which is the loop in one artifact.

This goal fixes the loop FIRST and publishes SECOND, in that order, because the
predecessor proved the other order does not terminate.

Designed from what the predecessor LEARNED, not from what it left over: the
leftover is "publish 6.3.0", but the lesson is that publishing 6.3.0 was never
the blocked thing — reviewing it was.

## Non-Goals

- NOT a redesign of the claims-review contract. The distinct-observer floor,
  the byte floor, the added-not-edited narrative rule and the prepared-stop
  topology are unchanged; only the SCOPE of what a verdict covers is declared.
- NOT a way to publish with fewer checks. Advisory findings are recorded and
  published, never dropped; the laundering guard is tested as hard as the split.
- NOT the remaining referent-gate and scope-split residue: the non-ASCII path
  case, `issue/` vs `issues/`, and the test module's `sys.path` cleanup are left
  for a later pass and named in `## Off-Goal Findings`.

## Boundaries

- External side-effect scope: name which phase or bundle any approved
  publish / push / remote-CI / apply applies to. That approval is phase-scoped
  and does not carry forward — after an approved publish/CI/apply lane
  completes, done-early test-only quality continuation is local by default
  (batch remote proof, run CI once over the final bundled state). Per-slice
  remote publication is assumed only when the operator explicitly asks or a
  runtime-affecting slice requires earlier publication.

## User Acceptance

- A claims round can converge: it returns findings that are ABOUT the shipped
  bundle, and defects in session narrative do not gate a tag.
- A `pass` cannot hide what it waived — the published record names each waived
  defect and the scope it covered.
- 6.3.0 is published and read back through a channel other than tag state.

## Agent Verification Plan

- Unit: the classifier, the laundering guard, and the completeness check, each
  negative-controlled (removing the defect flips the verdict).
- Wiring: deleting the guard's call site must break a test — round 1 found it
  did not.
- End to end: a real claims round against the real prepared commit, with the
  scope derived from the real delta rather than hand-written.
- Release: `run-quality.sh --release` over the full suite, then a distinct
  channel (GitHub API) for the publication itself.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Declare what a claims verdict is ABOUT | Two releases stalled on the same non-converging loop | A classifier over the real delta, a `pass` that must carry what it waived | landed; three commits touching `claims_review_scope.py` (`git log --oneline -- skills/public/release/scripts/claims_review_scope.py`). Two-round cap consumed; round-2 repairs accepted-unreviewed |
| 2 | Ship the bundle | Slices C, B and A reach consumers only through a release | Published readback through a distinct channel; a claims round that converges | landed; the tag and its commit are whatever `git describe --tags --abbrev=0` and `gh release view` report |

## Backlog Recount

Recount the tracker before scope; see the `achieve` skill's
`references/lifecycle-before.md`. That path is SKILL-relative — resolve it from
`$SKILL_DIR`, not from this artifact's own directory, where it does not exist.

- Counted: To be filled by the achieve Before-phase
- Claims: To be filled by the achieve Before-phase
- Not claimed: To be filled by the achieve Before-phase

## Operator Decision Queue

none — every consequential decision this run was either resolved in-flight
against the repo's own contracts (the scope split, the bump level, the two-round
cap) or is already carried as an open issue. The one item an operator would
otherwise inherit — whether the fixed issues may be closed — is recorded in
`## Coordination Cues` as a deferral with its reason, not parked here.

## Coordination Cues

- Phases: impl, quality, critique, issue, release, retro

- Routing: `achieve` — owns this goal's lifecycle, its slice log and this cue slot.
- Routing: `impl` — slice 1 is ordinary implementation on a release-flow surface.
- Routing: `quality` — the scope split changes verdict logic on a proof surface,
  so it went through the changed-line lane, the dup ratchet and the length caps.
- Routing: `critique` — two bounded fresh-eye rounds on slice 1 (the cap) plus a
  full claims round on slice 2; all three found blockers that changed code.
- Routing: `issue` — #701's fix landed here, and #612's diagnosis was
  recorded against the tracker rather than folded into this goal's prose.
- Routing: `release` — slice 2 ran the repo-owned publish helper end to end.
- Routing: `retro` — the closing review, persisted and bound in
  `## Final Verification`.

- Gather: n/a — no external URL, Slack, Notion, Docs or Drive source informed
  this run; every input was repo-local or an issue in this tracker.

- Release: published. The tag, its commit and the publication timestamp are
  whatever `git describe --tags --abbrev=0` and
  `gh release view --json tagName,publishedAt` report; the record is
  `charness-artifacts/release/latest.md` and the claims evidence is
  `charness-artifacts/release-review/2026-08-22-v6.3.0-round5-claims-review.md`.
  Readback was through the GitHub API, a channel other than tag state.

- Issue closeout: **DEFERRED, not n/a.** #701 is fixed by slice 1 and is NOT
  closed: no `--close-issue` was passed and no closeout ledger was staged, so
  the per-issue behavioural floor never ran. Closing on the strength of "the fix
  shipped" is the substitution that floor exists to refuse. #689, #690, #691,
  #696, #697, #698, #699, #700 likewise stay open. Closure is left to a session
  that runs the floor.

- Successor goal: `charness-artifacts/goals/2026-08-23-gate-by-property-not-by-enumeration.md`

## Discuss Before Activation

A Before-phase summary of any consequential activation decision — surfaced from
the Non-Goals / Boundaries / Verification / Interview / Critique sections — that
must be resolved before `/goal`. Required only when a trigger fires (live/prod
proof, issue close/split, broad scope, irreversible side effect, or a
proof-level non-claim); replace the `fill` line below, or delete it when none
applies.

- Discuss before activation: fill — replace with resolved, confirmed, or approved, then the consequential activation decision and how it was settled

## Slice Log

### Slice 1: declare the claims-review scope

- Objective: make a claims verdict say which surfaces it covers, so narrative defects stop gating a tag and the round can converge.
- Commits: `git log --oneline -- skills/public/release/scripts/claims_review_scope.py` — the split, then round-1 repairs, then round-2 repairs, in that order.
- What changed: `skills/public/release/scripts/claims_review_scope.py` (NEW — classification, the laundering guard, the completeness check), `publish_release_claims_review.py` (schema v2 -> v3, the guard wired into `validate_claims_review`), `publish_release_resume_publish.py` and `publish_release_artifact_sections.py` (the waived findings reach the published record), plus the ownership allowlist, the timing-layer table and the consumer-validator catalog.
- Critique: TWO bounded rounds; the cap is consumed and the round-2 repairs are accepted-unreviewed. Round 1 recommended `unproven` and was right: `classify()` had NO production caller, so the declared scope was unverified free text and a record declaring a shipped release-gate file as `advisory` was accepted. Deleting the guard's call site also broke no test. Round 2 then found the round-1 repairs had opened a post-tag inlet — `advisory_findings` was rendered verbatim into a record that is pushed AFTER the tag, so a newline could inject a `target version:` line that refuses every later push, and the prepared-stop marker could permanently reclassify a finished release. It also found the `.md`-is-narrative rule classified `quality/latest.md` and `recent-lessons.md` — both machine-read — as advisory.
- Targeted verification: `python3 -m pytest -q tests/quality_gates/test_claims_review_scope.py` plus every release suite it touches. Both defect paths negative-controlled — removing the defect flips the verdict, and deleting the guard's call site fails two tests. The laundering record round 1 demonstrated is refused by name.

### Slice 2: ship 6.3.0

- Objective: publish the bundle three earlier slices produced, through a claims round that converges.
- Commits: the release commit, its claims-evidence child, and the post-publish record — `git log --oneline $(git describe --tags --abbrev=0)~1..` shows all three in order.
- Targeted verification: the release gate REFUSED twice before passing — first on four checks (harness stub, mirror drift, a `--json` flag against this repo's YAML-only contract, a validator-count pin), then on two (six uncovered changed lines, and a runtime budget this release's own scope widening had broken). Covering the changed lines found a live defect: `missing_paths` tested the matched substring for `://`, but the scheme is outside the match, so every external link in a disposition would have been reported as a missing file.
- Claims review: round 5 returned three blockers, ALL in the blocking scope — the exact inverse of the four rounds before it, every one of whose blockers was session narrative rather than shipped code. All three were false claims on shipped surfaces: a stale path count that understated the never-critiqued portion severalfold, "no existing artifact reddens on update" (false — `draft` is a shaping status and the hollow floor has no date grandfather), and "no consuming repo authors a claims record" (false — the release skill ships in the export). Nine advisory findings were reported; five are published in the record under SHIPPED KNOWN-INACCURATE.

## Context Sources

- The predecessor goal `charness-artifacts/goals/2026-08-22-proof-cost-portability-and-the-cadence-contract.md`, which produced slices C, B and A and could not publish them.
- `charness-artifacts/release-review/2026-08-16-v6.0.0-claims-review.md` — the same non-convergence at a previous release, stopped at three rounds with the holding "publishing on a fourth round would be reviewing until it passes".
- Issue #701, which this goal's first slice closes.

## Interview Decisions

- Decision: fix the convergence loop BEFORE publishing, not after. Rationale: four rounds of evidence that the other order does not terminate.
- Decision: split by scope rather than by reviewing less. A wrong blocker tally in a retro stays a reported defect; it just does not gate a tag, because a tag is a claim about shipped code.
- Decision: require a `pass` to carry what it waived. The obvious failure of a scope split is that it becomes a laundering channel, so the record must name each waived defect.

## Plan Critique Findings

No Before-phase plan critique: this goal was created at the predecessor's closeout and pursued directly. What stands in its place is two bounded fresh-eye rounds on slice 1 and a full claims round on slice 2, all three of which found blockers that changed the implementation rather than only the prose.

## Closeout Binding Plan

Shape these minimum fields before activation and keep them current. The field
check proves shape only; closeout workflows prove the values and identities:

- Reviewed inputs: name semantic goal/issue/quality inputs; retro, packet, reviewer, and lock records are terminal evidence.
- Frozen target: commit the semantic baseline, then bind the packet to that exact commit SHA.
- Fresh-eye: name a distinct reviewer and a different observer/evidence channel.
- Verification lock: name the lock command and evidence location; semantic input edits require rebinding.
- Complete flip: record packet/reviewer/lock evidence, then write terminal status/evidence bookkeeping outside the reviewed identity.

## Off-Goal Findings

- A non-ASCII filename in a release delta makes the release unpublishable: git quotes it, so the quoted form reads as `invented` and the plain form as `missing`. Not filed; recorded here.
- `charness-artifacts/issue/` (singular, extant) classifies blocking while `issues/` (plural) is advisory. Fail-closed, so it yields false blockers rather than escapes.
- The new test module's `sys.path.insert` has no cleanup.
- #612: the mutation harness has not RUN on `main` since at least 2026-08-17 — `Select mutation sample` times out. Measured locally: the sampler completes the standing suite in 197.6s and is still working past 420s. Candidate cause: #697, the shared coverage-report path.

## Final Verification

Retro: charness-artifacts/retro/2026-08-22-claims-convergence-and-ship-retro.md
Host log probe: skipped: host-log-not-exposed: this goal recorded no `Host metric window:` line, so `probe_host_logs.py --goal-path` has no scoped window to read. No turn, token or tool-call figure is claimed anywhere in this artifact or its retro.
Disposition review: charness-artifacts/release-review/2026-08-22-v6.3.0-round5-claims-review.md

## User Verification Instructions

The publication is real and checkable without trusting this artifact:

- `gh release view v6.3.0 --repo corca-ai/charness --json tagName,publishedAt,isDraft` — a channel other than tag state.
- `git ls-remote --tags origin v6.3.0` — the tag on the remote.
- `git show v6.3.0:packaging/charness.json` — the version as it exists at the tag.
- `grep -A 8 "Verdict scope" charness-artifacts/release/latest.md` — the five defects published KNOWN-INACCURATE rather than repaired.

## Auto-Retro

Retro dispositions: applied: the claims-review scope split (`skills/public/release/scripts/claims_review_scope.py`), which closes #701 and is what made the fifth claims round converge. applied: waived defects now reach the published record through `_scope_lines` instead of being validated and dropped. applied: the `://` guard in `scripts/artifact_referents.py` tested the matched substring, so it never fired — every external link in a disposition would have been reported as a missing file.
Structural follow-up: issue #612 (recurs: a verification surface that stops verifying and keeps reporting — the mutation harness has not run on `main` since 2026-08-17, and the failure reads as a step failure rather than as unmeasured coverage).
