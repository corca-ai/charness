<!-- charness-work-item-key: checkout-first-routing-and-8-0-3 -->

## Objective

Inside the charness repo, skill scripts resolve to the working tree instead of the installed 8.0.2 plugin (four hand fallbacks in Goal Run #775), and release 8.0.3 (173 commits since v8.0.2) is either cut through the `release` skill or its deferral recorded.

## Owned scope

- `skills/shared/references/bootstrap-resolution.md` and `.agents/claude-host.md`: when the working tree is the authoring repo (identified by its remote or adapter identity, not by directory name), `$SKILL_DIR` resolution prefers `skills/public/<skill>/scripts` in the checkout; the rule says why the installed copy is still what a consumer runs.
- Proof: `/goal #<parent>` pickup from a session in this repo reads the checkout with no hand fallback; `docs/development.md` drops the open-path sentence and points at the rule.
- 8.0.3, only per the activation decision (interview Q2): `plan_release_run.py`, bump, critique, publish readback from a consumer checkout, recorded under the item.

## Acceptance

- Pickup and one other skill script invocation resolve to the checkout, shown by their reported script path.
- `docs/development.md` no longer names the installed plugin as an open path.
- 8.0.3 published and read back, or the reason not to recorded in this item's closeout comment and under `charness-artifacts/goal-runs/<parent>/`.

## Focused verification

Standing lane on the bootstrap-resolution and pickup tests, export gates in the standing lane, then the standing runner; the release lane in a clean clone before any tag.

## Dependencies

none for the routing half. If 8.0.3 is cut in this item (interview Q2), lane-changed-line-done must have landed first, because the release cut relies on a trustworthy changed-line and release lane.

## Non-claims

Publishing is separately authorized at the moment; no install manifest or tag is written as a side effect of routing.
