# Lane brief P2: `mutation`, `worktree`, `hooks`, `plugin_export` (#770)

Follow `charness-artifacts/goal-runs/765/briefs/brief-770-p-common.md`.
Packages, one commit each: `mutation` (map 2.3 mutation plus the coverage
family folded in; `release_changed_line_coverage` and
`rust_changed_line_coverage` included), `worktree` (`worktree_*` plus
`checkout_view`; `git_checkout` and `git_status_snapshot` stay in `core`),
`hooks` (the `*hook*` set plus `classify_push_diff*`, `check_staged_*`,
`commit_msg_closeout_authorization`; re-point `.githooks/*`), `plugin_export`
(`packaging_lib`, `export_plugin`, `sync_root_plugin_manifests`,
`validate_packaging*`, `packaging_policy_validators`, `plugin_preamble`,
`supply_chain*`, `specdown_ephemeral_config`; re-point the `charness` CLI
spawn at `charness:2603` and `packaging/README.md`).
