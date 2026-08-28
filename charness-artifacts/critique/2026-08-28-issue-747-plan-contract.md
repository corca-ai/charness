# Critique record: 747 distribution plan, lifecycle correctness

> Date: 2026-08-28
> Reviewer: bounded-reviewer subagent (opus, explicit model override)
> Target: the rev 1 plan; all blockers and should-fixes dispositioned in rev 2

I've verified the plan's claims against the actual repo. Here is the report.

## Fresh-eye critique: issue #747 distribution plan — lifecycle correctness and failure modes

Fresh-eye context: `parent-delegated`. Envelope status: **`envelope-unbound`** — I can still see Bash, Edit, Write, and Agent tools in my inventory, so the host did not bind the read-only envelope for this spawn. I followed the read-only restrictions as hard instructions anyway; I made no writes, no git index mutations, and spawned no sub-agents.

Target: `/home/hwidong/codes/charness/charness-artifacts/design-studies/2026-08-28-issue-747-distribution-plan.md`

---

### Blockers

**B1. D2 and D3 are mutually exclusive as written: bumping the crate version breaks `cargo build --locked`.**
D3 says the crate version is synced to `packaging/charness.json`'s version by the release bump; D2 says the artifact is built with `cargo build --release --locked`. But `Cargo.lock` records the workspace member's own version:

```
/home/hwidong/codes/charness/native/repograph/Cargo.lock:470-472
[[package]]
name = "repograph"
version = "0.1.0"
```

`native/repograph/Cargo.toml:3` is `version = "0.1.0"` while `packaging/charness.json:5` is `8.0.0`. The moment the bump rewrites `Cargo.toml` to `8.0.1` without also rewriting that lock entry, `--locked` refuses with "the lock file needs to be updated". Regenerating the lock requires cargo on the bump machine, which the plan wants to avoid, and the plan's release check ("prove Cargo.toml version matches without requiring cargo") checks the wrong pair. Smallest fix: have the sync step rewrite both the `Cargo.toml` `version` and the `Cargo.lock` `[[package]] name = "repograph"` version block as text, and make the release check assert all three of packaging version, Cargo.toml version, and the lock's own-package version agree. That check is pure text and needs no cargo.

**B2. The release flow pushes the version-bearing branch before the release exists, so there is a guaranteed window where no consumer can satisfy D5.**
In `/home/hwidong/codes/charness/skills/public/release/scripts/publish_release_resume_publish.py:191` the branch and tag go out in one command:

```python
cli.run(["git", "push", args.remote, branch, tag_name], cwd=repo_root)
```

and `create_release` only happens afterward at line 198; asset upload would be later still. Consumers track a branch (`ensure_checkout` runs `git pull --ff-only`, `charness:1206`), not a tag. So from the instant of that push, every `charness update` fast-forwards to a checkout whose `packaging/charness.json` says version N while release N does not exist and its artifact has not been uploaded. D7 then classifies that as `stale` (pointer version ≠ checkout version) with remediation "run update" — advice the consumer just followed and which cannot succeed. If `create_release` or the upload fails (this repo has `publish_release_rollback.py` and elaborate resume machinery precisely because that happens), the window is unbounded. D5's phrase "the artifact for the checkout's release tag" is also undefined for a checkout sitting on an ordinary main commit between releases.

Smallest fix: make `awaiting-artifact` a first-class doctor state, distinct from `stale` and distinct from `offline`, reached when the release for the checkout version is absent or has no matching asset. Its remediation is "wait for the release to publish; the previous core stays active", not "run update". Reordering the publish to upload artifacts before the branch push is the alternative, but it means editing `publish` in a heavily-commented critical path the plan does not scope, so I recommend the typed-state fix.

**B3. D5 step 5's "move into `versions/`" is a cross-device rename on the default configuration.**
The staging temp dir and the state root are on different filesystems by default. `configure_runtime_environment` sets `TMPDIR` and `tempfile.tempdir` to the runtime root (`scripts/runtime_bootstrap.py:148-150,203`), and the runtime root resolves to `XDG_CACHE_HOME` or `TMPDIR` or `tempfile.gettempdir()` (`scripts/runtime_bootstrap.py:96-106`) — on a stock Linux box with neither variable set, that is `/tmp`, frequently tmpfs. The state root is `~/.local/state/charness` (`charness:172-187`). `os.rename` across those raises `EXDEV`; `shutil.move` silently degrades to a non-atomic copy, which is exactly the interrupted-activation case the fixture is supposed to prove. Smallest fix: stage inside the state root (`~/.local/state/charness/native/staging/<version>-<tuple>/`) and write the `current` pointer's temp file into `~/.local/state/charness/native/` so both `os.replace` calls are same-filesystem by construction; assert that in the interrupted-activation fixture rather than relying on host layout.

---

### Should-fix

**S4. D3 names the wrong file for the crate-version sync.** `skills/public/release/scripts/bump_version.py` is deliberately portable and adapter-driven: it knows only `packaging_manifest_path` and `sync_command` from the release adapter (lines 100-128), and its own comment at lines 104-118 explains that repo-specific assumptions there break consuming repos. Charness's `sync_command` is `python3 scripts/sync_root_plugin_manifests.py --repo-root .` (`.agents/surfaces.json:27,42`). The crate-version sync belongs in that sync target, not in `bump_version.py`. Fix: change D3 to say the repo's own sync command gains the Cargo sync, leaving `bump_version.py` untouched.

**S5. No activation lock, and retention can delete the rollback target.** Nothing in the plan serializes two concurrent `charness init`/`charness update` runs against the state root, and the D4 retention rule ("keep the last 2 versions") can prune the very version `charness native rollback` is supposed to return to — for instance when two upgrades land before anyone rolls back. The repo already has the lock-file idiom (`scripts/lesson_ledger_writer_lib.py`, `scripts/check_supply_chain_online.py`, `scripts/standing_pytest_basetemp.py` all use `fcntl`). Fix: take an exclusive lock on a `native/.lock` file for the whole stage-verify-activate-prune sequence, prune only after a verified activation, and never prune the version named by the pointer's recorded predecessor.

**S6. The artifact source is not bound to the checkout's origin.** `REPO_URL` is a module constant (`charness:28`) and `self_release_repo()` regex-extracts `corca-ai/charness` from it (`charness:936-938`) regardless of what the checkout's actual remote is. `charness init --repo-url <local path>` is a supported and tested shape (`tests/charness_cli/test_managed_install.py:75`). As written, a fork or a local clone would fetch and activate the upstream's binary while the identity document claims it belongs to that checkout. Fix: resolve the artifact repo from the checkout's `git remote get-url origin`, and type a `foreign-origin` refusal when it does not match the version's expected source instead of falling back to upstream.

**S7. The existing install tests will start traversing the native phase.** `tests/charness_cli/test_managed_install.py`, `test_managed_install_extended.py`, and `test_managed_install_release_checks.py` run real `charness init` against a seeded repo with `HOME` overridden. D8 promises "no test performs network I/O" for its new fixtures but says nothing about these. The established idiom is the `CHARNESS_RELEASE_PROBE_FIXTURES` env override (`charness:942`, used by four test modules). Fix: add the analogous `CHARNESS_NATIVE_ARTIFACT_STORE` override to D5 explicitly, and add "existing managed-install tests still pass with the native phase present" to D8's list.

**S8. The insertion point straddles a re-exec boundary.** D5 says "after checkout refresh, before reporting success", but both commands re-exec between those points: `maybe_reexec_refreshed_cli` at `charness:4108` (init) and `charness:4253` (update), plus a second `os.execv` at `charness:4130`. A native phase placed before those runs under the *old* CLI and then runs again in the replacement process. It is idempotent by D5 step 2, so this is not a correctness break, but it doubles the download attempt on first upgrade and makes the fixture's "interrupted activation" semantics ambiguous. Fix: name the exact line — after `install_surface` and after the `os.execv` at `charness:4130`, before `build_doctor_payload`.

**S9. The typed `native_core` status will not actually surface at the default response level.** `project_runtime_response` is a strict key allowlist (`charness:4017-4034`) that would silently drop `native_core`, so it would appear only under `--detail`. And "exact remediation" reaching the user means feeding `build_host_next_steps` (`charness:2384-2398`) and `build_doctor_next_action` (`charness:2401-2470`), both of which iterate a hardcoded `("codex", "claude", "grok")` tuple plus `repo_onboarding`. Fix: name these three functions in Lane F's scope and add a `native_core` candidate source to `build_doctor_next_action` with a priority that does not outrank a real host-delivery failure.

**S10. The dev-tree fallback is opt-out where it should be opt-in.** D6 orders the locator override, then the state pointer, then the dev-tree build. During the migration window the state pointer is *normally* absent, so on the maintainer machine — the one machine that runs the gates and has `native/repograph/target/release/repograph` present — the locator silently answers with a stale dev build while every consumer gets `missing`. "Explicitly marked `dev-tree-build`, never claimed as the managed core" is an instruction to callers, not a mechanism. Fix: gate the dev-tree branch behind an explicit `CHARNESS_ALLOW_DEV_NATIVE_CORE=1`, so the default answer on a source checkout with no managed core is `missing`, same as a consumer's.

**S11. D7's consumer obligation has no subjects and cannot be tested in this issue.** D9 states plainly that no gate starts invoking `repograph` in #747. So "Consumers of `native_core_path()` receiving `missing` must report their own claim as unestablished" is a rule with zero enforcement points and zero possible fixtures — it is instruction-following hope, which is exactly what the acceptance criterion "no silent native-claimed-complete" is trying to rule out. What *is* enforceable here is the shape of the return value. Fix: make the locator return a sum type where the non-healthy variants carry no path attribute at all, so a future consumer cannot unwrap `missing` into something executable; then move the consumer-side obligation into #748's acceptance and say so in D7 rather than claiming it here.

**S12. Lane F's declared scope omits a generated surface it will invalidate.** Adding `charness native rollback` changes `./charness --help`, and `docs/cli-reference.md` is generated from that help output — its header reads `<!-- GENERATED: do not edit. Regenerate via python3 scripts/render_cli_reference.py --repo-root . -->` (line 1), with `scripts/check_documented_command_flags.py` enforcing it. Lane F's scope is `charness`, `scripts/**`, `tests/**`, `docs/host-packaging.md`. Fix: add `docs/cli-reference.md` to the parent's post-integration regeneration list alongside the `plugins/` export.

**S13. Digest verification on every resolve is a latency trap.** D6 says the state-pointer branch resolves "verifying digest". A sha256 over a multi-megabyte binary on every `native_core_path()` call will be paid per invocation once #748 lands. This file is already latency-sensitive — see the comment at `charness:986-990` about 17ms of a ~114ms startup budget. Fix: verify the digest at activation and in `doctor`; on the hot resolve path check only that the pointer's recorded size and mtime still match, and treat a mismatch as `corrupt`.

---

### Notes

**N14. Third release-probe implementation.** `charness:986 probe_self_release` already queries `corca-ai/charness` releases/latest and already returns `asset_names`, and `scripts/upstream_release_lib.py:176 probe_github_release` does the same for integration tools (with a `gh`-based path at line 152 that handles auth). D5 step 3 needs exactly this and does not mention reusing either. Given CLAUDE.md's "prefer deleting stale rules, wrappers, gates, mirrors over adding another layer", the plan should name which one it extends.

**N15. `Cargo.lock` is an unrecognized supply-chain surface.** `scripts/supply_chain_lib.py` enumerates only JavaScript lockfiles (line 56) and `uv.lock` (line 186). Shipping a downloadable binary built from pinned Rust dependencies adds a supply-chain surface the existing contract cannot see. The plan should either extend the surface detector or record a typed non-coverage decision.

**N16. `scripts/build_native_artifact.py` would ship to consumers.** `packaging_lib.py:300` copies all of `scripts/` into the plugin export, minus the four names in `SOURCE_ONLY_PLUGIN_SCRIPTS` (`packaging_lib.py:42-46`). A cargo-invoking build script landing in the consumer plugin tree is harmless but reads against "no Cargo for consumers". Add it to that tuple.

**N17. Read-only state root.** `write_version_state` swallows `OSError` deliberately — "Version probes must stay usable even when host-local state is read-only" (`charness:844-846`). The native phase needs the same degradation path; the plan does not mention it.

**N18. Release rollback has no native-artifact story.** `skills/public/release/scripts/publish_release_rollback.py` exists; the plan does not say what happens to consumers who already activated a core from a release that is subsequently rolled back.

---

### Claims I checked that hold up

Worth recording so the parent does not re-verify: D6's export path is real — `plugins/charness/scripts/runtime_bootstrap.py` exists in the checked-in export, so `native_core_path()` genuinely reaches installed skills. `native/.gitignore` already contains `target/`, so cargo build output will not trip the untracked-path gates. The state-root helpers D4 depends on exist (`default_state_root`, `charness:186`) and `CHARNESS_STATE_HOME` (`charness:173`) gives the fixtures a clean redirect. The `charness native rollback` shape matches the existing `capability`/`tool`/`worktree` subparser groups. And D8's fake-`gh` precedent is real and the managed-install harness (`tests/charness_cli/test_managed_install.py:59-80`) already runs a full real `init` under an overridden `HOME`.

---

### Verdict

**No** — not sound to execute after should-fixes alone. B1, B2, and B3 are design changes rather than wording changes: B1 makes the D2/D3 pair unbuildable, B2 makes D7's state machine give consumers advice that cannot work during a window the current release flow guarantees on every release, and B3 makes D5's atomicity claim false on a common default host layout. Revise D2/D3, D5, and D7 for those three, fold in S4-S13, and the plan is then sound to execute.
