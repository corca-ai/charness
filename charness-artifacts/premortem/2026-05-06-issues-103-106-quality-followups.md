# Premortem: Issues 103-106 Quality Followups

Date: 2026-05-06

## Decision

Close GitHub issues #103-#106 with a compact repo slice:

- add a `quality` standing-test economics inventory before test pruning advice
- harden `markdown-preview` runtime states and backend health checks
- keep executable `*.spec.md` review routed to rendered Specdown reports when
  that is the authoritative reader surface
- make the dead-code advisory ignore deleted tracked paths and group common
  pytest/mock/test-protocol noise
- sync checked-in plugin export and close the issues after verification

## Fresh-Eye Satisfaction

parent-delegated

Subagents:

- `019dfd22-49f1-7c33-9f88-5c7954f7389e`
- `019dfd22-4a78-78e0-bd2e-3029e7660980`
- `019dfd22-4ae4-7071-bc26-eca1ed22c028`

## Counterweight Triage

Act Before Ship:

- Treat blank `glow` output for non-empty Markdown as `backend-error`, and add
  tests for both blank failure and file-stdout retry.
- Make `glow` readiness render a tiny non-empty sample instead of checking only
  binary presence.
- Keep `markdown-preview` path-portable across source tree and checked-in plugin
  export by rewriting `skills/support/` commands to `support/` during export.
- Filter deleted tracked Python files before invoking vulture.
- Add explicit runner-startup economics guidance before test pruning.
- Record the public-skill scenario review while Cautilus is disabled.

Bundle Anyway:

- Group dead-code advisory findings by classification while preserving raw
  findings and putting `review_candidate` first in human output.
- Add regression coverage for pytest fixture-ish functions, mock protocol
  attributes, test protocol methods, structured output fields, and exported
  support capability commands.

Over-Worry:

- Do not make Markdown preview a global hard gate for every `.md` file.
- Do not turn Ceal's Node isolation lesson into a Node-only quality rule.
- Do not make vulture advisory a strict reachability proof system.

Valid But Defer:

- Adapter-driven dead-code taxonomy can wait until more consumer-specific names
  accumulate.
- Rich automatic runner profiling can follow if repeated demand appears; this
  slice only needs a low-noise inventory and contract pin.

## Scenario Review

Consumer prompt:

> Review why the standing test gate feels slow, including local vs CI runtime
> differences, and install the next deterministic gate if the move is obvious.

Expected result:

- route to `quality`
- inspect standing-test economics before pruning
- name or refresh `charness-artifacts/quality/latest.md` only when durable state
  is persisted
- run or name existing quality gates before proposing new ones
- preserve delegated-review status for broad slow-gate recommendations

Observed decision:

- `docs/public-skill-dogfood.json` keeps the `quality` case reviewed and now
  records the runner-startup economics contract explicitly.
- Cautilus remained disabled by repo adapter; deterministic validators and this
  scenario review are the accepted proof for this slice.
