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
`charness catalog resolve-skill-path` (`<plugin-dir>/scripts/adapters/capability_catalog.py`)
from any directory whose `$SKILL_DIR` is known to discover the current
location:

```bash
charness catalog resolve-skill-path --repo-root . \
  --skill-id <id> --marketplace <m> --plugin <p> --reported-path <stale>
```

## Resolve `<plugin-dir>/` (and why `$SKILL_DIR/../..` is not it)

`<plugin-dir>/` names the **installed plugin package root** — the directory that
holds `skills/`, `shared/`, `support/`, and `scripts/` in a consumer's tree. It is
agent-resolved, like `$SKILL_DIR`: from a known `$SKILL_DIR` in an installed
layout it is two levels up.

```bash
{
  export PLUGIN_DIR="$(realpath "$SKILL_DIR/../..")"   # installed layout only
  python3 "$PLUGIN_DIR/scripts/<name>.py" --repo-root .
}
```

**Measured 2026-08-04, and this is the part that is easy to get wrong.**
`$SKILL_DIR/../..` lands on a DIFFERENT directory in each tree, and only two
entries exist at both positions:

| tree | `$SKILL_DIR/../..` | entries there |
| --- | --- | --- |
| charness source | `skills/` | `public/`, `shared/`, `support/` |
| installed plugin | `<plugin-dir>/` | `skills/`, `shared/`, `support/`, `scripts/`, `agents/`, … |

So `$SKILL_DIR/../../shared/…` and `$SKILL_DIR/../../support/…` are correct in
**both** trees — by the same exporter cancellation that makes a packaged
`parents[3]` correct in both, since the flattened `<kind>` level and the added
package level cancel. Everything else under that root exists only in the
installed tree: `scripts/` is at the repo root in the source tree, and a skill is
at `skills/<kind>/<skill>/` there rather than `skills/<skill>/`.

That gives a rule with no judgement in it:

- referencing `shared/` or `support/` → keep `$SKILL_DIR/../..`; it resolves in
  both trees, and the invariant above is why.
- referencing another skill, or a plugin-level `scripts/` helper → there is **no**
  both-trees relative spelling. Say `<plugin-dir>/skills/<skill>/…` or
  `<plugin-dir>/scripts/…` rather than guessing a `../` count. A charness
  maintainer reads the corresponding source at `skills/<kind>/<skill>/`.

Unlike `<repo-root>/`, this placeholder is **checkable**: each reference is
resolved against the matching path under the generated `plugins/<pkg>/` package,
and a dangling target is refused by the native `plugin-refs` gate
(`<plugin-dir>/scripts/native_gate_lib.py ... plugin-refs`). `<repo-root>/` means
the reader's own tree and is unverifiable from here by construction, which is what
let a class of unreachable references accumulate.

Non-claim: no host is known to substitute `<plugin-dir>/` textually. It is
resolved by the agent following this section, and the checker proves only that the
target exists in the package this repo generates.

## Enforced for write helpers inside the charness source tree

The "use the repo's own copy" rule above is now enforced, not just documented.
Write helpers that persist repo state — `refresh_recent_lessons.py`,
`persist_retro_artifact.py`, `build_debug_seam_risk_index.py` — call
`require_repo_local_helper` from
`<plugin-dir>/scripts/core/helper_provenance_lib.py`
before doing any work. `build_retro_lesson_selection_index.py` is guarded
indirectly and later, at the moment `recent_lessons_lib` writes;
`publish_release.py` is guarded at the entrypoint instead (below).

Two placements, with different scans:

- **Write sites** (the helpers above) check at the moment they persist state, and
  compare the loaded anchors plus already-imported modules.
- **Irreversible entrypoints** — `publish_release.py` and
  `issue_tool.py close-with-comment` — check before any mutation, and compare *every* Python
  module in both trees (`scan="tree"`). The wider scan is required because the
  module that drifts is usually imported lazily, long after the entrypoint, and
  because `publish_release` bumps the target version only after that point, so
  neither the import-anchor nor the version signal is available yet.

Its drift refusal (exit status 2) fires only when all of these hold: the running
script belongs to a different charness tree than `--repo-root`, that `--repo-root`
is a charness **source** checkout, and the two copies differ by declared version or by
compared module content. It refuses for two further reasons that are *not* drift,
both recorded below: `scope-unestablished` (a verdict reached with no counterpart
resolved at all) and `own-root-unestablished` (the running script's own tree could
not be located, so there is nothing to compare *from*).
"A different tree" includes one *contained* in the
target — the materialized `plugins/<pkg>` export is a second charness tree, and it
is stale during every `mutate -> sync` window, so it is compared rather than
exempted. When the target carries its own copy of the invoked helper, the refusal
names it and rewrites the invocation's own arguments in place — the repo root
retargeted to `.` where the operator put it, so a subcommand CLI stays runnable —
because that is the only remediation that terminates; re-running the drifted copy
overwrites the fix. For the repo's own materialized `plugins/<pkg>` export the
refusal names the resync instead, since that is the one command that ends its
staleness. For any other copy with no counterpart in the target, the refusal says
so and asks the operator to stop and decide rather than resync and retry, since
the resync can be what removes the entry point. `--help` and the read-only
`--prep-update-instructions` affordance are not refused. Runs against an ordinary
consuming repo are untouched, since a consuming repo owns no competing copy.
A verdict reached with no counterpart resolved at all is refused as
`scope-unestablished` rather than passed: "found no drift" and "compared nothing"
are different facts. A run whose *own* tree cannot be located — no
`<plugin-dir>/scripts/runtime_bootstrap.py` marker
above the invoked copy, so the guard cannot
name the tree it is comparing from — is refused as `own-root-unestablished` for
the same reason, and its refusal message names the missing marker rather than
claiming a comparison that never ran. That refusal is scoped to **source-tree
targets**: against an ordinary consuming repo, where no competing copy exists, an
unlocatable own root stays `consuming-repo` and is allowed.
`CHARNESS_ALLOW_FOREIGN_HELPER=1` downgrades any of these refusals to
a warning when the copies are known to be compatible.

**Known bypass.** `CHARNESS_REPO_ROOT` retargets
`<plugin-dir>/scripts/runtime_bootstrap.py`'s module
loader, so a guarded library imported through it belongs to the override root and
classifies `same-tree`. The code that runs is then the target's own, but the
invoking entry script's drift goes unchecked. Treat it as a second override
alongside `CHARNESS_ALLOW_FOREIGN_HELPER`, not as a supported way to write
through a stale copy.

That bypass covers library-site guards, which pass their own `__file__`. It does
**not** cover skill entry scripts, which pass the *invoked script's* `__file__`:
a markerless copy of one of those, run with `CHARNESS_REPO_ROOT` pointed at a
source checkout, is refused as `own-root-unestablished` rather than classified
`same-tree`.

**What this cannot do.** Every one of these checks lives in the copy being
invoked, so a copy old enough to predate the check does not carry it — which is
exactly how two `v2.11.2` publishes got through. That includes the contained
`plugins/<pkg>` mirror: the guard module a mirror invocation loads is the
mirror's own, so a change to the guard itself is unenforced until the next sync
(one window, not one update cycle)
(RCA in `<authoring-repo>/charness-artifacts/debug/2026-07-27-absent-guard-not-dead-guard.md`).
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
`<plugin-dir>/scripts/core/repo_layout.py` and flows through
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
