# Agent Production Runtime Quality Retro

## Context

This session added a provider-neutral `quality` lens for production LLM and
agent runtime review, including synced plugin exports, dogfood evidence,
deterministic tests, design critique, and implementation critique.

## Evidence Summary

- Design critique subagents agreed the slice belongs in `quality`, not a new
  public skill, wrapper, runner, detector, or adapter surface.
- Implementation critique found one real blocker: the new source and plugin
  reference files were untracked before commit.
- `run_slice_closeout.py --ack-cautilus-skill-review` passed after scenario
  review and dogfood evidence were recorded.

## Waste

- The first patch failed because I matched a wrapped sentence too literally.
- The first `validate_skills.py` run caught bad relative links from the new
  reference to shared references.
- I almost stopped after closeout without refreshing `find-skills`; changing a
  public skill reference means the local capability inventory can also change.

## Critical Decisions

- Naming the reference `agent-production-runtime.md` avoided the healthcheck
  implication of "readiness" while keeping the review provider-neutral.
- Keeping triggers tied to production runtime evidence prevents Charness's own
  eval fixtures and skill docs from causing noisy false positives.
- Treating cache, fallback, idempotency, streaming, and routing as evidence
  questions avoids turning Anthropic-specific advice into mandatory
  architecture.

## Expert Counterfactuals

- Michael Jackson would have forced the problem boundary earlier: production
  runtime review is distinct from eval scaffolding, prompt review, and provider
  SDK implementation.
- Charity Majors would have asked earlier whether the operator can debug the
  failure under pressure; that pushed telemetry, fallback reasons, and provider
  proof level into the reference.

## Next Improvements

- workflow: after adding a new public-skill reference, refresh `find-skills`
  before the first closeout run instead of after it.
- capability: if untracked synced reference files recur, add a structural
  export-sync check that fails when a source reference exists without its plugin
  counterpart or vice versa.
- memory: keep the scenario-review decision in the critique artifact when
  `run_slice_closeout.py` requires `--ack-cautilus-skill-review`.

## Persisted

Persisted via `persist_retro_artifact.py`.
