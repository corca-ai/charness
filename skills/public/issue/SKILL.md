---
name: issue
description: "Use when filing, resolving, or managing parent/sub-issue GitHub trackers through the adapter-resolved backend (`gh` by default, or a host-mediated capability). Issue creation reports the observed problem before suggesting solutions; resolution treats GitHub as source of truth and keeps causal/critique closeout discipline."
---

# Issue

Use this when the user wants the agent to file or resolve GitHub issues through
the adapter-resolved backend.

GitHub is the source of truth for issue identity, state, body, comments, labels,
milestones, and closeout. Session memory and local artifacts may provide
context, but they do not select or verify an issue. The selected backend comes
from the adapter; do not hardcode `gh` when the planner reports a different
`selected_backend`.

## Bootstrap

Resolve `$SKILL_DIR` per `../../shared/references/bootstrap-resolution.md`.
For a known target, resolve the adapter/backend once and act on that target.
Use the planner only when the target, operation, or provider is genuinely
ambiguous, or when an explicit preflight is requested; running it before every
ordinary read or mutation only repeats the same selection work.

```bash
python3 "$SKILL_DIR/scripts/issue_tool.py" plan --repo-root . --intent new --target <optional-org/repo>
python3 "$SKILL_DIR/scripts/issue_tool.py" plan --repo-root . --intent resolve -- <optional-repo> <optional-number-or-range>
```

Read the planner's `required_reads` before acting. Open `on_demand_reads` only
when the concrete issue classification, source, backend, or closeout path
matches its trigger. Treat `gate_packets` as evidence packets: trust
deterministic failures, but keep judgment for behavior verdicts, source
preservation quality, and whether a causal claim over-reaches.

The planner's `next_action.kind` is the next move. If `backend_ready` is false,
repair or surface the adapter/backend problem before reading, creating, or
closing anything.

## Intents

`issue new [repo]` creates an issue from the current context.

1. Resolve the target and selected backend once.
2. Shape the body problem-first: situation, experience, evidence, impact, target
   labels, milestone handling, source identity/preservation when external, and
   only a weak optional solution direction. When the issue records rework
   caused by a charness skill, add the `rework` label and a `Causing skill:`
   line per `references/issue-shaping.md`.
3. Assign only existing repository labels and milestones. Gate requested
   milestones with `issue_tool.py resolve-milestone`; never invent one.
4. Before creation, materialize image evidence from private provider URLs at a
   durable URL the issue audience can read, or replace the image syntax with an
   explicit `Media evidence unavailable:` disposition. A private source identity
   may remain as provenance; it is not itself renderable media evidence.
5. Create through `issue_tool.py create --body-file <path>`, then report only
   from the verified `{repo, number, url}` ledger plus the helper-returned title
   and `body_preview` summary. Warn explicitly when `body_verified` is not true.
   Known placeholder titles are refused before backend mutation unless
   `--allow-placeholder-title` is supplied intentionally. If `--skip-readback`
   is used, creation still occurs; only the post-create readback is skipped, so
   the result is unverified. Use `verify-create` for a later in-grammar readback.
   Do not ask for approval unless the user explicitly asks to review first.

`issue resolve [repo] [number|start-end]` resolves one or more issues.

1. Read the exact requested issue through the selected backend. If the target is
   ambiguous, use the planner before selecting it.
2. If no selector was supplied, select the newest open GitHub issue through the
   backend. Do not use the session's last-created issue.
3. Read each selected issue with
   `issue_tool.py read --repo <org/repo> --number <n>` and require
   `comments_read: true` before design.
4. Capture the reporter's job-to-be-done in one line and classify the fix-unit:
   `bug`, `feature`, `deferred-work`, `question`, `decision-needed`, or
   `consolidated` (the issue MOVES to an umbrella and the close claims nothing
   about the defect; it owes a destination floor instead of a resolution one,
   and must close via `close-with-comment --reason "not planned"`).
5. Follow the planner's `classification_actions`.
   - `bug`: use causal review when the cause is uncertain or the user asks for
     it. Do not force a reviewer, fingerprint, or second observer onto a
     routine, reversible fix; escalate only when the boundary warrants it.
   - `feature` / `deferred-work`: emit the pre-mutation resolution brief and
     name the capability or capability failure before proposing implementation;
     pause when open decisions are non-empty.
   - `question` / `decision-needed`: discuss or answer before mutation; the
     decision may change the classification.
6. Implement the smallest complete fix, preserving the issue's JTBD as the
   acceptance boundary. For siblings surfaced by review, bundle only cheap
   in-scope prevention; otherwise ask before filing or record a deferred item.
7. Publish the closeout carrier and verify the target state with
   `issue_tool.py verify-closeout --expect-state CLOSED`. Add critique or a
   second observer only when the change crosses a material boundary or the
   requested claim needs it; a process exit or prose-only status is never
   evidence of a remote write.
8. Render the per-issue behavior verdict or typed disposition from a channel
   distinct from `CLOSED` state and the carrier body.

Issue-native tracker mechanics are adapter-routed. Goal Run pickup, the
file-backed provider contract, parent amendments, observation binding, graph
proof, and closeout are owned by
[`references/issue-backend.md`](./references/issue-backend.md). The consuming
repository owns any broader lifecycle policy.

## Guardrails

- Target repo is durable workflow state once named or first resolved; on retry,
  reuse it or surface `target_unavailable: <full_name>`.
- Do not design from a stale local note, partial issue read, missing comments, or
  a backend fallback the adapter did not select.
- Do not skip the classification-specific pause/review path by relabeling work:
  default to `bug` when unsure about real-world divergence, and default to
  `feature` when unsure between `feature` and discussion-only.
- Do not close before the fix carrier is published and verified through GitHub
  readback. `carrier_verified` and `CLOSED` are necessary, not sufficient.
- When an active issue-native `achieve` receipt exists, file or defer off-goal
  findings here and link a new child only when it is independently closable and
  in scope. Do not mirror routine progress into the receipt.

## References

- `adapter.example.yaml` - full worked `issue_backend` example for a
  host-mediated backend.
- `references/resolve-flow.md` - resolve sequencing, GitHub source-of-truth
  selection, classification routing, and auto-close preference.
- `references/issue-shaping.md` - problem-first issue bodies, labels,
  milestones, weak solution direction, and external-source preservation.
- `references/resolution-brief.md` - feature/deferred-work pre-mutation brief,
  pause rules, persistence, and trivial-feature shortcut.
- `references/causal-review.md` - bug causal review, sibling search, recurrence
  critique record, and classification-specific close comment shape.
- `references/issue-backend.md` - adapter-selected backend, body-file safety,
  read/create/close operations, milestones, and closeout verification commands.
- `references/closeout-discipline.md` - verified ledger, target durability,
  auto-close carrier, behavior verdict, and final state proof.
- `../../shared/references/fresh-eye-subagent-review.md` - bounded reviewer
  contract used by causal review and critique.
- `../../shared/references/external-capability-proof-ladder.md` - proof levels
  for host-mediated GitHub capabilities.
- `../../shared/references/rca-ledger-append.md` - optional RCA event append
  with `--source issue` for bug closeout in repos that maintain the ledger.
- `scripts/issue_tool.py` - CLI entrypoint for planner, preflight, read, create,
  parent update/sub-issue operations, brief path, close, and closeout verification.
