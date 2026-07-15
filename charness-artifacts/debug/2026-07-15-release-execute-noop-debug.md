# Release Execute Noop Debug
Date: 2026-07-15

## Problem

`publish_release.py --execute` changed local release surfaces for v1.0.10 but
returned with no output, no release commit, no tag, and no GitHub release.

## Correct Behavior

Given a clean, release-ready v1.0.9 checkout, when the v1.0.10 publish command
is executed, then it must either create and report its release commit/tag/public
release or return a nonzero diagnostic without leaving an ambiguous mutation.

## Observed Facts

- The execute command's nested non-PTY process ended with empty captured output.
- It changed manifests and release/retro artifacts but `HEAD` remained
  `dcae80ae`; `gh release view v1.0.10` reported `release not found`.
- The v1.0.10 tag did not point at `HEAD`.
- Two direct `run-quality --release` reproductions stopped after the first
  phase at the configured outer execution window and never reached the shell's
  trailing exit-marker command.

## Reproduction

- Run `python3 skills/public/release/scripts/publish_release.py --repo-root . --part patch --critique-artifact charness-artifacts/critique/2026-07-15-compact-yaml-response-release-critique.md --execute` from the clean release-ready commit.

## Candidate Causes

- The execute wrapper may return after preparing release files instead of
  entering the commit/tag/publication phase.
- A child phase may fail while its status is discarded by the wrapper.
- The release command may have entered a resumable intermediate state whose
  resume protocol is required but not reported to the caller.

## Hypothesis

- The nested non-PTY command lifetime is bounded by the outer execution window,
  so it is killed during the release quality phase before the helper can commit;
  disconfirmer: run the same long command through a persistent PTY session and
  observe its final exit marker.

## Verification

- result: confirmed — the repeated quality command stopped at the outer window
  without its final marker, while the release source has no early return after
  the quality call; the interrupted state is explained by command transport,
  not a release-helper decision.

## Root Cause

The non-PTY nested command was canceled by the outer execution window during a
long-running quality gate. The release helper therefore never reached its
commit, tag, or publication phases.

## Invariant Proof

- Invariant: an `--execute` caller receives an unambiguous publication outcome.
- Producer Proof: `publish_release_execute.py` proceeds from quality directly
  to `git add` and commit; no source return exists at the observed boundary.
- Final-Consumer Proof: `git tag` and GitHub release lookup both remain absent.
- Interface-Shape Sibling Scan: `publish_release.py` and `publish_release_execute.py` must carry the same success/failure state.
- Non-Claims: no claim is made that publication was attempted or that its remote side effects succeeded.

## Detection Gap

- command transport | a long non-PTY nested call can be canceled before its
  final result reaches the caller | use a persistent PTY and poll it for
  publish, quality, and other long-running irreversible operations.

## Sibling Search

- Mental model: a yielded nested execution remains alive until its process exits.
- transport axis: `functions.exec` nested command | decision: use PTY for long work | proof: confirmed by missing final marker at the outer window.
- release axis: `publish_release_execute.py` | decision: no code change | proof: confirmed control flow reaches commit after quality.
- cross-file: skills/public/release/scripts/publish_release_execute.py is the paired phase consumer.

## Seam Risk

- Interrupt ID: release-execute-noop
- Risk Class: operator-visible-recovery
- Seam: local release mutation to public tag and GitHub release.
- Disproving Observation: a persistent PTY command also stops before its final exit marker.
- What Local Reasoning Cannot Prove: GitHub visibility until the release backend is queried after a successful publication.
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: resolved
- Critique Required: no
- Next Step: impl
- Handoff Artifact: none

## Prevention

Run the recovery and final publication through a persistent PTY session; never
treat a yielded non-PTY nested command as a completed long-running release.
