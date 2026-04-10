---
name: gather
description: "Use when facts, docs, links, or source material should become a durable local knowledge asset instead of a transient answer. Prefer primary sources, refresh existing assets in place when the source identity matches, and keep the result scoped to the user’s actual request."
---

# Gather

Use this when the goal is durable knowledge, not just a one-turn summary.

`gather` should produce a reusable local asset that later sessions can read
instead of re-fetching or re-summarizing the same source from scratch.

`gather` is one public concept even when it uses different capability providers
under the hood. Provider choice, credential mechanics, and onboarding details
belong in support and integration layers, not in the public skill definition.

Current `charness`-owned provider runtime lives under support skills such as
`gather-slack` and `gather-notion`. Google Workspace remains an external
runtime boundary and should flow through a real integration such as `gws-cli`.
When the source is Google Workspace, prefer the repo-owned helper below rather
than guessing the next operator step:

```bash
python3 "$SKILL_DIR/scripts/advise_google_workspace_path.py" --repo-root .
```

## Bootstrap

Resolve the adapter first, then prefer the narrowest relevant scope.

Resolve `SKILL_DIR` to the directory that contains this `SKILL.md`, then run:

```bash
python3 "$SKILL_DIR/scripts/resolve_adapter.py" --repo-root .
```

By default, `gather` writes its durable artifact to
`skill-outputs/gather/gather.md`. Repos can override the directory with
`.agents/gather-adapter.yaml`.

```bash
# 1. local context and existing knowledge assets
rg --files docs skills
sed -n '1,220p' <resolved-gather-artifact> 2>/dev/null || true
rg -n "knowledge|source|reference|vendor|upstream|artifact|gather" .

# 2. optional adjacent handoff or task context
rg -n "Workflow Trigger|Current State|Next Session|Current Slice|Success Criteria" docs skill-outputs .agents 2>/dev/null || true

# 3. direct local targets when the user named a path
rg -n "" <named-path> 2>/dev/null || true
```

If the source already exists locally in the repo or workspace, read it before
widening into web search or external discovery.

## Capability Resolution

Prefer the strongest honest access path first:

1. runtime capability grant or connector access already provided by the host
2. authenticated local binary already present on the machine
3. environment-variable or process-environment fallback when the host lacks a
   stronger grant path
4. public unauthenticated fetch path when that still answers the request
5. clean stop with an explicit missing-capability explanation

Examples:

- GitHub via runtime grant or authenticated `gh`
- Google Workspace via runtime grant or an approved external tool contract
- Slack via runtime grant or a bot-token-backed integration
- Notion via runtime grant, token-backed integration, or published-page
  fallback

Do not ask the user to paste secrets into chat. If private access is missing,
name the missing capability and stop cleanly or fall back to a public path.

## Workflow

1. Identify the source and intended scope.
   - what exact source or source class is being gathered
   - whether the request is repo-local, upstream-doc, or broad research
2. Prefer primary sources.
   - local files before external summaries
   - upstream docs before secondary commentary
   - direct URLs before search results when the user already named the source
3. Normalize the source into a durable asset.
   - keep it readable
   - preserve source identity and freshness context
   - avoid mixing raw source excerpts with unsupported guesses
4. Refresh in place when the source identity matches.
   - if an asset for the same source already exists, update that asset rather
     than creating duplicates
   - preserve a concise change note when freshness matters
5. Answer the immediate request.
   - give the directly requested facts first
   - only widen into adjacent context if the user asked for it or the current
     question cannot be answered honestly otherwise

## Output Shape

The result should usually include:

- `Source`
- `Canonical Asset`
- `Freshness`
- `Requested Facts`
- `Open Gaps`

## Guardrails

- Do not turn a narrow gather request into a broad architecture survey unless
  the user asked for that survey.
- Do not store credentials, tokens, or copied secret material in gathered
  assets.
- Do not present stale knowledge as current when freshness is uncertain.
- Do not prefer derived summaries when the primary source is accessible.
- If access is missing for a private source, say what is missing and stop
  cleanly instead of inventing the content.

## References

- `references/adapter-contract.md`
- `references/source-priority.md`
- `references/asset-refresh.md`
- `references/document-seams.md`
- `references/capability-contract.md`
- `references/google-workspace-via-gws.md`
- `scripts/advise_google_workspace_path.py`
