# Debug #305 — release publish-flow resilience (3 gaps from the v0.21.0 publish)

Date: 2026-06-05
Issue: #305 (bug-class; mechanisms documented from the live v0.21.0 publish)
Surface: `skills/public/release/scripts/publish_release_cli.py`,
`publish_release_plan.py`, `publish_release_preflight.py`,
`publish_release_retro.py`, new `publish_release_resume.py`.

## Gap 1 — not resumable across a mid-publish failure (confirmed)

`main()` makes the local `Release ... <version>` commit (publish_release_cli.py)
then the tag, then pushes. When the pre-push gate flaked on v0.21.0, the failed
push left commit+tag local, nothing on origin, no GitHub release. Re-running is
not idempotent: `git commit` -> "nothing to commit", `git tag` -> "tag exists",
and `ensure_release_target_available` blocks because the local tag exists.
Recovery was manual (push + `gh release create` + verified-record finalize).

**Fix:** new `--resume` flag (requires `--publish-current`). `resume_publish`
validates the partial state (HEAD is the release commit; tag local + points at
HEAD; refuses if already fully published or no consistent partial state),
RE-VALIDATES the pre-push gates that can flake (issue preflight, requested review,
CLI-skill-surface, quality command, fresh-checkout probes, narrative audit),
refreshes the release artifact, pushes only if the tag is not already on the
remote, creates the release only if it does not already exist, verifies,
finalizes, closes issues, and commits the verified record. `build_publish_plan`
skips `ensure_release_target_available` under `resume`.

## Gap 2 — cannot run from the installed plugin cache (confirmed)

`publish_release_retro.py` loaded `skills.public.retro.scripts.check_auto_trigger`
(repo layout). The exported plugin cache flattens `skills/public/retro` to
`skills/retro`, so from `plugins/charness` the import raised
`ModuleNotFoundError: No module named 'skills.public'`. Confirmed: the exported
tree has `skills/retro/scripts/check_auto_trigger.py`, no `skills/public/`.

**Fix:** `_load_public_skill_module` tries `skills.public.<x>` then `skills.<x>`,
tolerating only the `skills(.public)` layout miss and re-raising a genuine missing
dependency inside the target module. Exported `publish_release.py --help` now
exits 0.

## Gap 3 — stale update_instructions undetected (confirmed)

`release_adapter_preflight_payload` only runs when a release-adapter FILE changed
in the release delta, so update_instructions that should be refreshed but whose
file is not touched are never flagged; v0.21.0 shipped stale 0.20.0 operator
steps in the generated record.

**Fix:** unconditional `update_instructions_version_blocker(update_instructions,
target_version, previous_version)` wired into `build_publish_plan`. It flags when
the instructions still describe the previous version but not the target, using
plain substring containment of the concrete version strings (no general semver
scan), so it does not false-positive on dotted dates / version-agnostic prose and
matches `v`-prefixed forms transparently.

## Proof

Test-level only; no real `git push` / `gh release create` (resume proven with a
simulated failed-push partial state + fake git/gh; explicit non-claim).
`tests/quality_gates/test_release_publish_resilience.py` (staleness logic +
integration block; exported-layout import; resume idempotent continue; resume
refuses with no partial state; resume requires --publish-current) plus the full
release suite = 63+ green; deterministic closeout aggregate completed (incl.
public-skill validation/dogfood gates after recording the release dogfood
evidence). Mirrors byte-identical.
