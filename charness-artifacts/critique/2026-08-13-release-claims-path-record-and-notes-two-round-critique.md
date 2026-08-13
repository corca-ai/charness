# Release Claims Path, Record, and Notes Preflight Two-Round Critique

Date: 2026-08-13

## Decision Under Review

Resolve the three release residues filed by the previous session's round-2 reviews
(#613, #610, #611) rather than leaving them as recorded non-implementations, and
promote the retro's `skipped-is-not-passed` lesson to a contract.

All three change verdict logic on a proof surface: #613 changes which file the
claims-review floor reads and when it refuses, #611 adds a refusal to the only lane
that publishes, and #610 changes what the published release record asserts about a
release. Each therefore owed two bounded review rounds.

## Failure Angles

- A floor that resolves its subject differently from the writer that produced it,
  so the two name different files and nothing notices.
- Deleting a mitigation without replacing the property it was accidentally
  providing.
- A gate placed where firing it creates the state it then refuses.
- A record section that reports an absence as a presence, or that lets one
  operator-authored field answer a question it is not evidence for.
- A test that passes for the wrong reason, pinning a repair that is not there.

## Round 1

Three bounded reviewers, one per issue, distinct lenses (path-resolution blast
radius, record-binding integrity, gate placement and lane coverage). Boundary
window `causal-round1-610-611-613`, `verify` returned
`{"ok": true, "verdict": "clean", "drift": []}` with empty `parent_declared`,
run before any parent write. Delivery state: `findings-received` for all three.

Round 1 read the pre-repair surfaces, because for a bug-class resolution the
causal review runs before design. It changed the design of all three fixes:

- **#613 — the replacement refusal was missing from my plan.** I intended to
  thread `output_dir` and delete `assert_record_path_matches_adapter`. Deleting it
  with nothing in its place converts every derivation failure — absolute, `..`,
  empty, separator-mismatched, typo'd, and changed-since-prepare — back into a
  silent marker miss and an unreviewed publish. The old value comparison was
  catching the last of those only by accident, and the trigger set after threading
  is *larger* than "non-default `output_dir`". The design gained
  `assert_record_readable`, a positive check.
- **#613 — two path pins I had not listed.** `prepared_record`'s returned `path`
  is what `validate_claims_review` binds `release_record_path` against, so
  threading the three reads and leaving that one a constant yields a floor that
  reads the right file and demands the record name the wrong one. And
  `publish_release_resume_publish.py`'s `artifact` literal survives into the
  post-publish commit on the claims lane specifically — where `git diff --quiet`
  over a pathspec matching nothing exits 0, so that commit is skipped **silently**.
  Both verified directly: `git show HEAD:a//b` exits 128, and
  `git diff --quiet -- <nonmatching>` exits 0.
- **#610 — an injection vector I had not considered.** `observer_distinctness.signal`
  is the floor's only operator-authored free text (`verdict` and `kind` are closed
  enums, both paths go through `_review_relative_path`), and the design renders it
  verbatim into a document other gates parse. A newline yields a
  `- target version: X` line that makes `validate_current_pointer_freshness.py`
  refuse every post-publication push, or the prepared-stop marker, which
  permanently reclassifies a finished release as an outstanding stop. Both fire
  after the tag and release are public.
- **#610 — placement.** The narrative audit terminates the `## Release State`
  ledger at the first following `## ` heading and then requires all five of its
  entries, so a `## Claims Review` heading inserted above `## Public Release
  Verification` blocks release *preparation* with four "missing required entry"
  blockers. The section moved below `review_proof_lines`.
- **#611 — the `release_exists` guard.** Without it the preflight refuses a
  push-leg repair that cannot attach a body at all, which is a wrong stop on a
  legitimate recovery.
- **#611 — the `--close-issue` half is not enforceable here**, confirmed against
  the prepared record, the release commit message, the claims schema, the planner
  packet, and the artifact tree. Recorded rather than papered over.

## Round 2

Three bounded reviewers reading the REPAIRED surfaces whole. Boundary window
`round2-610-611-613`, `verify` returned
`{"ok": true, "verdict": "clean", "drift": []}` with empty `parent_declared`, run
before any parent write. Delivery state: `findings-received` for all three.

Round 2 found a defect inside a round-1 repair on every one of the three surfaces.

- **The gate created the state it then refuses.** The second `_notes_preflight`
  sat *after* `commit_artifact_before_push`. In exactly the scenario that call
  exists for — the pre-push gates leaving a drafted-notes file in the tree — the
  commit sweeps that file into a third commit on top of the claims evidence, and
  *then* the preflight refuses. The next resume can identify no single-parent
  prepared boundary and refuses with recovery text advising a reset past the
  committed claims record. Moved above the commit.
- **Refusing the marker alone left the same shape in three more places.** The
  signal could still carry `carrier-pending-state-verification`,
  `Issue closeout verification:`, or a `charness-artifacts/probe/` observer path —
  each a bare substring test in `publish_release_resume_closeout.py`'s
  carrier/final identity checks, each satisfiable on one line under the byte cap.
  Replaced the single-marker check with `RECORD_SENTINELS`, one owner for the rule.
- **The strip reintroduced the class it was added against.** `release_record_path`
  stripped `output_dir`; the writer and `publish_release_resume_closeout.py` do
  not. Normalization applied on one side only is precisely how two derivations come
  to name different files. Strip removed; `""` now derives `latest.md`, matching
  the writer, instead of refusing an adapter that had declared a root — which had
  made such a prepared stop unresumable by either route.
- **`git add` aborts on a pathspec matching nothing.** The widened
  `["charness-artifacts", <record dir>]` pathspec would kill a consumer's
  non-claims resume mid-lane. Verified: `git status` tolerates it (rc 0),
  `git add` exits 128, and `cli.run` is `check=True`. Each candidate is now
  statused separately and only matching ones are added. Also `output_dir: .`
  produced a `.` directory that was dropped entirely, so the root record was never
  swept; the record file is the scope there.
- **`flatten_signal` had zero production callers.** The renderer inlined the rule
  while the claims module held an orphan copy — worse than a duplicate, and the
  test that looked like the flattening proof exercised the orphan. Ownership moved
  to the renderer.
- **A test assertion passed with the repair reverted.** Counting
  `- Recorded signal:` lines does not discriminate: an injected remainder lands on
  its own line carrying no such prefix, so the count stays 1. Replaced with a
  structural assertion that every emitted line is blank, a heading, or a bullet.
- **`RESUME_REMEDY` was appended to blockers it does not fit**, including a
  mistyped `--notes-file` path (no candidate was printed to re-pass) and a
  mutable-pointer blocker whose only remedy *is* the worktree change the remedy
  says is unnecessary. Now scoped to the drafted-notes blocker, and its quoted
  terminal message corrected — on the claims lane the marker refusal fires, not
  `nothing to resume`.
- **A second derivation survived** at `publish_release_resume_closeout.py`, using
  platform-flavoured `Path` where `git diff-tree` emits forward slashes. Replaced
  with the classified `state["record_path"]`.
- **`## Claims Review` could render the literal `None`** on the `pass` branch,
  and the guard's test covered only the `unproven` branch.

Round-2 repairs ship **accepted-unreviewed**, per the two-round cap.

## Counterweight Pass

Three round-2 findings were declined as out of scope for this slice, recorded
rather than silently dropped:

- **The legacy marker-free lane is still fail-open** when the record is readable
  but carries no marker. Pre-existing, and closing it means refusing a documented
  recovery lane — a contract change that does not belong in an unreviewed round-2
  repair. The written non-claim now sits where a reader will meet it.
- **`check_requested_review_gate.py`'s adapter-declared unavailability patterns**
  are matchable by an *innocent* `unproven` signal ("independent review unavailable
  on this host"). Not reachable through either production lane — the prepare
  rewrites the record before the gate, and the claims lane skips the write — but
  the ordering that saves it is incidental, and the patterns are adapter-owned so
  a sentinel list cannot cover them.
- **The notes preflight keys on a filename convention** its own helper admits it
  cannot see through: a draft with no `notes` token, or one outside `output_dir`,
  is invisible. The class is narrowed, not closed. Closing it means recording
  `notes_mode` in the prepared record — the same missing-durable-record shape as
  the `--close-issue` half.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/publish_release_resume_publish.py:143 | action: fix | note: the second notes preflight sat after the artifact commit, so a firing gate created the third commit that strands the next resume; moved above the commit
- F2 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/publish_release_claims_review.py:29 | action: fix | note: refusing only the prepared marker in the signal left three more record sentinels satisfiable on one line; replaced with RECORD_SENTINELS as the single owner
- F3 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/publish_release_claims_review.py:136 | action: fix | note: stripping output_dir on the floor side only recreated the two-derivations class the slice exists to close; strip removed and blank now derives the repo root as the writer does
- F4 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/publish_release_resume.py:51 | action: fix | note: git add exits 128 on a pathspec matching nothing (verified), so the widened pathspec would kill a consumer's non-claims resume; candidates are statused separately now
- F5 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/publish_release_artifact.py:121 | action: fix | note: a Claims Review heading above the Release State ledger truncates it and blocks release preparation with four missing-entry blockers; placed below review_proof_lines
- F6 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/publish_release_claims_review.py:222 | action: fix | note: deleting the output_dir refusal with nothing in its place turns every derivation failure back into a silent marker miss; replaced by the positive assert_record_readable
- F7 | bin: act-before-ship | evidence: moderate | ref: skills/public/release/scripts/publish_release_resume_closeout.py:165 | action: fix | note: a surviving platform-flavoured second derivation; replaced with the classified state record_path
- F8 | bin: act-before-ship | evidence: moderate | ref: skills/public/release/scripts/publish_release_narrative_gate.py:114 | action: fix | note: RESUME_REMEDY was appended to blockers whose real remedy is a worktree change; scoped to the drafted-notes blocker
- F9 | bin: bundle-anyway | evidence: moderate | ref: tests/quality_gates/test_release_claims_review.py:646 | action: fix | note: the assertion presented as the flattening proof passed with flattening reverted; replaced with a structural line-shape assertion
- F10 | bin: bundle-anyway | evidence: moderate | ref: skills/public/release/scripts/publish_release_artifact_sections.py:54 | action: fix | note: flatten_signal had no production caller while the renderer inlined the rule; ownership moved to the renderer
- F11 | bin: valid-but-defer | evidence: strong | ref: skills/public/release/scripts/publish_release_resume.py:241 | action: document | note: the legacy marker-free lane stays fail-open when the record is readable but unmarked; closing it changes a documented recovery contract and does not belong in an unreviewed round-2 repair
- F12 | bin: valid-but-defer | evidence: moderate | ref: skills/public/release/scripts/check_requested_review_gate.py:73 | action: defer | note: adapter-declared unavailability patterns are matchable by an innocent unproven signal, but unreachable through both production lanes and adapter-owned, so no sentinel list can cover it
- F13 | bin: valid-but-defer | evidence: strong | ref: skills/public/release/scripts/drafted_release_notes.py:53 | action: document | note: the notes preflight keys on a filename convention it cannot see through, so the class is narrowed not closed; closing it needs notes_mode recorded in the prepared record
- F14 | bin: over-worry | evidence: contested | ref: skills/public/release/scripts/publish_release_resume_publish.py:23 | action: document | note: _assert_one_record_path is a tautology on every live path today; kept deliberately as the guard for the second-caller hazard the module already documents

## Non-Claims

- No release was published, no tag created, and nothing pushed by this slice.
- The claims-lane behaviour is proven by the repo's own fixture topology and
  in-process unit tests, not by a real consumer repo with a non-default
  `output_dir`. No such deployment was observed.
- Round 2's Windows-separator finding is reasoned from `pathlib` flavour
  semantics; no Windows host ran any of this.
- The `--close-issue` half of #611 remains unenforced on the
  `prepared-claims-review` lane. The post-publication lane does refuse its
  omission; this one has nothing durable to compare against.

## Reviewer Tier Evidence

- Requested tier: high-leverage — proof-surface verdict logic at a publication boundary.
- Requested spawn fields: none — this host's typed `bounded-reviewer` agent was used with no per-spawn model, reasoning-effort, or service-tier override.
- Host exposure state: host-defaulted
- Application state: n/a — with no fields sent, no tier application is claimed.
- Delivery state: findings-received

Envelope rail 2 is **unproven** on this host: each reviewer reported Read/Grep/Glob
as its only tools, which is reviewer self-report, not a recorded denial signal.
Rail 1 carried the enforcement — both windows
(`causal-round1-610-611-613`, `round2-610-611-613`) verified
`{"ok": true, "verdict": "clean", "drift": []}` at exit 0 with empty
`parent_declared`, each run at the moment the reviewers returned and before any
parent write.

## Fresh-Eye Satisfaction

parent-delegated — six bounded reviewers across two rounds, all spawned unnamed as
one-shot subagents, all returning findings text into the parent's own context.

## Reviewed Input Identity

<!-- No packet was consumed: the reviewed inputs were the live worktree surfaces named per reviewer, read whole, plus the three GitHub issue bodies re-read through the issue backend. -->

## Boundary Ownership

- Producer: the release adapter's `output_dir`, which the artifact writer has always honoured.
- Consumer: the claims-review floor, the run planner, the resume publish tail, and the post-publication closeout recovery.
- Owning surface: `skills/public/release` — the release skill's adapter contract.
- Verdict: owned-correctly

The producer/consumer question this slice turns on is *who owns the release
record's path*. The adapter produced that fact; the claims floor and the planner
each held a private constant instead of consuming it, which is the ownership
violation the three issues describe from three directions. The repair moves every
consumer onto the producer's value — one derivation in `release_record_path` —
rather than adding a reconciliation between copies.

Two boundaries were deliberately NOT moved, recorded above under Counterweight:
`REVIEW_ROOT` stays floor-owned (it has no adapter key, and deriving it would make
already-committed claims records unreadable), and
`validate_current_pointer_freshness.py` stays authoring-repo-pinned (it hard-
requires this repo's own manifests and cannot run in a consumer).
