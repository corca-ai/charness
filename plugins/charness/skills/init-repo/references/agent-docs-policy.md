# Agent Docs Policy

`init-repo` owns one explicit repo-level host policy:

- `<repo-root>/AGENTS.md` is the canonical repo instruction file
- `CLAUDE.md` should symlink to `<repo-root>/AGENTS.md` when Claude compatibility is needed
- when the repo requires bounded fresh-eye or premortem-style subagent review
  as a stop gate, `<repo-root>/AGENTS.md` should carry one short rule that this review is
  the user's explicit delegation request for that bounded scope and is already
  delegated by the repo contract
- for Charness-managed repos, that rule should also name task-completing
  `init-repo` and `quality` review runs as authorized to spawn bounded
  reviewers; a Premortem-only heading is too narrow for this policy
- when adapter-declared policy sources imply delegated review but
  `<repo-root>/AGENTS.md` lacks the explicit host-spawn rule, emit a reviewable
  recommendation instead of treating phrase matching as a hard fact
- when a repo uses Charness durable artifacts, `<repo-root>/AGENTS.md` should say
  meaningful `charness-artifacts/` changes are commit targets, and
  current-pointer helpers should no-op when canonical content has not changed

## Deterministic Cases

- no `<repo-root>/AGENTS.md`, no `CLAUDE.md`
  - create `<repo-root>/AGENTS.md`
  - create `CLAUDE.md -> AGENTS.md`
- `<repo-root>/AGENTS.md` exists, `CLAUDE.md` missing
  - create the symlink
- `CLAUDE.md` already symlinks to `<repo-root>/AGENTS.md`
  - leave it alone

## Ask-The-User Cases

- `CLAUDE.md` exists as a real file and `<repo-root>/AGENTS.md` is missing
  - ask whether to promote `CLAUDE.md` content into `<repo-root>/AGENTS.md` and replace
    `CLAUDE.md` with a symlink
- both exist as real files
  - ask whether to merge the meaningful Claude-only content into `<repo-root>/AGENTS.md`
    and replace `CLAUDE.md` with a symlink

## Rule

Do not silently overwrite or merge meaningful user-authored host instructions.

When the repo uses bounded fresh-eye or premortem-style subagent review as a
stop gate, prefer a short rule like:

- Repo-mandated bounded fresh-eye subagent reviews are already delegated by the repo contract.
- This rule is the user's explicit delegation request for the bounded review
  scopes it names.
- Task-completing `init-repo` and `quality` review runs are already authorized
  to spawn bounded reviewers.
- Do not wait for a second user message asking for delegation.
- If the host blocks subagent spawning, stop and report the host restriction explicitly instead of substituting a same-agent pass.

Place the rule in a general operating, validation, or review-policy section
when it covers more than premortem. Do not hide `init-repo` and `quality`
spawn authorization under a Premortem-only heading.

When the repo uses Charness artifacts, prefer a short rule like:

- Treat `charness-artifacts/` as repo state, not scratch.
- Commit meaningful durable artifact changes with the work they support.
- Current-pointer helpers should no-op when canonical content has not changed.
- If a helper rewrites an artifact without canonical change, treat that as
  invocation drift or a helper bug to fix.
