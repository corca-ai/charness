# Session Retro: check_python_lengths pre-commit gate

Mode: session

Goal: [charness-artifacts/goals/2026-05-29-n-length-precommit-gate.md](../goals/2026-05-29-n-length-precommit-gate.md)

## Context

`/handoff` (bare invocation) → chunker fired (#249) → unioned the live open-issue
backlog with the `## Next Session` memo → ranked 4 chunks → user picked chunk-1
→ `/achieve` shaped a goal skeleton → `/goal` pursued it. The goal: promote
`scripts/check_python_lengths.py` from a pre-push-only gate to a **staged-only
pre-commit gate** (new `--paths` mode + tests + export sync + `.githooks/
pre-commit` wiring). Two slices, fresh-eye critique (no blockers), all gates
green, zero rework. What matters next: this closes the silent-lib-growth trap
that recurred twice; the remaining handoff backlog (#250, #243, #219, ...) is
untouched.

## Waste

Low. No reworked commits, no failed gate retries, no user corrections that
exposed a workflow miss.

- Minor friction (not waste): a display-layer rewrite renders
  `check_python_lengths` as `n` / `n.py` in some shell output but not others
  (the `Read` tool and `python repr` show the true name). Cost ~2 tool calls to
  confirm the canonical name via `python -c "os.path.exists(...)"`. Recorded the
  quirk in the goal Boundaries so the next session does not re-derive it.
- One process-shaped near-miss avoided by measuring first: the test file was at
  659 lines with the 720 warn-band close by, so test additions were kept to 3
  compact cases (landed at 715, under the band) — eating the gate's own dogfood.

## Critical Decisions

- **Staged-only, not whole-repo, at commit** (user choice). Trades catching
  pre-existing debt at commit for quiet commits; backstopped by the unchanged
  pre-push whole-repo run. Decisive: it set the entire implementation shape
  (the `--paths` mode rather than a new threshold or a verbose hard-fail flag).
- **`--paths` = set-intersection with the glob universe**, not per-path
  re-classification. Single-sources the "what is gated" rule in the script's
  glob, so the hook can pass *all* staged `.py` and never gate an out-of-universe
  file (export mirror, top-level). This avoided a bash-side `scripts|skills|tests`
  regex that would drift from the script.
- **Hook passes every staged `.py`** and lets the script filter — kept the hook
  diff to one stanza inside the existing `STAGED_PY` guard (free no-py skip).

## Expert Counterfactuals

- **Gary Klein (pre-mortem lens): "Assume this gate silently fails to block a
  real over-limit commit — why?"** This question is what the fresh-eye critique
  effectively ran, and it surfaced the one genuine limitation: the check reads
  the **working tree**, not the staged blob, so a file staged over-limit then
  shrunk passes. Running this lens *before* implementation would have reached
  the same "accept it — shared with the hook's existing py_compile/ruff steps,
  pre-push backstops it" conclusion faster, but the outcome is unchanged. The
  lens earns its place by naming the residual risk explicitly rather than
  leaving it implicit.
- **Defense-in-depth reviewer (counter-lens):** would have argued for whole-repo
  at commit to force pre-existing debt down. The staged-only choice consciously
  rejects this for commit-noise reasons; the counter-lens is satisfied by the
  pre-push run still being whole-repo. No changed action — recorded so the
  tradeoff is not silently re-opened.

## Next Improvements

- **memory:** the gate-placement rule is now *realized*, not just stated —
  `check_python_lengths` joins `validate-attention-state-visibility` and
  `run-evals` as a pre-commit gate (cheap + agent-free + hard-fail). Recorded so
  the next "should this be pre-commit?" decision has a third worked example.
- **workflow (validated, no change needed):** the `/handoff` chunker →
  `/achieve` → `/goal` pipeline ran end-to-end on a real capability task with no
  friction. The chunker's `--with-issues` union correctly flagged the stale
  memo (closed #244/#245/#242/#233). No change proposed; the pipeline works.
- **capability (none):** no new tooling warranted. The `--paths` mode is the
  capability delta and it shipped.

## Sibling Search

Transferable pattern named: **a staged-file pre-commit check that reads the
working tree rather than the staged blob** (`git show :path`) can pass on a
shrunk working tree while an over-limit blob commits.

- Four-axis scan (same hook / same script-family / same gate-class / same
  doc-claim): the siblings are the **pre-existing `py_compile` and `ruff`
  staged steps in the same `.githooks/pre-commit`** — they share the identical
  behavior. No *new* sibling was introduced by this change.
- Decision: **no follow-up filed.** Severity is low (pre-push whole-repo run is
  the post-commit backstop for all three steps), the behavior predates this
  work, and a fix would require staging-blob extraction across every staged
  step — disproportionate churn for a backstopped edge. Recorded as a known
  limitation in the goal artifact's Plan Critique Findings instead.

## Persisted

(to be stamped by persist helper)
