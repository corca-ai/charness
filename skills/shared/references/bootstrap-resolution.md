# Bootstrap Resolution (Shared)

Every charness skill's `## Bootstrap` section runs commands of the form

```bash
python3 "$SKILL_DIR/scripts/<name>.py" --repo-root .
```

`$SKILL_DIR` is the directory that holds the SKILL.md being executed. In
agent runtime, the host injects `$SKILL_DIR` automatically. In a fresh
shell (or any non-agent context), it is unset and the commands fail with
`python3: can't open file '/scripts/<name>.py'`.

This reference is the single source of truth for resolving `$SKILL_DIR`
and the optional `$CHARNESS_SUPPORT_DIR` before running bootstrap commands.
Each public and support SKILL.md cites this file at the top of its
`## Bootstrap` section rather than duplicating the explanation.

## Resolve `$SKILL_DIR`

The directory layout determines the value.

### Inside the charness source tree

From the repo root:

```bash
SKILL_DIR=skills/public/<skill-id>    # for public skills
SKILL_DIR=skills/support/<skill-id>   # for support skills
```

Use the directory's relative path, not the absolute path; bootstrap
commands pair `$SKILL_DIR` with `--repo-root .`, so a relative
`$SKILL_DIR` from the current shell directory works the same as the
agent-injected value.

### Inside a consuming repo via Claude Code or Codex agent

The agent runtime injects `$SKILL_DIR` automatically. No operator action
needed — the commands run as written.

### Inside a consuming repo from a manual shell

Locate the SKILL.md in the installed plugin cache (the host's plugin
manager determines this path) and point `$SKILL_DIR` at its parent
directory:

```bash
SKILL_DIR="$(realpath path/to/cache/charness/skills/<skill-id>)"
```

For Codex plugin caches the path is host-defined and rotates on
`charness update`. When a documented path goes stale, use
[resolve_skill_path.py](../../public/find-skills/scripts/resolve_skill_path.py)
from any directory whose `$SKILL_DIR` is known to discover the current
location:

```bash
python3 "$SKILL_DIR/scripts/resolve_skill_path.py" \
  --skill-id <id> --marketplace <m> --plugin <p> --reported-path <stale>
```

## Resolve `$CHARNESS_SUPPORT_DIR` (split monorepo only)

The support tree (`capability.schema.json` and associated support skill
manifests) defaults to `<repo-root>/skills/support/`. Hosts that
materialize the support tree in a sibling package — for example,
`packages/charness-support/` next to `packages/charness-public/skills/` —
need to point loaders at the actual support location:

```bash
export CHARNESS_SUPPORT_DIR=packages/charness-support
```

The override is read by `support_dir()` in
[scripts/repo_layout.py](../../../scripts/repo_layout.py) and flows through
`load_support_capability_schema()` / `load_support_capabilities()`.
Default layouts need no override.

## Why this is operator-resolved, not script-internal

`Path(__file__).resolve().parent.parent` baked into scripts couples them
to a single source layout. Hosts that split public skills from support
assets, or that materialize multiple plugin caches at different hashes,
need an explicit injection seam.

`$SKILL_DIR` from the runtime plus `$CHARNESS_SUPPORT_DIR` when the
support tree is split is that seam. The agent runtime sets `$SKILL_DIR`
implicitly; operators set both manually when running bootstrap commands
outside the agent.
