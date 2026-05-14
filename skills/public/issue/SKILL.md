---
name: issue
description: "Use when filing a GitHub issue from current context or resolving GitHub issues end-to-end through the adapter-resolved backend (`gh` by default, or a host-mediated capability such as `ceal github`). Issue creation reports the observed problem before suggesting solutions; issue resolution treats GitHub as the source of truth, classifies the issue, runs a causal review for bug-class issues before designing the fix, and runs a resolution critique so the same class of issue does not recur."
---

# Issue

Use this when the user wants the agent to file or resolve GitHub issues
through the adapter-resolved backend.

`issue` has two command-shaped intents:

- `issue new [repo]`: create an issue from the current context
- `issue resolve [repo] [number|start-end]`: resolve one or more issues

GitHub is the source of truth. Do not prefer session memory, a just-created
issue, a local note, or a stale artifact over the target repository's current
GitHub state.

The skill resolves the issue backend through the adapter (default `gh`;
host-mediated alternates like `ceal github` register their own backend).
`preflight` reports `selected_backend` so non-`gh` backends substitute via
`commands` rather than direct `gh`. See `references/issue-backend.md` and
`../../shared/references/external-capability-proof-ladder.md`.

## Bootstrap

Resolve `$SKILL_DIR` per `../../shared/references/bootstrap-resolution.md`.

```bash
python3 "$SKILL_DIR/scripts/resolve_adapter.py" --repo-root .
python3 "$SKILL_DIR/scripts/issue_tool.py" preflight --repo-root . --json
python3 "$SKILL_DIR/scripts/issue_tool.py" resolve-invocation --repo-root . -- <issue-resolve-args>
# `select` runs only when the user did not pass an issue number to `issue resolve`.
python3 "$SKILL_DIR/scripts/issue_tool.py" select --repo <org/repo> --selector "<optional-number-or-range>"
```

With no selector, `select` queries the newest open GitHub issue for the target
repo by created date. It must not use the current session's last created issue.

## Target Rules

- `org/repo`: use that exact repository
- `repo`: use the adapter `default_org`, which defaults to `corca-ai`
- omitted repo: infer the current repository from Git remote; if the remote
  lacks an owner, use `default_org` and the current directory name
- for `issue resolve`, one numeric token or `start-end` token is the issue
  selector, not a repository name
- adapter defaults live in `.agents/issue-adapter.yaml`
- once named or first-resolved, the target is durable workflow state for the
  session; on retry, reuse it; if unreachable, surface
  `target_unavailable: <full_name>` and stop instead of silently switching to
  another accessible repo (see `references/closeout-discipline.md`)

## New Issue

1. Resolve the target repo.
2. Gather enough local context to make the observed problem transparent.
   Prefer current conversation, relevant local files, failing commands, logs,
   existing issue duplicates, and repository state over broad research.
3. Write the issue as problem context first:
   - what situation occurred
   - what the user, operator, or agent experienced
   - what outcome the reporter was trying to reach (job-to-be-done in one
     line); record `JTBD: not inferable` when the situation does not reveal it
   - what evidence or commands show it
   - why the current behavior is confusing, costly, or blocked
   - target-repo labels via the selected backend (gh:
     `gh label list --repo <org/repo>`; non-gh: host's label-list shape;
     never substitute direct `gh` when another backend is selected)
   - external source identity when filed from a Slack thread, Notion page,
     doc, or gathered artifact, per `references/closeout-discipline.md`
4. Add only an optional weak solution direction (`This may be solved by...`,
   `A useful outcome might be...`); avoid prescribing.
5. Create the issue through `selected_backend` (gh:
   `gh issue create --repo <org/repo>`; non-gh: follow `commands.create` or
   the host's shape — never substitute direct `gh`). Apply chosen labels
   through the backend's label flag.
   Do not ask for approval unless the user explicitly asks to review first.
6. Verify each created issue through `selected_backend` (gh:
   `gh issue view --repo <full_name> <number> --json number,url,state`;
   non-gh: follow `commands.view` or the host's shape). Render closeout
   only from the verified `{repo, number, url}` ledger. See
   `references/closeout-discipline.md`.

## Resolve Issue

1. Resolve the target repo and issue selector.
   - one number means one issue
   - `start-end` means the inclusive numeric range
   - no number means newest open issue from GitHub SoT
   - one non-numeric token means repo target; two tokens mean repo target plus
     selector
2. Read each selected issue from GitHub with body, comments, labels, state,
   linked PRs when available, and current branch/repo context. Capture the
   reporter's job-to-be-done in one line: what were they doing when they hit
   this, and what outcome were they trying to reach. If the body does not
   reveal JTBD, record `JTBD: not stated by reporter; inferred from <evidence>`
   or `JTBD: not inferable — proceed from observed problem`. Do not invent.
3. Classify as `bug`, `feature`, `question`, `decision-needed`, or
   `deferred-work` (default `bug` when real-world behavior diverges from a
   documented or implied contract). Routing: `bug` → step 4 causal review;
   `feature`/`deferred-work` → step 6 brief; `question`/`decision-needed`
   → step 7 discussion. Record the classification in the resolution notes.
4. For `bug`-class issues, run a **causal review** before design via a
   bounded fresh-eye subagent that consumes the `debug` substrate cite-only.
   It must include **mental-model sibling search**: abstract the mistaken
   model that allowed the bug, then scan structural siblings beyond keywords
   or nearby files. See `references/causal-review.md` for shape, evidence,
   over-reach rules, and trivial-bug handling. If subagent spawning is
   blocked, stop and report; step 9 is also blocked.
5. Order resolutions as a generative sequence (Christopher Alexander): the
   move that reduces uncertainty or unlocks the next issue comes first. For
   siblings surfaced by step 4, decide whether to bundle into this commit,
   file via `issue new` (ask first), or record as deferred in the close
   comment. Do not file siblings as new issues silently.
6. For `feature` and `deferred-work` issues, emit a **pre-mutation
   resolution brief** to the transcript before invoking any mutation tool.
   Non-empty `open decisions` always forces a pause; the adapter
   `feature_brief_pause` and the invocation flags `--auto`/`--pause` only
   control the empty-decisions case. See `references/resolution-brief.md`
   for the brief template, persistence rule (`issue_tool.py brief-path`
   resolves the dated artifact under `charness-artifacts/issue/` when the
   brief pauses), trivial-feature short-circuit, range-resolve handling,
   and close-comment coupling.
7. Discuss with the user before designing when the issue exposes a product,
   policy, scope, permission, or external-side-effect decision the agent
   should not own.
8. Otherwise, design and implement the smallest complete fix, keeping the
   issue problem statement and the reporter's JTBD as the acceptance boundary.
   Follow the `mutate -> sync -> verify` order from
   `docs/conventions/implementation-discipline.md`: sync generated, plugin,
   and export surfaces before validators. Verify with the strongest honest
   local gate.
9. Run a **resolution critique** focused on recurrence by delegating to
   the `critique` skill (which spawns its own bounded angle + counterweight
   subagents). Pass causal-review output via `references/causal-review.md`.
   When invoked from `impl`, declare `Critique: full <issue-resolution-artifact>`.
   One per fix-unit, not per selector; bundle cheap prevention and record
   deferred. If step 4 was blocked, report blocked state instead of running.
10. Commit, push, and prefer GitHub auto-close via explicit close keywords
    (`Close #1. Close #2.`) in the PR body or direct-to-default commit body;
    preserve them in squash/merge bodies. Use `issue_tool.py close-with-comment`
    only after auto-close is unsupported or fails after remote verification
    (`gh issue close --comment-file` does not exist). The auto-close carrier or
    manual close comment includes the closeout shape by classification:
    - `bug`: JTBD, root cause, `Debug artifact: <path>` (or `none (trivial fix)` / `cite-only`), siblings (bundled/deferred+location), prevention
    - `feature`/`deferred-work`: JTBD, boundary, `Resolution brief: <path>` (or `inline (no pause)` / `trivial`), implementation, prevention
    - `question`/`decision-needed`: JTBD, the answer or recorded decision

## Guardrails

- Do not turn `issue new` into an implementation request. Preserve problem
  context and keep solution ideas tentative.
- Do not resolve an omitted issue selector from session memory. Query GitHub.
- Do not close an issue before the pushed branch contains the fix.
- Do not skip close keywords when the backend can auto-close; manual close is
  the fallback, not the default success path.
- Do not hardcode `gh` when the adapter advertises a stronger backend, and
  do not hide missing backend auth behind a public fetch fallback for
  create, push, comment, or close.
- Do not silently retarget on retry: surface `target_unavailable` instead of
  falling through to another accessible repo.
- Render `issue new` closeout only from the verified `{repo, number, url}`
  ledger; include canonical source identity (URL, gathered-artifact path,
  access mode, freshness) when filed from an external source.
- Do not treat multiple issues as independent when one issue changes the design
  boundary for another.
- Do not misclassify to bypass review or brief: bug → other (skips causal
  review), feature/deferred-work → bug (uses trivial-bug short-circuit),
  feature/deferred-work → question/decision-needed (routes around both).
  Default to `bug` when unsure about real-world divergence; default to
  `feature` when unsure between `feature` and `question`/`decision-needed`.
- Do not skip the step 6 brief or its pause for non-empty `open decisions`
  regardless of adapter setting or `--auto`/`--pause` flags, and do not
  declare a brief "trivial" outside the strict single-file / no-contract /
  no-alternative-surface short-circuit.
- Do not collapse the causal-review or resolution-critique subagent into a
  same-agent local pass; if the host blocks subagent spawning, stop and
  report the blocked state with the concrete host signal.
- Do not satisfy sibling search with keyword or proximity matches alone; name
  the mental model and structural patterns scanned.
- Do not file siblings surfaced by causal review as new issues without first
  asking whether they should be bundled into the current fix.

## References

- `references/issue-shaping.md`
- `references/resolve-flow.md`
- `references/resolution-brief.md`
- `references/causal-review.md`
- `references/issue-backend.md`
- `references/closeout-discipline.md`
- `../../shared/references/fresh-eye-subagent-review.md`
- `../../shared/references/external-capability-proof-ladder.md`
- `scripts/issue_tool.py`
- `scripts/issue_runtime.py`
- `scripts/resolve_adapter.py`
- `scripts/init_adapter.py`
- `scripts/audit_brief.py`
