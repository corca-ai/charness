---
name: find-skills
description: "Use when the user asks which skill, support capability, or integration should handle a task, or names a skill/support/capability such as `X skill`, `X 스킬`, `support/X`, or `X integration`. Call this before filesystem search for named capabilities; support skills are intentionally hidden from the default skill list."
---

# Find Skills

Use this when the user is asking:

- what skill should handle a task
- whether a named skill, support skill, helper, or integration exists
- whether the current harness can do something
- whether a capability is native, support-driven, or external
- how to extend the harness for a recurring task

Do not treat ordinary design or workflow decision-shaped prompts as capability
discovery only because several public skills are nearby. Questions like "what do
we need to decide?", "what decision issues are still open?", "뭘 결정해야 하죠?",
or "결정할 쟁점은?" usually need an `ideation` or `spec` decision frame with
options, tradeoffs, a recommendation, and a next step. Use `find-skills` when
the user explicitly asks which skill, support capability, helper, or integration
should handle the task, or names one directly.

When the user names a capability directly, including phrases like `X skill`,
`X 스킬`, `X support`, `support/X`, `X helper`, or `X integration`, run
`find-skills` before `find`, `ls`, or `grep` filesystem discovery. Support
skills are intentionally hidden from the default public skill list; this is the
canonical discovery path for them.

When workflow or capability language implies a support skill, workflow
integration, or external tool, query task-text recommendations before nearby
public workflows or ad hoc shell. For example, executable-spec terms should
surface `support/specdown`, and new-worktree requests should surface
`charness worktree create --prepare` before raw `git worktree add`.

`find-skills` is one public concept:

- discover the right capability surface
- prefer local native skills first
- expand to adapter-configured trusted skill roots before treating a gap as new
- distinguish public skills, support skills, and external integrations honestly
- surface synced support skills separately when an external integration has
  already materialized one locally
- show the next usable path instead of only saying "not found"

Borrow Jef Raskin-style discoverability discipline: do not turn capability
search into a routing maze. Surface the smallest obvious next step and keep
lifecycle boundaries visible.

## Drive The Routed Workflow

The inventory is the means, not the end: **drive the routed workflow from your
result** rather than stopping at the capability map. A `SessionStart` trigger or
a bare `@docs/handoff.md`-style mention with no explicit task is a **pickup** —
follow the handoff `Workflow Trigger` and invoke the workflow it names (for the
default charness handoff, `charness:handoff`; invoke the skill, do not just
re-read the file). A pure "which skill handles X?" question is the exception:
the inventory answer is the deliverable. The 2026-05-28/2026-05-29 routing miss
was the inventory running while the routed workflow did not — owning the
"what next" here is the fix. See `references/session-start-routing.md`.

## Bootstrap

Resolve `$SKILL_DIR` and `$CHARNESS_SUPPORT_DIR` per `../../shared/references/bootstrap-resolution.md`.

Start local-first:

```bash
python3 "$SKILL_DIR/scripts/resolve_adapter.py" --repo-root .
python3 "$SKILL_DIR/scripts/list_capabilities.py" --repo-root .
python3 "$SKILL_DIR/scripts/list_capabilities.py" --repo-root . --read-only
python3 "$SKILL_DIR/scripts/list_capabilities.py" --repo-root . --recommend-for-task "<task summary>"
python3 "$SKILL_DIR/scripts/list_capabilities.py" --repo-root . --recommend-for-skill <skill-id>
python3 "$SKILL_DIR/scripts/list_capabilities.py" --repo-root . --recommendation-role <runtime|validation> --next-skill-id <skill-id>
sed -n '1,220p' docs/external-integrations.md 2>/dev/null || true
sed -n '1,220p' docs/support-skill-policy.md 2>/dev/null || true
```

Routing-only callers should stay read-only. Recommendation-shaped calls are
read-only by default; pass `--write-artifact` only when intentionally refreshing
the canonical inventory too.

If a host-provided installed skill path is missing, resolve the current path
before treating the capability as absent (add `--marketplace`/`--plugin` for a
non-charness plugin cache that rotated after `charness update`):

```bash
python3 "$SKILL_DIR/scripts/resolve_skill_path.py" --repo-root . --skill-id find-skills --reported-path <missing-path>
```

Inspect `skills/public/` for workflow concepts and support skills / integration
manifests for tool-use capability before proposing a new skill; search any
adapter-advertised trusted skill roots first.

Default durable artifact: `<repo-root>/charness-artifacts/find-skills/latest.md`
is canonical inventory only; recommendation queries stay in command output
unless `--write-artifact` is explicit.

After one run you get a local-first capability inventory (skill descriptions,
canonical paths, trigger phrases, referenced files), the smallest next usable
path across public skills, support seams, and integrations, refreshed
`charness-artifacts/find-skills/latest.*` artifacts, a closeout signal under
`artifacts`, and recommendation-query payloads for task/skill/route queries. It
does not do arbitrary external skill marketplace search unless the adapter
explicitly allows it.

## Workflow

1. Restate the capability need.
   - what task the user wants
   - whether they need a workflow, a tool-use seam, or a new extension point
2. Search local native capabilities first.
   - public skills for user-facing workflow concepts
   - support skills and synced support skills for tool-usage helpers
   - integration manifests for external binaries or upstream support skills
   - use task-text recommendation payloads when file shapes, syntax, reports,
     or runtime commands imply an unmentioned support skill
3. Expand to trusted skill roots when the adapter provides them.
   - host-trusted or repo-trusted skill packs the current harness may consult
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
   - use structured recommendation payloads for external-tool, runtime, validation, support, or verbatim-named public-skill (`public_skill_recommendations`) routes
   - when the user asks about stronger validation, prompt-affecting or
     behavior-affecting changes, validation-shaped review/closeout, issue
     closeout, or operator reading test wording, query
     `--recommendation-role validation --next-skill-id <skill-id>` instead of
     routing to HITL or manual review only
   - if the capability is genuinely missing, say whether it belongs in a new
     public skill, support skill, or integration manifest
6. Explain why.
   - why this is the right layer
   - what is already shipped
   - what is not yet shipped
   - whether an external skill ecosystem search is allowed by the current host
7. Drive the routed workflow from the result.
   - on a session-open pickup, follow the handoff `Workflow Trigger` and invoke
     `charness:handoff` rather than stopping at the inventory
   - on a named-capability request, start the matched durable work skill
   - only a pure "which skill handles X?" question ends at the inventory answer

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
- Do not answer ordinary decision-shaped prompts with routing alone when the
  user needs a decision frame; keep explicit skill/capability discovery on this
  skill.
- If nothing suitable exists yet, say so directly and classify the missing
  capability instead of hand-waving.
- Do not stop after emitting the inventory when the session opened on a pickup
  or named a concrete workflow; drive the routed workflow (pickup -> the handoff
  trigger's `charness:handoff`). Stopping at the map is the routing miss this
  skill exists to prevent.
- If the `artifacts` payload reports `requires_repo_closeout: true`, apply the
  host repo's commit or closeout policy for meaningful durable artifact changes
  before final response.

## References

- `adapter.example.yaml`
- `references/adapter-contract.md`
- `references/discovery-order.md`
- `references/support-consumption.md`
- `references/session-start-routing.md`
- `../ideation/references/decision-question-response.md`
- `scripts/list_capabilities.py`
- `scripts/list_capabilities_lib.py`
- `<repo-root>/scripts/resolve_adapter.py`
- `<repo-root>/scripts/init_adapter.py`
- `<repo-root>/scripts/list_capabilities.py`
