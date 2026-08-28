# Critique record: 747 distribution plan, operability/blast-radius

> Date: 2026-08-28
> Reviewer: bounded-reviewer subagent (opus, explicit model override)
> Target: the rev 1 plan; all blockers and should-fixes dispositioned in rev 2

Fresh-eye satisfaction: parent-delegated

## Reviewer Tier Evidence

- Requested tier: bounded read-only fresh-eye critique (repo
  bounded-reviewer envelope, one assigned lens)
- Requested spawn fields: host `bounded-reviewer` subagent type
  (Read/Grep/Glob only), shared parent worktree, lens-scoped prompt;
  explicit model override `opus`
- Host exposure state: applied
- Application state: host-confirmed: the subagent transcript metadata
  records model=opus for this spawn.
- Execution mode: typed-subagent
- Delivery state: findings-received

## Boundary Ownership

- Verdict: single-surface
- Producer: the reviewed design document (one plan file in this repo).
- Consumer: the parent orchestrating session revising that plan.
- Owning surface: charness-artifacts design study; findings were
  dispositioned in the plan revision, no state moved across surfaces.

I completed the review by reading the plan and then verifying each of its claims against the live repo surfaces. Envelope check: only Read/Grep/Glob were available, so the bounded envelope bound for this spawn. Fresh-eye context: `parent-delegated`. I did not need any command output or prior-version reads.

# Critique of the #747 distribution plan — simplification, operability, blast radius

Target: `/home/hwidong/codes/charness/charness-artifacts/design-studies/2026-08-28-issue-747-distribution-plan.md`

## Blockers

**1. The rollback command produces a state the plan itself classifies as broken.** (D5, D8, acceptance traceability)

D3 binds the native core version to `packaging/charness.json`'s version, and D7 defines `stale` as "pointer version ≠ checkout version". `charness native rollback` re-points `current` at the *previous* version while the checkout stays where it is — so a successful rollback lands exactly in the `stale` state doctor is supposed to remediate. The real remediation for a bad core is to roll the checkout back and re-run `charness update`; the binary is version-bound to the source, so moving it alone is incoherent by construction.

Smallest fix: delete the command. Keep the previous version directory on disk so `update` can re-activate an already-present, already-verified version without network. The acceptance bullet ("rollback with interrupted/invalid fixture") is still satisfied by two fixtures: the interrupted activation (temp staged, rename never happened, prior core still active) and a checkout pinned to the older version where `update` re-activates from disk with no fetch. This also deletes the entire obligation set in finding 3.

**2. Lane E's declared scope does not contain the file D3 requires it to edit, and that file must not be edited at all.** (D3, Execution shape)

D3 says "the bump script gains one more sync target". That script is `/home/hwidong/codes/charness/skills/public/release/scripts/bump_version.py:53` (`write_packaging_version`), and it is exported to `/home/hwidong/codes/charness/plugins/charness/skills/release/scripts/bump_version.py`. Lane E's scope is `native/**`, `scripts/**`, `packaging/**`, `tests/**` — `skills/public/**` is absent, so the work is either unassigned or written out of scope.

The deeper problem is that `bump_version.py` is a *portable* public-skill script that ships to consumer repos which have no `native/repograph`. Teaching it about a Rust crate path puts charness-specific knowledge into a shared surface and pulls in the `skill-packages`, `public-skill-policy`, `public-skill-dogfood`, and plugin-export obligations (`.agents/surfaces.json:187-211`, `:270-310`).

Smallest fix: don't sync the crate version at all. D3 already says the product version is the only version truth, so `native/repograph/Cargo.toml:3` is not a version owner — leave it. Have `build_native_artifact.py` read the product version from `packaging/charness.json` and stamp it into `artifact.json`. That deletes a sync target, its verification, a portable-skill edit, a plugin mirror, and four surface obligations in one stroke.

## Should-fix

**3. Five generated/registry surfaces a new subcommand obligates, none named in the execution shape.** If `charness native rollback` survives finding 1, it requires: an entry in `.agents/command-docs.yaml` (pinned as `cli_skill_surface_command_docs` at `.agents/release-adapter.yaml:28-29`); a regeneration of `docs/cli-reference.md` (`docs/cli-reference.md:11`); a regeneration of `charness-artifacts/capability-catalog/latest.{md,json}`, because the capability-catalog surface lists `charness` as a source path (`.agents/surfaces.json:214-235`) and its verify includes `validate_current_pointer_freshness.py`; an entry in `.agents/cli-side-effect-probes.json`, whose `coverage_scope` (line 3) covers *every* root command that mutates managed-install state; and advisory entries in `.agents/command-registry.json` / `command-archetypes.json`. Fix: cut the command, or add all five to lane F's scope and the parent's post-integration sync list.

**4. The typed `native_core` status will be invisible in default output.** `project_runtime_response` (`charness:4017-4034`) copies a fixed allowlist of keys and drops everything else unless `--detail` is passed. D5 and D7 both promise a typed `native_core` field in the operational response; as written it appears only under `--detail`. Fix: add `native_core` to that tuple with a small `_compact_*` projector modeled on `_compact_host_refresh` (`charness:3981-4000`).

**5. The state-root layout is right, but the path derivation and test isolation are a live hazard.** Nothing collides — `default_state_root` (`charness:186`) holds only `install-state.json`, `host-state.json`, `version-state.json` — but the plan restates the layout as `XDG_STATE_HOME`/`~/.local/state` instead of naming the function, which silently drops the `CHARNESS_STATE_HOME` override at `charness:173-175`. Worse: `resolve_state_home` prefers the *environment's* `XDG_STATE_HOME` over the passed `home_root`, and the CLI fixtures copy `os.environ` and set only `HOME` and `PATH` (`tests/charness_cli/support.py:182-184`) while hardcoding `home_root/.local/state/charness/*.json` (`support.py:139-146`). On any machine with `XDG_STATE_HOME` exported, a test run writes into the developer's real state root. Today that misplaces three small JSON files; under #747 it would write multi-megabyte binaries there and replace the developer's live `current` pointer. Fix: derive from `default_state_root(home_root)`, pin `CHARNESS_STATE_HOME` in the fixture env dicts, and refuse a resolved native root that escapes an explicitly-passed `--home-root` — the refusal precedent already exists at `scripts/runtime_bootstrap.py:86`.

**6. The session-scoped test seed runs a real `charness init`, so D8's "no test performs network I/O" is false unless the phase is inert.** `tests/charness_cli/support.py:169-192` builds a cached managed home by actually running `charness init`. Once init grows a native phase, every test that depends on that seed pays a fetch attempt at seed-build time. Fix (this is also the answer to "should the phase be a no-op stub behind a flag in v1" — yes, but the switch should be a declaration, not a hidden flag): gate the entire phase on `packaging/charness.json`'s `native_core` declaring an artifact for this version and tuple. Undeclared means typed `not-distributed`: no network, no state writes, no fixture plumbing.

**7. Nothing refuses, or even notices, a release published without the artifact.** Publication is `gh release create --verify-tag --notes-file` run by an agent on a maintainer machine (`skills/public/release/scripts/publish_release_helpers.py:186-195`); there is no `.github/workflows/release.yml`. D2 adds a wholly new build-and-upload step to that flow, D7 says a missing artifact does not fail install, and D9 says nothing consumes the binary yet — so a forgotten build step ships a silently incomplete release that no one observes until #748 lands.

The fix is nearly free, because the machinery already exists: `probe_self_release()` already returns `asset_names` (`charness:962-977`), `.agents/release-adapter.yaml:13` already runs `charness version` as the post-publish readback, and `make_release_fixture` (`tests/charness_cli/support.py:61-116`) already carries an `assets` list to fixture it against. Assert that `repograph-v<version>-<tuple>.tar.gz` appears in `asset_names` whenever packaging declares `native_core`, and add one `real_host_checklist` line requiring `native_core: healthy` after the post-publish `charness update`. No new gate, no new script.

On the second half of the question: yes, D2 as written creates a release-blocking dependency on one maintainer's Linux machine carrying the pinned Rust 1.96.0 toolchain. Bound it with the same declaration from finding 6 — a release from a machine without cargo can honestly publish with `native_core` undeclared for that version (typed `not-distributed`) rather than either silently shipping nothing or being hard-blocked.

**8. CI has no Rust toolchain and none is proposed.** `.github/workflows/quality-core.yml:44-64` sets up Python, Node, npm deps and ruff — that is all. Any lane E test that shells out to `cargo` fails there. Fix: state explicitly that `build_native_artifact.py`'s tests fake the cargo invocation (the repo idiom is the fake-binary fixtures under `tests/charness_cli/fixtures/fake_*.py`), and that real build proof is a recorded maintainer-host artifact rather than a gate.

**9. Lane F's headline fixtures are excluded from the default closeout gate.** The `repo-python` surface note says plainly: "Release-only install/update lifecycle tests are excluded from the standing Python closeout gate" (`.agents/surfaces.json:878`). D8's entire battery is install/update lifecycle. A green closeout would not have run any of it. Fix: name the explicit pytest node set in the parent's per-lane verification, don't rely on `run_standing_pytest --mode read-only`.

## Notes

**10. `repograph --version` is neither additive nor needed — and cutting it removes #747's only `native/**` touch.** `ABI.md:32-35` types an unknown option as a usage error, exit 2, so adding `--version` changes a frozen top-level contract and requires an ABI.md amendment lane E does not list. It also buys nothing at install time: the digest chain (SHA256SUMS fetched for the release tag, then sha256 of the staged file) already binds the binary to its version, and D5's other smoke command, `parse-corpus --help`, already proves it executes on this host (exit 0 per `ABI.md:32`). Cutting it means #747 stops touching `native/**` entirely, which dissolves the lane E ↔ #746 serialization the execution shape imposes.

**11. Per-call digest verification (D6) costs more than it proves.** The pointer is written by the same process tree that verified the file. Verify at activation and in `doctor`; at locator time compare `(size, mtime_ns)` against values recorded in the pointer and fall back to a full digest only on mismatch. Keep the typed `corrupt` result either way.

**12. `CHARNESS_NATIVE_CORE` is only a footgun if doctor reports the pointer while consumers run the override.** Fix: doctor resolves through the same locator and reports `provenance`, with `override` and `dev-tree-build` as their own reported states that are never `healthy`. Precedent for refusing rather than trusting an env-supplied path already exists at `scripts/runtime_bootstrap.py:86` and in `require_repo_local_helper` (`scripts/helper_provenance_lib.py`).

**13. "One locator" is one seam short of covering skills.** There are two bootstrap modules with disjoint export lists: `scripts/runtime_bootstrap.py` (repo scripts, root shim at `runtime_bootstrap.py:18-40`) and `scripts/skill_runtime_bootstrap.py` (skill scripts, shim at `skill_runtime_bootstrap.py:18-34`). Adding `native_core_path()` to the first does not reach skill scripts. Also, `runtime_bootstrap` is imported by every Python entrypoint and this repo measures that cost — `charness:987-990` documents 17ms of a 114ms startup spent on one import. Keep the locator's imports lazy and say explicitly which seam skills use.

**14. Doctor can report `healthy` while the core is stale relative to the source.** The managed checkout tracks branch HEAD, not a tag: `init.sh` clones HEAD and `ensure_checkout` does `git pull`. `packaging/charness.json`'s version only changes at release, so on main between releases the pointer version equals the checkout version while the source is N commits ahead of the tag the artifact was built from — and D7's `stale` is pure version inequality, which cannot see it. D2 already records the git tag and commit in `artifact.json`; use it. Doctor compares the artifact's commit against `checkout_git_head`, which is already in the payload (`charness:2750`), and reports `stale (ahead-of-artifact)` rather than `healthy`. This bites #748's consumers, but the honest-claim obligation is #747's.

**15. `uninstall`/`reset` would leave the binaries behind.** `cmd_uninstall` (`charness:4481-4538`) removes the plugin root, codex cache, wrapper and `host-state.json`, but not the state root's other files and, as drafted, nothing under `native/`. It would strand the largest artifact charness ever writes, and `charness reset` (an alias, `charness:4541-4542`) would not clear a corrupt core. Fix: remove `<state_root>/native/` and report `removed_native_core`.

**16. Don't build a third atomic pointer writer.** `scripts/current_pointer_writer_lib.py:20-59` already does exactly D4's design — temp file, `os.replace`, JSON variant, plus the subtlety of replacing an existing symlink without following it — and `scripts/refresh_current_pointer.py` owns the symlink-style variant. D4 describes the mechanism without citing either.

**17. `build_native_artifact.py` will trip the scan-hygiene gate on its first run.** The `python-scan-hygiene` surface (`.agents/surfaces.json:914-930`) requires any repo Python that traverses the filesystem to be gitignore-aware, and this script walks `native/repograph/target/`, which is gitignored.

## Riskiest file, and where the code should live

The riskiest file the lanes touch is `charness` itself — for an unusual reason. `check_python_lengths.py:146-158` gates `scripts/*.py` at 480 code lines, skill helpers at 360, and tests at 800, matching by glob; the root `charness` matches none of them, so it is the one Python file in the repo with no length cap. Lane F can accrete several hundred lines of staging, verification, activation and doctor-state logic there and no gate will object. Put the lifecycle in a capped `scripts/native_core_lib.py` and keep `charness` to command wiring and payload assembly.

Second-riskiest is `scripts/runtime_bootstrap.py`: every Python entrypoint imports it, it has two root shims with hand-maintained export lists, and it is mirrored into `plugins/charness/scripts/`.

On the execution shape's own question: yes, the plan correctly reserves `plugins/` sync and gate runs to the parent. `scripts/**` is a source path of the `checked-in-plugin-export` surface deriving `plugins/charness/**` plus both marketplace files, synced by `sync_root_plugin_manifests.py` and verified by `validate_packaging.py` and `validate_packaging_committed.py` (`.agents/surfaces.json:5-45`). Touching `charness` and `scripts/**` also selects `repo-python` (lint, lengths, attention-state, test-copy invariants, boundary-bypass ratchet, shell lint, standing pytest) and `python-scan-hygiene`.

## Sequencing

Land **F before E**, with the packaging declaration from finding 6 as the switch. With the declaration absent, lane F is provably inert on main: no network, no state writes, a typed `not-distributed` line in doctor, and its full fixture battery already proven against a local directory artifact store (which D8 already specifies). Lane E then lands the build script, the upload step, and the declaration together, and that single commit is what turns the path on. The reverse order puts a new release-time upload step on main whose output nothing can install or verify, which is a strictly longer half-distribution window.

## Smallest-complete v1

Keep: the `native_core` object in `packaging/charness.json` (tuple list plus the per-version artifact declaration that acts as the switch); `scripts/build_native_artifact.py` producing the tarball, `SHA256SUMS`, and an embedded `artifact.json` whose version comes from the packaging manifest; one `gh release upload` step plus the `asset_names` assertion in the existing post-publish readback; `scripts/native_core_lib.py` doing stage → verify (sha256, tuple, version, `parse-corpus --help` smoke) → atomic activate via the existing `write_current_pointer_json`, retaining the previous version directory; `native_core_path()` with typed provenance; the init/update phase call, the doctor section, the compact-projector entry, and the uninstall cleanup; and D8's fixtures minus the rollback command, plus an offline re-activation case.

Cut: `charness native rollback` and its five registry/generated-surface obligations; "keep the last 2 versions" as a policy (keep exactly "the previous one"); `repograph --version` and the ABI amendment it drags in; the `Cargo.toml` version sync and the portable-skill edit it requires; and per-call digest verification.

## The single biggest simplification

Make the packaging manifest's `native_core` declaration the one switch that turns the whole native phase on. One declaration decides whether init/update fetches anything, whether doctor reports `not-distributed` or a real state, and whether the release flow must carry an artifact. It replaces the flag-stub question, decouples lane F from release timing so F can land first and inert, keeps the session test seed network-free with no fixture plumbing, and gives the release process the answer it currently lacks to "was an artifact required here?"

## Proportionality verdict

The objective is proportionate — a version-bound binary genuinely needs staging, checksum verification, atomic activation, and typed absence, and none of that exists in this repo today (`git pull` is the entire current update mechanism). The plan as drafted is roughly a third over-built for a v1 with no consumer: it adds a subcommand whose success state its own model calls unhealthy, a second version-sync target the design says is not a version owner, an ABI change that buys nothing the digest chain does not already prove, and a retention policy ahead of any need. Two of those are blocker-level, and there is a set of generated-surface obligations the execution shape does not name.

Recommendation: approve the objective and D1/D4/D6/D7 broadly, require the cut list and the declaration switch, re-sequence to F → E, and re-scope lane E away from `skills/public/**` and `native/**` entirely.
