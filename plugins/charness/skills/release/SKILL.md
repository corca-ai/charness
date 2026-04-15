---
name: release
description: "Use when a maintainer needs to cut, bump, or verify a repo release surface such as plugin versions, generated install manifests, and operator update instructions."
---

# Release

Use this when the task is to advance or verify a repo-owned release surface,
not just to describe recent changes.

`release` is the maintainer-facing workflow for versioned plugin or package
surfaces that ship checked-in install metadata. It should keep one repo's
release contract honest instead of improvising version bumps, CLI update
advice, or generated-file edits by hand.
When the release decision is non-trivial, use the standalone `premortem`
skill before mutating versions so compatibility, install/update fallout, and
real-host proof requirements are triaged explicitly.
Routine release hygiene does not need a standalone session when the release
caller can do a short bounded local premortem honestly.

## Bootstrap

Resolve the adapter first.

```bash
python3 "$SKILL_DIR/scripts/resolve_adapter.py" --repo-root .
```

Default durable artifact:

- `charness-artifacts/release/latest.md`

If the repo has no checked-in release adapter yet, scaffold one:

```bash
python3 "$SKILL_DIR/scripts/init_adapter.py" --repo-root .
```

Then inspect current release state:

```bash
python3 "$SKILL_DIR/scripts/current_release.py" --repo-root .
python3 "$SKILL_DIR/scripts/check_real_host_proof.py" --repo-root .
git status --short
git log --oneline -5
sed -n '1,220p' <resolved-release-artifact> 2>/dev/null || true
```

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
3. Run a bounded premortem on non-trivial release decisions.
   - use the standalone `premortem` skill when compatibility expectations,
     install/update instructions, deletions, or real-host proof boundaries
     could be misread
   - carry back `Act Before Ship`, `Bundle Anyway`, `Over-Worry`, and
     `Valid but Defer` into the release plan instead of keeping them as chat
     debris
4. Choose the lightest honest bump.
   - patch for bug fixes, copy fixes, and behavior repairs
   - minor for new maintained capability or additive operator surface
   - major only when compatibility or invocation expectations break
5. Apply the release mutation through the repo helper.
   - prefer the checked-in bump helper over manual JSON edits
   - sync generated install surfaces immediately after bumping
6. Verify the release surface.
   - packaging and generated files agree on the same version
   - canonical quality gate passes
   - no generated install surface was left stale
   - if `check_real_host_proof.py` says release-time proof is required, carry
     that checklist into the closeout instead of claiming local CI replaced it
7. End with operator-facing update steps.
   - how operators refresh the managed `charness` install
   - what Claude and Codex still need after `charness update`
   - what still requires manual human confirmation

## Output Shape

The result should usually include:

- `Current Version`
- `Target Version`
- `Release Scope`
- `Premortem` when the release decision was non-trivial
- `Verification`
- `User Update Steps`
- `Real-Host Proof` when the adapter says a human-run smoke is required
- `Open Risks`

## Guardrails

- Do not hand-edit generated plugin manifests when the repo has a sync helper.
- Do not bump a version without stating why that bump level is justified.
- Do not push, tag, or announce a release without explicit user confirmation.
- Do not mutate installed host caches from inside the skill; update instructions
  belong in the closeout.
- Do not turn host-specific human proof into fake standing CI. If a support or
  install surface still depends on PATH, package managers, or host cache
  state, say so explicitly and carry a short checklist.
- Do not skip the standalone `premortem` pass when a release changes
  compatibility, install/update flow, or host-proof expectations in a way the
  next maintainer could misread.
- If the repo lacks the declared release files or sync script, stop cleanly and
  name the missing seam instead of inventing one.

## References

- `references/adapter-contract.md`
- `references/version-policy.md`
- `references/install-surface.md`
- `scripts/current_release.py`
- `scripts/check_real_host_proof.py`
- `scripts/bump_version.py`
