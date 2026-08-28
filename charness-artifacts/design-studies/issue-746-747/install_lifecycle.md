I now have a complete picture of the lifecycle. Here is the report.

## 1. init.sh

`init.sh:1-49` is the entrypoint people curl/run first. It has no version pinning of its own:

- `MANAGED_CHECKOUT` defaults to `$HOME/.agents/src/charness` (`init.sh:6`), overridable via `CHARNESS_MANAGED_CHECKOUT`.
- `REPO_URL` defaults to `https://github.com/corca-ai/charness` (`init.sh:7`).
- `ensure_managed_checkout()` (`init.sh:20-36`) does a plain `git clone` of either the repo URL or, if running from an already-cloned dev tree with `packaging/charness.json` and `charness` present, the local `$SCRIPT_DIR` — into `MANAGED_CHECKOUT`. No ref/tag selection logic exists; it just clones whatever `HEAD` the source points at (dev tree = current branch, remote = default branch).
- It then `cd`s into the managed checkout, calls `scripts/bootstrap_runtime.py --print-python` to get/build the bootstrap Python runtime, and `exec`s `./charness init "$@"` inside that checkout. So `init.sh` never runs from a versioned tag — it's always "whatever HEAD `git clone` gives you," and version selection happens later inside `charness init`/`update` (which do `git pull`, not ref pinning, per `ensure_checkout`).

## 2. `charness init` / `charness update`

Both live in the single 5,985-line `charness` script (`charness:4090-4428`).

- `resolve_repo_root()` (`charness:923-929`) picks the source-of-truth repo root: explicit `--repo-root`, else remembered install state, else the managed checkout at `~/.agents/src/charness` (`managed_checkout_root`, `charness:190-191`).
- `ensure_checkout()` (`charness:1195+`) clones (init, `allow_clone=True`) or `git pull`s (update, `allow_pull=True` unless `--no-pull`). This is the only "activation" step — there is no staging directory, no atomic swap, and no rollback: `git pull` mutates the managed checkout in place. If a pull fails partway, there is no documented recovery beyond `charness doctor`/manual git surgery.
- `install_surface()` (`charness:2578+`) materializes host-facing artifacts (Codex plugin dir at `~/.codex/plugins/charness` via `default_plugin_root`, `charness:194-195`; Claude wrapper; CLI at `~/.local/bin/charness`, `charness:230-231`) from the checked-out repo tree.
- `write_version_state()` (`charness:829+`) and `build_version_provenance()` (`charness:1039+`) persist version/provenance under the state root (`default_state_root` → `XDG_STATE_HOME` or `~/.local/state`, `/charness`, `charness:172-187`).
- No rollback command exists. `charness uninstall`/`reset` (`charness:4481-4543`) removes install artifacts but does not revert to a prior version.
- The bootstrap Python runtime (interpreter + site-packages for stdlib-external deps) lives under a *scratch* runtime root, not a persistent versioned asset store — see `scripts/runtime_bootstrap.py:79-113` (`runtime_root()`), which computes `<XDG_CACHE_HOME|TMPDIR|tmp>/charness/runtime/<sha256(repo_root)[:16]>/`, guarded to never be inside the repo. This is scratch/cache space for pycache, tmp, coverage, pip/npm caches — explicitly not meant as a durable release-asset directory (`configure_runtime_environment`, `runtime_bootstrap.py:131-206`).

## 3. `charness doctor`

`cmd_doctor` (`charness:4429-4457`) calls `build_doctor_payload(...)` and emits a typed YAML/JSON operational response (`emit_operational_response`, shared contract used by init/update/doctor for consistent `next_action`/`host_next_steps` fields). Payload includes: checkout version, Codex source/cache-manifest version and drift status, per-host guidance (`codex_host_guidance`, `claude_host_guidance`, `grok_host_guidance`), `repo_onboarding`, and a `next_action` message. There's also a parallel, more generic `charness tool doctor` subsystem (`cmd_tool_doctor`, `charness:4741-4769`) that runs `scripts/doctor.py --tool-id <id>` against declarative manifests under `integrations/tools/*.json` (e.g. `agent-browser.json`), each with `checks.detect` / `checks.healthcheck` (shell commands + `success_criteria`) and a `doctor_disposition` that can block. **This tool-manifest pattern (`integrations/tools/<id>.json` → `lifecycle.install`/`lifecycle.update` + `checks.detect`/`checks.healthcheck`) is the natural existing slot for a native-core doctor check**, but it currently assumes externally-managed binaries (npm/cargo global installs, `command -v` detection, `version_expectation.policy: advisory`) — not a version-bound, repo-shipped asset that must match the exact charness release. A native-core manifest would need a stricter check (`exact-match not advisory`) and a different install mode (fetch/build-from-source, not "run this npm command").

## 4. Plugin export / host install layout

`docs/host-packaging.md` is the authoritative doc. Key facts:

- Shared source-of-truth directories (`skills/`, `profiles/`, `presets/`, `integrations/tools/`) are host-neutral; `scripts/export_plugin.py` + `packaging/charness.json` materialize host layouts. A checked-in generated tree lives at `plugins/charness/` (`docs/host-packaging.md:52-58`).
- Claude/Codex/Grok all consume the **generated, checked-in plugin tree**, not a copy that runs scripts from the managed checkout directly — but `charness init`/`update` install a thin CLI wrapper and manage a **machine-local exported plugin surface** (`~/.codex/plugins/charness`, `~/.grok/plugins/charness`) that is refreshed from the managed checkout (`docs/host-packaging.md:185-211`). So: skills execute from the machine-local exported copy; that copy is refreshed by `charness update` pulling from the managed checkout.
- "One documented runtime locator" isn't an existing named concept I found verbatim, but the closest analog is `runtime_bootstrap.py`'s `runtime_root()`/`configure_runtime_environment()` — the single documented function every Python entrypoint in the repo calls to find its external scratch root — plus `skill_script()` (`runtime_bootstrap.py:236-250`) which is the one documented locator for "find script X inside skill Y, in dev tree OR collapsed export layout." A native-core binary locator would need an equivalent single documented function (e.g., `native_core_path(repo_root)`) resolving dev-tree vs. export vs. installed-plugin layouts consistently, rather than each skill re-deriving the path.
- Host packaging explicitly forbids skill execution requiring network at runtime ("read-only... does not turn skill execution into a networked self-update loop," `docs/host-packaging.md:230-231`) and explicitly has no SessionStart/startup hooks (`docs/host-packaging.md:233-238`).

## 5. Where a versioned asset dir + atomic `current` pointer would live

Nothing in the repo today implements atomic version pointers. Existing root candidates, in order of fit:

- `default_state_root(home_root)` = `XDG_STATE_HOME`/`~/.local/state` + `/charness` (`charness:186-187`) — used for install-state, version-state, host-state JSON. This is the natural home for a **new** `native/` subdirectory holding versioned binaries plus a `current` symlink/pointer file, since it's already the durable (non-cache) per-machine state root charness owns and doctor/init/update already read/write here.
- `runtime_root()` (`scripts/runtime_bootstrap.py:79-113`) is explicitly scratch/cache (pycache, tmp, pip cache) and is documented as safe-to-delete; it should **not** hold a durable versioned binary since nothing currently protects it from being wiped.
- `default_plugin_root`/managed checkout are host-plugin-surface and source-checkout roots respectively — mixing a compiled binary into either would blur "generated artifact" vs. "source of truth" boundaries the packaging doc is careful to keep separate.

## DESIGN CONSTRAINTS

- **Single source of version truth**: `packaging/charness.json` is the only checked-in version authority (`docs/host-packaging.md:19-30, 148-152`); a native-core version must be derivable from/pinned to this, not a second independent version file.
- **No network during skill execution**: skill scripts must not fetch binaries at invocation time; any native-core fetch/build must happen during `init`/`update`, matching the existing "no networked self-update loop" rule (`docs/host-packaging.md:230-231`).
- **Offline/degraded behavior**: every tool manifest pattern in `integrations/tools/` has a `degradation.when_missing` contract; a native core must define an equivalent Python-fallback or explicit-fail path, since Rust cannot be assumed present on consumer machines (per the task).
- **No Rust required on consumer machines**: the crate today is built with `cargo build --release` from source (`native/repograph/README.md:6-13`) and is explicitly a **non-production spike** ("no gate, hook, skill, or export may depend on it," `native/repograph/README.md:3-4`) — issue #747 must change that to prebuilt-binary distribution.
- **No staging/rollback today**: `git pull` in `ensure_checkout` is the entire "update" mechanism with no atomic activation or rollback; a native-core versioned-asset-dir + `current` pointer would be the first atomic-swap primitive in this codebase and should not silently assume the rest of the update flow (checkout refresh) has the same safety.
- **Checked-in plugin tree is read-only / generated-only**: don't put mutable per-machine binaries inside `plugins/charness/` (the checked-in generated tree) — that's a repo artifact, not per-machine state.
- **Host parity**: whatever locator/doctor check is added must work identically across Claude, Codex, and Grok Build consumption paths (`docs/host-packaging.md` Host Mapping section), since skills are shared across hosts.

## OPEN QUESTIONS

- Should the native-core binary be fetched (prebuilt release asset, e.g. GitHub Releases) or built locally with a vendored/offline Rust toolchain during `init`/`update`? The spike crate currently only supports local `cargo build --release --offline` (`native/repograph/README.md:6-13`), which still requires Rust — the opposite of the #747 goal.
- Where exactly does platform/arch selection (linux/macos/x86/arm) fit into the manifest schema — does it reuse `integrations/tools/manifest.schema.json`'s `platforms` array, or does the native core need its own schema given it's repo-built rather than externally-packaged?
- Does `charness doctor`'s existing `doctor_disposition`/blocking-status vocabulary (`BLOCKING_DOCTOR_DISPOSITIONS`, used by `cmd_tool_doctor`) get reused for the native core, or does version-skew (installed binary version != checkout version) need a new disposition category since it's not "present/absent" but "present-but-wrong-version"?
- Should the versioned-asset-dir-plus-`current`-pointer live under `default_state_root` per the analysis above, or does the team want a wholly separate `~/.cache/charness/native/` root (distinct from both state and the scratch `runtime_root()`) to keep large binary caches out of state backups?

Relevant files: `/home/hwidong/codes/charness/init.sh`, `/home/hwidong/codes/charness/charness` (`cmd_init` 4090-4228, `cmd_update` 4231-4426, `cmd_doctor` 4429-4457, `cmd_tool_doctor` 4741-4769, path defaults 172-231), `/home/hwidong/codes/charness/scripts/bootstrap_runtime.py`, `/home/hwidong/codes/charness/scripts/runtime_bootstrap.py`, `/home/hwidong/codes/charness/docs/host-packaging.md`, `/home/hwidong/codes/charness/integrations/tools/agent-browser.json`, `/home/hwidong/codes/charness/integrations/tools/README.md`, `/home/hwidong/codes/charness/native/repograph/README.md`, `/home/hwidong/codes/charness/charness-artifacts/design-studies/issue-745/verdict-2026-08-28.md` (the #745 spike "go" verdict that unblocks #746/#747).