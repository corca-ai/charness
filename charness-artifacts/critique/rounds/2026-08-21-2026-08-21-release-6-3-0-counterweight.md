# Critique Round Findings

- Round: 2
- Recorded date: 2026-08-21
- Boundary window id: `2026-08-21-release-6-3-0-counterweight`
- Boundary snapshot: `charness-artifacts/critique/snapshots/2026-08-21-release-6-3-0-counterweight.json`
- Boundary snapshot SHA-256: `3f2ca28eb75b77d70aea98077c6b4478d246d34ec39a436c0b17d625727ccfd3`
- Findings SHA-256: `b8489eaa054b2639dbfb917064939f3eec8352874a5df070b0b6c6f2468488bd`

## Findings Returned

Verdict: **HOLD**

Target: `6.3.0` / `v6.3.0`, from current `6.2.0`.

Execution: read-only, parent-delegated; no spawn, writes, git mutation, or publication.

Packet identity is resolved: JSON SHA is `da91b2c1cf73fabda39a4c706449f08060b95db95116df8b9d3219b967cf2c36`; Markdown SHA is `88d954e6999f43718dceaa9d0320f4fbad57e2f8839c16c2749c387882ad777b`. The contract binds the JSON bytes, so Minto’s SHA concern is false. The separate reviewed-input identity is `cfecfe…`.

Live evidence:

- Checker passes locally: `133 / 133 / 14 / 119`; source/plugin catalog and checker copies are byte-identical.
- `charness catalog list` is the hidden capability inventory, not the validator catalog. It exits `0` even for `/definitely/not-a-repo`; the validator checker correctly exits `1`.
- Current release surfaces remain `6.2.0`, with no drift. The saved planner is targetless: `target_version: null`, `tag_name: null` ([planner](/home/hwidong/codes/charness/charness-artifacts/release/2026-08-20-slice-0-release-planner.raw.yaml:116)).
- The goal requires stable IDs, artifact type, adoption policy, documented doctor/inventory exposure, and `wired`/`opt_out_reason` declarations ([goal](/home/hwidong/codes/charness/charness-artifacts/goals/2026-08-20-repairs-that-carry-their-class.md:356)); the live catalog/checker does not provide those fields ([catalog](/home/hwidong/codes/charness/skills/public/quality/references/consumer-validator-catalog.yaml:13), [checker](/home/hwidong/codes/charness/scripts/check_consumer_validator_catalog.py:145)).

### Act Before Ship

- **Gawande — target binding:** Act. Re-run a current plan explicitly bound to `6.3.0`, `v6.3.0`, the candidate commit, JSON packet SHA, and reviewed-input identity. The existing receipt cannot authorize this target.
- **Minto/Raskin — #670 contract mismatch:** Act. Either complete the goal’s promised consumer-facing contract or narrow/rebind the 6.3.0 scope explicitly to the implemented packaged catalog and record the missing discovery/declaration behavior as a non-claim. Shipping it as the full #670 capability would overstate the target.
- **Gawande — install/update/doctor proof:** Act before publication. The adapter requires managed `charness update`, `charness version`, and `charness doctor` evidence ([adapter](/home/hwidong/codes/charness/.agents/release-adapter.yaml:12)); current fresh-checkout status is `not_established`. Local catalog success does not discharge this.

### Bundle Anyway

- Correct or historical-mark the goal’s stale `132/13` counts; live evidence is `133/14`.
- Generate final 6.3.0 notes with exact bounded scope, `charness update`, version/doctor checks, and rollback from 6.2.0. Omit catalog quantities unless a derived claim surface is added.
- Add the packaged catalog path and invocation guidance if the narrowed scope is accepted.
- Improve nested argparse next-action wording; current failures are nonzero and fail closed.

### Valid but Defer

- The resume publisher’s missing release-surface gate is real but pre-existing and only blocks if this release must use the resume path ([resume](/home/hwidong/codes/charness/skills/public/release/scripts/publish_release_resume.py:234)).
- Wrong-owner `charness catalog list` behavior is real, but it belongs to the separate capability-inventory contract, not this validator-catalog release surface.
- A dedicated rollback command, multi-host install matrix, and hosted/public readback belong to later release-boundary work.

### Over-Worry

- The JSON/Markdown SHA difference; the JSON contract is the authoritative packet identity.
- `charness-artifacts/release/latest.md` still saying 6.2.0; no 6.3.0 release artifact is expected before release mutation.
- Treating the external doctor temporary-directory failure as a product defect.
- Requiring all 133 candidates to be consumer-facing, Cautilus proof for this static catalog, or a full CLI redesign.

Exact smallest next move: bind the release plan to `6.3.0`, then make the one scope decision for #670—narrow and explicitly non-claim the missing fields, or implement them—before version mutation. After that, run the clean packaged install/update/version/doctor proof and generate the final release notes.

Non-claims: no version bump, tag, install, update, doctor run, hosted/public readback, or publication was established. The local checker proves package enumeration/classification only, not consumer adoption or installed behavior.
