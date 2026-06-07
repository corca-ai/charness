# Resolution Critique — #332 commit-boundary structural-sweep enforcement

Date: 2026-06-07
Issue: #332 (the cheap commit-boundary structural sweep — `validate_skill_ergonomics`
/ `validate_attention_state_visibility` / the `check_skill_surface_preflight`
authoring preflight — was discretionary: a new skill-package or `scripts/*.py`
edit could defer those gates to the slow broad gate, recurring across #308 / #325
/ #329). Resolution: make the cheap structural sweep the FIRST verdict the full
`run_slice_closeout.py` produces (a label-filtered SUBSET of the existing
`staged_commit_gate_plan`, run fail-fast before surface-match / cautilus / broad
pytest), plus a staged/e2e regression test — presence/structural only, single
source of truth, no new judgment, no parallel mechanism.
Reviewer provenance: bounded fresh-eye subagent review (independent agent context
`a0c76fcd06b21618b`, read-only in the shared parent worktree), run at the Slice 2
fix boundary per the goal's Agent Verification Plan. Verdict: SHIP (after the
initial BLOCKER was folded; first pass returned BLOCKER, re-review returned SHIP).
Fresh-eye satisfaction: satisfied — a different-context bounded reviewer returned
a real BLOCKER (the change could not pass its own function-length gate), it was
folded before ship, and the re-review independently confirmed the fix
behavior-preserving with a fresh red/green check.

## Scope reviewed

- `scripts/staged_commit_gate_plan.py` — NEW `STRUCTURAL_SWEEP_LABELS`,
  `structural_sweep_gates` (label-filtered subset of `staged_commit_gate_plan`),
  `structural_sweep_planned_commands`, `run_structural_sweep_preflight`,
  `block_on_structural_sweep`.
- `scripts/run_slice_closeout.py` — `main()` runs the sweep FIRST via a new
  `_run_preexecution_blocks` helper; `--plan-only` lists the sweep first.
- `tests/quality_gates/test_staged_commit_gate_plan.py` — +5 tests incl. the e2e
  `test_full_closeout_blocks_329_class_violation_at_structural_sweep`.
- `plugins/charness/scripts/{staged_commit_gate_plan,run_slice_closeout}.py` —
  generated mirror (byte-identical to source).

## Findings

- **BLOCKER (folded): `main()` exceeded the 100-line function limit.** The +16-line
  sweep block pushed `run_slice_closeout.py:main()` from exactly 100 to 116, so
  `check-python-lengths (staged)` — the very cheap commit-boundary gate this PR
  hardens — would have rejected the commit (or forced a `--no-verify` bypass).
  The author's pre-review proof checked FILE length (471/480 warn band) but missed
  the FUNCTION-length hard fail. Folded: extracted the cohesive fail-fast gate
  chain into `_run_preexecution_blocks` (main() 116→86, helper 30; both well under
  100); re-review confirmed behavior-preserving.
- **No further blockers.** Ordering correct (sweep before surface-match / cautilus
  / risk / broad pytest); single-source-of-truth genuine (subset of the plan, no
  duplicated gate logic); per-gate non-uniform coverage preserved; mirror
  byte-identical; e2e test honest (drives real `main()`, red-without-fix
  re-verified twice — once by the author, once by the reviewer on a tmp copy).

## Structured Findings

- function-length-blocker | bin: act-before-ship | evidence: strong | ref: scripts/run_slice_closeout.py main() | action: fix | note: +16-line sweep block pushed main() 100→116 over the FUNCTION_MAX=100 gate this PR hardens; folded by extracting `_run_preexecution_blocks` (main() 116→86). Reviewer + author both re-verified rc=0.
- file-length-warn-band | bin: valid-but-defer | evidence: moderate | ref: scripts/run_slice_closeout.py | action: defer | note: file now 474/480 (advisory, exit 0); already in the warn band (457) pre-#332; god-module split is an explicit #332 Non-Goal. follow-up:run-slice-closeout-module-split — next addition to this file must land in a new module.
- duplicate-cheap-gate-rerun | bin: over-worry | evidence: strong | ref: scripts/staged_commit_gate_plan.py block_on_structural_sweep | action: document | note: the sweep re-runs ergonomics+attention-state (~1.1s) which also run in verify; fail-fast on the cheap gates avoids the expensive surface-match/cautilus/broad-pytest round-trip — a goal-sanctioned tradeoff, not the duplicate-pressure refactor the Non-Goals exclude.
- label-string-coupling | bin: over-worry | evidence: moderate | ref: scripts/staged_commit_gate_plan.py STRUCTURAL_SWEEP_LABELS | action: document | note: the sweep selects plan gates by label string; a plan-label rename would silently shrink it, but `test_structural_sweep_covers_each_329_class_file_type` asserts each of the three labels is present per file class and would fail on a rename.
- path-resolution-parity | bin: over-worry | evidence: strong | ref: scripts/run_slice_closeout.py _run_preexecution_blocks | action: document | note: the full closeout feeds the sweep its resolved `changed_paths` (working-tree/--paths), not the staged index; the e2e test exercises this and no false-negative seam was found. follow-up:slice-2-path-resolution-parity resolved.
- reviewer-worktree-mutation | bin: act-before-ship | evidence: strong | ref: skills/shared/references/fresh-eye-subagent-review.md | action: document | note: the bounded reviewer ran `git checkout -- scripts/run_slice_closeout.py` (a forbidden worktree-mutating op, #258-class) during its first pass, discarding the unstaged source fix; it self-disclosed and restored from the byte-identical mirror. Verified non-corrupting (source==mirror sha256, all changes intact) by both author and reviewer. Recorded for the retro as a reviewer-contract violation that happened to be recoverable here only because the mirror still held the change.

## Reviewer Tier Evidence

- Requested tier: bounded fresh-eye subagent review (independent agent context, read-only in the shared parent worktree).
- Requested spawn fields: slice review packet — intent, changed files + owning/generated surfaces, expected invariants (sweep-first, single-source, non-uniform coverage, docs-only no-op, predict-commit unchanged), proof already run, non-claims, out-of-scope lines, and seven adversarial reviewer questions (ordering, single-source, duplicate pressure, path-resolution parity, mirror, test honesty, blockers).
- Host exposure state: applied
- Application state: host-confirmed: subagent `a0c76fcd06b21618b` completed a first pass (BLOCKER) and a resume re-review (SHIP); the BLOCKER was folded before ship and the re-review independently re-verified the fold with a fresh red/green check.

## Verification proof

- Targeted gate-plan tests after the fold: 26/26 (`test_staged_commit_gate_plan.py`).
- Closeout-touching suites: 122 (author) / 175 (reviewer's broader `-k` selection) passed.
- Red-without-fix / green-with-fix: verified twice (author neutralized the call in
  the worktree then restored; reviewer neutralized `_run_preexecution_blocks` on a
  tmp copy) — the e2e test goes red without the fix.
- `ruff`, `check_python_lengths` (function gate now passes; file 474/480 advisory),
  `py_compile`, mirror byte-synced (sha256 match): all green.

## Counterweight pass

- Folding the BLOCKER was not scope creep: it is the difference between a change
  that passes its own hardened gate and one that requires a `--no-verify` bypass;
  the extraction is a behavior-preserving move of an already-cohesive block.
- The file-length defer is honest: splitting the god-module is the registered
  follow-up's job and an explicit #332 Non-Goal; doing it here would bundle an
  unrelated refactor into a gate-hardening slice.
- The deliberate non-claims hold: this fix does not force an agent to run any
  command — the pre-commit hook (on `git commit`) and the pre-push broad-gate
  backstop remain the hard teeth; #332 closes the latency/ordering gap so any
  closeout the agent DOES run surfaces the cheap structural verdict first. No
  coverage broadening, no host/live/provider proof.
