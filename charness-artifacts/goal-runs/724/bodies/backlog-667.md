<!-- charness-work-item-key: backlog-667 -->
# Existing Work Item #667 — Specialized release-lane discovery

## Purpose and premise

Generic release planning must not turn the absence of a generic route into a
false repository verdict when the repository has an explicit specialized lane.
The planner needs a small, repo-owned input that names that lane without
pretending to inspect or authorize hosted release behavior.

## Owned change and acceptance

`specialized_release_lanes` in `.agents/release-adapter.yaml` is the discovery
input. Each mapping declares `id`, `workflow`, `tag_pattern`, and the exact
read-only `command` an operator can inspect or run through the repository's
specialized lane. One declaration returns `next_action.kind:
route_specialized_release_lane` with the complete lane identity; multiple
declarations return `select_specialized_release_lane` without choosing one
silently. An empty declaration retains the existing generic planner behavior.

The resolver rejects malformed, unknown, or duplicate lane declarations rather
than silently dropping them. The planner only reports the declaration and never
executes a release command or treats the route as release approval.

## Verification and evidence boundary

Implementation commit: `3101eeceae0640cc7f36418293c0e45c08bf6197`.

Clean proof used named branch `proof/issue-667-release-lane-20260827` at the
target commit, with explicit base `1d19ea15cde57bdf6f3d5cf05ab6633a7ecf0dcc`
and target `3101eeceae0640cc7f36418293c0e45c08bf6197`, under
`/tmp/charness-667-proof-20260827`. The exact standing target returned `28
passed`; the direct focused file returned `34 passed`. Compile, Ruff,
source/plugin parity, and clean-status checks passed. Cache, pycache, and proof
logs were kept outside the worktree.

This is a narrow planner/adapter contract proof. Changed-line proof was not
used as a universal blocking gate, and no release mutation, hosted workflow or
tag execution, installed-host action, remote CI, push, tag, publication, or
fresh-eye review is claimed. Planner output is not release approval.
