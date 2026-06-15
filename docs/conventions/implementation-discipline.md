# Implementation Discipline

This document owns the validation and mutation rules that are too detailed for
the root instruction file but still apply to Charness maintenance work.

## Validation Discipline

- Repo-owned diff obligations live in [.agents/surfaces.json](../../.agents/surfaces.json);
  use `python3 scripts/check_changed_surfaces.py --repo-root .` to inspect them.
- The full `run_slice_closeout.py` runs the cheap structural sweep FIRST
  (`staged_commit_gate_plan` subset: `validate_skill_ergonomics`,
  `validate_attention_state_visibility`, the `SKILL.md` authoring preflight),
  fail-fast, before surface-match / cautilus / broad pytest. A #329-class
  regression therefore blocks at the cheap boundary in <1s instead of deferring
  to the slow gate (#332). A `structural-sweep` failure phase in closeout output
  means a cheap presence/structural gate fired; fix it before rerunning.
- Run `python3 scripts/run_slice_closeout.py --repo-root . --skip-broad-pytest`
  as a pre-lock rehearsal when the slice spans generated surfaces or multiple
  validator families. Before the final broad closeout, record that the mutation
  set is locked and rerun with `--verification-lock`; a broad closeout without
  either flag must refuse before launching broad pytest. The runner prints a
  broad-pytest policy mode and recommendation when broad pytest is selected or
  skipped. Under `--verification-lock`, broad pytest proof is cached by mutation
  fingerprint under `.charness/closeout/`; the same locked diff reuses the cached
  proof, while a changed fingerprint blocks until the operator reruns with
  `--refresh-broad-pytest-proof`. Record focused current-diff proof for pre-lock
  slices rather than treating the skipped broad run as final evidence.
- When a slice changes eligible mutation-pool Python files, add
  `--produce-mutation-coverage` to the final `--verification-lock` closeout. By
  default, it instruments that one broad pytest run with plain coverage (no
  double run) and emits `reports/mutation/test-coverage.json` plus the
  `.fingerprint` freshness marker the pre-push changed-line gate
  (`check-changed-line-mutation-coverage`) reuses. When the changed pool has an
  honest focused pytest proof, prefer a focused producer command alongside
  `--produce-mutation-coverage`; for example,
  `--mutation-coverage-command "python3 -m pytest -q tests/quality_gates/test_x.py"`.
  The broad pytest proof stays on the normal closeout/cache path, and only the
  focused command is instrumented for the freshness marker. Without a fresh
  producer run the gate skips non-blocking, so run the producer before a
  pool-touching push to keep the gate active. To check your own uncommitted slice
  early, run the producer (it stamps the marker over base->worktree) then the
  consumer, or run the consumer over a head that includes the worktree — a manual
  `--head-sha HEAD` dry-run **before commit** is a false green (HEAD is the
  parent, so `base..HEAD` excludes your changes and they are judged only
  post-commit). The consumer now **warns** (non-blocking `warning` field +
  stderr) when the analyzed head resolves to `HEAD` and an eligible mutation-pool
  file has uncommitted worktree changes, so this trap is surfaced instead of
  silently passing (handoff-4). Also run the cheap doc gates the broad pytest
  enforces, such as `python3 scripts/check_spec_evidence_durability.py`, before
  paying for the producer run (see the
  [producer-rerun retro](../../charness-artifacts/retro/2026-06-07-producer-rerun-waste.md)).
- Run and record the critique required by
  [operating-contract.md](./operating-contract.md) before final closeout for
  task-completing repo work.
- Run the fresh-eye slice critique BEFORE the locked `--produce-mutation-coverage`
  producer run, not after: critique-driven code or test changes invalidate the
  coverage fingerprint and force a full instrumented broad-pytest rerun (two
  reruns in one goal on 2026-06-10 — one per mutating slice).
- `python3 scripts/sync_support.py --json` and
  `python3 scripts/update_tools.py --json` are dry-run sanity checks.
- Use `python3 scripts/doctor.py --json` only when intentionally collecting
  real machine-state diagnostics.
- Route evaluator-backed validation through `quality` before `hitl` or
  same-agent manual review.

## Change Discipline

- Before authoring into a gated surface, skim
  [authoring-preflight.md](./authoring-preflight.md): the attention-state banned
  vocabulary, the length-headroom check, and a string/regex edge checklist —
  the constraints existing gates enforce, gathered so you know them up front
  rather than after a rework cycle (#308).
- Before a large addition to a skill helper or repo script, check headroom with
  `python3 scripts/check_python_lengths.py --headroom --paths <file>`
  (`limit − current`, where current is measured by `tokei` Python code lines);
  if the file is near its limit, start a new module rather than append.
  [run_slice_closeout.py](../../scripts/run_slice_closeout.py) auto-surfaces
  near-limit *changed* files at every slice closeout, so the near-limit trap is
  workflow signal, not memory (#256).
  The advisory never blocks on near-limit status; the existing length gate is
  the hard floor. Function limits remain AST-span based because `tokei` does not
  report function-level counts.
- Before adding prose to `skills/public/*/SKILL.md`, `skills/support/*/SKILL.md`,
  or their `references/*.md`, run
  `python3 scripts/check_skill_surface_preflight.py --repo-root . --path <file> --preview-delta <planned-lines>`;
  it reports SKILL.md total/core headroom plus markdown, doc-link, mirror-sync,
  and staged-index couplings before the broad gate.
- Before authoring into a general doc surface (the handoff artifact or any
  `docs/*.md`), run
  `python3 scripts/check_doc_authoring_preflight.py --path <doc>`; it aggregates
  the markdownlint, wrapped-inline-code, `check_doc_links`, and surface
  length-cap constraints in one pass (reusing the real validators), so the doc
  passes `check-markdown.sh` / `check_doc_links.py` first try instead of one
  serial rejection at a time. Affordance only — the doc still commits without it.
- When deleting a public symbol or named concept, run
  `python3 scripts/check_symbol_residue.py --repo-root .` before closeout. It is
  advisory by design (#259): it scans deleted Python symbols and common phrase
  variants across `docs/` and `skills/`, then leaves intentional historical
  mentions to human judgment. For a concept that is not derivable from a deleted
  Python name, pass `--concept "<name>"` or `--symbol <name>` explicitly.
- Never stop a background process with a loose `pkill -f <pattern>` — the pattern
  can match your own replacement/parent command and kill it (observed: a stray
  poll loop's `pkill` killed the in-flight goal flip). Target by PID, or use the
  harness `TaskStop` for background tasks.
- Prefer deleting drift over documenting drift.
- Current-pointer helpers should be no-op when canonical content has not
  changed. If a startup or inventory command rewrites an artifact without a
  canonical change, treat that as invocation drift or a helper bug.
- Treat `mutate -> sync -> verify -> publish` as hard phase barriers.
- After a command rewrites generated surfaces, plugin exports, versioned
  manifests, or git state, finish that phase before starting validators or
  publish steps.
- Use parallel tool calls only for read-only inventory or file inspection;
  never run sync, export, bump, install, update, or git mutation commands in
  parallel with validators, closeout, or publish steps.

## Floor-Addition Restraint

The repo's reflex to an observed waste is "add one more deterministic floor."
That reflex is asymmetric: it over-applies blocking teeth where they create
authoring churn (the validator-post-hoc-churn class, spec
[achieve-efficiency-improvements](../../charness-artifacts/spec/achieve-efficiency-improvements.md)
Problem 1) while real recurrences stay teeth-less. Before adding a **new
deterministic blocking floor** (a gate that refuses closeout/commit), run this
checklist and record the call:

1. **Does it raise closeout-contract weight?** A new required field/section/form
   the author must satisfy up front is Problem-1 cost: it is one more shape an
   author discovers by failing the flip. If yes, the bar to add it is higher, not
   lower.
2. **Is advisory/prose enough?** Default to a **non-blocking advisory** (stderr +
   durable payload, like the over-slice and gate-runtime advisories in
   [slice_closeout_advisories.py](../../scripts/slice_closeout_advisories.py)).
   Promote to a blocking floor only when prose has a **recorded recurrence count**
   (the lesson kept decaying and recurring) — not on first sight. An advisory that
   false-fires trains token-theater; so does a premature floor.
3. **Can an existing describe-first preflight absorb it?** If the concern is "the
   author did not know the required shape," the fix is usually to surface it in the
   describe-first closeout preflight
   ([describe_goal_closeout_shape.py](../../skills/public/achieve/scripts/describe_goal_closeout_shape.py))
   so it is seen up front, **not** a new serial gate. A floor the author meets
   only as a reactive end-gate is the churn pattern; a floor the preflight lists is
   absorbed. Caveat: today's preflight renders a **static catalog**, so it can
   absorb only *static or form-shaped* floors. A *goal-conditional* floor (one that
   needs runtime evaluation of the specific artifact) cannot be absorbed by the
   current preflight — that is A2 (deferred); such a floor stays a `keep` gate, and
   adding one is a `keep`, not an `absorb`.

Prefer advisory or describe-first absorption over a new blocking floor unless the
recurrence is recorded. The standing closeout floors are audited (with an
`absorb`/`merge`/`keep` call each) in
[closeout-floors audit](../../charness-artifacts/audit/closeout-floors.md);
consult it before adding a sibling floor that an existing one could merge.

**Teeth (non-blocking).** This checklist is prose and shares the decay risk it
guards against, so a deterministic **non-blocking** nudge gives it the intended
(advisory) teeth: `advise_floor_addition_restraint` in
[slice_closeout_advisories.py](../../scripts/slice_closeout_advisories.py)
(wired into `run_slice_closeout.py`) runs a conservative before/after detector
over the slice diff and, when it sees a **new** blocking floor — a new
`report["ok"] = False` site or a new `REQUIRED_*` / `_SECTIONS` / `_EVIDENCE_NAMES`
member in `skills/`/`scripts/` source — *without* a recorded restraint call, it
prints an advisory naming this checklist. **Record the call** to silence it (and
to leave the durable provenance): a `Floor-Addition Restraint:` line in the
slice's commit/goal/critique, or a `# floor-addition-restraint: <call>` comment at
the floor site. The detector is deliberately conservative (a probe): exotic floor
shapes may escape it — a missed nudge beats a false one that trains token-theater.
A *blocking* enforcement gate for this rule is deliberately rejected: it would be
the exact reflex the rule names.

## Generated And Installed Surfaces

- **Portability classification is a closeout checkpoint, not an optional
  nicety.** It fires for two scopes, not one:
  - a *new reusable mechanism* — a repo-root `scripts/*.py`, a new gate, or a
    generalizable pattern/doctrine (an invariant, failure mode, or cost lesson);
  - an *improvement, issue, or policy* whose resolution should be inheritable by
    charness-consuming repos — a new operating rule, a contract, a lint/check, or
    a lesson that other repos would also want.

  For either scope, classify it `host-local` vs `skill-capability` before
  closeout and state the call. In this harness repo do **not** default to
  repo-local: if the mechanism, policy, or doctrine generalizes, route it to the
  owning public skill or reference (at minimum a `references/*.md` doctrine line,
  a `quality`/skill capability, or a packaging/[AGENTS.md](../../AGENTS.md)
  absorption) so adopting repos inherit it, not just charness. A soft "inspect
  whether a skill should absorb the lesson" version of this rule already existed
  and still did not fire during a defect-repair slice — the low-altitude framing
  of defect, improvement, or issue work keeps the call out of view — so make the
  classification explicit rather than remembered. The narrower code-mechanism-only
  reading is exactly why a portable policy nearly shipped repo-local; see the
  [portability-miss retro](../../charness-artifacts/retro/2026-06-07-premerge-gate-portability-miss.md).
  A deterministic nudge (flagging a new repo-root capability script that belongs in
  a skill) is a tracked follow-up: `follow-up:portability-classification-tripwire`.
- If a public skill needs repeated bootstrap, adapter resolution, artifact
  naming, or recovery behavior, ship a helper script instead of leaving it as
  prose-only guidance.
- When tool install, update, or support-sync work is partly manual or mutates
  the operator surface, emit structured output and persist machine-readable
  state so a later agent can continue without rediscovering the machine.

## Sync Before Validation

- Repo-owned diff obligations and closeout stay downstream of generated-surface
  sync.
- If checked-in plugin export is touched, run
  `python3 scripts/sync_root_plugin_manifests.py --repo-root .` before
  validators.
- A pre-commit gate
  ([check_staged_mirror_drift.py](../../scripts/check_staged_mirror_drift.py),
  wired in `.githooks/pre-commit`) blocks committing when exported source is
  staged but its regenerated `plugins/` mirror is not — it archives the staged
  index (`git write-tree`) and validates that snapshot, catching both "forgot to
  sync" and "synced but forgot to stage the mirror" at commit time instead of
  post-commit at `validate_packaging_committed` (#257). Still stage the
  regenerated mirror (`git add plugins/ .claude-plugin/ .agents/plugins/`)
  alongside the source.
- A commit-message gate
  ([check_issue_closeout_commit_msg.py](../../scripts/check_issue_closeout_commit_msg.py),
  wired in `.githooks/commit-msg`) blocks commits that stage issue closeout
  artifacts with `Close #N` keywords unless the final commit message carries
  those keywords and the required closeout ledger. `pre-commit` cannot enforce
  this because it does not see the final message.
- Machine-local discovery output under `.agents/charness-discovery/` is not a
  checked-in surface; generated local stubs should not be committed as drift.
