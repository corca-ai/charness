# Agent Docs Policy

`init-repo` owns one explicit repo-level host policy:

- `AGENTS.md` is the canonical repo instruction file
- `CLAUDE.md` should symlink to `AGENTS.md` when Claude compatibility is needed

## Deterministic Cases

- no `AGENTS.md`, no `CLAUDE.md`
  - create `AGENTS.md`
  - create `CLAUDE.md -> AGENTS.md`
- `AGENTS.md` exists, `CLAUDE.md` missing
  - create the symlink
- `CLAUDE.md` already symlinks to `AGENTS.md`
  - leave it alone

## Ask-The-User Cases

- `CLAUDE.md` exists as a real file and `AGENTS.md` is missing
  - ask whether to promote `CLAUDE.md` content into `AGENTS.md` and replace
    `CLAUDE.md` with a symlink
- both exist as real files
  - ask whether to merge the meaningful Claude-only content into `AGENTS.md`
    and replace `CLAUDE.md` with a symlink

## Rule

Do not silently overwrite or merge meaningful user-authored host instructions.
