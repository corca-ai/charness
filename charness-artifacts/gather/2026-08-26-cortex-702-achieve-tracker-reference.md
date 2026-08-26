# Cortex #702 — hierarchical issue tracker reference

- Source: https://github.com/corca-ai/cortex/issues/702
- Source identity: `corca-ai/cortex#702`
- Title: `[Tracking] 결제 정확성·상태 경계 강화 (2026-08-26 독립 감사)`
- Knowledge capability: preserve the concrete parent/sub-issue operating pattern requested for the Charness `achieve` redesign.
- Freshness: fetched 2026-08-26; source `updatedAt` was `2026-08-25T22:41:20Z`; source state was `OPEN`.
- Access mode: authenticated GitHub CLI (`gh issue view`) after the anonymous public URL route returned HTTP 404.
- Route / selected attempt: gather public URL attempt degraded without writing a record; authenticated binary read then returned the exact issue, body, labels, state, and zero comments.

## Requested Facts

Cortex #702 is a tracking issue created after three independent billing audits. It is explicitly a parent tracker rather than one implementation unit. Its operating shape is:

1. State shared background, release principles, scope, and completion criteria once in the parent.
2. Create narrow executable child issues and connect them through GitHub's actual sub-issue relationship.
3. Group children by priority and boundary (`P0`, `P1`, structural prevention, documentation consistency).
4. Record dependency-aware execution order in the parent.
5. Keep completion defined in terms of child closure plus evidence requirements; deferred structural children need a reason and follow-up milestone.
6. Avoid combining independently reproducible P0/P1 defects into one pull request; each child owns its own fault/race reproduction and migration/rollout plan.

The parent currently lists child issues #703–#712 plus existing documentation issue #538, ordered so correctness and concurrency boundaries precede shared contracts and operational automation.

## Relevance to Charness Achieve

The reusable pattern is a GitHub-native hierarchy:

- one parent issue owns durable goal intent, boundaries, acceptance, dependency order, and progress synthesis;
- sub-issues own independently closable work units and their evidence;
- the parent is updated as work learns, rather than leaving the current state only in a separate goal file;
- issue relations and issue state are the shared source of truth for humans and agents.

This source does not specify Charness interview limits, adapter fields, creation timing, offline fallback, synchronization rules, or how a host goal slot binds to the GitHub parent. Those remain Charness design decisions.

## Captured vs Human Confirmation

- Captured from the exact issue: hierarchy intent, child grouping, dependency order, completion style, release principles, and source metadata.
- Human confirmation still needed: which parts of this pattern become mandatory Charness behavior and which remain repo/adapter policy.

## Open Gaps

- The public gather helper's GitHub domain route is not implemented; the exact issue was accessible only through authenticated `gh` in this run.
- No GitHub mutation was performed while gathering.
