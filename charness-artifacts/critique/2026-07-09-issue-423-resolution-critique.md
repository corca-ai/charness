# Resolution Critique — issue #423 (capture-skill-run.sh eval-identity leak)

- **Target**: `references/code-critique.md` — pre-commit resolution critique of
  the uncommitted diff that resolves #423, recurrence focus ("what would let
  the captured run learn its eval identity again").
- **Execution**: 3 bounded fresh-eye angle reviewers (Jackson/problem-framing,
  Weinberg/diagnostic, Gawande/operational) + 1 separate counterweight
  reviewer; all completed their assigned lens directly.
- **Fresh-Eye Satisfaction**: parent-delegated (repo `Subagent Delegation`
  contract; four real subagent spawns via the host Agent tool).
- **Packet Consumed**: `charness-artifacts/critique/2026-07-08-174958-packet.md`.

## Reviewer Tier Evidence

- requested tier: high-leverage
- requested spawn fields: model `gpt-5.5`, reasoning_effort `medium`,
  service_tier `priority` (from `.agents/critique-adapter.yaml`
  `reviewer_tiers.high-leverage`)
- host exposure state: host-defaulted
- application state: not applied — the Claude Code host exposes no surface for
  the Codex-shaped adapter fields; reviewers ran on the host default reviewer
  model.

## Change

Close #423: the claim-fidelity capture harness ran the captured `claude -p`
with cwd inside the descriptive `--out-dir`, so the captured agent saw its own
eval identity in every absolute path and could read grader siblings
(`justification.md`) via `..` — observed in real transcripts (observer effect
against the representative-run premise). The diff moves ALL run-visible state
(worktree, config, empty-hooks, stream/stderr redirect targets) to a neutral
`mktemp -d` run base; the descriptive out-dir keeps grader-side artifacts plus
post-run `worktree`/`config` symlinks and `run-base.txt`; `--run-cwd` under
`--out-dir` is refused (with worktree cleanup) and descriptive-name overlap
warns; an advisory canary greps `stream.jsonl` for the out-dir basename;
`run_skill_efficiency_ab.py::_cleanup_run` removes the run base; the length
cap (D33 trigger) forced a cohesive extraction of the pure aggregation/report
section to `scripts/skill_efficiency_report.py`.

## Capability at Stake

Eval integrity of every claim-fidelity capture: a run that knows which floor
it is graded against can perform differently from a naive session, weakening
the "representative run" premise of all capture-gated pass/keep decisions.

## Angles + Findings (deduped)

1. **[Act Before Ship — verified regression]** Moving `stream.jsonl` to
   out-dir broke the observation builder's sibling-stream auto-resolve
   (three-up from the session tree = run base), silently re-introducing the
   #409 Gap 2 false-MISS for the README manual flow. **Fixed before commit**:
   post-run leak-free symlink `run_base/stream.jsonl -> out_dir/stream.jsonl`,
   stale mjs USAGE/comment text corrected, README updated.
2. **[Bundle Anyway]** Source-string tests alone stay green through a refactor
   that moves state back under out-dir. **Bundled**: behavioral pytest
   (`test_capture_script_behavioral_no_identity_in_run_view`) executes the
   real script with a PATH-shimmed fake `claude` and asserts the invariant
   (no out-dir basename in cwd/env/fd1, no grader files in `ls ..`, symlink +
   cleanup end-to-end).
3. **[Bundle Anyway]** TMPDIR is the documented relocation lever and re-opens
   the hole on the default path. **Bundled**: run-base-under-out-dir refusal +
   basename-overlap warning right after `mktemp -d`.
4. **[Bundle Anyway]** Cleanup parity: by-hand runs now span two locations.
   **Bundled**: `RUN_BASE=` printed on success; usage + eval README carry the
   two-location cleanup contract.
5. **[Bundle Anyway]** Deferred sibling (post-capture identity-leak assertion
   in the scoring path) was recorded nowhere durable. **Bundled**:
   `docs/deferred-decisions.md` D37; D33 marked fired-and-satisfied.
6. **[Bundle Anyway — recorded as non-claim]** Residual channel: the
   worktree's `.git` file / `git worktree list` expose the dev-clone path and
   sibling run bases. Accepted, not fixed: it reveals "you are a charness
   worktree", not the graded eval floor; recorded in the close comment.

## Counterweight Triage

- Act Before Ship: finding 1 (applied pre-commit).
- Bundle Anyway: findings 2–6 (all applied pre-commit; 6 as close-comment
  non-claim).
- Valid but Defer: post-capture identity-leak assertion in the scoring path
  (D37).
- Over-Worry: invocation/spec-prompt taint analysis (eval-authoring problem;
  canary already covers basename overlap in the stream); positive pre-launch
  runtime invariant (false-positive hazard when out-dir basename equals repo
  basename; the behavioral test asserts the same invariant from outside);
  `rm -rf` trust in script-authored `run-base.txt`; ENOSPC partial-run-base
  leak (self-heals on same-out-dir re-run); test-compat re-export seam in the
  module extraction.

## Deliberately Not Doing

- No blocking identity-leak floor in the capture script or scoring path
  (floor-addition restraint: advisory canary + behavioral test now; promote
  only on recorded recurrence — D37 owns the reopen trigger).
- No prompt/invocation taint analysis; spec prompts are eval-authoring
  surface, not harness surface.
- No runtime positive invariant inside the script (false-positive hazard;
  asserted externally by the behavioral test instead).

## Per-Issue Behavioral Verdict (#423)

**verified** — distinct evidence channel: a live execution of the fixed script
with a PATH-shimmed fake `claude` recording the run-visible view showed
cwd/config/hooks/fd1 all under the neutral run base with zero occurrence of
the descriptive out-dir name, and `ls ..` from the run cwd listed no grader
files (`justification.md` unreachable); the canary stayed silent. The same
check is now durable as `test_capture_script_behavioral_no_identity_in_run_view`
(37/37 focused tests pass). This channel is distinct from the GitHub `CLOSED`
state and the carrier body.

## Boundary Ownership

- Producer: `scripts/agent-runtime/capture-skill-run.sh` produces the
  run-visible namespace (cwd, config, hooks, redirect targets) for every
  captured run.
- Consumer: the captured agent (must see a naive-session view) and, post-run,
  the observation builder / scoring path reading the grader-side out-dir.
- Owning surface: the capture harness scripts under `scripts/agent-runtime/`
  (mirrored to `plugins/charness/scripts/agent-runtime/`); the fix, the
  regression repair, and the behavioral guard all land there and in the
  harness's own test file.
- Verdict: owned-correctly

## Next Move

Commit the fix + bundles with the `Closes #423` carrier, push, verify
closeout, and record the RCA ledger event (`--source issue`).
