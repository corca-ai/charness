# Session Retro: Issue Routing Closeout
Date: 2026-04-23

## Context

- Unit of work: close GitHub issues #59, #60, and #61 through public skill,
  integration, Cautilus scenario, and plugin export updates.
- Auto-trigger: changed `find-skills`, checked-in plugin export, and
  integrations/control-plane surfaces.

## Waste

- #60 initially looked like a documentation-only routing clarification, but
  fresh-eye review correctly found that the acceptance was not locked by a
  maintained scenario.
- The first maintained Cautilus case expected direct Cautilus selection, then
  exposed that the honest public route is `quality` plus validation
  recommendations.

## Critical Decisions

- Keep Cautilus hidden from public top-level skills while adding closeout and
  operator-reading-test trigger hints to the integration manifest.
- Add a maintained instruction-surface case that proves validation-shaped
  closeout routes to evaluator-backed `quality` before HITL/manual review.
- Keep HITL state durability and nested-fence presentation rules in HITL rather
  than spreading them into ad hoc review behavior.

## Expert Counterfactuals

- Gary Klein: run the representative scenario before claiming #60 is covered;
  the mismatch is a signal about the real route, not just an expected-value
  typo.
- Daniel Kahneman: treat "review" as an anchoring hazard. Ask whether the task
  needs human judgment, evaluator-backed validation, or both before choosing
  HITL.

## Next Improvements

- Workflow: when an issue acceptance says "future agent should route/discover",
  add or update a maintained scenario before calling the prompt-surface change
  complete.
- Capability: keep validation-shaped closeout examples near Cautilus scenario
  coverage, because this is where hidden-tool discovery can regress.
- Memory: fresh-eye review should run before the first full closeout when the
  slice changes public skill routing, not after the validators already pass.

## Persisted

- yes: this artifact is persisted by the retro helper, and recent lessons are
  refreshed from it.
