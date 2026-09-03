<!-- charness-work-item-key: checkout-first-routing-and-8-0-3 -->

## Objective

Inside the charness repo, skill scripts resolve to the working tree instead of the installed 8.0.2 plugin (four hand fallbacks in Goal Run #775), and release 8.0.3 (173 commits since v8.0.2) is cut through the `release` skill; the operator pre-approved the release on 2026-09-03.

## Owned scope

- `skills/shared/references/bootstrap-resolution.md` and `.agents/claude-host.md`: when the working tree is the authoring repo (identified by its remote or adapter identity, not by directory name), `$SKILL_DIR` resolution prefers `skills/public/<skill>/scripts` in the checkout; the rule says why the installed copy is still what a consumer runs.
- Proof: `/goal #<parent>` pickup from a session in this repo reads the checkout with no hand fallback; `docs/development.md` drops the open-path sentence and points at the rule.
- 8.0.3: `plan_release_run.py`, bump, critique, clean-clone release lane, publish, readback from a consumer checkout (`charness update`), recorded under the item. The pre-approval covers the decision to ship; no step of the release skill is skipped.

## Acceptance

- Pickup and one other skill script invocation resolve to the checkout, shown by their reported script path.
- `docs/development.md` no longer names the installed plugin as an open path.
- 8.0.3 published and read back from a consumer checkout.

## Focused verification

Standing lane on the bootstrap-resolution and pickup tests, export gates in the standing lane, then the standing runner; the release lane in a clean clone before any tag.

## Dependencies

lane-changed-line-done (the release cut relies on a trustworthy changed-line and release lane; the routing half may start earlier).

## Non-claims

No install manifest or tag is written as a side effect of routing; the tag and publish happen only through the release skill's own commands.
