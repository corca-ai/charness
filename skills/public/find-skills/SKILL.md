---
name: find-skills
description: "Use when the user wants to discover which skill, support capability, or integration should handle a task. Search the current harness first, expand to adapter-configured trusted skill roots when available, and explain the next usable path without hiding missing capability gaps."
---

# Find Skills

Use this when the user is asking:

- what skill should handle a task
- whether the current harness can do something
- whether a capability is native, support-driven, or external
- how to extend the harness for a recurring task

`find-skills` is one public concept:

- discover the right capability surface
- prefer local native skills first
- expand to adapter-configured trusted skill roots before treating a gap as new
- distinguish public skills, support skills, and external integrations honestly
- surface synced support skills separately when an external integration has
  already materialized one locally
- show the next usable path instead of only saying "not found"

## Bootstrap

Start local-first:

```bash
python3 "$SKILL_DIR/scripts/resolve_adapter.py" --repo-root .
python3 "$SKILL_DIR/scripts/list_capabilities.py" --repo-root .
python3 "$SKILL_DIR/scripts/list_capabilities.py" --repo-root . --recommend-for-skill <skill-id>
sed -n '1,220p' docs/external-integrations.md 2>/dev/null || true
sed -n '1,220p' docs/support-skill-policy.md 2>/dev/null || true
```

If the user's need sounds like a public workflow, inspect `skills/public/`
first. If it sounds like a tool-use capability, inspect support skills and
integration manifests before proposing a new public skill.
If the adapter advertises trusted skill roots, search those before proposing a
new local skill.

## Workflow

1. Restate the capability need.
   - what task the user wants
   - whether they need a workflow, a tool-use seam, or a new extension point
2. Search local native capabilities first.
   - public skills for user-facing workflow concepts
   - support skills and synced support skills for tool-usage helpers
   - integration manifests for external binaries or upstream support skills
3. Expand to trusted skill roots when the adapter provides them.
   - host-trusted skill packs
   - other maintained skill roots that the current harness is allowed to
     consult
4. Classify the best match honestly.
   - `public skill`
   - `trusted skill`
   - `support skill`
   - `synced support skill`
   - `external integration`
   - `missing capability`
5. Recommend the smallest usable next step.
   - invoke an existing public skill
   - point to an adapter-configured trusted skill if the current host uses one
   - use a support capability through the right workflow
   - install or wire an external integration if the policy already supports it,
     and surface the supported access modes when that changes the next step
   - when the best-match public skill has a declared external-tool route, use
     the structured recommendation payload instead of prose-only install advice,
     including whether the route is a runtime path or a validation path
   - if the capability is genuinely missing, say whether it belongs in a new
     public skill, support skill, or integration manifest
6. Explain why.
   - why this is the right layer
   - what is already shipped
   - what is not yet shipped
   - whether an external skill ecosystem search is allowed by the current host

The Vercel-style skill-ecosystem flow is still useful here:

- understand what the user needs
- search the best existing capability surface before inventing a new one
- verify source quality before recommending installation
- offer the smallest trustworthy next step

In `charness`, that flow is local-first. External skill registries are optional
and host-governed rather than the default.

## Output Shape

The result should usually include:

- `Need`
- `Best Match`
- `Layer`
- `Search Surface`
- `What Exists`
- `Next Step`

## Guardrails

- Do not recommend a new public skill when an existing public concept already
  covers the task.
- Do not skip adapter-configured trusted skill roots if the host has declared
  them as part of its supported discovery surface.
- Do not recommend a support skill when the task is really a user-facing
  workflow concept.
- Do not pretend an external capability is native to the repo if it only exists
  as a future integration.
- Do not recommend installing from a generic external skill ecosystem unless the
  host policy or adapter explicitly allows that path.
- If nothing suitable exists yet, say so directly and classify the missing
  capability instead of hand-waving.

## References

- `adapter.example.yaml`
- `references/adapter-contract.md`
- `references/discovery-order.md`
- `references/support-consumption.md`
- `scripts/resolve_adapter.py`
- `scripts/init_adapter.py`
- `scripts/list_capabilities.py`
