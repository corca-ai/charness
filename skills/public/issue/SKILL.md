---
name: issue
description: "Use when filing a GitHub issue from current context or resolving GitHub issues end-to-end through `gh`. Issue creation reports the observed problem before suggesting solutions; issue resolution treats GitHub as the source of truth, classifies the issue, runs a causal review for bug-class issues before designing the fix, and runs a resolution premortem so the same class of issue does not recur."
---

# Issue

Use this when the user wants the agent to file or resolve GitHub issues with
`gh`.

`issue` has two command-shaped intents:

- `issue new [repo]`: create an issue from the current context
- `issue resolve [repo] [number|start-end]`: resolve one or more issues

GitHub is the source of truth. Do not prefer session memory, a just-created
issue, a local note, or a stale artifact over the target repository's current
GitHub state.

This skill consumes the `github-gh` integration. When `gh` is missing or not
authenticated enough for the requested operation, follow
`../../shared/references/binary-preflight.md` and stop with the exact missing
capability.

## Bootstrap

Resolve `SKILL_DIR` to the directory that contains this `SKILL.md`.

```bash
python3 "$SKILL_DIR/scripts/resolve_adapter.py" --repo-root .
python3 "$SKILL_DIR/scripts/issue_tool.py" preflight --json
python3 "$SKILL_DIR/scripts/issue_tool.py" resolve-invocation --repo-root . -- <issue-resolve-args>
```

Before `issue resolve`, select issue numbers through GitHub when the user did
not provide them:

```bash
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
4. Add solution direction only as an optional weak candidate:
   - "This may be solved by..."
   - "A useful outcome might be..."
   - avoid prescribing the receiving agent's design or implementation
5. Create the issue immediately with `gh issue create --repo <org/repo>`.
   Do not ask for approval unless the user explicitly asks to review first.
6. Report the created issue URL and a one-line summary.

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
3. Classify the issue: `bug`, `feature`, `question`, `decision-needed`,
   `deferred-work`. Discriminator: if real-world behavior diverges from a
   documented or implied contract, it is `bug`; default to `bug` when unsure.
   Only `bug` requires the full causal review at step 4. `feature` and
   `deferred-work` skip step 4 and go to step 8 with a design-only premortem.
   `question` and `decision-needed` route to step 6 first. Record the
   classification in the resolution notes.
4. For `bug`-class issues, run a **causal review** before design. Use a bounded
   fresh-eye subagent so the analysis is not anchored on the implementer's
   first hypothesis. The subagent answers three lenses with evidence cited as
   `file:line`, plus an `Over-reach check` line per lens stating the simplest
   evidence the lens found nothing real:
   - root cause: 5-whys or causal chain ending in a structural reason, not a
     symptom
   - detection gap: why this slipped past existing tests, gates, reviews, or
     monitoring until a human reported it
   - sibling search: same pattern at the same layer, abstracted up, or
     specialized down — list concrete locations to inspect
   The subagent prompt must explicitly forbid invoking `issue`, `premortem`,
   `debug`, or other skills that themselves spawn reviewers; nested delegation
   is not allowed unless this skill explicitly requests it. See
   `references/causal-review.md` for the exact prompts, subagent contract, and
   premortem handoff template. If the host blocks subagent spawning, stop and
   report the blocked path; step 8 is also blocked for this run. Do not
   substitute a same-agent pass.
   Run causal review per bug-class issue when resolving a range; share findings
   only when step 5 bundles fixes.
   **Trivial-bug short-circuit**: if the fix is single-line, the root cause is
   self-evident from the diff, no public contract changes, and no plausible
   siblings exist, record `Causal review: trivial; root cause = <one line>` and
   skip the subagent. Step 8 still runs.
5. Choose the resolution order that reduces uncertainty. If one issue unlocks
   another, do it first. If causal review at step 4 surfaced sibling problems,
   decide here whether to bundle their fix into this commit, file them as
   separate issues via `issue new` (resolve owns the "ask first" decision; the
   filing itself follows `issue new`'s create-immediately rule), or leave them
   in the close comment as deferred items. Do not file siblings as new issues
   silently.
6. Discuss with the user before designing when the issue exposes a product,
   policy, scope, permission, or external-side-effect decision the agent
   should not own.
7. Otherwise, design and implement the smallest complete fix, keeping the
   issue problem statement and the reporter's JTBD as the acceptance boundary.
   Follow the `mutate -> sync -> verify` order from
   `docs/conventions/implementation-discipline.md`: sync generated, plugin,
   and export surfaces before validators. Verify with the strongest honest
   local gate.
8. Run a **resolution premortem** focused on recurrence: what would let this
   class of issue (and the siblings surfaced at step 4) come back. Delegate
   to the `premortem` skill, which spawns its own bounded angle and
   counterweight subagents. Pass causal-review output as prior context using
   the handoff template in `references/causal-review.md`. This resolution
   premortem satisfies the CLAUDE.md task-completion premortem obligation;
   when invoked from `impl`, declare `Premortem: full <issue-resolution-artifact>`
   instead of running a second generic pass. If step 4 was blocked and there
   is no causal-review output to chain, do not run premortem against an empty
   prior context — report the blocked state in the close artifact. Run one
   premortem per fix-unit (single issue or bundled siblings), not per issue
   selector. Bundle structural prevention (guard, test, doc, tool) with the
   fix when cheap; record what is deliberately deferred.
9. Commit, push, and close the GitHub issue only after the fix is on the
   remote. Use explicit close keywords per issue (`Close #1. Close #2.` and
   so on) when relying on GitHub auto-close behavior. The close comment
   shape depends on classification, restated per issue when resolving a range:
   - `bug`: JTBD, root cause, sibling decisions (bundled or deferred with
     locations), recurrence-prevention move
   - `feature` / `deferred-work`: JTBD, what was implemented, any
     premortem-bundled prevention
   - `question` / `decision-needed`: JTBD, the answer or recorded decision

## Guardrails

- Do not turn `issue new` into an implementation request. Preserve problem
  context and keep solution ideas tentative.
- Do not resolve an omitted issue selector from session memory. Query GitHub.
- Do not close an issue before the pushed branch contains the fix.
- Do not hide missing `gh` auth behind a public fetch fallback when the task
  requires creating, pushing, commenting, or closing.
- Do not treat multiple issues as independent when one issue changes the design
  boundary for another.
- Do not skip causal review on bug-class issues by classifying them as
  `feature`, `question`, `decision-needed`, or `deferred-work` to bypass the
  subagent step. Misclassification is the failure mode this guard exists to
  catch; default to `bug` when unsure.
- Do not collapse the causal-review or resolution-premortem subagent into a
  same-agent local pass. If the host blocks subagent spawning, stop and report
  the blocked state with the concrete host signal.
- Do not file siblings surfaced by causal review as new issues without first
  asking whether they should be bundled into the current fix.

## References

- `references/issue-shaping.md`
- `references/resolve-flow.md`
- `references/causal-review.md`
- `../../shared/references/fresh-eye-subagent-review.md`
- `scripts/issue_tool.py`
- `scripts/issue_runtime.py`
- `scripts/resolve_adapter.py`
- `scripts/init_adapter.py`
