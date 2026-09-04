# Spec: tracked on-disk proof must be visible knowledge

> Status: current
> Last verified: 2026-09-05

Debug handoff: `charness-artifacts/debug/2026-09-05-tracked-claim-ephemeral-carrier.md`.
#797 is the same class on task-run retention.

## Invariant

When a tracked producer names an on-disk carrier as the proof of a public claim
(`worker-delivered`, and any later sibling of that shape), a clean clone must
be able to open that path. Hidden runtime (`.charness/**`, `.artifacts/**`) is
not that path.

## Worker-delivered

1. `_report_path` refuses a carrier whose repo-relative first part is
   `.charness` or `.artifacts`, even if the file exists on this disk.
2. `run_review` still uses `.charness/reviewer-round-<attempt>/` as the run
   directory (fingerprint/gitignore stay). After a report exists it copies
   `worker-report.yaml` to
   `charness-artifacts/critique/workers/<attempt>/worker-report.yaml` and
   emits `paths.durable_report` as the citeable path.
3. The critique scaffold tells authors to cite the durable path.
4. Live-corpus `--all` stays strict.

## Non-claims

- Mutation job budget after the sampler is green.
- `accepted-unreviewed` Worker report lines that the validator does not bind.
- Promoting stderr, prompts, or semantic-input; only the combined report.
