# Recent Retro Lessons

## Current Focus

- This retro reviews the work from 2026-04-07 through 2026-04-14, when the repo closed the open support-tool and bootstrap guidance issues, tightened the tool control plane, and released `charness 0.0.6`.
- The important question is not whether work shipped, but where our process still created avoidable waste even while the repo was moving quickly.

## Repeat Traps

- We repeatedly treated adjacent surfaces as if they guaranteed each other: source checkout vs managed checkout vs installed PATH binary vs checked-in plugin export vs host cache. That caused stale-binary, export-drift, and stale-lock failures to surface late.
- We still let some generated or vendored surfaces reach standing validation before their policy was explicit. The `specdown` markdown burst and the late-discovered plugin export drift were both examples of "ship the surface, then discover the gate semantics afterward."
- We sometimes verified the right thing too late or in the wrong order. Running sync/closeout concurrently and only then discovering plugin-tree corruption is a process smell, not just a one-off mistake.
- We were too loose about discovery semantics while tightening support-tool flows. "Support-backed", "integration-only", "host-visible", and "repo-local support surface" were distinct ideas in code, but not always in our working mental model.

## Next-Time Checklist

- keep a default review checklist for any install/update/support change that explicitly covers source checkout, managed checkout, installed CLI, checked-in plugin export, host cache, and PATH visibility as separate seams.
- do not run sync-producing commands in parallel with closeout or packaging verification. Generate first, verify second.
- keep pushing "next action" into structured output. Any `doctor`/`install`/`sync-support` surface that still requires prose interpretation should be treated as incomplete.
- add one repo-owned validator for vendored-surface policy so markdown or packaging exceptions are declared at intake time instead of discovered at standing-quality time.
- consider a surface-separation helper or checklist for support discoverability so "host-visible", "repo-local generated", and "integration-only" cannot be conflated while implementing follow-ons.

## Sources

- `skill-outputs/retro/weekly-2026-04-14.md`

