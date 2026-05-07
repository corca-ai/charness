# Premortem: Issue #111 init-repo Inspector Worktree-Adapter Precondition

Date: 2026-05-07

## Decision

Close GitHub issue #111 with a compact repo slice that closes the inspector's
silent gap when a Node-style hook manager exists without
`.agents/worktree-adapter.yaml`:

- add `_detect_worktree_adapter_normalization` to
  `scripts/init_repo_agent_docs_lib.py`. Detect `lefthook.{yml,yaml}`,
  `.husky/`, and `package.json` with a `simple-git-hooks` key. When a hook
  manager is detected and the adapter is missing, emit a structured finding
  and a typed `seed_artifact` recommendation pointing at
  `seed_worktree_adapter.py`.
- promote init-repo-adapter absence from a `resolve_adapter` warning to an
  inspector-visible advisory recommendation (Optional 1) so preset
  provenance becomes a real nudge instead of a wall-of-warnings line.
- expose both blocks under `agent_docs.normalization.worktree_adapter` and
  `agent_docs.normalization.init_repo_adapter`, and merge their recommendations
  into the existing top-level `recommendations[]` so consumer agents see a
  ranked actionable list, not a silent `recommendations: []`.
- keep the `seed_worktree_adapter.py` template untouched; the
  `--package-manager` flag from the issue's optional follow-up #2 is deferred
  to a separate slice to keep this one focused on the detector gap.

## Likely Misread

A future operator could misread the new `init_repo_adapter_missing`
recommendation as a hard "this repo is broken" gate when in practice it is an
advisory nudge that defaults still work. The recommendation entry carries
`priority: advisory` and `kind: seed_artifact`, and the suggested action
explicitly names "preset provenance" rather than "blocker." The worktree
recommendation uses `priority: medium` because a fresh worktree genuinely
fails to install hooks without the adapter, which is the strongest signal
this slice can give.

## Counterweight Triage

Act Before Ship:

- Use deterministic structural detection (`lefthook.{yml,yaml}`, `.husky/`,
  `package.json[simple-git-hooks]`) instead of probing live git state, so the
  inspector stays cheap and offline.
- Surface the new state vectors at `agent_docs.normalization.worktree_adapter`
  and `agent_docs.normalization.init_repo_adapter` so consumer agents have a
  machine-readable answer in addition to the recommendation list.
- Pop `extra_recommendations` after merge so it does not appear as duplicate
  state alongside the post-filter `recommendations[]`.

Bundle Anyway:

- Add seven regression tests covering each detector branch (lefthook, husky,
  simple-git-hooks, adapter present, no hook manager) plus init-repo-adapter
  present/absent.
- Run the full `tests/quality_gates` and `tests/control_plane` surfaces
  after sync to catch any payload-shape break in adjacent inspector tests.

Over-Worry:

- Do not lift `agent_docs.recommended_action` from `leave_as_is` to
  `seed_worktree_adapter` — that field is about AGENTS.md/CLAUDE.md state,
  and conflating two concepts would break existing consumers. The
  recommendation entry on `recommendations[]` is the right surface.
- Do not turn the worktree recommendation into a `review_required` priority;
  defaults still install for non-hook-managed repos, and the advisory tier
  is honest about the state.
- Do not template-rewrite `seed_worktree_adapter.py` to detect package
  managers in this slice. Optional follow-up #2 is real but deserves a
  separate matrix decision (pnpm/npm/yarn × bundled/system lefthook ×
  husky/lefthook/simple-git-hooks).

Valid But Defer:

- `--package-manager {pnpm,npm,uv,none}` flag on `seed_worktree_adapter.py`
  with a detector-aware default body — defer to a follow-up slice.
- A `worktree doctor`-vs-`init-repo` cross-check fixture that proves the two
  inspectors agree on the same hook-manager state under non-default
  `core.hooksPath` — defer until a real disagreement is reported.

## Fresh-Eye Satisfaction

parent-delegated

This is a deterministic local-risk slice (inspector detection plus a typed
recommendation entry). Deterministic validators and the seven new regression
tests cover the behavior contract. No bounded reviewer subagent was spawned
because the slice does not change prompt-affecting surfaces or public-skill
ergonomics, and Cautilus stays `disabled` by repo adapter.

## Scenario Review

Consumer prompt:

> Apply `init-repo` to this repo. It uses lefthook for git hooks and has no
> `.agents/worktree-adapter.yaml` yet.

Expected result:

- `inspect_repo.py` returns `agent_docs.normalization.worktree_adapter.hook_manager_detected: "lefthook"`
- `recommendations[]` contains an entry with `id: worktree_adapter_missing_for_hook_manager`,
  `target: .agents/worktree-adapter.yaml`, `kind: seed_artifact`,
  `priority: medium`, and `suggested_action` pointing at
  `seed_worktree_adapter.py`
- a non-init-repo-adapter repo also gets an advisory `init_repo_adapter_missing`
  recommendation that names preset provenance instead of staying buried in
  `adapter.warnings[]`

Observed decision:

- `tests/quality_gates/test_init_repo_inspect_policy.py` extends the suite
  with seven cases that lock in the contract above; all 30 inspector tests
  pass and the broader 435-test `tests/quality_gates` plus 48-test
  `tests/control_plane` surfaces stay green.
- Cautilus remained disabled by repo adapter; deterministic validators and
  this scenario review are the accepted proof for this slice.
