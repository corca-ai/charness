# Cautilus Support Surface Miss

## Mode

session

## Context

The reviewed miss is the realization during issue #146/#148 Cautilus proof
work that Charness does not currently have a repo-local `skills/support`
Cautilus support skill, even though the Cautilus integration manifest records
an upstream bundled skill source.

## Evidence Summary

- `integrations/tools/cautilus.json` declares `external_binary_with_skill` and
  `support_skill_source.path: skills/cautilus-agent`.
- `python3 skills/public/find-skills/scripts/list_capabilities.py --read-only
  --recommend-for-task ...` found the Cautilus integration but no matching local
  support skill.
- `.agents/` contains Cautilus adapters but no materialized
  `.agents/skills/cautilus` entrypoint.
- Prior Cautilus eval logs showed Codex loading installed plugin-cache skills,
  which hid the missing repo-local support-skill surface.

## Waste

The workflow treated three different states as equivalent: an integration
manifest reference, an upstream skill that may exist at a pinned release, and a
repo-local support skill that the agent can actually read through local
discovery. That collapsed distinction let Cautilus be "available" as a binary
and adapter while not being available as a repo-local support-skill contract.

## Critical Decisions

The decisive mistake was checking whether `cautilus` was an integration and
whether Cautilus eval could run, then assuming the support guidance path had
also been consumed or was locally discoverable. The later runner contamination
made this easier to miss because installed Charness plugin skills were visible
inside eval runs.

## Expert Counterfactuals

Gary Klein premortem lens: before trusting evaluator proof, ask what local
surface could be absent while the command still succeeds. That would have
separated binary readiness from support-skill materialization.

Daniel Kahneman base-rate lens: Charness has repeated misses around installed
plugin state versus repo-local source. The correct default should have been to
verify the actual loaded local path, not infer it from manifest metadata.

## Next Improvements

- workflow: When a task mentions a support skill, require `find-skills` evidence
  of `support_skill_path` or an explicit "integration-only/upstream-only"
  statement before saying the support skill was used.
- capability: Track the missing Cautilus repo-local support-skill materialization
  or isolation issue as part of the Cautilus adapter follow-up.
- memory: Keep this as a concrete lesson in retro artifacts so future
  integration work distinguishes binary, upstream support source, synced support
  skill, and installed plugin cache.

## Persisted

yes: `charness-artifacts/retro/2026-05-12-cautilus-support-surface-miss.md`
