# Spec: Historical Mutation-Baseline Observation Identity and Path Portability

Date: 2026-08-07 (written to discharge a forced-interrupt obligation that was
recorded but never paid — see Provenance).
Source: debug #516
(`charness-artifacts/debug/2026-08-07-issue-516-mutation-regression-debug.md`),
interrupt ID `mutation-516-historical-baseline-identity-and-portability`.
Seam class: `external-seam` (FORCED).
Status: **the repairs already shipped**; this spec records the contract they
established, and names what is still unbuilt.

## Provenance — why this exists now and not on 2026-08-07

The #516 debug artifact declared `Risk Class: external-seam`, which
`scripts/risk_interrupt_lib.py` treats as a FORCED risk interrupt. A forced
interrupt owes three things: `Critique Required: yes`, `Next Step: spec`, and a
`Handoff Artifact` under `charness-artifacts/spec/*.md`. The artifact recorded the
critique, but wrote `Next Step: issue-closeout-complete` — not a value in the
validator's enum — and pointed its handoff at the critique instead of a spec.

`build_debug_seam_risk_index.py --check` refused it from `bb3ff353` onward, which
is one of the five failures that kept the pre-push gate red across thirteen
unpushed commits. The obligation was real and unmet; this document pays it rather
than editing the risk class to make the requirement go away.

## Problem (the seam, not the single file)

Two distinct failures met at one seam and were initially read as one bug:

1. **A historical automated alert was read as a current bug.** The scheduled
   mutation workflow filed #516 against SHA `79ea3447`, where the handoff's
   publish-state claim was bound to `7eed13ec` while the goal/manifest ledger
   expected `e7c3e1b3`. `publish_state_ledger.py` refused `sources.handoff.claim`
   and the four reported test failures cascaded from that invalid baseline. By
   the time anyone read the issue, the four tests passed at `HEAD` — because
   `8d6ad5e7` had aligned the claim. Nothing in the issue distinguished "fixed
   since" from "never reproduced".

2. **A durable artifact stored a machine-local absolute path.** A critique packet
   recorded an absolute path that resolved outside the CI runner's checkout, so
   `test_live_corpus_critique_artifacts_pass_whole_tree_validation` passed
   locally and failed remotely. The validator was correct; the artifact was not
   portable.

The seam both sit on: **scheduled GitHub Actions checkout -> durable claim/packet
path -> local validator -> operator-facing issue record.** A verdict computed in
one execution root becomes a durable claim read in another.

## Contract

- **A mutation-baseline failure is an observation bound to a SHA, not a standing
  defect.** The producer must preserve the failing SHA and the exact failing
  nodeids. A later passing run at a different SHA is a SEPARATE observation and
  never silently closes the historical one.
- **Closeout of such an issue requires a current-SHA recheck of the exact
  reported nodeids**, recorded distinctly from the original observation.
- **Durable artifacts store repo-relative paths.** Any path in a checked-in
  artifact that a validator will resolve must be relative to the repo root, and
  the containment check stays fail-closed. An absolute path is a portability
  defect in the artifact, not in the validator that refuses it.

## What Shipped

- The packet field was made repo-relative; local whole-tree critique validation
  passes and the failing regression test passes.
- Post-repair Quality Core run `31117396157` at `9e2c390d` passed both the core
  deterministic gates and changed-line mutation coverage — an independent channel
  from the local run.
- #516 was closed with the historical observation preserved rather than
  overwritten.

## What Is NOT Built (the honest residual)

- **No gate enforces the recheck contract.** Nothing mechanically requires a
  current-SHA nodeid recheck before an automated mutation-baseline issue is
  closed. The 2026-08-07 closeout did it by hand. This is the part of the seam
  that could recur, and it is the reason this spec is worth having.
- **No general absolute-path refusal for durable artifacts.** The specific packet
  field was repaired. A checked-in artifact carrying an absolute path in some
  other field would still pass locally and fail remotely.
- **No historical-checkout reproduction was performed.** Reproducing the original
  `79ea3447` failure needs an isolated checkout with the runner's dependency
  state. It was not done, so runner dependency equivalence remains unproven.

## Non-Claims

- No claim about provider or cross-host behavior.
- No claim that the recheck contract is enforced anywhere; it is currently a
  convention this document records, not a gate.
- No Cautilus proof.
