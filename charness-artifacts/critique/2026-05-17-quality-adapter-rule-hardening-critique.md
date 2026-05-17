# Quality Adapter Rule Hardening Critique

- Date: 2026-05-17
- Target: implemented diff that restores `gather_provider.<source>.mode` wording and makes invalid `skill_ergonomics_gate_rules` fatal through the ergonomics validator, root wrapper, and adapter validator.
- Fresh-Eye Satisfaction: parent-delegated
- Verification Context: targeted pytest, `validate_public_skill_dogfood.py`, `run-quality.sh`, and `run_slice_closeout.py` passed before this artifact was recorded.

## Act Before Ship

- None. Two bounded reviewers found no code blocker in the implemented diff.

## Bundle Anyway

- Record this artifact with the patch because the slice changes public skill wording, validator behavior, checked-in plugin export, and public-skill dogfood evidence.
- The implemented patch closes the concrete `gather` semantic drift by using exact `gather_provider.<source>.mode` wording in examples and `access mode` in closeout.
- The invalid-rule class is covered through three entrypoints: the public quality helper, the root wrapper, and `validate_adapters.py`.

## Over-Worry

- Do not expand this patch into a general schema/taxonomy euphemism detector.
- Do not rewrite critique packet generation for commit-aware changed paths in this patch.

## Valid But Defer

- A future strict/permissive adapter-loading split could make validator-vs-inventory behavior clearer.
- A future selected-label runner test for `CHARNESS_QUALITY_LABELS=validate-skill-ergonomics` may improve operator proof, but the core failure paths are covered now.
