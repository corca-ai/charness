---
name: gather
description: "Use when a Slack thread, Notion page, Google Docs or Drive file, GitHub content, arbitrary URL, or other external source should become a durable local knowledge asset instead of a transient answer. Prefer primary sources, refresh existing assets in place when the source identity matches, and keep the result scoped to the user’s actual request."
---

# Gather

Use this when the goal is durable knowledge, not just a one-turn summary.

`gather` should produce a reusable local asset that later sessions can read
instead of re-fetching or re-summarizing the same source from scratch.

`gather` is one public concept even when it uses different capability providers
under the hood. Provider choice, credential mechanics, and onboarding details
belong in support and integration layers, not in the public skill definition.

Provider routing is adapter-driven. Each gather source (`github`,
`google_workspace`, `slack`, `notion`) reads
`gather_provider.<source>.mode` from `.agents/gather-adapter.yaml`:
`direct-cli` (default, maintainer-local CLIs such as `gh`/`gws`),
`host-mediated` (the host's `<provider>` capability command), or `none`
(stop with a missing-capability explanation). Skill scripts and support
skills only invoke the path the adapter selected.
Charness-owned runtime lives under support skills (`gather-slack`,
`gather-notion`); browser-mediated private SaaS still flows through
`agent-browser`. When the source is a Slack thread, route through the
repo-owned helper below before checking unrelated private-source helpers:

```bash
python3 "$SKILL_DIR/scripts/advise_slack_path.py" --repo-root .
```

When the source is Google Workspace, route through the repo-owned helper below
rather than guessing the next operator step:

```bash
python3 "$SKILL_DIR/scripts/advise_google_workspace_path.py" --repo-root .
```

## Bootstrap

Resolve the adapter first, then prefer the narrowest relevant scope.

Resolve `$SKILL_DIR` per `../../shared/references/bootstrap-resolution.md`, then run:

```bash
python3 "$SKILL_DIR/scripts/resolve_adapter.py" --repo-root .
```

By default, `gather` writes its durable artifact to
`<repo-root>/charness-artifacts/gather/latest.md`. Repos can override the directory with
`<repo-root>/.agents/gather-adapter.yaml`.

```bash
# Required Tools: rg
# Missing-binary protocol: ../../shared/references/binary-preflight.md
# 1. local context and existing knowledge assets
rg --files docs skills
sed -n '1,220p' <resolved-gather-artifact> 2>/dev/null || true
rg -n "knowledge|source|reference|vendor|upstream|artifact|gather" .

# 2. optional adjacent handoff or task context
rg -n "Workflow Trigger|Current State|Next Session|Current Slice|Success Criteria" docs charness-artifacts .agents

# 3. direct local targets when the user named a path
rg -n "" <named-path>
```

If the source already exists locally in the repo or workspace, read it before
widening into web search or external discovery.

## Capability Resolution

Prefer the strongest honest access path first:

1. local durable asset for the same source identity already exists
2. runtime capability grant or connector access already provided by the host
3. authenticated local binary or official API/export path already present on
   the machine
4. environment-variable or process-environment fallback when the host lacks a
   stronger grant path
5. browser-mediated fallback through `agent-browser` when the user has a
   private SaaS URL or stable UI path and the official API/export path is
   unavailable, insufficient, or still requires the same authenticated browser
   session
6. clean stop with an explicit missing-capability explanation when browser
   auth/bootstrap is missing or the source still needs human-only approval
7. degraded path only when it still produces honest partial value

Examples — each example follows whichever `gather_provider.<source>.mode`
the adapter selected; never substitute direct CLIs/tokens under
`host-mediated` or `none`:

- GitHub: runtime grant or authenticated `gh` (direct-cli); host capability
  command (host-mediated); stop with missing-capability (none)
- Google Workspace: authenticated `gws` (direct-cli); host capability
  command (host-mediated); stop with missing-capability (none)
- Slack: `support/gather-slack/scripts/export-thread.sh` via
  `advise_slack_path.py` (direct-cli); host capability command
  (host-mediated); stop with missing-capability (none)
- Notion: token-backed integration or published-page fallback (direct-cli);
  host capability command (host-mediated); stop with missing-capability (none)
- Arbitrary public URL: route through `support/web-fetch` with the repo-owned
  helper so the durable gather asset preserves route, attempts, selected proof,
  and open gaps:

```bash
python3 "$SKILL_DIR/scripts/gather_public_url.py" --repo-root . --url <public-url> --execute
```

- private SaaS roster: official export first, then `agent-browser` only if
  the export path is absent

Do not ask the user to paste secrets into chat. If private access is missing,
name the missing capability and stop cleanly or fall back to a public path.
For the browser-mediated private-source ladder, read
`references/browser-mediated-private-sources.md`.

## Workflow

1. Identify the source and intended scope.
   - what exact source or source class is being gathered
   - whether the request is repo-local, upstream-doc, or broad research
2. Prefer primary sources.
   - local files before external summaries
   - upstream docs before secondary commentary
   - direct URLs before search results when the user already named the source
   - for private SaaS, official API/export docs before browser automation
3. Normalize the source into a durable asset.
   - keep it readable
   - preserve source identity and freshness context
   - preserve the access path and auth/bootstrap mode that were actually used
   - avoid mixing raw source excerpts with unsupported guesses
4. Refresh in place when the source identity matches.
   - if an asset for the same source already exists, update that asset rather
     than creating duplicates
   - preserve a concise change note when freshness matters
   - the resolved gather artifact path may be a current pointer (regular
     file or a symlink to a dated canonical record). Never edit it directly
     with `apply_patch` or other writers that follow symlinks; the edit
     will silently overwrite the prior canonical asset. Write a new dated
     record under the gather output directory first, then update the
     pointer atomically. See `references/asset-refresh.md` and the
     scripted writer `scripts/write_record.py`.
5. Answer the immediate request.
   - give the directly requested facts first
   - only widen into adjacent context if the user asked for it or the current
     question cannot be answered honestly otherwise
   - render closeout only from the verified gathered-asset ledger (canonical
     source URL, asset path, access mode, freshness); reuse the resolved
     source on retry instead of re-walking discovery, per
     `../../shared/references/closeout-discipline.md`

## Output Shape

The result should usually include:

- `Source`
- `Canonical Asset`
- `Freshness`
- `Access Mode`
- `Requested Facts`
- `Captured vs Human Confirmation`
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
- Do not jump to `agent-browser` before checking whether an official API or
  export path already exists.
- Do not treat local desktop profile reuse as equivalent to a remote/headless
  runner; say when a one-time manual or headed bootstrap is still required.
- Do not edit the resolved gather artifact path (e.g., `latest.md`) when it
  is a symlink; the write follows the link and overwrites the canonical
  dated record. Use the scripted writer or the atomic pointer-refresh path
  in `references/asset-refresh.md`.

## References

- `references/adapter-contract.md`
- `references/gather-provider.md`
- `references/source-priority.md`
- `references/asset-refresh.md`
- `references/document-seams.md`
- `references/capability-contract.md`
- `references/browser-mediated-private-sources.md`
- `references/google-workspace-via-gws.md`
- `../../shared/references/closeout-discipline.md`
- `<repo-root>/scripts/advise_google_workspace_path.py`
- `<repo-root>/scripts/refresh_current_pointer.py`
- `scripts/write_record.py`
