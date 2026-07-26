# v2 11 1 release critique
Date: 2026-07-26

## Decision Under Review

Publish charness 2.11.0 -> 2.11.1 carrying two commits: the xdist per-test scheduling
fix (`--maxschedchunk 1` in the standing pytest runner, 45.5s -> 26.9s on the standing
gate) and the re-derived `local-linux-x86_64-36cpu` runtime bars that speedup
invalidated, plus the suppression-warning fix this critique produced.

## Failure Angles

- **Bump level inflation by precedent misuse.** The slice was first planned as MINOR on
  the strength of `docs/handoff.md`'s "a new exported flag plus module sets a MINOR
  bump — three releases running". Citing a precedent for a strictly weaker case is how
  a bump ratchet drifts, and this repo already has a critique dedicated to that class.
- **Shipping a blocking gate tightening to machines that never recorded a sample.** The
  runtime profile id is machine-CLASS (`local-{system}-{machine}-{cpu}cpu`), not
  machine identity, so any linux/x86_64 box with 36 usable CPUs inherits these bars.
- **A bar coupled to a flag that can be suppressed silently.** If `--maxschedchunk 1`
  stops applying, the gate returns to the regime the bars were just tightened out of.
- **Undocumented operator knob.** A new env var with no doc surface is only defensible
  if the bump level does not claim it as operator-facing capability.
- **Overclaim leakage from the slice critique into the release record.**

## Counterweight Pass

- The cross-machine narrowing (F-B) is a narrowing of an already-accepted design, not a
  new defect: profile-by-class predates this slice, and enforcement is median-of-20, so
  a single slow machine-run cannot block anyone. Ship with disclosure, do not redesign
  profile identity in a release slice.
- The ini-`addopts` override gap is real but has no proven consumer: nothing in
  `skills/public/**` executes the plugin's copy of the runner, and a downstream repo
  that copied the runner owns its copy, which a plugin refresh does not overwrite. Note
  it; do not hold the release for it.
- The undocumented env var is CONSISTENT with the pre-existing `CHARNESS_PYTEST_WORKERS`
  (neither appears under `docs/`). Consistency is the right call at patch level; it
  would have been self-contradictory at minor.
- Neither of the two publish-blockers was a design flaw — both were a stale claim and a
  missing signal, each one edit.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: .agents/quality-adapter.yaml:262 | action: fix | note: `run-quality-full: 62000` sits BELOW the 67172ms pre-flag median this same file records, and `choose_sched_chunk` suppressed the flag on three paths without a word — two of them involuntary (xdist < 3.2, an unrelated PYTEST_ADDOPTS tuning). A blocking red with nothing regressed and no pointer to the cause. Fixed: the chooser now returns a suppression reason and the runner prints it to stderr.
- F2 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_standing_pytest_runner.py:207 | action: fix | note: the slice corrected the round-robin claim in production but left it standing verbatim in a test docstring one file over — a known-false statement shipping in the release. Fixed.
- F3 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/critique/2026-07-26-xdist-scheduler-chunking-and-the-budget-bars-it-invalidated.md | action: fix | note: that artifact claimed the bar windows were "turned over to convergence"; true for `pytest` (20/20), false for both aggregates (13/20). Fixed by actually converging them to 20/20 and re-verifying every bar against the full window, then correcting the claim.
- F4 | bin: act-before-ship | evidence: strong | ref: docs/handoff.md:26 | action: fix | note: bump level. The cited MINOR precedent covered a new public MODULE plus a new CLI FLAG on an exported public-skill gate script; this slice has neither. `CHARNESS_PYTEST_SCHED_CHUNK` is an env var on a repo-root dev-gate runner — not under `skills/public/`, not a `charness` subcommand, absent from `.agents/command-docs.yaml` and `docs/generated/cli-reference.md`. `version-policy.md` "runtime corrections that preserve the same public shape" fits directly. Bump set to PATCH (2.11.1), and the handoff pointer is being reworded so the precedent is not re-applied to env vars.
- F5 | bin: bundle-anyway | evidence: moderate | ref: .agents/quality-adapter.yaml:186 | action: document | note: the profile id is machine-CLASS, so a second, slower 36-CPU linux/x86_64 box inherits bars now at 1.41-1.71x rather than the previous ~2x headroom. Median-of-20 enforcement means it takes sustained slow runs, not one. Disclosed in the release notes and handoff so that red is diagnosable in seconds.
- F6 | bin: valid-but-defer | evidence: moderate | ref: scripts/run_standing_pytest.py:254 | action: document | note: the deference covers `PYTEST_ADDOPTS` only; a downstream ini `addopts = --maxschedchunk N` is silently overridden. No proven consumer executes the plugin's copy of this runner, so this is a note for downstream adopters, not a publish blocker.
- F7 | bin: valid-but-defer | evidence: moderate | ref: tests/quality_gates/support.py:472 | action: defer | note: `seeded_quality_runner_repo` is module-scoped and not seed-cache-backed, so scattering rebuilds it per worker. The measured win is already net of this; seed-cache-backing it is the next speed slice.
- F8 | bin: over-worry | evidence: moderate | ref: .agents/quality-adapter.yaml:139 | action: defer | note: the `default`, 4cpu, and aarch64 profiles are untouched and now looser relative to reality — failing in the tolerable direction. The 4cpu profile also recorded a single much faster run (95694 vs a 126302 median) inside `run-quality`, which is a re-derive owed on evidence, not a risk.
- F9 | bin: over-worry | evidence: weak | ref: docs/handoff.md:37 | action: fix | note: the handoff's "unrestricted pytest is still 51.4s of a 54.4s run" is now false and it is the post-publish baton. Corrected during closeout rather than treated as a release blocker.

## Reviewer Tier Evidence

- Requested tier: `bounded-reviewer` (repo-typed read-only fresh-eye reviewer, Read/Grep/Glob only), scoped to release-specific angles: bump level, installed-user exposure, blocking-bar safety across profiles, release-readiness gaps, and overclaim audit of the slice critique.
- Requested spawn fields: `subagent_type: bounded-reviewer`, release-critique prompt naming the candidate commit and the surfaces to read, session-model inheritance per the Claude Code branch of the per-host subagent contract.
- Host exposure state: applied
- Application state: host-confirmed: spawn accepted and findings returned; `reviewer_boundary_fingerprint.py verify` reported `{"ok": true, "drift": []}` against the pre-review snapshot at `f4368f57`.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

`parent-delegated`

## Reviewed Input Identity

<!-- Packet-bound critiques replace this comment with three bullets copied from prepare_packet.py after the reviewed packet is final: Packet path, exact Packet SHA256, and Identity SHA256. Leave this section comment-only when no packet was consumed. -->

## Boundary Ownership

- Producer: the release slice — `scripts/run_standing_pytest.py` for behavior, `.agents/quality-adapter.yaml` for the bars it invalidated.
- Consumer: maintainers running `scripts/run-quality.sh` on any profile matching `local-linux-x86_64-36cpu`, and downstream repos that copied the runner.
- Owning surface: `.agents/release-adapter.yaml` for the bump and notes; the quality adapter for the bars; the handoff for the stale speed claim.
- Verdict: owned-correctly
