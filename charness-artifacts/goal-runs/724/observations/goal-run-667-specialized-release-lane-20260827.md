# Goal Run observation — #667 specialized release lane

Date: 2026-08-27 Asia/Seoul

## Scope receipt

- Parent: `corca-ai/charness#724`
- Child: `#667`, `backlog-667`
- Base SHA: `1d19ea15cde57bdf6f3d5cf05ab6633a7ecf0dcc`
- Target SHA: `3101eeceae0640cc7f36418293c0e45c08bf6197`
- Path scope:
  - `skills/public/release/scripts/resolve_adapter.py`
  - `plugins/charness/skills/release/scripts/resolve_adapter.py`
  - `skills/public/release/scripts/plan_release_run_packets.py`
  - `plugins/charness/skills/release/scripts/plan_release_run_packets.py`
  - `skills/public/release/adapter.example.yaml`
  - `plugins/charness/skills/release/adapter.example.yaml`
  - `skills/public/release/references/adapter-contract.md`
  - `plugins/charness/skills/release/references/adapter-contract.md`
  - `tests/quality_gates/test_release_run_planner.py`
- Implementation commit: `3101eeceae0640cc7f36418293c0e45c08bf6197`

## Clean proof

The proof worktree was created by the repo worktree command at
`/tmp/charness-667-proof-20260827` on named branch
`proof/issue-667-release-lane-20260827`, not detached HEAD. It started and
ended with empty `git status --porcelain`; the worktree doctor reported an
isolated git directory. `__pycache__`, `.pytest_cache`, coverage, temp files,
and logs were directed outside that worktree.

Executed evidence:

- `python3 scripts/run_standing_pytest.py --repo-root . --mode read-only --pytest-target tests/quality_gates/test_release_run_planner.py` — `28 passed`.
- Direct `python3 -m pytest -q tests/quality_gates/test_release_run_planner.py` — `34 passed`.
- `py_compile` and Ruff on the changed Python surfaces — passed.
- Canonical/plugin `cmp` parity for resolver, planner packet, example, and
  adapter reference — passed.
- `git diff --check` and final clean-status assertion — passed.

The specialized fixture proved a declared lane produces the exact structured
`route_specialized_release_lane` action, includes the lane identity, emits no
publish packets, and leaves the packaging manifest and quality marker
unchanged. The existing no-lane fixture retained generic `inspect_only`/
publish-planning behavior.

## Boundary and non-claims

Charness owns the adapter declaration and planner routing shape. It does not
discover or validate hosted workflow triggers, tag topology, release approval,
consumer-repository release commands, publication, push, tag creation, remote
CI, installed-host state, or fresh-eye review. Changed-line proof was not made
a universal implementation gate; the focused planner contract is the blocking
evidence for this narrow surface. The operator-directed execution mode also
omits forced fresh-eye, handoff, and micro-slice steps.

## Goal Run provider and external readback

The #724 Goal Run provider updated #667 and returned `status:
verified-write`, `body_verified: true`. Its receipts are:

- `charness-artifacts/goal-runs/724/observations/backlog-667-specialized-release-lane-20260827-1.started.json`
  (`cdacbc91a3e55038bc448053d8d55ee12f695a74e354920bb2419feda1c59f60`)
- `charness-artifacts/goal-runs/724/observations/backlog-667-specialized-release-lane-20260827-1.terminal.json`
  (`5a92772f1d56716555af8d931ffac8263c29ad899b383008eb08c891bce8f84e`)

An independent `issue_tool.py read` returned `comments_read: true`, one
closeout comment, and `state: CLOSED`. The comment is
`https://github.com/corca-ai/charness/issues/667#issuecomment-5430076144`.
`verify-closeout --expect-state CLOSED` returned `ok: true`, `status: verified`,
with missing fields, state mismatches, and manual-comment gaps empty. Its only
review advisory records the intentionally skipped forced fresh-eye critique.
