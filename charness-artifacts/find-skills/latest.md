# Find Skills Inventory
Date: 2026-04-18
Updated: 2026-04-18T18:16:30Z

## Summary
- public skills: 17
- support skills: 6
- synced support skills: 1
- support capabilities: 4
- integrations: 7
- trusted skills: 0

## Public Skills
- `announcement`: Use when drafting or delivering human-facing repo change communication such as release-note style summaries or chat-ready updates. Draft value comes first; delivery, audience, and omission policy stay adapter-driven.
- `create-cli`: Use when creating or upgrading a repo-owned CLI, bootstrap script, or command runner. Define the command surface, install/update contract, structured output, dry-run and doctor behavior, distribution path, and quality gates before spreading ad hoc shell or Python entrypoints.
- `create-skill`: Use when creating a new charness skill or improving a migrated one. Defines the canonical portable authoring contract: classify public/support/profile/integration boundaries, simulate failure modes, keep host-specific behavior in adapters and presets, and express external tool dependencies through manifests instead of hidden assumptions.
- `debug`: Use when investigating a bug, error, or unexpected behavior. Follow a disciplined root-cause workflow, preserve a durable debug artifact so future sessions inherit what was learned, and do not jump to fixes before a falsifiable hypothesis exists.
- `find-skills`: Use when the user asks which skill, support capability, or integration should handle a task, or names a skill/support/capability such as `X skill`, `X 스킬`, `support/X`, or `X integration`. Call this before filesystem search for named capabilities; support skills are intentionally hidden from the default skill list.
- `gather`: Use when a Slack thread, Notion page, Google Docs or Drive file, GitHub content, arbitrary URL, or other external source should become a durable local knowledge asset instead of a transient answer. Prefer primary sources, refresh existing assets in place when the source identity matches, and keep the result scoped to the user’s actual request.
- `handoff`: Use when the user wants the next session prepared or asks to update a handoff artifact. Keep the handoff short, current, and operationally useful, and treat mention-only pickup as an instruction to continue the workflow named in the handoff trigger.
- `hitl`: Use when automated review is not enough and deliberate human judgment needs to be inserted into a bounded review loop. Keeps review state resumable, chunked, and adapter-driven without hardcoding one host runtime.
- `ideation`: Use when the user is still shaping a product, system, or workflow concept and needs discovery before `spec` or implementation. Build the concept through conversation because the user may not know the full shape yet: maintain a living world model, separate verified facts from assumptions, test demand/status quo/wedge/moat early, think about feedback and expansion from the start, and treat agents, APIs, CLI, and interface choices as first-class design constraints.
- `impl`: Use when work should move into code, config, tests, or operator-facing artifacts. Consume the current implementation contract when it exists, bootstrap a small honest contract inline when it does not, implement the smallest meaningful slice, verify it aggressively, and keep the contract synchronized when reality changes it.
- `init-repo`: Use when a repo needs its initial operating surface created or normalized. Bootstrap README, AGENTS.md, CLAUDE.md symlink policy, roadmap, and operator-acceptance docs from minimal ideation for greenfield repos, or realign those same surfaces for partially-initialized repos without pretending quality review or deep product ideation already happened.
- `narrative`: Use when a repo's source-of-truth docs and current product or project story need to be aligned together. Tighten the durable narrative first, then derive one audience-neutral brief skeleton when a compressed handoff artifact would help.
- `premortem`: Use when a non-trivial design, deletion, rename, release, or workflow decision needs a before-the-fact failure review. Probe distinct failure angles, then run a counterweight pass that separates real blockers from over-worry before the caller locks the decision.
- `quality`: Use when the goal is to understand and improve the repo's current quality bar. Detect existing gates, run the available ones, inspect concept integrity, test confidence, and security posture, then propose concrete next gates instead of only complaining about what is missing.
- `release`: Use when a maintainer needs to cut, bump, or verify a repo release surface such as plugin versions, generated install manifests, and operator update instructions.
- `retro`: Use after a meaningful work unit or when the user asks for a retrospective. Reviews what happened, what created waste, which decisions mattered, which named expert lens or direct counterfactual would have changed the next move, and which workflow/capability/memory improvements should make the next session better. Auto-selects `session` or `weekly` mode from context; ambiguous cases default to `session`.
- `spec`: Use when a concept needs to become a living implementation contract. Refine ideation artifacts or existing design docs into the current build contract, decide what must be fixed now versus probed during implementation, define testable success criteria, and keep the contract synchronized as `impl` learns new facts.

## Support Skills
- `agent-browser` (support skill): Use agent-browser CLI for browser automation, JS-rendered pages, and interactive browser debugging. Prefer this when a direct URL needs real browser execution or when you must inspect live DOM state.
- `gather-notion` (support skill): Internal support capability for gathering published Notion pages into durable local markdown without requiring consumer repos to supply their own export helper.
- `gather-slack` (support skill): Internal support capability for gathering Slack threads into durable local markdown without asking consumer repos to reimplement Slack export helpers.
- `markdown-preview` (support skill): Internal support capability for rendering checked-in Markdown into durable preview artifacts so doc-facing workflows can review real terminal output instead of raw source alone.
- `specdown` (support skill): Write, run, and fix specdown executable specifications. Use when the user asks to create, edit, run, or fix specs.
- `web-fetch` (support skill): Internal support capability for routing public-web fetch requests through the strongest honest access path and classifying blocked or partial fetch responses without turning those tactics into a public workflow concept.
- `cautilus` (synced support skill): Use when intentful behavior evaluation itself is the task and the repo should run Cautilus's checked-in workflow instead of reconstructing compare, held-out, and review commands by hand.

## Support Capabilities
- `gather-notion`: charness-owned published Notion gather runtime used by the public gather skill. Supports `gather`.
- `gather-slack`: charness-owned Slack thread gather runtime used by the public gather skill. Supports `gather`.
- `markdown-preview`: charness-owned markdown preview support that renders checked-in Markdown into width-specific text artifacts for doc-facing workflows. Supports `announcement, narrative, quality`.
- `web-fetch`: charness-owned public-web fetch routing and response classification support used by gather when plain direct fetch is weak, blocked, or ambiguous. Supports `gather`.

## Integrations
- `agent-browser` (external_binary_with_skill, upstream-consumed): access modes `binary, human-only, degraded`
- `cautilus` (external_binary_with_skill, upstream-consumed): access modes `binary, human-only, degraded`
- `github-gh` (external_binary, integration-only): access modes `binary, public, degraded`
- `gitleaks` (external_binary, integration-only): access modes `binary, degraded`
- `glow` (external_binary, integration-only): access modes `binary, degraded`
- `gws-cli` (external_binary, integration-only): access modes `binary, env, human-only, degraded`
- `specdown` (external_binary, integration-only): access modes `binary, human-only, degraded`

## Trusted Skills
- none
