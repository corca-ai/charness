# Non-Gitignore-Aware File Scanner CI-Only Failure Debug
Date: 2026-06-30

## Problem

A repo scanner enumerates files with a raw walk (`Path.rglob`/`os.walk`) instead
of a gitignore-aware listing, so it ingests gitignored/generated files. It passes
locally (clean tree) but fails in CI (checkout materializes those files). Worked
example below: `validate_attention_state_visibility.py:173`.

## Correct Behavior

Given a scanner that decides pass/fail by enumerating repo files; when it lists
candidates; then it must use only the gitignore-aware view (`git ls-files
--cached --others --exclude-standard`, i.e. `iter_matching_repo_files` /
`visible_repo_files`), so gitignored/generated files never enter the set.
Capability restored: a green local scan reliably predicts the CI result.

## Observed Facts

- `validate_attention_state_visibility.py:173` walks `scripts`, `skills/public`,
  `skills/support` via `rglob("*.py")`, filtering only `__pycache__` (line 176).
- `.gitignore` puts gitignored subtrees inside scanned roots / repo root:
  `skills/support/generated/*` (line 29), `mutants/`, `reports/`, `.artifacts/`,
  `pytest-tmp/`, `__pycache__/`, `*.pyc`.
- Canonical gitignore-aware seam exists (`repo_file_listing.py`, ~20 consumers)
  but adoption is opt-in.
- Assumption, NOT confirmed: a CI step materializes files under
  `skills/support/generated/` / `mutants/`. `support_sync_lib.py` does not write
  there; locally only `.gitkeep`. Producer unproven.

## Reproduction
```bash
mkdir -p skills/support/generated/demo_pkg
printf 'STATE="disabled"\ndef run(): return {"status":"skipped"}\n' > skills/support/generated/demo_pkg/probe.py
git check-ignore skills/support/generated/demo_pkg/probe.py   # path IS gitignored
python3 scripts/validate_attention_state_visibility.py --repo-root .; echo $?
# -> "...probe.py: attention state(s) disabled, skipped are not declared"  exit 1
rm -rf skills/support/generated/demo_pkg                      # green again
```

## Candidate Causes

- Enumeration (confirmed): raw walk never filters gitignored paths.
- Environment/state: gitignored/generated file present in CI, absent locally —
  the trigger that fires the latent bug.
- Pattern B fallback: helper silently reverts to raw `rglob` when CI `git` fails
  (dubious-ownership), since helpers default `require_git=False`.
- Declaration-drift (rejected): stale JSON would also fail, but the falsifier
  pins it to a gitignored file in the raw set, not a tracked-file omission.

## Hypothesis

Falsifiable claim: a gitignored file under a scanned root enters the raw set and
makes the scanner exit non-zero, while `git ls-files --cached --others
--exclude-standard` excludes it. | disconfirmer: compare `git ls-files` vs
`rglob` on a synthetic gitignored `*.py`, then run the real scanner against one.

## Verification

- Result: confirmed.
  - Falsifier 1: throwaway repo (`.gitignore`: `ignored/`, `*.gen.py`) —
    `git ls-files` = `['.gitignore','tracked.py']`; `rglob("*.py")` =
    `['ignored/dep.py','keep.gen.py','tracked.py']`. Raw walk ingests both.
  - Falsifier 2: real scanner exited **1** on the gitignored probe
    (`git check-ignore` confirmed); removing it returns to green.
- Non-claim: the CI producer and the Pattern B git-failure path are reasoned
  mechanisms, not observed in an actual CI run.

## Root Cause

Structural bottom: **a missing enforced invariant — no single mandatory
gitignore-aware "list repo files" seam — plus a hygiene gate whose scope misses
the offending scanners.**

1. CI failed / local passed → scanner flagged a file present in CI, absent local.
2. Present only in CI → it lives under a gitignored subtree
   (`skills/support/generated/*`); local tree has only `.gitkeep`.
3. Scanner saw it → `rglob("*.py")` (line 173) filters only `__pycache__`.
4. Not gitignore-aware though a seam exists → enumeration is ad hoc per scanner;
   seam is opt-in, two parallel impls, no single source of truth.
5. Seam not enforced → the gate (`inventory_gitignore_scan_hygiene.py`) inspects
   only a narrow name-glob set excluding these scanners and flags only
   repo-root-rooted walks (see Detection Gap).
6. Secondary path → helpers default `require_git=False`
   (`repo_file_listing.py:26/54/90`, `git_inventory_lib.py:15`), so CI `git`
   failure silently falls back to a raw walk.

## Invariant Proof

- Invariant: when a scanner enumerates files (producer), the pass/fail gate
  (consumer) must decide only over the gitignore-aware view.
- Producer Proof: `git ls-files` vs `rglob` diverge on gitignored paths (Falsifier 1).
- Final-Consumer Proof: gate honored the raw set — exit 1 on the gitignored probe
  (Falsifier 2); the seam would have hidden the file.
- Interface-Shape Sibling Scan: any enumerate→gate path using raw `rglob`/`os.walk`
  shares the broken interface (see Sibling Search).
- Non-Claims: CI producer + Pattern B git-failure path unproven at runtime.

## Detection Gap

- `inventory_gitignore_scan_hygiene.py` `DEFAULT_PATH_GLOBS` (lines 27-33:
  `*inventory*`/`*quality*`/`*scan*` + quality scripts) | did not fire: the
  raw-walker scanners match no glob, so the gate inspected **0** of them (verified
  `--json` findings `[]`). | fix: broaden to `scripts/*.py`.
- `_is_repo_wide_glob` (lines 85-95) | did not fire: flags `rglob`/`glob('**')`
  only on a repo-root-name receiver; the subtree `absolute_root.rglob` emitted
  nothing even when force-fed (verified). | fix: flag any `rglob`/`os.walk`
  outside a git-aware context, any receiver.
- `run-quality.sh:499-502` | gate runs with `--require-empty
  --require-git-file-listing`; presence is not the gap, scope is (the flag
  mitigates Pattern B only for this gate's own listing). Over-reach check: real —
  the gate provably returns empty for the failing scanner, demonstrated above.

## Sibling Search

- Mental model: *a safety check trusts a raw filesystem walk as the authority for
  "what files are in the repo" instead of the gitignore-aware seam; the walk
  diverges from the committed tree wherever a gitignored/generated subtree exists*
  (reference trap: "checks that trust an implicit default as the authority").
- cross-file: scripts/validate_packaging_install_surface.py
- same layer (literal raw walk; all `same class, diagnostic-only` / `static`
  unless noted): `validate_attention_state_visibility.py:173` (**same bug**,
  runtime repro); `operator_acceptance_lib.py:29` (`repo_root.rglob("*.md")`,
  repo-wide); `check_title_slug_drift.py:99` (`*.md` over committed dirs);
  `check_test_repo_copy_invariants.py:134` + `check_test_completeness.py:38`;
  `check_skill_cut_safety.py:71` + `check_skill_contracts.py:268`
  (`references_dir.rglob`); `check_prose_pin.py:107`.
- abstraction up — "every enumeration routes through one gitignore-aware seam":
  two parallel seams (`repo_file_listing.py` + `git_inventory_lib.py`) = no single
  source of truth | same class, diagnostic-only | static.
- specialization down — `validate_packaging_install_surface.py:143` builds
  *expected* via `collect_files(generated_plugin_root)` (no `repo_root` → raw
  `rglob`, line 133) while *actual* (line 144) is `git ls-files`; a gitignored
  file in the generated root = false mismatch | valid follow-up outside the slice
  | static (lines 143 vs 144) |
  follow-up: deferred docs/handoff.md#non-gitignore-aware-scanner-seam
- mental-model siblings (Pattern B): `iter_repo_files` + `visible_repo_files`
  (`require_git=False`) revert to raw listing on `git` failure | same class,
  diagnostic-only (mitigated only for run-quality's gate) | static + Falsifier 1.
- Over-reach: each is a literal raw `rglob`/`os.walk` feeding a gate, not a name
  coincidence (packaging entry defended by its asymmetric call sites).

## Seam Risk

- Interrupt ID: 2026-06-30-gitignore-scan-seam
- Risk Class: host-disproves-local, repeated-symptom, external-seam
- Seam: CI checkout vs local tree — CI materializes gitignored/generated subtrees
  (and may run `git` under different ownership); local does not.
- Disproving Observation: identical code + command, green local / red CI.
- What Local Reasoning Cannot Prove: which CI step populates the subtree; whether
  CI `git` failure triggers Pattern B — need a real CI run/log. Class recurs
  despite two seams, a hygiene gate, and a CI/local parity inventory (part-fenced).
- Generalization Pressure: factor-now

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: spec
- Handoff Artifact: charness-artifacts/spec/2026-06-30-gitignore-aware-scanner-seam.md

## Prevention

Routed to `spec`: the fix spans many scanners, redesigns a public-skill quality
gate, and sets a `require_git` policy on a host-disproves-local seam.

1. Close the detection gap first: broaden `inventory_gitignore_scan_hygiene.py`
   globs to `scripts/*.py` and make `_is_repo_wide_glob` flag subtree
   `rglob`/`os.walk` outside a git-aware context — turns every sibling into a fail.
2. Migrate same-class siblings to the seam, starting with line 173.
3. Set the `require_git` policy (Pattern B): `require_git=True` for gate-class
   callers, so CI `git` failure is hard, never a silent raw-walk fallback.
4. Fix `validate_packaging_install_surface.py:143/144` asymmetry (pass `repo_root`
   to both `collect_files`).

Required at fix time: full standalone critique (validator, public-skill quality
gate, packaging/export surfaces).
