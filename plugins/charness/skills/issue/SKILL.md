---
name: issue
description: "Use when filing a GitHub issue from current context or resolving GitHub issues end-to-end through the adapter-resolved backend (`gh` by default, or a host-mediated capability such as `acme github`). Issue creation reports the observed problem before suggesting solutions; issue resolution treats GitHub as the source of truth, classifies the issue, runs a causal review for bug-class issues before designing the fix, and runs a resolution critique so the same class of issue does not recur."
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

Resolve `$SKILL_DIR` per `../../shared/references/bootstrap-resolution.md`, then
start every run with the planner:

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

1. Run the planner with `--intent new`.
2. Shape the body problem-first: situation, experience, evidence, impact, target
   labels, milestone handling, source identity/preservation when external, and
   only a weak optional solution direction.
3. Assign only existing repository labels and milestones. Gate requested
   milestones with `issue_tool.py resolve-milestone`; never invent one.
4. Create through `issue_tool.py create --body-file <path>`, then report only
   from the verified `{repo, number, url}` ledger plus the helper-returned title
   and `body_preview` summary. Warn explicitly when `body_verified` is not true.
   Do not ask for approval unless the user explicitly asks to review first.

`issue resolve [repo] [number|start-end]` resolves one or more issues.

1. Run the planner with `--intent resolve`.
2. If no selector was supplied, select the newest open GitHub issue through the
   backend. Do not use the session's last-created issue.
3. Read each selected issue with
   `issue_tool.py read --repo <org/repo> --number <n>` and require
   `comments_read: true` before design.
4. Capture the reporter's job-to-be-done in one line and classify the fix-unit:
   `bug`, `feature`, `deferred-work`, `question`, or `decision-needed`.
5. Follow the planner's `classification_actions`.
   - `bug`: run the causal-review fresh-eye subagent before design; if spawning
     is blocked, stop and report the host signal.
   - `feature` / `deferred-work`: emit the pre-mutation resolution brief and
     name the capability or capability failure before proposing implementation;
     pause when open decisions are non-empty.
   - `question` / `decision-needed`: discuss or answer before mutation; the
     decision may change the classification.
6. Implement the smallest complete fix, preserving the issue's JTBD as the
   acceptance boundary. For siblings surfaced by review, bundle only cheap
   in-scope prevention; otherwise ask before filing or record a deferred item.
7. Run the resolution critique, publish the closeout carrier with explicit close
   keywords when auto-close is available, then verify with
   `issue_tool.py verify-closeout --expect-state CLOSED`.
8. Render the per-issue behavior verdict or typed disposition from a channel
   distinct from `CLOSED` state and the carrier body.

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
- When an active `achieve` goal artifact exists, file or defer off-goal findings
  here and append only the issue reference/reason to that goal artifact.

## References

- `references/resolve-flow.md` - resolve sequencing, GitHub source-of-truth
  selection, classification routing, and auto-close preference.
- `references/issue-shaping.md` - problem-first issue bodies, labels,
  milestones, weak solution direction, and external-source preservation.
- `references/resolution-brief.md` - feature/deferred-work pre-mutation brief,
  pause rules, persistence, and trivial-feature shortcut.
- `references/causal-review.md` - bug causal review, sibling search, recurrence
  critique handoff, and classification-specific close comment shape.
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
- `../../shared/references/active-goal-coordination.md` - off-goal issue handling
  while an `achieve` goal is active.
- `scripts/issue_tool.py` - CLI entrypoint for planner, preflight, read, create,
  brief path, close, and closeout verification.
