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
   only a weak optional solution direction.
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

`issue tracker` operations support an issue-native `achieve` goal. A routine
Goal Run pickup reads the parent once and may request GitHub's
`subIssuesSummary` in that same response; this is a cheap live count, not a
full child-graph read or a second progress store. It then reads only the
parent's cursor child. A closed cursor child is reported as a typed sync stop;
routine pickup does not scan every child to repair the cursor.

For a complete Goal Run, prefer the file-backed provider surface:
`goal-run-preflight`, `goal-run-read`, and one `goal-run-apply` per operation
(`update-body`, `create-or-reuse-child`, `list-children`, `add-child`,
`remove-child`, or `record-observation`). Inputs are strict repo-contained JSON
files carrying the parent, immutable draft/binding hashes, attempt identity, and
observation directory, so the command line stays small without dropping the
identity proof. `goal-run-close` is the only path that may close a Goal Run; it
requires a separate proof file and a separately bound
`charness.goal-run-final-proof-index/v1` file. The close proof binds the
complete bytes of its comment and index inputs. The index binds the same
draft/binding/repository/parent identity, a typed expected-child file, the
parent-obligation bytes, and role-labelled evidence artifacts. All referenced
files are validated as
repo-contained inputs before the adapter is selected or a provider is called;
stale, malformed, foreign, or mismatched evidence is a typed refusal.

The close then performs exact graph/child/evidence readback and one guarded
close. After the immutable terminal observation is written, only the mutable
terminal metadata fields (`terminal_observation_path` and
`terminal_observation_sha256`) are updated through the existing tracker body
update/readback boundary. A distinct parent read must still report `CLOSED`
and bind that receipt; a metadata update or readback failure is
`unverified-write`, not a successful close. The primitive tracker commands
below remain useful compatibility and diagnostic surfaces.

Retry never repeats a receipt-proven comment or re-closes a closed parent. The
Goal agent owns evidence-role sufficiency; Issue core validates byte bindings.

1. For bootstrap, graph repair, or an explicitly requested diagnostic, run
   `issue_tool.py tracker-preflight --repo <owner/repo> --number <parent>`.
   Ordinary mutations resolve the provider once; their mutation functions own
   the target read and post-write readback, so they do not run this probe again.
2. Create a managed child with `create-or-reuse-child`. Its exact body contains
   `<!-- charness-work-item-key: <key> -->`; retry first performs exhaustive
   read-only discovery and refuses duplicate or mismatched keys. A prior
   matching started-only or unverified-write observation interlocks later
   attempts: they may recover an exact discovered issue but cannot invoke
   create again until operator disposition resolves the earlier write.
3. Use `update --body-file` for a complete body replacement. An already-current
   body is a no-mutation read; an update cannot strip or alter immutable Goal Run
   metadata, and any performed write needs byte-identical readback. The default
   assumes one updating agent and adds no concurrency protocol.
4. Use `add-sub-issue` / `remove-sub-issue` for real relationships and
   `list-sub-issues --expect-child-file <json>` for exact graph proof. The
   source file binds kind, repository, parent, child identities, and its
   complete-byte SHA-256 so a long approved manifest is not transcribed into
   shell arguments. An explicitly empty set remains an exact expectation; it is
   not treated as an omitted expectation. An already-linked child is an idempotent
   no-mutation result; a Markdown link never satisfies readback.
   Any invoked mutation without conclusive readback is `unverified-write` and
   stops for a fresh read; it is never reported as `no-write` or retried blindly.
5. File-backed Goal Run operations carry binding/draft hashes, an attempt id,
   and an observation directory so an interrupted external write can be
   recovered. Simple issue operations do not inherit that Goal Run ceremony.
6. Before closing a parent, require `list-sub-issues --expect-all-closed`.

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
