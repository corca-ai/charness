# #724 Final Graph Readback

Date: 2026-08-26 Asia/Seoul
Status: verified-read

## Command

```text
python3 skills/public/issue/scripts/issue_tool.py list-sub-issues --repo corca-ai/charness --number 724 --expect-child-file charness-artifacts/goal-runs/724/bootstrap-final-graph.json --repo-root .
```

## Result

- `ok: true`, `status: verified-read`, `outcome: verified-read`
- repository/parent: `corca-ai/charness#724`
- expected graph file SHA-256: `f9cb68e8026982b81714576a080e9e490e1a48cc85f37e9884df952740a3c8a9`
- direct children: 31
- completed: 3; open: 28
- missing identities: none
- unexpected identities: none

Exact children: `546, 628, 634, 637, 667, 668, 669, 692, 693, 694, 695,
697, 698, 699, 700, 701, 703, 704, 706, 708, 710, 715, 717, 721, 722, 723,
725, 726, 727, 733, 734`.

The reconciliation added #733 (`goal-evidence-lineage`) and #734
(`goal-binding-v1`) after exact create/reuse readback, and removed the
unexpected #3 relationship. The immutable initial binding and frozen
`bootstrap-existing-graph.json` were not edited.

## Boundary

The parent remains `OPEN`. The parent metadata still says
`bootstrap_verification: pending-target-roundtrip` because a clean `/goal #724`
consumer pickup has not been run in this slice. No parent or child was closed.
