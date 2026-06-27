---
name: gather
description: "Use when a Slack thread, Notion page, Google Docs or Drive file, GitHub content, arbitrary URL, or other external source should become a durable local knowledge asset instead of a transient answer. Prefer primary sources, refresh existing assets in place when the source identity matches, and keep the result scoped to the user's actual request."
---

# Gather

Use this when the goal is durable knowledge, not a one-turn summary.

`gather` produces a reusable local asset that later sessions can read instead
of re-fetching or re-summarizing the same source. It is one public concept even
when provider runtimes differ: provider choice, credentials, browser fallback,
and source-specific tactics belong in adapters, support skills, integrations,
and helper scripts.

## Bootstrap

Resolve `$SKILL_DIR` per `../../shared/references/bootstrap-resolution.md`, then
resolve the adapter and plan the source before acquiring it:

```bash
python3 "$SKILL_DIR/scripts/resolve_adapter.py" --repo-root .
python3 "$SKILL_DIR/scripts/gather_plan.py" --repo-root . --url <source-url>
```

By default, durable records live under
`<repo-root>/charness-artifacts/gather/` with `latest.md` as the current pointer.
Repos may override the directory with `.agents/gather-adapter.yaml`.

For Slack and Google Workspace, use the repo-owned path advisers before trying
unrelated private-source helpers:

```bash
python3 "$SKILL_DIR/scripts/advise_slack_path.py" --repo-root .
python3 "$SKILL_DIR/scripts/advise_google_workspace_path.py" --repo-root .
```

The Slack direct-cli path points at `support/gather-slack/scripts/export-thread.sh`.
For Google Workspace and private SaaS, read official API/export docs before browser automation.

For arbitrary public URLs, let the public URL helper consume `support/web-fetch`
and preserve route, attempts, selected proof, typed verdict, and open gaps:

```bash
python3 "$SKILL_DIR/scripts/gather_public_url.py" --repo-root . --url <public-url> --execute
```

## Workflow

1. Identify the exact source and requested scope.
   - name the knowledge capability later sessions need from this source
   - classify the source as local, public URL, GitHub, Slack, Notion, Google
     Workspace, browser-mediated private source, or broad research
   - Prefer primary sources.
   - local files before external summaries
   - if the user named a source URL/path, do not widen into search until the
     primary-source path is impossible or explicitly insufficient
2. Run the planner and follow its route.
   - `gather_plan.py` names required reads, adapter selection, support owner,
     route order, exact-source policy, gate packets, and next command
   - for public URLs, `support/web-fetch` owns source-specific tactics such as
     X/Twitter exact status routes, Reddit feed routes, media metadata, reader
     extraction, browser render/network recon, and archive/cache stops
   - for provider sources, follow the planner's selected provider path and stop
     when the adapter declares the source unavailable
3. Acquire through the strongest honest path.
   - local durable asset for the same source identity
   - runtime grant or authenticated binary/official export
   - public/source-specific route
   - browser-mediated fallback through `agent-browser` when official paths are
     absent, insufficient, or equally gated
   - typed clean stop when access, auth, challenge, or confidence gaps remain
4. Normalize the result into a durable asset.
   - preserve canonical source identity, freshness, access mode, route trace,
     selected attempt, typed verdict, and open gaps
   - Refresh in place when the source identity matches.
   - write dated records first and update `latest.md` atomically with
     `$SKILL_DIR/scripts/write_record.py`; never write through a current-pointer
     symlink directly
5. Answer from the gathered ledger.
   - give requested facts first
   - distinguish captured content from human confirmation
   - render closeout only from the verified gathered-asset ledger; reuse the
     resolved source on retry instead of re-walking discovery
   - if acquisition stops, report the typed reason instead of inventing or
     substituting content

## Source Integrity

Primary-source identity is load-bearing. A similar search result, snippet, cache,
or adjacent post is not the source the user asked to gather.

For X/Twitter status URLs, exact-source acquisition must either produce
`exact-fetched` or stop with `exact-blocked` / `exact-unavailable`; never present
a similar public source as the original. The acquisition trace should also
surface `source_resolution.terminal_state` so callers can distinguish
`exact-post-acquired`, `exact-post-blocked-by-x`,
`authenticated-browser-required`, and `unsupported-route`.
`authenticated-browser-required` means the default public/non-live route did not
attempt exact-source endpoints and the next attempt needs an operator-approved
live X route, authenticated browser/profile, or exact-source provider. For
Reddit, prefer source-bound RSS feeds before JSON/raw-page fallbacks and
preserve the Reddit URL identity even when the route blocks.

## Output Shape

The result should usually include:

- `Source`
- `Knowledge Capability`
- `Canonical Asset`
- `Freshness`
- `Access Mode`
- `Route / Selected Attempt`
- `Requested Facts`
- `Captured vs Human Confirmation`
- `Open Gaps`

## Guardrails

- Do not turn a narrow gather request into a broad survey unless the user asked.
- Do not store credentials, tokens, or secret material in gathered assets.
- Do not present stale knowledge as current or derived summaries as primary
  sources when the primary source is reachable.
- Do not ask users to paste secrets into chat.
- If private access is missing, name the missing capability and stop cleanly or
  fall back only to an honestly labeled public/degraded path.
- Do not treat local desktop profile reuse as equivalent to a remote/headless
  runner; say when manual or headed bootstrap is still required.

## References

- `references/adapter-contract.md`
- `references/gather-provider.md`
- `references/source-priority.md`
- `references/asset-refresh.md`
- `references/document-seams.md`
- `references/capability-contract.md`
- `references/browser-mediated-private-sources.md`
- `references/google-workspace-access.md`
- `../../support/web-fetch/references/routing-table.md`
- `../../shared/references/closeout-discipline.md`
- `<repo-root>/scripts/advise_google_workspace_path.py`
- `<repo-root>/scripts/refresh_current_pointer.py`
- `scripts/gather_plan.py`
- `scripts/gather_public_url.py`
- `scripts/write_record.py`
