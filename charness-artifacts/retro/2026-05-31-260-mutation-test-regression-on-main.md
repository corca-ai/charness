# Retro — #260 mutation-regression goal (session)

## Mode

session

## Context

The #260 achieve goal: make the scheduled mutation gate green again on `main`
and raise durable mutated-behavior coverage. Five slices: reproduce+locate,
cover the blocking trio, kill the 22 survivors (+ surgical trio hardening),
preventive teeth, prove+close. Both #260 FAIL causes are fixed and locally
proven; closeout staged (not pushed).

## Evidence Summary

- Goal artifact slice log + 4 implementation commits (`236908b`, `0c53a59`,
  `c35e028`, + closeout).
- Faithful gate repro: `classify_changed_line_scope_gap` (blocking) +
  scoped Cosmic Ray sessions (`/tmp/cr-260-*.sqlite`) for the score path.
- `check_mutation_score.py` on the #260 survivor dump → 100.0% / 101 PASS.
- Full suite `pytest -m 'not release_only'` → 1868 passed.
- Host-log probe (claude session jsonl): token/tool-call counts derivable;
  exact figures not quoted (no fabricated metrics).

## Waste

- **Timeout-killed `cosmic-ray exec` left a mutation applied.** Wrapping
  `cosmic-ray exec` in the Bash tool's 600s `timeout` killed it mid-mutant;
  cosmic-ray only restores between mutants, so `render_cli_reference.py:102`
  was left mutated (`repo_root >> args.output`). Caught by `git status` before
  the Slice-2 commit and restored. Adopted mid-session: run exec in the
  background (no tool-timeout kill) + always `git checkout` the module-path
  files after every exec.
- **Coarse-grained dump parsing slips.** First dump parse used lowercase
  `"survived"` (the field is uppercase `SURVIVED`) and read a stale truncated
  `.jsonl`; one extra analysis cycle. Switched to reading the session sqlite
  directly (ground truth).
- **Polling cadence on long async runs.** The trio/survivor mutation runs were
  ~15–25 min each; monitoring them is legitimate (not redundant work — the
  triage lock was "wait for the async job"), but several short sleep+poll
  cycles could have been fewer/coarser by leaning on background-completion
  notifications.

## Critical Decisions

- **Targeted scoped re-run over reproducing the CI seeded fill sample (A1).**
  Gave a precise local survivor set (and matched CI's 101 executable exactly)
  without a full sampler run.
- **Ran the whole trio through mutation, not just the gap lines.** This
  surfaced 94 pre-existing latent survivors AND that `closeout_evidence` /
  `coordination_floors` are fill-eligible — a recurrence vector the goal's
  scope had not anticipated. Surfaced it to the user rather than silently
  picking; the user chose surgical hardening. Highest-leverage call of the
  session: a same-agent assumption would have shipped a thin-margin trio.
- **Self-checked the teeth as a new mutation-pool file.** It was 70.4%
  mutation (would have planted a *new* score failure the next cron) — caught
  and hardened to 90.1% by dogfooding the exact line-102 `repo_root / args.X`
  fix the whole goal is about.

## Expert Counterfactuals

- **Gary Klein (pre-mortem).** "Assume the next cron still fails — why?" run at
  *Slice-3 planning* would have front-loaded both the fill-eligibility risk and
  the teeth-self-failure risk, which I instead discovered reactively (via the
  trio re-run and a deliberate teeth self-check). Changed action: run a "what
  new files/lines enter the mutation denominator?" pre-mortem **before** writing
  the fix tests, not after.
- **Michael Feathers (mutation/characterization).** Line coverage ≠ behavior
  coverage — `render_cli_reference.py:102` was "executed" yet its else-branch
  Div mutants survived. Lead with the *mutation* map (which branches/operators
  are unkilled), not the line-coverage map. Already internalized this session;
  worth keeping as the default lens for any mutation-gate work.

## Next Improvements

- **capability:** `run_cosmic_ray_mutation.py` (or a thin wrapper) should
  `git checkout` the configured `module-path` files on exit/interrupt
  (defensive restore via try/finally + signal handling), so a killed exec never
  leaves a mutated working tree. Candidate teeth → filed as a follow-up.
- **workflow:** when adding a NEW mutation-pool file (any `scripts/*.py`,
  `skills/*/scripts/*.py`), immediately verify it clears BOTH the blocking floor
  (100% changed-line coverage) and the score floor (≥80% mutation) before
  committing — a new helper can become the next regression. Applied this
  session for the teeth.
- **memory:** persist the two transferable lessons (timeout-killed exec leaves a
  mutation; new pool file must clear both floors) into recent-lessons via this
  artifact.

## Sibling Search

Transferable waste pattern: **an in-place file mutator killed mid-run leaves the
working tree mutated** (relies on a between-units restore that a kill skips).

- Four-axis scan: (1) other in-place mutators in the repo — Cosmic Ray (Python,
  the hit here) and StrykerJS (JS). StrykerJS runs in its own sandbox/temp tree
  rather than mutating the checked-in working tree the same way, so the
  working-tree-pollution sibling is essentially the Cosmic Ray path only.
  (2) codemods/formatters run via subprocess — none in this repo mutate then
  rely on a between-step restore. (3) the mutation *sampler* rewrites
  `cosmic-ray.toml` in place — but that is config the runner regenerates, and
  the gate already guards it. (4) any test that writes outside `tmp_path` — the
  stray `sub/dir/out.md` (a mutated render run writing relative to cwd) is the
  one instance; cleaned, and normal test runs use `tmp_path`.
- Decision: **fix-the-primary** (the Cosmic Ray runner defensive-restore
  improvement above) + **monitor** (no other in-place working-tree mutators
  today). Not a blanket sweep.

## Persisted

yes — `charness-artifacts/retro/2026-05-31-260-mutation-test-regression-on-main.md`
(recent-lessons + lesson-selection-index refreshed by `persist_retro_artifact.py`).
