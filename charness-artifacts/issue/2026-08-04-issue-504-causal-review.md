# Issue #504 Causal Review

Date: 2026-08-04
Issue: https://github.com/corca-ai/charness/issues/504
Classification: bug

## JTBD

Retro persistence should bind achieve closeout evidence to its owning goal.

## Causal Review

Fresh-eye satisfaction: parent-delegated. The bounded reviewer read the staged
implementation read-only; boundary verification for window `issue-504-causal`
returned `verdict: clean` with `drift: []`.

### Root cause

The shared writer had no goal-aware contract, so the final achieve evidence
consumer could reject a wrong-owner retro only after persistence had already
changed local state. The repaired API now validates exact identity before its
writes when `--goal-path` is supplied. This remains an opt-in producer contract;
release/session callers intentionally omit the flag.

### Invariant proof

- Producer: exact pre-write validation and complete no-write mismatch snapshots
  cover artifact, summary/index, event, and output-directory effects.
- Final consumer: achieve closeout binding remains a defense-in-depth refusal.
- Siblings: release persistence is an intentional goal-free boundary, confirmed
  by static caller inspection.
- Non-claims: no host-installed, live, provider, or runtime invocation proof is
  claimed.

### Detection gap

Focused tests prove supplied-identity success/refusal, slug canonicalization,
legacy mode, and the maintained achieve/retro caller contract. They do not
prove a live agent invocation cannot omit `--goal-path`; that host behavior is
not exposed by this local repository contract.

### Bundle vs defer

Bundle the opt-in capability, its no-write tests, canonical output, and the
checked-in caller contract. Defer any remote issue-close claim that would imply
host-level invocation proof; keep the remote issue open unless a separate
resolution critique accepts a typed local-only disposition.
