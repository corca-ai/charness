# Goal Run #724 Parent-Cursor Roundtrip Readback

Date: 2026-08-27 Asia/Seoul
Status: verified; live parent-only pickup and progress update read back

## Executed proof

The parent progress update used the file-backed `update-body` operation
`progress-cursor-724-20260827-1`. It returned `verified-write` with
byte-identical body readback. The decisive pickup command was:

```text
python3 skills/public/achieve/scripts/goal_run_pickup.py --repo-root . --objective '/goal #724'
```

The achieve pickup helper read `/goal #724` in a clean Python process. It read
the live parent, validated the exact frozen Goal Draft and Goal Binding
identities, consumed the parent-owned progress cursor, and made zero child
issue reads.

Result: `ok: true`, `status: selected`, `outcome: verified-read`,
`mutation_invoked: false`, `bootstrap_verification: verified-target-roundtrip`,
`membership_sha256: c5895ca6cf9eaccf739cb444a3a51c24149b9314b1e0f89061eb34041b7e8d6b`,
selected Work Item `backlog-708` on `corca-ai/charness#708`, rank `1`, cursor
revision `2`. The parent remained OPEN and the cursor reports 31 total, 14
completed, and 17 open. #698's separate closeout and final state readback are
recorded under the Goal Run observations.

The explicit graph read remains available for sync/closeout and independently
returned 31 direct children with 14 CLOSED and 17 OPEN. It is no longer part of
routine `/goal` pickup.

The supporting provider commands also passed; the graph read was read-only:

```text
python3 skills/public/issue/scripts/issue_tool.py goal-run-read --repo corca-ai/charness --number 724 --repo-root .
python3 skills/public/issue/scripts/issue_tool.py goal-run-preflight --repo corca-ai/charness --number 724 --plan-file charness-artifacts/goal-runs/724/approved-plan.json --repo-root .
```

The earlier temporary-marker probe is retained only as historical context; it
is not used as the runtime proof.

## Non-claims

This record does not claim parent completion, further child completion beyond
the separately verified #698 closeout, push, release, tag, hosted CI,
installed-host behavior, or fresh-eye review.
It also does not claim that an external child close automatically advances the
parent cursor; the one updater must publish that transition.
