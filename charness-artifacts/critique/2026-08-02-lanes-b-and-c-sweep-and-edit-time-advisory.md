# Lanes B and C sweep and edit-time advisory
Date: 2026-08-02

## Decision Under Review

Lane B: measure the "a rule that cannot fire where it was written to" class with a
predicate written down BEFORE the population was read, repair the unambiguous,
file the rest, and resolve #473. Lane C: give the duplicate-ratchet trap the same
edit-time affordance the length-headroom trap already has (#474).

## Failure Angles

- **The sweep's own counts are a verdict surface.** A count nobody can re-derive,
  or a denominator measured at the wrong moment, is the defect the sweep is
  measuring, applied to the sweep.
- **Surveyor claims taken at face value.** An agent asked to find inert rules
  will find them; without adversarial verification the artifact ships confident
  wrong findings.
- **The advisory reproducing the class.** An advisory that computes correctly and
  never reaches the agent is a rule that cannot fire where it was written.
- **A new floor by accident.** The advisory rides an edit-time hook; anything that
  raises or changes an exit code turns an allowed edit into a failure.

## Counterweight Pass

- **Adversarial verification earned its cost outright: it refuted 11 of 14
  `cannot-fire` claims.** Without it the sweep would have shipped ~14 findings of
  which 11 were wrong — a confident, checked-in, wrong measurement, which is worse
  than no measurement.
- The one confirmed finding was independently re-read by the parent before repair.
- #473 was NOT deleted. The predicate's own wording settled it: the situation the
  flag was written for is the grandfather LEAKING, not the current corpus, and in
  that situation it fires. Deleting a tripwire because its regression has not
  happened yet is the opposite error from the one this goal is about.
- Over-worry raised and NOT folded: making the dup advisory answer "is this file
  already in a duplicate family". The gate baseline stores fingerprints and member
  content hashes, not paths, so that needs a full rescan (~2.8s) on every edit.
  Scope is the cheap question and it is the one the issue actually asked.
- Over-worry raised and NOT folded: a threshold derived from the detector's
  24-token minimum. The reviewer was right that 30 added lines does not BOUND
  family creation, so the docstring and the reference now say that plainly rather
  than the threshold pretending to a precision it does not have.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/post_edit_skill_anchor_guard.py | action: fix | note: the advisory printed to stderr while the hook contract branches on exit 0 vs 2, so it computed correctly and was discarded - the class itself, freshly minted; moved to hookSpecificOutput.additionalContext on stdout
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/dup_ratchet_edit_advisory.py | action: fix | note: an absent dup_ratchet adapter section fell back to the default scope, so a consumer repo that never opted in would be advised, pointing at a command that may not exist there
- F3 | bin: act-before-ship | evidence: strong | ref: scripts/dup_ratchet_edit_advisory.py | action: fix | note: added lines are measured cumulatively versus HEAD, so every later edit to the same file re-emitted the whole advisory - observed live three times in this session; now once per file per HEAD
- F4 | bin: act-before-ship | evidence: moderate | ref: scripts/dup_ratchet_edit_advisory.py | action: fix | note: a py-only suffix filter was silent for the mjs and sh files the ratchet really scans, and this repo already carries two checked-in mjs duplicate families
- F5 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_dup_ratchet_edit_advisory.py | action: fix | note: the scope test used only non-source files so the suffix filter satisfied it and the root check was never exercised - deleting the root check left every test green
- F6 | bin: act-before-ship | evidence: strong | ref: scripts/validate_current_pointer_freshness.py | action: fix | note: validate_quality_runtime_signal_claims was registered as one of seven checks with a body of `_ = repo_root`, so a reader saw seven checks and six ran; deleted from the list
- F7 | bin: valid-but-defer | evidence: moderate | ref: skills/public/quality/references/dup-ratchet.md | action: document | note: the threshold correlates with family creation but does not bound it, and a small copy-paste still reaches the aggregate; stated in the reference rather than left implied
- F8 | bin: over-worry | evidence: weak | ref: scripts/dup_ratchet_edit_advisory.py | action: defer | note: membership-aware advising would need a full rescan per edit; scope is the cheap question the issue asked and the expensive one is not worth an edit-time budget
- F9 | bin: valid-but-defer | evidence: moderate | ref: charness-artifacts/quality/dup-review.json | action: defer | note: the eighth copy of the git-invocation idiom is classified intentional on blast-radius grounds rather than on non-extractability; the reviewer was right that the disposition-differs argument does not hold and the note says so

## Reviewer Tier Evidence

- Requested tier: high-leverage (an edit-time advisory that ships to consuming repos, plus a measurement artifact whose counts are claims).
- Requested spawn fields: typed `bounded-reviewer`, session-model inheritance (per-host contract; the Codex model/effort request does not apply on a Claude Code host).
- Host exposure state: host-defaulted
- Application state: n/a — this host exposes no per-subagent model/effort confirmation signal.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated — one bounded reviewer over Lane C (window `lane-c-round-1`, `reviewer_boundary_fingerprint.py verify` exit 0, `{"ok": true, "verdict": "clean", "drift": []}`, nothing parent-declared), plus 12 surveyor and adversarial-verifier agents over Lane B's population in a dynamic workflow. All findings received in the parent context.

Fresh-eye pass: scripts/dup_ratchet_edit_advisory.py — the bounded reviewer found the stderr-vs-stdout delivery defect (the advisory could not reach the agent it was written for), the absent-adapter fallback, the re-fire-on-every-edit behaviour, the `.py`-only scope gap, and a test that passed for the wrong reason. All repaired. Remaining accepted: the pathspec-glob edge and the 10s git timeout, recorded as F8-adjacent and not repaired this slice.
Fresh-eye pass: scripts/post_edit_skill_anchor_guard.py — same reviewer; the advisory is called before any anchor logic, returns None on every path, and cannot change the guard's exit code. Verified by reading and pinned by a test.
Fresh-eye pass: scripts/validate_current_pointer_freshness.py — the sweep's one confirmed finding, adversarially verified and then independently re-read by the parent before the repair.

Lane C's round 1 produced repairs, so a second round would ordinarily be owed. It is NOT claimed here: the round-2 obligation was discharged for Lane A (this goal's verdict-logic slice) and Lane C's surface is a non-blocking advisory that cannot change any exit code, pinned by a test. Round-1 repairs to Lane C are recorded as accepted-unreviewed.

## Reviewed Input Identity

<!-- No prepare packet was consumed; the reviewer received an inline bounded packet naming intent, changed files, design choices, invariants, non-claims, and out-of-scope lines. -->

## Boundary Ownership

- Producer: the duplicate ratchet's declared scope and the repo's rule population.
- Consumer: an agent mid-slice deciding whether to run the ratchet now, and a later reader of the sweep's counts.
- Owning surface: skills/public/quality/references/dup-ratchet.md for the advisory arm; charness-artifacts/audit/2026-08-02-can-this-rule-fire-sweep.md for the measurement.
- Verdict: owned-correctly
