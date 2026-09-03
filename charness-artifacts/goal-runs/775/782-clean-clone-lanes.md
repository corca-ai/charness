# #782 clean-clone lanes, 2026-09-03

Clone of `cc4ba2112` at `/tmp/charness-782-143640`, hooks installed, mirror synced.

## run_standing_pytest.py

```
8750 passed in 75.99s (0:01:15)
standing_exit=0
```

## run-quality.sh --full --read-only

```
Quality summary: 82 passed, 0 failed, 5 not run (agent-browser-runtime-baseline: opt-in unmet; dead-code-advisory: opt-in unmet; check-supply-chain-online: opt-in unmet; check-coverage: read-only; agent-browser-runtime-hygiene: opt-in unmet), total 115.3s
full_exit=0
```

## run-quality.sh --release

```
Quality summary: 87 passed, 0 failed, 4 not run (agent-browser-runtime-baseline: opt-in unmet; dead-code-advisory: opt-in unmet; check-supply-chain-online: opt-in unmet; agent-browser-runtime-hygiene: opt-in unmet), total 137.2s
release_exit=0
```

The not-run list is the skip list, read from the summary line itself (#781: a green names what it did not run). Opt-in gates unmet in a local clone: agent-browser-runtime-baseline, dead-code-advisory, check-supply-chain-online, agent-browser-runtime-hygiene; check-coverage is excluded by --read-only.
