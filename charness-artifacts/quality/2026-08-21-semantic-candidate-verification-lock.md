# Semantic Candidate Verification Lock

Date: 2026-08-21

## Receipt

- Target HEAD: `0784bb041` (`docs: close semantic candidate fresh-eye review`)
- Scope: committed paths from `origin/main..HEAD`, passed explicitly through
  `--paths`; untracked intermediate packets were excluded.
- Command:
  `git diff --name-only origin/main..HEAD | xargs python3 scripts/run_slice_closeout.py --repo-root . --verification-lock --ack-cautilus-skill-review --refresh-broad-pytest-proof --paths`
- Status: `completed`
- Effective exit code: `0`
- Executed command count: `53`
- Standing pytest: `10,792 passed in 92.65s`
- Broad proof fingerprint: `dbcf626dd2ec1b8fae22730f508712ab9a4939efc1ace1e6b5b7ea10a0c5865c`
- Broad proof elapsed: `94.22s`
- Closeout log: `/tmp/charness-semantic-lock-0784bb041-refresh.log`
- Closeout log SHA-256: `d31ce8966568653bd69cdcc87fdfcf0f80f5cf8df361d2091452084764c05fdf`

## Failure-Smell Recovery

The first exact-range invocation was refused because a cached broad proof had a
different locked-diff fingerprint. Its log was preserved at
`/tmp/charness-semantic-lock-0784bb041.log` with SHA-256
`9176624892ab30366c85348c1f60519a08b25147791c9a86c95f195f39497fde`.
The recovery used the closeout's explicit `--refresh-broad-pytest-proof`
contract only after the mutation set was final. A separate planning invocation
also placed `--plan-only` after `--paths` under `xargs`; argparse refused those
arguments before execution. The corrected command places every option before
`--paths` and keeps the committed-path scope explicit.

## Boundary and Non-claims

This receipt closes the local verification lock for the semantic candidate at
the target HEAD. It does not authorize version mutation, tag, push, publication,
hosted/install readback, issue closure, or Cautilus evaluation. The lock is
bound to the target commit; later documentation commits must not be mistaken
for a new source/release candidate without a matching rebind.
