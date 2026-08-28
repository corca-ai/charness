# Lane brief: 747-install (lane F)

Governing contract: read
`charness-artifacts/design-studies/2026-08-28-issue-747-distribution-plan.md`
(rev 2) FIRST and follow it exactly — especially D2 (the `native_core`
declaration switch; with the declaration ABSENT, which it is on main, the
whole phase must be provably inert), D4 (state-root layout, same-filesystem
staging, lock, retention), D5 (insertion point and step order, typed
statuses), D6 (locator sum type), D7 (doctor states + response
projection), D9 (fixture battery and where logic lives). Do not spawn
descendant agents. This lane touches PRODUCTION surfaces of a heavily
gated repo — read the named integration points in the `charness` script
before editing: `resolve_repo_root`, `ensure_checkout`,
`maybe_reexec_refreshed_cli` and the `os.execv` in `cmd_init`/`cmd_update`,
`install_surface`, `write_version_state`, `build_doctor_payload`,
`project_runtime_response`, `build_host_next_steps`,
`build_doctor_next_action`, `cmd_uninstall`, `default_state_root`,
`probe_self_release`; plus `scripts/runtime_bootstrap.py`,
`scripts/skill_runtime_bootstrap.py`,
`scripts/current_pointer_writer_lib.py`,
`tests/charness_cli/support.py`.

## Outcome (this lane only)

1. `scripts/native_core_lib.py` (respect the 480-code-line cap for
   `scripts/*.py` — split into two capped modules if needed): declaration
   reading, tuple detection, staging/verify/activate/prune under an
   `fcntl` lock per plan D4/D5, re-activation-from-disk, typed status
   values, artifact resolution honoring `CHARNESS_NATIVE_ARTIFACT_STORE`
   (local directory store; mirrors the `CHARNESS_RELEASE_PROBE_FIXTURES`
   idiom) and reusing `probe_self_release` asset names for the network
   path, `foreign-origin` refusal from `git remote get-url origin`.
   Pointer writes reuse `current_pointer_writer_lib.py`.
2. `native_core_path()` in `scripts/runtime_bootstrap.py` (lazy imports —
   this module is startup-budgeted) re-exported through
   `skill_runtime_bootstrap.py`: sum-type result per plan D6 (non-healthy
   variants carry NO path), resolution order override → pointer
   (size+mtime_ns hot check, digest on mismatch → corrupt) → dev-tree
   only under `CHARNESS_ALLOW_DEV_NATIVE_CORE=1`. Update both root shims'
   export lists.
3. `charness` wiring only (no lifecycle logic in the script): the phase
   call at the D5 insertion point in `cmd_init` and `cmd_update`; the
   typed `native_core` block in the doctor payload with all D7 states +
   `source_drift`; `project_runtime_response` allowlist entry + compact
   projector (modeled on `_compact_host_refresh`); a `native_core`
   candidate source in `build_doctor_next_action` prioritized below
   host-delivery failures; `cmd_uninstall`/reset removing
   `<state_root>/native/` with `removed_native_core` reported.
4. `packaging/charness.json`: the `native_core` declaration SCHEMA support
   only — do NOT add a declaration for any version (the switch stays off;
   main must be inert). Document the shape in `docs/host-packaging.md`.
5. Fixture battery per plan D9 (pytest under `tests/charness_cli/`, local
   artifact store, `CHARNESS_STATE_HOME` pinned in every fixture env dict
   — also pin it in the existing `support.py` env construction so no test
   can ever write a developer's real `XDG_STATE_HOME`): all thirteen
   cases listed in D9, plus "existing managed-install tests pass
   unchanged with the phase present".

## Verification to run before finishing

- The full new fixture battery plus the existing
  `tests/charness_cli/test_managed_install*.py` modules.
- Focused quality: `python3 -m pytest` on the touched test modules;
  `ruff check` on touched files; `python3 scripts/check_python_lengths.py`
  if runnable standalone. Do NOT run the plugin export sync and do NOT
  touch `plugins/**` — the parent owns generated surfaces and full gates.

## Boundaries and non-claims

- Scope: `charness`, `scripts/**`, `tests/**`, `packaging/**`,
  `docs/host-packaging.md`. Never touch `plugins/**`, `native/**`,
  `skills/**` (including `bump_version.py`), `.agents/**`.
- No new CLI subcommand, no `charness native rollback`, no network in any
  test, no crate changes, no build script (lane E owns it).
- The locator's healthy path has NO consumer in this issue; do not wire
  any gate or skill to it.

## Stop condition and result shape

Stop when the verification passes in your worktree. One coherent commit,
prefix `dist(747):`. Final message: what was built, exact commands +
observed results (test counts), confirmation that main-state behavior is
inert (name the test proving it), any deviation from plan rev 2 with its
reason.
