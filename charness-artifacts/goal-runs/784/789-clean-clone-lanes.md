# #789 clean-clone lanes, 2026-09-04

Clone of `b5fb69dba` at `/tmp/charness-789-063532`, hooks installed, mirror synced
(`sync_root_plugin_manifests.py`). Run by `/tmp/charness-789-lanes.sh`, each
lane's full output kept beside the clone as `standing.out`, `full.out`,
`release.out`.

## run_standing_pytest.py

```
8863 passed in 87.00s (0:01:26)
standing_exit=0
```

## run-quality.sh --full --read-only

```
Quality summary: 83 passed, 0 failed, 5 not run (agent-browser-runtime-baseline: opt-in unmet; dead-code-advisory: opt-in unmet; check-supply-chain-online: opt-in unmet; check-coverage: read-only; agent-browser-runtime-hygiene: opt-in unmet), total 124.0s
full_exit=0
```

## run-quality.sh --release

```
Quality summary: 88 passed, 0 failed, 4 not run (agent-browser-runtime-baseline: opt-in unmet; dead-code-advisory: opt-in unmet; check-supply-chain-online: opt-in unmet; agent-browser-runtime-hygiene: opt-in unmet), total 151.3s
release_exit=0
```

The not-run list is the skip list, read from the summary line itself. Opt-in
gates unmet in a local clone: agent-browser-runtime-baseline,
dead-code-advisory, check-supply-chain-online, agent-browser-runtime-hygiene;
check-coverage is excluded by --read-only. One advisory in the release lane:
`check-plugin-import-smoke` recent median over its 9000 ms runtime budget
(advisory, not a failure).
