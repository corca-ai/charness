# Gitignore-Unaware File Scanner CI-Only Failure Debug
Date: 2026-06-30

## Problem

A repo script's file scanner enumerates gitignored files; it passes locally but
fails only in CI.

## Capability Failure

An operator/CI cannot trust any `scripts/*` validator's verdict as a statement
about the *repo's* files: the scanned file set silently depends on the runtime
environment (git presence, pre-existing gitignored artifacts), so the same code
greens locally and reds in CI for reasons unrelated to the change under review.

## Correct Behavior

- Given a repo with gitignored paths (e.g. `__pycache__/`, `*.pyc`, vendored
  deps, `charness-artifacts` generated content),
- When any `scripts/*` file scanner enumerates "the repo's files" — in any
  runtime context (git on PATH or not, `.git` present or not, generated ignored
  files present or not),
- Then the scanned set equals git's tracked + unignored set and never includes
  a gitignored path; if the environment cannot establish that set (git
  unavailable), the scanner fails loud rather than silently degrading to a
  filesystem walk.

## Observed Facts

- Canonical lister `scripts/repo_file_listing.py` is gitignore-aware via
  `git ls-files -z --cached --others --exclude-standard`
  (`scripts/repo_file_listing.py:29`).
- `iter_repo_files` silently degrades to a gitignore-blind walk when git fails
  and `require_git=False` (the default): `for path in repo_root.rglob("*")`
  (`scripts/repo_file_listing.py:64-68`).
- `iter_matching_repo_files` has the same silent degrade: its `else` branch
  (git failed) drops the `path not in allowed` filter and globs the raw
  filesystem (`scripts/repo_file_listing.py:115-122`).
- Every helper caller exposes `--require-git-file-listing` as
  `action="store_true"` defaulting to **off** (10+ callers, e.g.
  `scripts/check_doc_links.py:351`, `scripts/check_python_runtime_inheritance.py:114`).
- CI (`.github/workflows/quality-core.yml`) invokes validators without that flag
  (e.g. `python3 scripts/check_doc_links.py --repo-root .`, line 78). Disconfirmer
  grep of `.github/workflows/*.yml` for `require-git|require_git|ls-files`
  returned only unrelated `GITHUB_OUTPUT` lines — the strict path is never armed.
- `scripts/check_current_pointer_writes.py:30-50` re-implements the *same*
  git-primary + silent-`rglob`-fallback shape independently, with **no**
  `require_git` option at all — but its fallback is subtree-scoped to
  `SCAN_ROOTS = (scripts, skills/public, skills/support)` over `rglob("*.py")`,
  so it is narrower than a repo-root walk (it can ingest a gitignored `.py`
  under those trees; `__pycache__`/`.pyc` are excluded by the `*.py` filter).
- `scripts/validate_packaging_install_surface.py:120-133` `collect_files` has the
  same silent shape: `git ls-files ... -- <prefix>` primary, falling back to
  `root.rglob("*")` on non-zero exit (and whenever `repo_root is None`), with no
  `require_git` knob; scoped to a packaging/plugin prefix subtree.
- Raw repo-root walkers that never touch git: `scripts/narrative_adapter_lib.py:251`
  and `scripts/list_external_links.py:50` (`repo_root.rglob("*")`),
  `scripts/operator_acceptance_lib.py:29` (`repo_root.rglob("*.md")`).

## Reproduction

Smallest honest repro (ran during this investigation): a non-git directory
containing `tracked.py`, a gitignored `generated.pyc`, a gitignored
`__pycache__/foo.py`, and a `.gitignore`. Calling
`iter_repo_files(root, require_git=False)` returned
`['.gitignore', 'foo.py', 'generated.pyc', 'tracked.py']` — `INGESTED
GITIGNORED? True`. With git present and initialized, `git ls-files` succeeds and
the same call excludes the ignored paths. This is the exact local-pass /
CI-fail flip.

## Candidate Causes

- **Environment/control-flow (root): silent git-unavailable fallback.** In a
  non-git CI context (exported/packaged tree without `.git`, container step
  without git on PATH, shallow tarball), `git ls-files` fails, `require_git`
  defaults false, and the scanner degrades to a gitignore-blind `rglob`. Local
  dev always has `.git` + git → green. (Reproduced.)
- **State: generated gitignored artifacts present only in CI.** Even with git,
  the raw repo-root walkers (`narrative_adapter_lib`, `list_external_links`,
  `operator_acceptance_lib`) never call git; locally the tree is clean, but CI
  runs `npm ci` / `pip install` / test steps that create `node_modules/`,
  `__pycache__/`, coverage, etc. before the scan, which the walk then ingests.
- **Dependency/logic: missing enforcement.** No gate forbids raw repo-root
  `os.walk`/`rglob`, and the one strict knob (`--require-git-file-listing`) is
  opt-in and never armed in CI — so gitignore-awareness is a runtime accident,
  not enforced by construction.

## Hypothesis

Falsifiable claim: the scanner's gitignore-awareness depends on runtime
conditions (git reachable AND no pre-existing ignored artifacts) rather than
being enforced; remove either condition and a gitignored file enters the scanned
set. Observable change if true: enumerate the same tree once where `git
ls-files` succeeds and once where it fails — the failing-git enumeration
includes the gitignored path. Disconfirmer: run `iter_repo_files` in a non-git
tree seeded with a gitignored file; if the ignored file is absent, the
hypothesis is false.

## Verification

- Result: **confirmed.** The non-git reproduction above ingested `generated.pyc`
  and `__pycache__/foo.py`; the git-present path excluded them. Identical code,
  divergent set, driven only by environment — matching local-pass / CI-fail.

## Root Cause

Gitignore-awareness in the repo's file scanners is an environmental accident
rather than an invariant enforced by construction. The canonical lister treats
"`git ls-files` failed" as a soft signal and silently falls back to a
gitignore-blind `rglob` walk (default `require_git=False`); the pattern variant
drops its allow-set filter the same way; and several scanners bypass the lister
entirely with raw repo-root walks. Whether a gitignored path enters the scanned
set therefore depends on (1) git being reachable and (2) ignored artifacts being
absent — both true on a clean local checkout, both violable in CI (non-git /
exported context, or generated artifacts present). The strict path that would
convert "git unavailable" into a loud failure exists but is never armed in CI.

## Invariant Proof

- Invariant: a scanner's operated-on file set MUST equal git's tracked+unignored
  set (exclude every gitignored path) regardless of git availability or
  pre-existing generated files; this set propagates to each validator's
  pass/fail verdict.
- Producer Proof: producer = `repo_file_listing` (or a raw walk). Proven only on
  the happy path (git reachable, clean tree) → gitignore respected.
- Final-Consumer Proof: NOT proven end-to-end. The consumer (each validator's
  verdict) inherits the blind set whenever git is unavailable or artifacts are
  present; a local green producer run does not prove the CI consumer set.
  Producer-only proof is not end-to-end workflow proof.
- Interface-Shape Sibling Scan: the produced `list[Path]` flows identically into
  every helper caller; the silent-degrade defect is at the producer, so all
  consumers share the exposure (see Sibling Search).
- Non-Claims: not claimed that any specific CI run's failing log was located
  (the operator-described symptom is the trigger); not claimed git is actually
  absent in the current CI image — the structural cause holds for both the
  non-git and the generated-artifact directions.

## Detection Gap

- `--require-git-file-listing` strict knob on helper callers | did not fire:
  `action="store_true"`, default off, and `quality-core.yml` invokes every
  validator without it, so git-unavailable degrades silently instead of raising |
  smallest change: arm `--require-git-file-listing` in CI (or default
  `require_git=True` for CI invocation) so a non-git/exported scan context fails
  loud.
- Structural lint over scanner scripts | did not fire: no gate forbids raw
  repo-root `os.walk`/`rglob("*")` or requires routing enumeration through
  `repo_file_listing`, so `narrative_adapter_lib`, `list_external_links`,
  `operator_acceptance_lib`, and `check_current_pointer_writes` ship
  gitignore-blind unchallenged | smallest change: add a source-guard-style check
  flagging repo-root filesystem walks outside `repo_file_listing.py` unless
  explicitly exempted.
- Local-vs-CI environment parity | did not fire: no test runs scanners against a
  tree that contains a gitignored generated file, so the only difference that
  matters (CI generates ignored artifacts; CI may lack `.git`) is never
  exercised | smallest change: a regression test that seeds a gitignored file
  (and a non-git context) and asserts each scanner excludes it.

## Sibling Search

- Mental model (wrong assumption that made the bug plausible): "the filesystem
  the scanner can walk == the repo's authoritative file set," i.e. trusting the
  ambient working directory / a best-effort git probe as the authority for
  membership instead of enforcing it. Matches the trap shape "safety checks that
  trust current working directory or an implicit default as the authority."
- same layer (literal raw repo-root walk treated as the repo file set):
  - `scripts/narrative_adapter_lib.py:251` `repo_root.rglob("*")` | decision:
    valid follow-up outside the slice | proof: static scan only |
    follow-up: deferred docs/handoff.md#gitignore-aware-scanners
  - `scripts/list_external_links.py:50` `repo_root.rglob("*")` | decision:
    valid follow-up outside the slice | proof: static scan only |
    follow-up: deferred docs/handoff.md#gitignore-aware-scanners
  - `scripts/operator_acceptance_lib.py:29` `repo_root.rglob("*.md")` |
    decision: valid follow-up outside the slice | proof: static scan only |
    follow-up: deferred docs/handoff.md#gitignore-aware-scanners
- abstraction up (general pattern: gitignore-awareness is a runtime accident /
  git-probe failure silently degrades to a blind walk):
  - `scripts/repo_file_listing.py:64-68` `iter_repo_files` silent rglob fallback
    | decision: same bug, fix now (subject) | proof: runtime reproduction
  - `scripts/check_current_pointer_writes.py:46-50` independent git-primary +
    silent rglob fallback, no `require_git` knob; fallback is **subtree-scoped**
    to `SCAN_ROOTS` over `*.py` (narrower than repo-root; not a `*` walk) |
    decision: valid follow-up outside the slice (cannot even be made strict
    today) | proof: static scan only |
    follow-up: deferred docs/handoff.md#gitignore-aware-scanners
  - `scripts/validate_packaging_install_surface.py:120-133` `collect_files`
    git-primary + silent `root.rglob("*")` fallback (also when `repo_root is
    None`), no `require_git` knob; prefix-scoped | decision: valid follow-up
    outside the slice | proof: static scan only |
    follow-up: deferred docs/handoff.md#gitignore-aware-scanners
  - helper callers defaulting `require_git=False` + CI never arming the flag |
    decision: same class, diagnostic-only for this slice (this is the detection
    gap, owned above) | proof: static scan only
- specialization down (narrower instance inside the subject file):
  - `scripts/repo_file_listing.py:115-122` `iter_matching_repo_files` else-branch
    drops the `path not in allowed` filter on git failure | decision: same bug,
    fix now | proof: static scan only
- mental-model siblings (same "trust an unscoped ambient scan as authority" trap
  under a different noun):
  - prior incident #365 `scripts/agent_browser_runtime_guard.py` trusted a
    machine-wide `ps` scan with no ownership filter | decision: intentional
    cross-link (different domain, same trap family) | proof: prior debug record
    (see Related Prior Incidents)
- cross-file: scripts/check_current_pointer_writes.py:46 (sibling outside the
  subject file `repo_file_listing.py`)
- Over-reach check: each `same layer` / `abstraction up` entry is defended by the
  concrete walk root (`repo_root.rglob` / git-primary+rglob-fallback) that can
  ingest a gitignored path, not by a shared name; scoped-subtree walkers
  (`tests_dir`, `references_dir`, `skill_dir`, `presets/*`, `session_dir`) were
  inspected and excluded as low/no exposure because gitignored generated files do
  not live under those subtrees — mechanism-shared but not exposure-shared.

## Seam Risk

- Interrupt ID: gitignore-unaware-file-scanner-ci-only
- Risk Class: host-disproves-local
- Seam: scanner file enumeration depends on the runtime environment (git on
  PATH, `.git` present, gitignored artifacts present) which differs local vs CI
- Disproving Observation: identical scanner code passes locally (git present,
  clean tree) and fails in CI (non-git/exported context or generated gitignored
  files present); a local green run cannot prove gitignore-correctness
- What Local Reasoning Cannot Prove: that any scanner is gitignore-correct —
  only a non-git context and/or an artifact-seeded tree proves it
- Generalization Pressure: factor-now (one shared structural cause across many
  scanners → centralize gitignore-aware enumeration and add an enforcing gate)

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: spec
- Handoff Artifact: docs/handoff.md#gitignore-aware-scanners (+ this debug record)

## Prevention

Maps to the Detection Gap and Sibling Search outputs, not the root cause restated.
Hand to `spec` (host-disproves-local seam → spec, not direct impl; the fix
touches validator/export/host-proof surfaces and needs full review):
1. Centralize all repo file enumeration through `repo_file_listing`; make the
   git-unavailable path fail loud in CI (arm `--require-git-file-listing` in
   `quality-core.yml` or default `require_git=True` for CI), and remove the
   independent fallback in `check_current_pointer_writes.py`.
2. Add a structural gate forbidding raw repo-root `os.walk`/`rglob` outside
   `repo_file_listing.py` (source-guard / boundary-bypass style) so new
   gitignore-blind scanners cannot ship.
3. Add a regression test that seeds a gitignored file (and a non-git context)
   and asserts every scanner excludes it.

Scoped diagnosis/repair-risk critique (recorded at handoff, full review owed at
spec/impl): the repair must not over-narrow to the helper alone — three raw
walkers and one independent fallback share the exposure; flipping `require_git`
default risks breaking genuinely-non-git callers (e.g. packaging surface
inspection) that legitimately walk an exported tree, so the centralization must
distinguish "repo scan" from "arbitrary-tree scan" rather than blanket-forcing
git. The fix's blast radius (10+ callers, exports, validators) is exactly why
the next step is `spec` with a full standalone review, not a same-agent patch.

## Related Prior Incidents

- `charness-artifacts/debug/2026-06-14-issue-365-agent-browser-orphan-ownership.md`
  (#365): `agent_browser_runtime_guard` killed a neighbor's daemon because it
  trusted a machine-wide `ps` scan with no ownership filter. Same mental-model
  family as this incident — a scan trusts an unscoped ambient environment as the
  authority for membership instead of enforcing a proven scope. Reinforces the
  factor-now generalization pressure.
