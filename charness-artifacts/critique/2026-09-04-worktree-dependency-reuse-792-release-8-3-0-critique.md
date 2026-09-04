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
- Changed surfaces: `scripts/worktree/worktree_dependency_reuse.py` (new),
  `worktree_doctor_lib.py` (`run_prepare`, manifest validation),
  `worktree_create_lib.py`, `worktree_prepare.py`, `charness` CLI,
  `scripts/task_run/task_run.py`, the schema, example, seed template and its
  library, `.agents/worktree-adapter.yaml`, two docs pages, the CLI reference;
  final consumers are `charness worktree prepare` in consumer repos and every
  `task run` lane in this one.
- Minimum sufficient proof: twelve focused tests in
  `tests/charness_cli/test_worktree_dependency_reuse.py` (parent link, digest
  mismatch refusal, cache seed and fallback, existing directory untouched,
  reflink probed on one file, prepare skips the install command, installer runs
  and seeds the cache, disable flag recorded, doctor-rejection next step, cache
  root keyed by the owning repo); the seed-template and CLI test packages; a
  live `charness worktree create --prepare` against this ext4 checkout
  (strategy `hardlink`, origin `parent`, 164 ms, `npm ls --depth=0` passing in
  the new worktree); `./scripts/check-docs.sh`; the full release read-only lane
  `./scripts/run-quality.sh --full --release --read-only`; two file-backed
  fresh-eye reviews.
- Deliberately omitted checks: no CoW-filesystem live proof (no APFS/Btrfs/ZFS
  host available; the reflink branch is covered by the probe test and its
  failure branch by the live ext4 run); no multi-lane concurrency stress (the
  cache write is staged-and-renamed and a losing renamer discards its staging;
  recorded as an accepted residual, not proven under load).
- Verifier contract: `scripts/review/validate_critique_artifacts.py`,
  unchanged in this slice; the release lane's `test_subprocess_form_gate`
  refused the first tree (direct `subprocess.run`) and passed after the module
  moved onto `scripts/core/subprocess_guard.run_process`, so the verifier
  discriminated on this subject.
- Failure classification: subject-defect
- Negative control: `charness worktree create --prepare` on the tree before
  the manifest declaration was committed | expected: no reuse, full `npm ci` |
  observed: link count 1 on `node_modules/.package-lock.json`, install ran
  past the 5-minute window | receipt: session record 2026-09-04, first live
  run; the reuse path is inert without the declaration.
- Subject identity: sha256:6bc8768a2a1ef6dd2a7524ae79e7de4746870b1eedddfa536896147e41f42192
- Verifier identity: sha256:fdae081f53f503cfc7eb37bd0790ab07ad0ee04855e2af9f0bf6d47f11c5ae08
- Input identity: sha256:ed242a4b19913dfd831667b0a47a8d2a7b2fe9914f2d88b9ae15e18ef49cb92d
- Failure identity: stable:none
- Evidence identity: none
- Retry disposition: first-attempt
- Retry key: sha256:59eb346250811ea7b2307a415504fa0746c588bbc084de3811de8113a0e926b9

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
  refused (now `run_process`).
- Bundled: `result.json` documentation states when the `dependency_reuse` key
  is present; the reflink attempt is probed on one file before the tree so an
  ext4 host does not pay a full failing walk (731 ms became 164 ms).
- Over-worry: "the cache validates only the lockfile digest, not tree content"
  as a poisoning vector. The doctor's covering check runs after every reuse
  and a rejected tree names the source and the `--no-dependency-reuse` exit;
  content hashing a hundred-thousand-file tree would cost what the feature
  saves. Recorded, not folded.
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
- Worker report: .charness/reviewer-round-release-8-3-0-code-2/worker-report.yaml
- Worker report identity: TODO_CODE2_REPORT_SHA
- Worker report approval: TODO_CODE2_APPROVAL
- Worker report delivery: findings-received
- Worker report packet identity: eff224c8a8e95edf2afe046b5b0e665e846786843aaa58e1441ab0a51b368927
- Worker report input identity: ed242a4b19913dfd831667b0a47a8d2a7b2fe9914f2d88b9ae15e18ef49cb92d
- Worker report parent receipt identity: TODO_CODE2_PARENT_RECEIPT
- Worker report findings identity: TODO_CODE2_FINDINGS

## Fresh-Eye Satisfaction

worker-delivered; two file-backed Codex workers ran through `run_review.py`. Reviewer 1 (attempt `release-8-3-0-surface-1`, release lens: Gawande checklist and Raskin interface over the operator surface) read commits `ea20b31c3..1bd0c5f2c` and delivered `block` with five findings; F1 through F5 above record their disposition, and four were repaired in commit `d3ba6869e`. Reviewer 2 (attempt `release-8-3-0-code-2`, code lens over hard-link failure modes) read the final tree `e191e89d4..d3ba6869e` and delivered TODO_CODE2_VERDICT. A bounded `Explore` subagent spawned for the source-of-truth audit went idle without a report and is recorded as unrun; that audit was performed in the parent against the real tree and its findings are F8 and F9. No same-context substitute was used for either fresh-eye review.

## Reviewed Input Identity

- Packet consumed: charness-artifacts/critique/release-8-3-0-code-2-packet.json
- Packet path: charness-artifacts/critique/release-8-3-0-code-2-packet.json
- Packet SHA256: eff224c8a8e95edf2afe046b5b0e665e846786843aaa58e1441ab0a51b368927
- Identity SHA256: ed242a4b19913dfd831667b0a47a8d2a7b2fe9914f2d88b9ae15e18ef49cb92d
- Reviewer 1 packet: charness-artifacts/critique/release-8-3-0-surface-1-packet.json, SHA256 600581d799393dba17f3ad6231c5f7c93ae7429585e0762e37e8bbdaea4083cb, identity 1a288a74c9cea567d4ad4779ba1f95f28b47f5d464f98fc8fa2ea3bb752d0c04, verdict block, five findings, worker report `.charness/reviewer-round-release-8-3-0-surface-1/worker-report.yaml`, findings identity ffd6c69521d3cedf77d1b1b2a2531f17c4aa09a3175031bbcdedfcaffd171e5d, parent receipt parent-ab0c618b84040b6e8f7958a0adb4ed21838ed8118a2306e6.
- `release-8-3-0-code-1-packet.json` was a dry-run packet on the pre-repair tree that no reviewer consumed; it is removed in this record's commit.

## Boundary Ownership

- Producer: `scripts/worktree/worktree_dependency_reuse.py` produces the linked tree and the `dependency_reuse` record; `worktree_doctor_lib.run_prepare` decides which prepare command it replaces.
- Consumer: `charness worktree prepare` and `worktree create --prepare` payloads, and `task run`'s `result.json`, which lifts the record unchanged.
- Owning surface: worktree preparation (`docs/worktree-prepare.md`, `scripts/worktree/`); `task run` only carries the record and names the shared cache root.
- Verdict: owned-correctly
