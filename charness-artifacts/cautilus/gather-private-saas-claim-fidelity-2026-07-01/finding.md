# gather claim-fidelity — private-SaaS scenario (NEW, 2026-07-01)

## Verdict

**NEW conditional scenario PROVEN.** The corrected per-condition design predicted (from
the docs+routing alone, no capture) that a private-SaaS source with no export/host path
forces `browser-mediated-private-sources.md`. A fresh capture confirms it: a representative
`/charness:gather` of a private SSO-gated HR roster **genuinely Reads**
`references/browser-mediated-private-sources.md` (real Read tool call, NOT a subagent-prompt
name-mention), **outcome=passed**, RCF `[browser-mediated-private-sources.md]` satisfied.

## Why this is the right fixture (corrects #411)

The single public-URL fixture opened ZERO docs (0/8) and #411 concluded "gather needs a
substance judge." Tracing each ref to its trigger (gather-fixture-redesign.md) showed only
ONE of the 4 census-DEPTH docs is a genuine RUN-time floor — this one — and it is forced only
under the private-SaaS condition the single fixture never exercised. The fix was a MISSING
SCENARIO, designed from the docs, not a substance judge. gather now fans out by source
condition (registry fan_out_fit yes).

## What ran

`/charness:gather` of a private SSO-gated HR roster (no public access, no export/API, browser
only) at `HEAD`=c7c51835, isolated worktree, exit 0, **150405ms**, 1.15M tokens, tool profile
Bash=11 Read=2 Skill=1. Graded against `private-saas.spec.json`:

- **outcome=passed** — "All declared claims met." RCF `[browser-mediated-private-sources.md]`
  satisfied by a **genuine Read** of the file (verified in-stream; no Agent/Task mention).
- coverage 1/6 DEPTH (the other DEPTH docs are on-demand for their own conditions or
  script-resolved — adapter/asset-refresh/document-seams/gather-provider/google-workspace — not
  this condition; expected).
- **Faithful representative behavior:** the run tried the strongest paths (grant → browser),
  reached a **clean stop**, explicitly did NOT claim the roster was acquired, left
  `charness-artifacts/gather/latest.md` untouched (no fabricated pointer refresh), and named the
  auth/bootstrap next step — exactly the browser-mediated decision-ladder intent the doc owns.

## Status of the rest of gather (next steps, not this scenario)

- public-URL default spec: retire the INLINE RCF `[source-priority, capability-contract]` (inline
  the Access-Modes enum into SKILL.md first) and floor on the produced artifact (output). Still the
  #411 hard part; separate.
- gather-provider.md / google-workspace-access.md: reclassify as script-resolved (advisers emit
  their content), engage-always but not RCF floors.

## Non-Claims

- n=1 capture: the private-SaaS RCF is PROVEN at a single sample, suggestive of a
  reliably-forced doc-open, not a stability proof.
- Scope is this scenario only. The public-URL default floor stays #411's open hard
  part (retire the INLINE RCF + floor on the produced artifact) and is not closed here.
- Not a matcher softening: the RCF was satisfied by a genuine Read (verified
  in-stream, no subagent-prompt name-mention), not a relaxed matcher.
