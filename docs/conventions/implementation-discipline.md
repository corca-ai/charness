# Implementation Discipline

This document owns the validation and mutation rules that are too detailed for
the root instruction file but still apply to Charness maintenance work.

## Validation Discipline

- Repo-owned diff obligations live in [.agents/surfaces.json](../../.agents/surfaces.json);
  use `python3 scripts/check_changed_surfaces.py --repo-root .` to inspect them.
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
  `--produce-mutation-coverage` to the final `--verification-lock` closeout: it
  instruments that one broad pytest run with plain coverage (no double run) and
  emits `reports/mutation/test-coverage.json` plus the `.fingerprint` freshness
  marker the pre-push changed-line gate (`check-changed-line-mutation-coverage`)
  reuses. Without a fresh producer run the gate skips non-blocking, so run the
  producer before a pool-touching push to keep the gate active. To check your own
  uncommitted slice early, run the producer (it stamps the marker over
  base->worktree) then the consumer, or run the consumer over a head that
  includes the worktree — a manual `--head-sha HEAD` dry-run **before commit** is
  a false green (HEAD is the parent, so `base..HEAD` excludes your changes and
  they are judged only post-commit). Also run the cheap doc gates the broad
  pytest enforces (e.g. `python3 scripts/check_spec_evidence_durability.py`)
  before paying for the producer run (retro 2026-06-07).
- Run and record the critique required by
  [operating-contract.md](./operating-contract.md) before final closeout for
  task-completing repo work.
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

## Generated And Installed Surfaces

- **Portability classification is a closeout checkpoint, not an optional
  nicety (retro 2026-06-07).** When a slice adds a *new reusable mechanism* — a
  repo-root `scripts/*.py`, a new gate, or a generalizable pattern/doctrine
  (an invariant, failure mode, or cost lesson) — classify it `host-local` vs
  `skill-capability` before closeout and state the call. In this harness repo do
  **not** default to repo-local: if the mechanism or its doctrine generalizes,
  route it to the owning public skill or reference (at minimum a `references/*.md`
  doctrine line, or a packaging/[AGENTS.md](../../AGENTS.md) absorption) so
  adopting repos inherit it. A soft "inspect whether a skill should absorb the
  lesson" version of this rule already existed and still did not fire during a
  defect-repair slice — the defect-repair frame keeps altitude low, so make the
  classification explicit rather than remembered. A deterministic nudge (flagging
  a new repo-root capability script that belongs in a skill) is a tracked
  follow-up: `follow-up:portability-classification-tripwire`.
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
