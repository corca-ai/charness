# Bootstrap Resolution (Shared)

Every charness skill's `## Bootstrap` section runs commands of the form

```bash
python3 "$SKILL_DIR/scripts/<name>.py" --repo-root .
```

`$SKILL_DIR` is the directory that holds the SKILL.md being executed. An
agent runtime may know the skill source location without exporting a
`SKILL_DIR` variable into the command shell. In a fresh shell (or any
non-agent context), it is unset and the commands fail with
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
{
  export SKILL_DIR=skills/public/<skill-id>    # for public skills
  # or: export SKILL_DIR=skills/support/<skill-id>
  python3 "$SKILL_DIR/scripts/<name>.py" --repo-root .
}
```

When the command is launched from the Charness source root, this relative
path pairs with `--repo-root .`. If it is launched from another directory,
resolve an absolute skill path and pass the consuming repository's absolute
root instead:

```bash
{
  export SKILL_DIR="$(realpath /path/to/charness/skills/public/<skill-id>)"
  python3 "$SKILL_DIR/scripts/<name>.py" --repo-root /path/to/consuming-repo
}
```

Keep the export and every dependent expansion in the same persistent shell
session/tool invocation; exporting in one ephemeral tool call does not set
the variable for a later call.

### Inside a consuming repo via Claude Code or Codex agent

The runtime's skill source locator is not proof that the command environment
contains `$SKILL_DIR`. Check it (`printf '%s\n' "${SKILL_DIR-}"`) and export
the resolved path in the shell when it is missing.

### Inside a consuming repo from a manual shell

Locate the SKILL.md in the installed plugin cache (the host's plugin
manager determines this path) and point `$SKILL_DIR` at its parent
directory:

```bash
{
  export SKILL_DIR="$(realpath path/to/cache/charness/skills/<skill-id>)"
  python3 "$SKILL_DIR/scripts/<name>.py" --repo-root /path/to/consuming-repo
}
```

Do not put the assignment in front of the command as an environment prefix:

```text
SKILL_DIR=/path/to/skill python3 "$SKILL_DIR/scripts/<name>.py"
```

Shell expands `"$SKILL_DIR"` before applying that temporary assignment, so
this can use the previous value (including an unset value and `/scripts/...`).

For Codex plugin caches the path is host-defined and rotates on
`charness update`. When a documented path goes stale, use
[charness catalog resolve-skill-path](../../../scripts/capability_catalog.py)
from any directory whose `$SKILL_DIR` is known to discover the current
location:

```bash
charness catalog resolve-skill-path --repo-root . \
  --skill-id <id> --marketplace <m> --plugin <p> --reported-path <stale>
```

## Enforced for write helpers inside the charness source tree

The "use the repo's own copy" rule above is now enforced, not just documented.
Write helpers that persist repo state — `refresh_recent_lessons.py`,
`persist_retro_artifact.py`, `publish_release.py`,
`build_retro_lesson_selection_index.py`, `build_debug_seam_risk_index.py` — call
`require_repo_local_helper` from
[scripts/helper_provenance_lib.py](../../../scripts/helper_provenance_lib.py)
before doing any work.

Two placements, with different scans:

- **Write sites** (the helpers above) check at the moment they persist state, and
  compare the loaded anchors plus already-imported modules.
- **Irreversible entrypoints** — `publish_release.py` and `issue_tool.py
  close-with-comment` — check before any mutation, and compare *every* Python
  module in both trees (`scan="tree"`). The wider scan is required because the
  module that drifts is usually imported lazily, long after the entrypoint, and
  because `publish_release` bumps the target version only after that point, so
  neither the import-anchor nor the version signal is available yet.

It refuses (exit status 2) only when all of these hold: the running script
belongs to a different charness tree than `--repo-root`, that `--repo-root` is a
charness **source** checkout, it carries its own copy of the same helper, and the
two copies differ by declared version or by compared module content. The refusal
names the target repo's own copy and repeats the invocation's other arguments,
because that is the only remediation that terminates — re-running the drifted
copy overwrites the fix. `--help` and the read-only
`--prep-update-instructions` affordance are not refused. Runs against an ordinary
consuming repo are untouched, since a consuming repo owns no competing copy.
`CHARNESS_ALLOW_FOREIGN_HELPER=1` downgrades the refusal to a warning when the
copies are known to be compatible.

**What this cannot do.** Every one of these checks lives in the copy being
invoked, so a copy old enough to predate the check does not carry it — which is
exactly how two `v2.11.2` publishes got through
([RCA](../../../charness-artifacts/debug/2026-07-27-absent-guard-not-dead-guard.md)).
Treat it as a fast, well-worded failure for copies that carry it, not as closure
of the foreign-write class; the target repo's own validators remain the
enforcement that does not depend on the caller's age.

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
support tree is split is that seam. A host may provide the skill source
locator without exporting `$SKILL_DIR`; operators set both manually when
running bootstrap commands outside the agent.
