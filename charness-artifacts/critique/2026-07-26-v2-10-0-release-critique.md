# v2.10.0 release critique
Date: 2026-07-26

## Decision Under Review

Whether to publish the charness release surface at 2.10.0, and at what bump
level. Seven commits sit between the v2.9.0 tag and HEAD `4eacdcd9`; six exported
source files changed (`check_seed_fixture_budget.py`, `record_quality_runtime.py`,
`check_dup_ratchet.py`, `dup_ratchet_rebaseline.py`, `pytest_temp_scan_lib.py`,
`runtime_profile_lib.py`), each with a `plugins/charness/` mirror.

## Failure Angles

One bounded read-only `bounded-reviewer` subagent across five angles: bump-level
honesty against `version-policy.md`, mirror integrity between canonical and
exported copies, downstream blast radius in a repo that does not look like
charness (no `du`, BusyBox `du`, no adapter, restricted CPU affinity), release-note
honesty about which commits reach an installed user, and anything that should
block.

Parent-side integrity was fingerprinted around the review; post-review `verify`
returned `{"ok": true, "drift": []}`.

## What The Review Changed

**The bump was wrong and is now 2.10.0, not 2.9.1.** I had planned `patch` on the
reading that this release is mostly behavior repair. The reviewer found two
additive public surfaces and, decisively, that this repo had already ruled on the
identical class one release ago: F1 of the v2.9.0 release critique moved that
release from patch to minor for exactly a new exported flag plus a new exported
module. Shipping the same shape as a patch one release later would have
reintroduced the inconsistency that critique existed to prevent.

The reviewer could not run git and said so, deriving the claim from the 2.9.0
notes, the 2026-07-25 quality review, and the five-item critique. Verified
directly afterward:

```
git diff --name-status v2.9.0..HEAD -- skills/public scripts | grep ^A
  A  skills/public/quality/scripts/dup_ratchet_rebaseline.py
git log -S"--restamp-tool-version" v2.9.0..HEAD -- .../check_dup_ratchet.py
  361f8b95, fc3133ea
```

New public module, new operator flag. `minor` under version-policy.md.

**A gate can go red on upgrade, and the notes now say so.**
`runtime_profile_lib.py` keys the profile id on `sched_getaffinity` rather than
`os.cpu_count()`. On an affinity-restricted machine the derived id changes, and a
repo whose adapter populates a non-empty `runtime_budget_profiles` gets
`profile_config_errors` and exit 1 from `check_runtime_budget.py` — green in
2.9.0, red in 2.9.1 on upgrade alone. That includes this repo: the adapter
configures `local-linux-x86_64-36cpu` and `local-linux-aarch64-4cpu` and no
`local-linux-x86_64-4cpu`, so `taskset -c 0-3 ./scripts/run-quality.sh` fails
today. Disclosed as a migration note rather than quietly shipped.

**The seed gate moved in the opposite direction from what 2.9.0 announced.**
2.9.0's headline was that a failed `du` scan no longer exits 0. `fc3133ea` adds
`advisory_only_unowned_temp_root`, which makes a direct invocation with
`PYTEST_DEBUG_TEMPROOT` unset exit 0 again. Without a note, 2.9.0's description
stays the operator's most recent and now partly wrong account of that gate.

## Counterweight Pass

- **The mirrors are clean.** All six canonical/plugin pairs match line-for-line,
  and the reviewer specifically re-probed the v2.9.0 F3 defect class (an exported
  script dead because its dependency is not at the flattened path) against the new
  module: `check_dup_ratchet.py` loads `dup_ratchet_rebaseline` as a sibling and
  the plugin copy has it. That class did not recur.
- **Nothing hard-fails downstream.** Missing `du`, non-executable `du`, and
  BusyBox `-B` rejection are all capability gaps that stay advisory; a repo with no
  adapter gets an inert dup-ratchet gate; the default bootstrap renders
  `runtime_budget_profiles: {}`, which falls through with no error — so the R2
  upgrade break needs a *populated* profiles block, which the default consumer does
  not have.
- **Four of the seven commits ship nothing to an installed user** and must not be
  listed as user-facing: the test-only sibling sweep, the handoff refresh, the
  v2.9.0 verification record, and the CI-mirror change (`tests/` and `.github/` are
  outside both the plugin export and every `cli_skill_surface_change_globs` entry).
- **The one invocation-expectation change is not major.** Two dup-ratchet
  mutation modes together now `parser.error` (exit 2 rather than 1), but the prior
  behavior was the dead-end loop that change fixed, so no honest caller depended on
  it.

## Residuals

- **`sched_getaffinity` catches only `AttributeError`.** It can raise `OSError`
  under some restricted sandboxes, which would crash every `check-runtime-budget`
  and `record_quality_runtime` run on such a host where 2.9.0's `os.cpu_count()`
  could not fail. One-token fix (`except (AttributeError, OSError)`), deliberately
  NOT smuggled into the release: it is a source change needing its own test and its
  own verification pass. Carried to the handoff.
- **This repo's own `local-linux-x86_64-4cpu` profile still has no budgets block.**
  Adding it would fix charness and not downstream, so the note is owed either way;
  it stays a backlog item rather than a release-time edit.
- **`--restamp-tool-version` is undocumented outside the scripts and artifacts.**
  The documented-command-flag gate passes, so this is discoverability, not a
  contract break.
- **Byte-level mirror identity is unverified** (the reviewer had Read only, and
  the repo's own mirror-drift gate is what the publish helper re-runs).
- **The handoff `RECONCILE REQUIRED` from 2.9.0 will fire again**; the disposition
  has now been carried forward twice without being decided.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/scripts/dup_ratchet_rebaseline.py:1 | action: fix | note: a new exported module plus a new operator flag on an exported gate make this minor, not patch — the identical call this repo made one release ago in the v2.9.0 critique; target changed to 2.10.0
- F2 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/scripts/runtime_profile_lib.py:29 | action: document | note: the affinity fix renames the runtime profile id, and a repo with a populated runtime_budget_profiles goes from green to exit 1 on upgrade; disclosed as a migration note
- F3 | bin: act-before-ship | evidence: strong | ref: scripts/check_seed_fixture_budget.py:103 | action: document | note: the unowned-temp-root carve-out loosens the gate 2.9.0 advertised as newly strict; without a note the 2.9.0 description stays the operator's latest and now-wrong account
- F4 | bin: bundle-anyway | evidence: strong | ref: charness-artifacts/release/2026-07-26-v2.9.0-notes.md:6 | action: document | note: four of seven commits reach no installed user; listing the test-only sweep or the CI-mirror change as user-facing would be an overclaim, and re-announcing the 2.9.0 fail-open closure would sell it twice
- F5 | bin: valid-but-defer | evidence: moderate | ref: skills/public/quality/scripts/runtime_profile_lib.py:30 | action: defer | note: only AttributeError is caught around sched_getaffinity; an OSError host would crash where 2.9.0 could not — real but unverified, and a source change does not belong inside a release cut
- F6 | bin: over-worry | evidence: strong | ref: plugins/charness/skills/quality/scripts/dup_ratchet_rebaseline.py:1 | action: document | note: the v2.9.0 dead-export class was re-probed against the new module and did not recur; all six mirror pairs match
- F7 | bin: valid-but-defer | evidence: moderate | ref: skills/public/quality/scripts/check_dup_ratchet.py:287 | action: document | note: combining two baseline-mutation modes now exits 2 instead of 1; caller-visible but the prior path was the dead end this change fixed

## Reviewer Tier Evidence

- Requested tier: typed `bounded-reviewer` subagent (read-only: Read/Grep/Glob), session-model inheritance per the Claude Code host branch of the repo subagent contract.
- Requested spawn fields: `subagent_type: bounded-reviewer`, five-angle pre-publish release scope, no model or effort override.
- Host exposure state: applied
- Application state: host-confirmed: the reviewer reported Read/Grep/Glob only and named its envelope as bound; the parent-side boundary fingerprint verified clean.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated

The reviewer had no git, so its central finding — that the bump was wrong — was
reconstructed from checked-in release notes and critiques rather than a diff. It
named that limit and the exact commands it wanted. Both claims were then verified
directly with `git diff --name-status` and `git log -S`, and both held. The
release target changed as a result.

## Reviewed Input Identity

<!-- No prepared packet was consumed; the reviewer read the worktree at 4eacdcd9 plus the v2.9.0 notes, the v2.9.0 release critique, the five-item critique, the release adapter, and the quality adapter. -->

## Boundary Ownership

- Producer: the release surface, which decides what version an installed user receives and what the notes claim it contains.
- Consumer: a downstream repo running `charness update`, whose gates can change verdict on upgrade.
- Owning surface: the release notes and version number, the only channel that reaches a consumer who never reads this repo.
- Verdict: owned-correctly — the upgrade-visible risks belong in the notes and the bump, not in a downstream repo's incident.
