# Runtime tree sweep, 2026-09-03 (hand-run, before slice 4)

Operator decision in this session: delete now, directly, no report step. This is
the one-off cleanup; slice 4 `runtime-root-retention` builds the mechanism.

## Before

`~/.cache/tmp/charness/runtime/`: 1,871 keys, 340 GB. Disk: `/dev/nvme1n1p1  1.9T  1.1T  710G  61% /home`.
Largest: installed plugin key 271 GB (250 GB = 254 ceal `task-run/` records,
16 GB = charness `task-run/`), charness key 50 GB (41 GB = 23,401 nested
fixture keys).

## Classification (`/tmp/runtime_survey.py`, keys hashed from every live repo path)

| Class | Count | Action |
| --- | --- | --- |
| finished lane, worktree clean and HEAD on a branch | 254 | worktree and runtime removed; `result.json` and logs kept |
| finished lane, worktree with uncommitted tracked edits | 110 | `uncommitted.patch` (git diff HEAD, binary), `uncommitted-untracked.tar` where untracked files existed, and `uncommitted.json` (HEAD, sizes) written beside `result.json`; every patch verified with `git apply -R --check` (one, `writer-commit-smoke`, failed only on a staged new file; content intact); then worktree and runtime removed |
| lane with no `result.json` (unfinished, last touched 2026-08-31) | 1 | same salvage, then removed |
| nested fixture runtime roots under a live key's `xdg-cache` | 23461 | removed |
| top-level keys whose repo path no longer exists | 1867 | removed |
| live repo keys (path exists) | 5 remain | kept |

69 removals first failed on read-only `manifest.json` files inside lane
runtimes; removed after `chmod -R u+w`. `git worktree prune` in ceal and
charness pruned nothing (the lanes were not registered worktrees of the parent).

## After

Keys: 5 (charness 13 GB: pytest-tmp 4.5, pycache 2.4, coverage 2.1,
xdg-cache 1.4; installed plugin 5 GB; ceal and two ceal worktrees). Tree about
25 GB. Disk: `/dev/nvme1n1p1  1.9T  764G 1019G  43% /home` then `747G used, 1.1T free` after the chmod pass.
Wall time 304 s plus the chmod pass.

## Salvaged lane records (patch kept beside result.json)

- `811b9f8f8a808bfa/xdg-cache/charness/runtime/811b9f8f8a808bfa/task-run/reviewer-status-carrier`
- `811b9f8f8a808bfa/xdg-cache/charness/runtime/811b9f8f8a808bfa/task-run/prose-honesty-advisory`
- `811b9f8f8a808bfa/xdg-cache/charness/runtime/811b9f8f8a808bfa/task-run/cover-standalone-imports`
- `811b9f8f8a808bfa/xdg-cache/charness/runtime/811b9f8f8a808bfa/task-run/retro-artifact-identity`
- `811b9f8f8a808bfa/xdg-cache/charness/runtime/811b9f8f8a808bfa/task-run/751-critique-empty-packet`
- `811b9f8f8a808bfa/xdg-cache/charness/runtime/811b9f8f8a808bfa/task-run/lesson-lifecycle-restore`
- `811b9f8f8a808bfa/xdg-cache/charness/runtime/811b9f8f8a808bfa/task-run/752-doctor-coverage-intersect`
- `811b9f8f8a808bfa/xdg-cache/charness/runtime/811b9f8f8a808bfa/task-run/candidate-carrier-identity`
- `811b9f8f8a808bfa/xdg-cache/charness/runtime/811b9f8f8a808bfa/task-run/cover-ratio-and-inference`
- `811b9f8f8a808bfa/xdg-cache/charness/runtime/811b9f8f8a808bfa/task-run/integrations-lock-refusal`
- `811b9f8f8a808bfa/xdg-cache/charness/runtime/811b9f8f8a808bfa/task-run/cover-real-host-proof`
- `811b9f8f8a808bfa/xdg-cache/charness/runtime/811b9f8f8a808bfa/task-run/writer-commit-smoke`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/goal755-slack-ingress-lifecycle`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/notion-people-connector`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/duplicate-request-registration-shell`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/host-os-service-plans-r1`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/goal793-private-controller-r1`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/host-request-authority-core`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/provider-read-cache-policy`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/goal793-github-human-provenance`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/test-request-serving-fixture-owner`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/request-lineage-serving-contract`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/instance-access-authority-reconstruction`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/goal755-slack-thread-continuation`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/github-comment-capability-identity`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/host-natural-prompt-flag-surface`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/admin-demo-human-rendering-v2`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/commercial-quota-r2`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/host-private-manifest`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/instance-access-reconstruction`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/goal755-github-local-intents`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/issue747-gateway-management`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/slack-corpus-complete-coverage-conflict`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/agent-ingress-session-cohesion`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/release-corca-host-distribution-fast`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/go-wire-boundary-v3`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/admin-human-rendering`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/gateway-core-primitive-owners`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/invocable-discovery-output`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/slack-corpus-ingress-producer`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/go-wire-boundary-validation-v2`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/provider-read-cache-semantic-eligibility`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/ingress-phase-join`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/leased-document-request-approval-bridge`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/cloudflare-mail-definitive-outcome`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/codex-host-local-relay`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/agent-attachment-continuity`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/admin-pathful-origin-repair`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/provider-read-cache-route-policy`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/admin-demo-filmable-projection`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/gateway-trusted-host-ingress`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/serving-click-container-owner`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/slack-agent-feedback-overlap`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/agent-initial-feedback-prechecked-scope`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/cealctl-gateway-activate-r1`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/provenance-notion-trash-r2`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/github-durable-corpus-adapter`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/admin-demo-projection-close`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/operation-current-truth-v2`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/commercial-org-authority-r2`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/host-opaque-source-binding`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/slack-text-control-settlement`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/agent-feedback-timing-rebase`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/corca-admin-routing-r2`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/test-agent-feedback-fixture-owner`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/goal793-flat-tenant-serving-r1`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/test-admin-auth-fixture-owner`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/goal755-slack-open-source`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/goal-764-cli-catalog-revalidation`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/goal-755-host-efficiency-scorer`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/provenance-notion-trash-r3`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/operation-current-truth`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/canonical-http-adapter`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/durable-activity-continuations`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/go-wire-boundary-validation`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/slack-corpus-complete-coverage`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/release-corca-host-distribution-r3`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/offline-test-release-signer`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/test-canonical-runtime-fixture-owners`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/goal755-github-parity`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/gateway-semantic-failure-owner`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/test-slack-activity-world-owner`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/cli-result-custody`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/admin-demo-negative-controls`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/global-always-approve-policy`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/release-corca-host-distribution-r5`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/corca-role-routing-r5`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/generic-resource-url-resolution`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/provider-read-cache-corpus`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/slack-first-visible-latency`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/gateway-lease-acquired-timing`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/leased-document-always-approve-policy`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/slack-corpus-positive-partial-reuse`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/admin-p0-session-instance`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/slack-corpus-concurrent-writer`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/gateway-activation-startup-gate-r1`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/host-natural-prompt-conditional-input-surface`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/agent-http-control-feedback-concurrency`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/notion-page-get-neutral-readback`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/admin-visual-hierarchy-followup`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/duplicate-json-output-drain`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/agent-active-recheck-reconnect`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/issue747-native-client`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/dependency-batch-r2`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/goal793-slack-human-provenance`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/leased-projection-audit-only`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/goal755-notion-file-fetch`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/ddef9c1536a6013a/task-run/slack-corpus-activity-consumer`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/811b9f8f8a808bfa/task-run/769-r1-gate-list`
- `a349c5fc98dc0a12/xdg-cache/charness/runtime/811b9f8f8a808bfa/task-run/769-u0-universes`

## What this changes for slice 4

The one-off sweep is done; the mechanism is still owed: `task run` removing a
finished lane's worktree and runtime at completion (with the same uncommitted
salvage), `_runtime_root` not nesting under the parent's `XDG_CACHE_HOME`, and
retention rows for `pycache`, `coverage`, and keys. Slice 4 keeps its scope;
its "before" numbers are the ones above.
