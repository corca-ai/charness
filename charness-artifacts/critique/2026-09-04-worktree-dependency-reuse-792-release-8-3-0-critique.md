# Worktree dependency reuse (#792) release 8.3.0 critique

Date: 2026-09-04

## Decision Under Review

Release charness 8.3.0 (minor) carrying one capability: `charness worktree
prepare` links an already-installed dependency tree instead of re-running the
installer (#792). The manifest opt-in `prepare.dependency_reuse` names the
install command, the lockfile, and the installed directory; prepare tries the
parent tree (matching lockfile digest) then the runtime cache keyed by that
digest, `cp --reflink=always` after a one-file probe, then `cp -al`, and skips
the install command when a link held. `task run` lanes inherit it through
`worktree create --prepare`, and `result.json` records the path taken.

## Release Scope

- Version 8.3.0, tag `v8.3.0`, minor: a new additive operator surface (a
  manifest field, a CLI flag, a payload key) that existing consumers adopt
  without migration; nothing renamed or removed.
- For consumers: a worktree whose adapter declares `dependency_reuse` prepares
  in seconds on ext4 instead of a full `npm ci`; the field is absent from every
  existing manifest, so behavior is unchanged until declared.

## Surface-Lock Inventory

- Generated: `docs/cli-reference.md` (`worktree prepare --no-dependency-reuse`),
  the `plugins/charness` mirror through the publish helper.
- Consumer-visible behavior: `charness worktree prepare` and `worktree create
  --prepare` payload key `dependency_reuse`; `task run` `result.json` top-level
  `dependency_reuse`; the `--no-dependency-reuse` flag; the runtime cache tree
  `<runtime root>/worktree-deps/<key>/{tree,meta.json}`.
- Documentation: `docs/worktree-prepare.md` (Dependency reuse section, manifest
  note, consumer setups), `docs/agent-task-runs.md` (result key).
- Adapter surfaces on disk: `integrations/worktree/manifest.schema.json`
  (`prepare.dependency_reuse`), `integrations/worktree/adapter.example.yaml`
  (commented block), the setup seed template
  `worktree_dependency_reuse.yaml.txt` (commented block), and this repo's own
  `.agents/worktree-adapter.yaml` (declared).

## Verification Scope Decision

- Claim under test: with `dependency_reuse` declared, a fresh worktree on a
  non-CoW filesystem gets a doctor-passing installed tree from its parent (or
  the cache) without running the install command, and without it the declared
  command runs exactly as before.
- Changed surfaces: `scripts/worktree/worktree_dependency_reuse.py` and
  `worktree_prepare_lib.py` (new), `worktree_doctor_lib.py` (manifest
  validation, prepare re-export), `worktree_create_lib.py`,
  `worktree_prepare.py`, `charness` CLI, `scripts/task_run/task_run.py` and
  `task_run_support.py`, the schema, example, seed template and its library,
  `.agents/worktree-adapter.yaml`, two docs pages, the CLI reference;
  final consumers are `charness worktree prepare` in consumer repos and every
  `task run` lane in this one.
- Minimum sufficient proof: twenty-four focused tests in
  `tests/charness_cli/test_worktree_dependency_reuse.py` (parent link, digest
  mismatch refusal, cache seed and fallback, existing directory untouched,
  reflink probed on one file, prepare skips the install command, installer runs
  and seeds the cache, a doctor-rejected install is not published, disable
  flag recorded, exactly-one command match, covering-check blame versus the
  doctor's own next step, plain prepare derives the main worktree, cache root
  keyed by the owning repo, cache entries keyed by the runtime fingerprint,
  the fingerprint naming the install tool and `node`, an unanswered probe
  neither publishing nor consuming the cache); the seed-template and CLI test
  packages; live
  runs against this ext4 checkout: `worktree create --prepare` (strategy
  `hardlink`, origin `parent`, 178 ms) and a raw `git worktree add` followed by
  plain `worktree prepare` (hardlink from the parent, 1 s), `npm ls --depth=0`
  passing in both; `./scripts/check-docs.sh`; the full release read-only lane
  `./scripts/run-quality.sh --full --release --read-only`; nine file-backed
  fresh-eye reviews.
- Deliberately omitted checks: no CoW-filesystem live proof (no APFS/Btrfs/ZFS
  host available; the reflink branch is covered by the probe test and its
  failure branch by the live ext4 run); no multi-lane concurrency stress (the
  cache write is staged-and-renamed and a losing renamer discards its staging;
  recorded as an accepted residual, not proven under load).
- Verifier contract: `scripts/review/validate_critique_artifacts.py`,
  unchanged in this slice. The release lane discriminated on this subject
  three times: `test_subprocess_form_gate` refused the direct `subprocess.run`;
  `check-python-lengths` refused two files over the cap;
  `validate-skill-ergonomics` and `validate-attention-state-visibility`
  refused an issue anchor in the portable seed package and an undeclared
  `skipped` term. Each was a subject defect, repaired, and the lane rerun.
- Failure classification: subject-defect
- Negative control: command `charness worktree create --prepare` on the tree before the manifest declaration was committed | expected refusal: no reuse, a full `npm ci` | observed result: link count 1 on the worktree's `node_modules/.package-lock.json`, install ran past the 5-minute window | receipt: session record 2026-09-04, first live run; the reuse path is inert without the declaration. <!-- reproduction-source -->
- Subject identity: sha256:b84b84e3382713752e483f1ee06d87f0a71b2b1c66bcf0ae51885068223d24bc
- Verifier identity: sha256:fdae081f53f503cfc7eb37bd0790ab07ad0ee04855e2af9f0bf6d47f11c5ae08
- Input identity: sha256:328112bdceb433b006e880638a0e1d0ca2f38e108ea4a3d150600441d958a9b1
- Failure identity: stable:none
- Evidence identity: none
- Retry disposition: first-attempt
- Retry key: sha256:798649626bbc2f5540ad0ba709636e3607a137ac802b4469e945ad7b09a3bec6

## Failure Angles

- Partial or poisoned trees: a half-copied `node_modules` or a cache entry that
  no longer matches its lockfile would be handed to a lane that skipped its
  install; covered by staging-and-rename, digest keying, and the post-prepare
  doctor (`npm ls --depth=0`) still gating the verdict.
- Shared inodes: hard links couple the parent, the cache entry, and every
  linked worktree; an in-place rewrite under the linked directory reaches all
  of them. Package managers replace files, so installs stay isolated; the
  trade is accepted by declaring the field.
- Opt-in that is not one: a seeder that emits the field active turns the
  documented opt-in into a default for every npm/yarn/bun consumer.
- Flag that overpromises: `--no-dependency-reuse` could not "always run the
  install command" while `skip_if_doctor_passes` coverage can still skip prepare.
- Two validation owners: the JSON schema and the runtime validator accept
  different manifest languages; the new field widens that gap on the runtime
  side (reference and relative-path checks the schema cannot express).
- Wrong cache home: a lane's private runtime root would give every lane its
  own cache; the cache root is keyed by the parent repo's runtime root, passed
  explicitly from `task run`.

## Counterweight Pass

- Real blockers, fixed before ship: the seeder emitting `dependency_reuse`
  active (now commented out with the trade-off stated); the flag help (now
  states that a doctor-licensed skip still needs `--force`); the undocumented
  donor/cache/sibling inode sharing and its recovery (now in the docs section
  and the module docstring); the direct `subprocess.run` the release gate
  refused (now `run_process`); the cache seeded before the doctor judged the
  install (now after a pass only); plain prepare ignoring the main worktree
  (now derived); a `command_id` matching several commands (now exactly one);
  reuse blamed for unrelated doctor failures (now only through a covering
  check).
- Bundled: `result.json` documentation states when the `dependency_reuse` key
  is present; the reflink attempt is probed on one file before the tree so an
  ext4 host does not pay a full failing walk (731 ms became 164 ms).
- Over-worry: "the cache validates only the lockfile digest, not tree content"
  as a poisoning vector. The cache is now published only from a tree the
  doctor accepted, the covering check runs after every reuse, and a rejected
  tree names the source and the `--no-dependency-reuse` exit; content hashing
  a hundred-thousand-file tree would cost what the feature saves. Likewise a
  donor lock protocol against a parent edited mid-copy: the operating contract
  forbids parent edits while a lane is live, and a changed parent digest now
  discards the copy. Recorded, not folded.
- Valid but deferred: schema and runtime manifest validators accept different
  languages, the `worktree_isolation` canonical check is undocumented, and the
  linked spec artifact describes a superseded output contract. All three
  predate this change and are filed as
  [#793](https://github.com/corca-ai/charness/issues/793).

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/setup/scripts/templates/worktree_dependency_reuse.yaml.txt | action: fix | note: the seeder rendered `dependency_reuse` active for every npm/yarn/bun repo while docs and schema call it opt-in; now emitted commented out with the hard-link trade-off named (surface reviewer F2).
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/worktree/worktree_dependency_reuse.py | action: document | note: a cache entry is a hard-link copy of the donor install, so donor, cache, and every later worktree share inodes and an in-place edit propagates; documented in the docs section and module docstring with the recovery path (delete the entry, prepare with `--no-dependency-reuse`) (surface reviewer F3).
- F3 | bin: act-before-ship | evidence: strong | ref: charness | action: fix | note: `--no-dependency-reuse` help promised the install command always runs, but an established doctor skip returns first; help and docs now state that `--force` is needed to override the skip, CLI reference regenerated (surface reviewer F4).
- F4 | bin: act-before-ship | evidence: strong | ref: scripts/worktree/worktree_dependency_reuse.py | action: fix | note: the module spawned `cp` through `subprocess.run`; the release lane's subprocess-form gate refused it; now `run_process` with the guard's timeout sentinel.
- F5 | bin: bundle-anyway | evidence: moderate | ref: docs/agent-task-runs.md | action: document | note: the top-level `dependency_reuse` key is present only when prepare evaluated a declared reuse step; stated (surface reviewer F5).
- F6 | bin: bundle-anyway | evidence: strong | ref: scripts/worktree/worktree_dependency_reuse.py | action: fix | note: `cp -a --reflink=always` on ext4 fails per file and walked the whole tree before falling back; a one-file probe now decides the strategy (live run 731 ms to 164 ms).
- F7 | bin: over-worry | evidence: contested | ref: scripts/worktree/worktree_dependency_reuse.py | action: defer | note: cache metadata validates digest and directory, not tree content; the post-prepare doctor gates every reuse and content hashing would cost what the feature saves (surface reviewer F3, second half).
- F8 | bin: valid-but-defer | evidence: strong | ref: integrations/worktree/manifest.schema.json | action: file-issue | follow-up: https://github.com/corca-ai/charness/issues/793 | note: schema and runtime validator accept different manifest languages (unknown keys, id pattern, unique `covers`, boolean-as-integer, and the new reference checks); predates this change (surface reviewer F1; parent SoT audit).
- F9 | bin: valid-but-defer | evidence: strong | ref: docs/worktree-prepare.md#canonical-doctor-checks | action: file-issue | follow-up: https://github.com/corca-ai/charness/issues/793 | note: the `worktree_isolation` canonical check exists in code, cannot be disabled, and is absent from the documented table and `CANONICAL_CHECK_IDS` (parent SoT audit).
- F10 | bin: act-before-ship | evidence: strong | ref: scripts/worktree/worktree_prepare_lib.py | action: fix | note: a fresh install was published to the shared cache before the post-prepare doctor judged it, so an exit-zero but unready tree could become every later lane's donor; the cache is now seeded only after the doctor passes, and a rejected install records `cache_seed.seeded: false` with the reason (code reviewer 2 F1; regression test added).
- F11 | bin: act-before-ship | evidence: strong | ref: scripts/worktree/worktree_prepare_lib.py | action: fix | note: plain `charness worktree prepare` never tried the main worktree the docs promised; `source_root` now defaults to the checkout's main worktree when it is a different tree (code reviewer 2 F3; unit test plus a live raw-worktree run: hardlink from the parent in 1 s).
- F12 | bin: act-before-ship | evidence: strong | ref: scripts/worktree/worktree_dependency_reuse.py | action: fix | note: `dependency_reuse.command_id` could match several prepare commands and skip them all; validation now requires exactly one match (code reviewer 2 F4, first half; the schema-parity half is F8).
- F13 | bin: bundle-anyway | evidence: strong | ref: scripts/worktree/worktree_prepare_lib.py | action: fix | note: every post-doctor failure after a reuse was blamed on the reused tree; the recovery message now fires only when a FAILED doctor check declares it covers the reused command, otherwise the doctor's own next step stands (code reviewer 2 F6).
- F14 | bin: bundle-anyway | evidence: moderate | ref: scripts/worktree/worktree_dependency_reuse.py | action: fix | note: a parent whose lockfile digest changed while its tree was being linked is now discarded and recorded; a donor lock or generation protocol is not added because the operating contract already forbids parent edits while a lane is live (code reviewer 2 F2, partial).
- F15 | bin: act-before-ship | evidence: strong | ref: scripts/worktree/worktree_dependency_reuse.py | action: fix | note: the cache key first carried only platform and architecture, which reviewer 3 (RV-F5) showed still lets a tree built under one Node ABI serve another; the fingerprint now adds the install tool's `--version` and `node --version`, metadata records it, and a test shows two fingerprints cannot share an entry (code reviewer 2 F5, then reviewer 3 RV-F5).
- F16 | bin: act-before-ship | evidence: strong | ref: scripts/worktree/worktree_doctor_lib.py | action: fix | note: the release lane's length gate refused `worktree_doctor_lib.py` (507 > 480) and `task_run.py`; the prepare half moved into `worktree_prepare_lib.py` with the doctor module re-exporting `run_prepare`, and the create recorder moved beside the other task-run result helpers.
- F18 | bin: bundle-anyway | evidence: strong | ref: tests/charness_cli/test_worktree_dependency_reuse.py | action: fix | note: reviewer 5 accepted the probe repair but required proof of its two invariants; tests now show consecutive fingerprint calls observe a changed version and a non-Node install tool never probes `node` (reviewer 5 RV-F5-PROBE-TEST-1).
- F19 | bin: act-before-ship | evidence: strong | ref: scripts/worktree/worktree_dependency_reuse.py | action: fix | note: `cache_entry` re-probed the runtime, so a version change between two probes could key the entry path with one fingerprint and write another to its metadata; the fingerprint is now observed once per seed or reuse and passed through, with a test that the path and metadata agree (reviewer 6 RV-F6-FINGERPRINT-SNAPSHOT).
- F20 | bin: bundle-anyway | evidence: strong | ref: docs/worktree-prepare.md | action: fix | note: the page claimed `spec`, `impl`, and `hitl` bootstrap the doctor probe; `impl` has no such call (source-of-truth audit, item 4 on #793); corrected to `spec` and `hitl`. Reviewer 7 read this edit as part of the final tree.
- F21 | bin: bundle-anyway | evidence: strong | ref: skills/public/quality/references/attention-state-visibility.json | action: fix | note: the `skipped` attention-state declaration still named `worktree_doctor_lib.py` after prepare moved out of it; the release lane's visibility gate refused, and the entry now names `worktree_prepare_lib.py`. A gate declaration relocated after reviewer 7, with no code change; not re-reviewed.
- F22 | bin: act-before-ship | evidence: strong | ref: scripts/worktree/worktree_dependency_reuse.py | action: fix | note: version probes ran in the launcher's working directory, not the worktree, so corepack or a `packageManager` field selecting a tool per tree, or a relative launcher, could key the cache to the wrong runtime; the fingerprint is now observed with the target tree as cwd for both seed and reuse, with a test asserting the cwd (reviewer 8 F1, on content reviewer 7 had passed).
- F17 | bin: act-before-ship | evidence: strong | ref: scripts/worktree/worktree_dependency_reuse.py | action: fix | note: a version probe that failed collapsed to the literal `absent`, so two unknown runtimes could share one cache entry, and a per-process probe cache ignored a PATH change; a probe that does not answer now yields no fingerprint, the cache is neither consumed nor published without one, `node` is probed only for the Node package managers, and nothing is cached across calls (reviewer 4 RV-F5-PROBE-1; test added).

## Operator Action Required

- None outstanding: F1 through F6 are in the shipped tree.

## Upgrade Path

- Existing manifests are unaffected until `prepare.dependency_reuse` is
  declared. To adopt: add the block from `adapter.example.yaml`; to back out:
  remove it, or pass `--no-dependency-reuse`, and delete the cache entry under
  the runtime root's `worktree-deps/` if a tree is suspect.

## Reviewer Tier Evidence

- Requested tier: n/a (run_review.py default; adapter `reviewer_runner` is `file-backed-worker`, backend `codex_exec`, boundary `read-only-worker`).
- Requested spawn fields: file-backed Codex worker through `run_review.py`; no host subagent spawn.
- Host exposure state: host-defaulted
- Application state: unverified-by-packet; the packet records the request, not the model the host chose.
- Delivery state: findings-received
- Execution mode: file-backed-worker
- Worker report: .charness/reviewer-round-release-8-3-0-code-9/worker-report.yaml
- Worker report identity: a69d9347e2f6ba63756d8c6758ce0ddc69d8a696e27333fe5cb67cd259cdb2b4
- Worker report approval: approval_eligible: true
- Worker report delivery: findings-received
- Worker report packet identity: aa257fac51e9a200bce6cae7f0b9a1363725af7a03559153162eb5461e6974cb
- Worker report input identity: 328112bdceb433b006e880638a0e1d0ca2f38e108ea4a3d150600441d958a9b1
- Worker report parent receipt identity: parent-79f1302903fd86eeae5cab8ae49b02e7a8f42f81e12ff756
- Worker report findings identity: 176879469356c3b38ddf1dd4afad40dad4705f845be1892fd48ba02d695455c1

## Fresh-Eye Satisfaction

worker-delivered; nine file-backed Codex workers ran through `run_review.py`. Reviewer 1 (attempt `release-8-3-0-surface-1`, release lens: Gawande checklist and Raskin interface over the operator surface) read commits `ea20b31c3..d9509087e` and delivered `block` with five findings, four repaired in commit `d3ba6869e` (F1 to F5). Reviewer 2 (attempt `release-8-3-0-code-2`, code lens over hard-link failure modes) read `e191e89d4..d3ba6869e` and delivered `block` with six findings, repaired or dispositioned in commit `3be0cd98b` (F10 to F15). Reviewer 3 (attempt `release-8-3-0-code-3`, repair verification over `e191e89d4..3be0cd98b`) confirmed F1, F3, F4, and F6 of round 2 resolved and delivered `block` on one finding, RV-F5, repaired in commit `2d228d022` (F15). Reviewer 4 (attempt `release-8-3-0-code-4`, repair verification over `e191e89d4..2d228d022`) confirmed RV-F5 resolved and delivered `block` on one finding, RV-F5-PROBE-1, repaired in commit `68b7da9f3` (F17). Reviewer 5 (attempt `release-8-3-0-code-5`, over `e191e89d4..68b7da9f3`) confirmed the probe repair and delivered `block` for two missing tests and for this record's then-unfinished state; the tests landed in commit `6f20511c4` (F18). Reviewer 6 (attempt `release-8-3-0-code-6`, over `e191e89d4..6f20511c4`, with this record held out of the tree because it is written from the review's result) delivered `block` on one finding, RV-F6-FINGERPRINT-SNAPSHOT, repaired in commit `5fe84b296` (F19). Reviewer 7 (attempt `release-8-3-0-code-7`, repair verification over the final tree `e191e89d4..5fe84b296`, same hold-out) delivered `pass`, `approval_eligible: true`, with no findings. Reviewer 8 (attempt `release-8-3-0-code-8`, the same content on the commit-pinned range `e191e89d4..5fe84b296`, same hold-out) delivered `block` on one finding, the probe cwd, repaired in commit `5a332d7e8` (F22). Reviewer 9 (attempt `release-8-3-0-code-9`, final verification over the commit-pinned range `e191e89d4..5a332d7e8`, same hold-out) delivered `pass`, `approval_eligible: true`, with no findings. No same-context substitute was used for any of the nine. A bounded `Explore` subagent spawned for the source-of-truth audit reported only after the parent had repeated the audit against the real tree; its report confirmed F8 and F9 and added four more divergences plus one behavior defect, recorded on #793 and #794 and, for the false `impl` sentence, repaired here as F20.

## Reviewed Input Identity

- Packet consumed: charness-artifacts/critique/release-8-3-0-code-9-packet.json
- Packet path: charness-artifacts/critique/release-8-3-0-code-9-packet.json
- Packet SHA256: aa257fac51e9a200bce6cae7f0b9a1363725af7a03559153162eb5461e6974cb
- Identity SHA256: 328112bdceb433b006e880638a0e1d0ca2f38e108ea4a3d150600441d958a9b1
- Reviewer 8 packet: charness-artifacts/critique/release-8-3-0-code-8-packet.json, SHA256 b9ab6a3207038140752e0cb68775ea54a74e6b571cca4c6b9ad1196bc6ac1e0b, identity 553d8c6c801846308b56ddbbdc41e516e39ca2388384f0b03c036fc92d010b08, verdict block, one finding (probe cwd), worker report `.charness/reviewer-round-release-8-3-0-code-8/worker-report.yaml` (SHA256 8d5247706fca40a805f5de44217c07de7372c0c7a79cb0947689a6e61bc44e82), findings identity 6dc636abb4d5c6f1bcd30aea77844ca8cdf53a26051090f0fe3fa9087b71f444, parent receipt parent-ef9628821cad07de345f0dbf39ecf89ad8e5492bb70f4d83. <!-- reproduction-source -->
- Reviewer 7 packet: charness-artifacts/critique/release-8-3-0-code-7-packet.json, SHA256 24da3b65e9d8cf321b10e3c175598605519c79755a275c30581397e8e8ca152e, identity 88cb87e3db1663d0f8833179d631fa5a94df4add395263a3b72b2a92655be34b, verdict pass, approval-eligible, no findings, worker report `.charness/reviewer-round-release-8-3-0-code-7/worker-report.yaml` (SHA256 bf91dd98a9fcfc3f2cb8d69494402fdda5b6e9c4e80ad4433d5a742645aa60ba), findings identity f4bff9dd59e5097e092e5a9647da4913bd2526e50bee5f0ba41c32c39c6f3e3b, parent receipt parent-c0a52c1a38999bca175fdf878b0c848a1c98f28553212c38. Its packet named the range as `e191e89d4..HEAD`, which the binding check re-resolves at the current HEAD, so it could not stay current once the record itself was committed; reviewer 8 re-read the same content on the commit-pinned range. <!-- reproduction-source -->
- Reviewer 6 packet: charness-artifacts/critique/release-8-3-0-code-6-packet.json, SHA256 7c6f728b09eb103a695b543c36a2d5e3eee540aa31f1612f094445c5d170e62c, identity f053e5adee2664c49120318de0727d951c3be37f1390505dc73b29c2d218b835, verdict block, one finding (RV-F6-FINGERPRINT-SNAPSHOT), worker report `.charness/reviewer-round-release-8-3-0-code-6/worker-report.yaml` (SHA256 eacf056cf6cc52845366039a371d468c72f34a8e98f38c51b2efd3f9ae26dbcb), findings identity 6b7c0f77dd002cf8135ba75a988da784282c2d45f3cdd0b288e5563515892118, parent receipt parent-dc56d6bf40b12040996ddaae931dda79dae0e0f3fc62c2b0. <!-- reproduction-source -->
- Reviewer 5 packet: charness-artifacts/critique/release-8-3-0-code-5-packet.json, SHA256 5a016067d9d2c0b1a1cfa6cca106b383e2107825d7329c8742aa5b6184b88f8b, identity 4e19a911f8399d4267e550d63c01157d062ada8a4c2e78e8e219db77d7f97716, verdict block, two findings (RV-F5-PROBE-TEST-1 on missing tests; RV-RECORD-1 on this record's then-unfinished state), worker report `.charness/reviewer-round-release-8-3-0-code-5/worker-report.yaml` (SHA256 3a72a7079e847c6ce919c89235d0d8ee55fc29fd44a6e59a8482489a31c1d122), findings identity 2e479a8ac31b5d718aae496d995aefa29dfbc0bc5322e651da3c5b19614cb8ac, parent receipt parent-85877dca8d40e2e14d2866693b822ee495ca6cb4d5c559fd. <!-- reproduction-source -->
- Reviewer 4 packet: charness-artifacts/critique/release-8-3-0-code-4-packet.json, SHA256 2ca78e0099891cf24aac248d29ad0b7f822484fca0de0f3262fafc9ae73203e9, identity 551864768352ebddffb7bfa2111d18d55593c7a744403166fc750f31e7b83605, verdict block, one finding (RV-F5-PROBE-1), worker report `.charness/reviewer-round-release-8-3-0-code-4/worker-report.yaml` (SHA256 3c5c44d09b742134bad5e269a5e25788f3dfb5ab54a30628a94266613ae63442), findings identity 088a6ac7cff5001f4a7e0b269d0444ee5c3bdc0c0a2cda397ea5028b6042917b, parent receipt parent-cba8d75055cad390633e1d9f2aec7147febace9d85898696. <!-- reproduction-source -->
- Reviewer 3 packet: charness-artifacts/critique/release-8-3-0-code-3-packet.json, SHA256 bda5851f01c948e5c14becbd9186c7d1ac5e686a3153f16d361114232de0c52e, identity b7f30276932005bbc26a606a66724a741a9ec53923d6af042d3d02ada6691e74, verdict block, one finding (RV-F5), worker report `.charness/reviewer-round-release-8-3-0-code-3/worker-report.yaml` (SHA256 0fb6694a1b44a3d786c63ce371ae727c0a7ce85f66e1ea1416ea3d9b76108c05), findings identity c7b6fbc132a938d9e9fae8c5a69e3df5f4b2c4e0e9fe3541d81ac7084411aa3c, parent receipt parent-e7d4ec1ba8fa43079a40d6acdefe058cce3b714d8de3af1d. <!-- reproduction-source -->
- Reviewer 2 packet: charness-artifacts/critique/release-8-3-0-code-2-packet.json, SHA256 eff224c8a8e95edf2afe046b5b0e665e846786843aaa58e1441ab0a51b368927, identity ed242a4b19913dfd831667b0a47a8d2a7b2fe9914f2d88b9ae15e18ef49cb92d, verdict block, six findings, worker report `.charness/reviewer-round-release-8-3-0-code-2/worker-report.yaml` (SHA256 517edb8e836c7066e907530bab77a08d3caa2544097ec93184aac917b37aed8d), findings identity be7246a834f973d3e5b7e786de589955f3b348835bd94a77fb0515e7c89adb83, parent receipt parent-6643846a384346dcbad91f491171038bf5818340868b7ee9. <!-- reproduction-source -->
- Reviewer 1 packet: charness-artifacts/critique/release-8-3-0-surface-1-packet.json, SHA256 600581d799393dba17f3ad6231c5f7c93ae7429585e0762e37e8bbdaea4083cb, identity 1a288a74c9cea567d4ad4779ba1f95f28b47f5d464f98fc8fa2ea3bb752d0c04, verdict block, five findings, worker report `.charness/reviewer-round-release-8-3-0-surface-1/worker-report.yaml`, findings identity ffd6c69521d3cedf77d1b1b2a2531f17c4aa09a3175031bbcdedfcaffd171e5d, parent receipt parent-ab0c618b84040b6e8f7958a0adb4ed21838ed8118a2306e6. <!-- reproduction-source -->
- `release-8-3-0-code-1-packet.json` was a dry-run packet on the pre-repair tree that no reviewer consumed; it is removed in this record's commit.

## Boundary Ownership

- Producer: `scripts/worktree/worktree_dependency_reuse.py` produces the linked tree and the `dependency_reuse` record; `worktree_doctor_lib.run_prepare` decides which prepare command it replaces.
- Consumer: `charness worktree prepare` and `worktree create --prepare` payloads, and `task run`'s `result.json`, which lifts the record unchanged.
- Owning surface: worktree preparation (`docs/worktree-prepare.md`, `scripts/worktree/`); `task run` only carries the record and names the shared cache root.
- Verdict: owned-correctly
