---
name: release
description: "Use when a maintainer needs to cut, bump, or verify a repo release surface such as plugin versions, generated install manifests, and operator update instructions."
---

# Release

Use this when the task is to advance or verify a repo-owned release surface,
not just to describe recent changes.

`release` is the maintainer-facing workflow for versioned plugin or package
surfaces that ship checked-in install metadata. It keeps release contracts
honest instead of improvising bumps, update advice, or generated-file edits.
Every task-completing release slice records critique before closeout. Routine
hygiene may use a short scoped critique; compatibility, install/update,
deletion, host-proof, or public visibility decisions use standalone `critique`.

## Bootstrap

Resolve `$SKILL_DIR` per `../../shared/references/bootstrap-resolution.md`, then resolve the adapter first.

```bash
python3 "$SKILL_DIR/scripts/resolve_adapter.py" --repo-root .
```

Default durable artifact: `<repo-root>/charness-artifacts/release/latest.md`.

If the repo has no checked-in release adapter yet, scaffold one:

```bash
python3 "$SKILL_DIR/scripts/init_adapter.py" --repo-root .
```

If the adapter is missing, stop after shaping or scaffolding the release
contract. Do not mutate versions, tags, or publish state in earnest until the
repo has declared its release boundary and proof expectations.

Then inspect current release state:

```bash
python3 "$SKILL_DIR/scripts/current_release.py" --repo-root .
python3 "$SKILL_DIR/scripts/check_fresh_checkout_probes.py" --repo-root . --json
python3 "$SKILL_DIR/scripts/check_fresh_checkout_probes.py" --repo-root . --run-probes --json
python3 "$SKILL_DIR/scripts/check_real_host_proof.py" --repo-root .
python3 "$SKILL_DIR/scripts/check_requested_review_gate.py" --repo-root .
python3 "$SKILL_DIR/../../../scripts/check_cli_skill_surface.py" --repo-root . --adapter-path .agents/release-adapter.yaml --json 2>/dev/null || true
git status --short
git log --oneline -5
sed -n '1,220p' <resolved-release-artifact> 2>/dev/null || true
```

When the repo treats version bumps and published releases as one coupled
maintainer action, prefer the repo-owned publish helper instead of stopping at
push-only state:

```bash
python3 "$SKILL_DIR/scripts/publish_release.py" --repo-root . --part patch --execute
```

If tag push only starts a later release workflow, treat the helper closeout as
local publish state until the workflow and public release surface are actually
verified.

## Workflow

1. Restate the release goal.
   - check only
   - patch or minor maintenance release
   - explicit target version
2. Read the current release surface before mutating it.
   - canonical package version
   - generated plugin manifest versions
   - generated compatibility metadata version
   - dirty or drifted working tree state
3. Run or record the required critique before release mutation.
   - every task-completing release slice records critique before closeout; scale the pass instead of asking whether it is needed
   - record `Critique: short <scope>` for routine release hygiene focused on version drift, generated surfaces, publish boundary, and operator risk
   - record `Critique: full <artifact-or-subagent-status>` after standalone `critique` when compatibility, install/update, deletion, host-proof, or public visibility could be misread
   - use `Critique: not-applicable <reason>` only for inspect/status/routing-only release requests that do not mutate or close repo work
   - if required critique is blocked because the host cannot provide subagents,
     first apply `../../shared/references/fresh-eye-subagent-review.md` (it owns the blocked-vs-available determination and the reviewer tier), then record `Critique: blocked <host-signal>` instead of continuing
4. Choose the lightest honest bump.
   - patch for bug fixes, copy fixes, and behavior repairs
   - minor for new maintained capability or additive operator surface
   - major only when compatibility or invocation expectations break
5. Apply the release mutation through the repo helper.
   - prefer the checked-in bump helper over manual JSON edits
   - if the repo couples version+push+tag+GitHub release, prefer one checked-in
     publish helper that closes all four in order
   - if the helper only starts a later workflow publish step, record that boundary
     honestly instead of calling the release finished at tag push
   - sync generated install surfaces immediately after bumping
   - refresh the committed `latest.md` to document the target tag before push, or
     make generated release notes self-contained so stale records cannot mislead
   - keep release work phase-ordered: mutate, then sync generated surfaces,
     then verify, then push/tag/publish
6. Verify the local release surface.
   - packaging and generated files agree on the same version
   - canonical quality gate passes
   - no generated install surface was left stale
   - distinguish local/tag success from later workflow or public verification
   - if `check_real_host_proof.py` says release-time proof is required, carry
     that checklist into the closeout instead of claiming local CI replaced it
   - if `fresh_checkout_probes` are declared, run them before tag publish and
     report status; if none are declared, say no fresh-checkout proof was configured
   - if `check_requested_review_gate.py` reports review unavailability, fix the
     gate, select a correct adapter, or record an explicit waiver before publish/tag
   - if CLI, bundled-skill, launcher, or install seams moved, run the declared
     surface checks and report startup proof when applicable
   - run `audit_public_release_narrative.py` so the committed `latest.md` names the
     target tag with expected sections/ledger, and rejects a `--notes-file` at a mutable source-tree record
7. Close the public release boundary.
   - distinguish `local/tag state complete`, `workflow publication complete`,
     and `public release surface verified`
   - if a repo has tag-triggered or otherwise async publication, do not treat
     helper success or tag push alone as publish completion
   - if the repo has no repo-owned public verifier yet, leave the release explicitly open at that boundary
   - render closeout only from the verified release ledger (tag, version, URL) per
     `closeout-discipline.md`; once the target is named, surface `target_unavailable` instead of silently retargeting
   - when the release resolves GitHub issues, pass `--close-issue <number>` so the
     helper preflights `gh issue view`, writes close keywords, and verifies/falls back to manual close
8. End with update steps, then refresh the maintainer's own install.
   - how operators refresh the managed install, what hosts still need after
     update, and what still requires manual human confirmation
   - when the adapter declares `post_publish_install_refresh`, the publish helper
     AUTO-RUNS it after a verified publish so the installed surface ends
     `== repo` (recorded as `install_refresh`); do NOT downgrade it to a manual
     `charness update` ask (detail: `references/install-surface.md`)

## Output Shape

The result should usually include:

- `Current Version`
- `Target Version`
- `Release Scope`
- `Critique`
- `Verification`
- `Release State`
- `Public Release Verification`
- `User Update Steps`
- `Maintainer Install Refresh` (the auto-run `install_refresh` result) when declared
- `Real-Host Proof` when the adapter says a human-run smoke is required
- `Startup Proof` when startup-probe surfaces moved
- `Open Risks`

## Guardrails

- Do not hand-edit generated plugin manifests when the repo has a sync helper.
- Do not bump a version without stating why that bump level is justified.
- Do not push, tag, or announce a release without explicit user confirmation.
- Do not report a release-linked issue as resolved until GitHub verifies it closed via close-keyword carrier or manual fallback.
- Do not use `--close-issue` unless target issues are reachable through authenticated `gh`; fail before release mutation when they are not.
- Do not leave a repo that treats version bumps as published releases stuck in a
  push-only state; encode that boundary in one repo-owned publish helper.
- Do not treat `tag pushed`, publish-helper success, workflow completion, and
  `public release surface verified` as interchangeable states.
- Do not point public release notes at mutable source-tree records (such as
  `charness-artifacts/release/latest.md` at the target tag URL); generate
  self-contained notes or audit the file before passing `--notes-file`.
- The publish helper's only installed-host mutation is the adapter-declared
  `post_publish_install_refresh`, auto-run on the authoring machine after a
  verified publish (opt-in, recorded, non-blocking); do not auto-mutate other
  host caches or downgrade it to a manual ask.
- Do not turn host-specific human proof into fake standing CI. If a support or
  install surface still depends on PATH, package managers, or host cache
  state, say so explicitly and carry a short checklist.
- Do not call eventual-consistency delay flaky publication noise when the repo
  still owes bounded retry/backoff or a public visibility check.
- Do not run sync, export, bump, install/update, or git-mutation commands in
  parallel with validators. Use parallelism only for read-only inspection.
- Do not skip critique for task-completing release work. Use the standalone
  `critique` pass when a release changes compatibility, install/update flow,
  public visibility, or host-proof expectations in a way the next maintainer
  could misread.
- Do not call a same-agent review a critique.
- If the required critique is blocked, stop instead of downgrading to a local
  substitute and still calling the release reviewed.
- Do not downgrade a user-requested review gate failure into a release caveat.
  A release record that says review was unavailable needs a fix, an explicitly
  selected working adapter, or an explicit review waiver before publish/tag.
- If the repo lacks the declared release files or sync script, stop cleanly and
  name the missing seam instead of inventing one.

## References

- `references/adapter-contract.md`
- `references/version-policy.md`
- `references/install-surface.md`
- `references/closeout-critique-gate.md`
- `../../shared/references/closeout-discipline.md`
- `../../shared/references/fresh-eye-subagent-review.md`
- `<repo-root>/scripts/current_release.py`
- `<repo-root>/scripts/check_real_host_proof.py`
- `<repo-root>/scripts/check_requested_review_gate.py`
- `<repo-root>/scripts/bump_version.py`
- `<repo-root>/scripts/publish_release.py`
