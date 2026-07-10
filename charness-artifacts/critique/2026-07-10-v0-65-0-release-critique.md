# Fresh-Eye Release Critique — charness v0.65.0

Date: 2026-07-10
Release: v0.65.0 (minor bump from v0.64.0), publishing HEAD `7531144a`
Goal: `charness-artifacts/goals/2026-07-10-428-reviewer-boundary-enforcement-release.md`
Fresh-Eye Satisfaction: parent-delegated

## Reviewer Tier Evidence

- Requested tier: high-leverage (release closeout depth)
- Requested spawn fields: subagent_type=bounded-reviewer, model inherited
  from the parent session (no override)
- Host exposure state: host-defaulted
- Application state: not-confirmed — spawn accepted but the envelope's tool
  restriction did not bind mid-session (#430); reviewer read-only conduct
  proven by the rail-1 fingerprint (verify ok, drift empty at HEAD 7531144a)
  and a transcript tool-use audit, not self-report.

## Decision Under Review

Whether the v0.65.0 bundle (capture-script credentials fix + #428 two-rail
enforcement + critique artifacts) is safe to bump minor, tag, push, publish,
and carry the #428 close.

## Per-Lens Findings

1. Deployment confidence: no consumer-break risk; the bundle is purely
   additive and all three consumer-shipped files byte-match their
   `plugins/charness/` mirrors (independently diffed). Rail 2 is
   intentionally host-local and unpackaged.
2. Release hygiene: all version surfaces read 0.64.0 with `drift: []`;
   `bump_version.py` + the adapter sync command move packaging manifest,
   claude/codex manifests, and marketplace together. Remaining `0.64.0`
   strings are historical notes only.
3. Issue-close honesty: the #428 resolution critique's per-acceptance-line
   verdict is carried conservatively; the presence floor
   (`release_issue_closeout.py` → `issue_verify_closeout_body.py`) checks a
   verdict line exists, so the wording itself was operator-confirmed to carry
   the three non-claims (rail-2 binding unproven this session; no automated
   spawn-denial regression; line 5 scoped to the git-state class).
4. Rollback: clean; additive-only bundle, no migration, gitignored scratch
   orphans harmlessly; reverting reintroduces only the pre-existing CI
   baseline red.
5. Counterweight: unpackaged rail 2, `<repo-root>` prose paths in consumer
   installs, and absent Codex-host enforcement are tracked over-worry
   (#430/#431), not blockers.

## Verdict

- Verdict: RELEASE-OK — ship v0.65.0 with the confirm-at-boundary check on
  the #428 close-body wording (applied: the behavior-verdict line passed to
  the publish helper carries all three non-claims verbatim) and post-close
  readback via a distinct channel.

## Boundary Ownership

- Verdict: owned-correctly

The release surfaces under review (packaging manifest, generated plugin
manifests, marketplace) are producer-owned by `packaging/charness.json` plus
the sync helper, and the release delta was verified against the checked-in
mirrors; the one producer/consumer seam found (rail-1 spawn-step wiring in
consuming skills) was already escalated as
[#431](https://github.com/corca-ai/charness/issues/431) by the resolution
critique and is not a release-surface ownership defect.

## Non-Claims

- Commit-author placeholder (`hotl proof <hotl-proof@example.invalid>`) on 62
  existing commits is durable in pushed history; repo-local config was unset
  so the release commit carries the maintainer identity, and the structural
  fix is tracked as [#432](https://github.com/corca-ai/charness/issues/432).
- No claim that the mutation CI gate is green until its next scheduled run
  reads back on the pushed HEAD (#421 stays machine-owned).
