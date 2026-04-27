# Mandatory Premortem Closeout Retro

## Mode

- session

## Context

- Unit: user correction that `premortem needed?` still left optional room after
  many prior discussions, followed by repo contract and public skill repairs.
- Relevant outcome: task-completing repo work now treats premortem as mandatory;
  only the review depth scales.

## Evidence Summary

- User explicitly rejected optional premortem applicability language.
- `run_slice_closeout.py` blocked until public-skill dogfood review was recorded.
- Cautilus first run rejected the AGENTS change because slow-gate quality routing
  still lacked a direct reason; the second run passed after the phase-map repair.
- `./scripts/run-quality.sh` passed with 47 checks.

## Waste

- The first wording fix still centered on removing optional phrases inside
  skills, but the AGENTS phase map also needed to name why quality-contract
  links matter.
- `impl` and `release` grew past the public skill line budget, so the first
  closeout run caught avoidable verbosity after export sync.

## Critical Decisions

- Make premortem mandatory for every task-completing repo change, with
  `short` versus `full` as the scaling axis.
- Reserve `Premortem: not-applicable <reason>` for inspect/status/routing-only
  requests that do not complete repo work.
- Keep full standalone `premortem` tied to bounded subagent review instead of
  creating a same-agent substitute.

## Expert Counterfactuals

- Gary Klein: would have forced the pre-commit question to be "what likely
  misread remains?" rather than "is this risky enough for premortem?"
- Daniel Kahneman: would have removed the availability-biased optional wording
  because agents will choose the cheap interpretation when under context
  pressure.

## Next Improvements

- workflow: when a user correction targets a repeated workflow miss, update the
  root phase map and the owning skill gates in the same slice.
- capability: keep `run_slice_closeout.py` blocking on public-skill dogfood
  review for prompt-affecting skill-core changes.
- memory: preserve the Cautilus failed-then-repaired result as proof that link
  purpose belongs in AGENTS, not only deeper docs.

## Persisted

- yes: `charness-artifacts/retro/2026-04-27-mandatory-premortem-closeout-retro.md`
