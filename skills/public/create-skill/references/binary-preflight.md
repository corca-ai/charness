# Binary Preflight

This reference defines how charness skills handle missing non-baseline
binaries. It exists because public skills historically assumed `rg` was
installed and silently returned empty output when it was not, producing
false-healthy signals.

## Baseline

`CHARNESS_BASELINE` names the tools every skill may call without preflighting.
Absence of any baseline tool is a host-bringup failure, not a skill-level
preflight concern.

- `sh` / `bash`
- `git`
- `python3`
- `sed`
- `find`
- `awk`
- `grep`
- basic coreutils (`echo`, `cat`, `head`, `tail`, `sort`, `wc`, `cut`, `tr`, `ls`)

Anything outside this list is non-baseline. Today that notably includes `rg`
(ripgrep), `jq`, `fd`, `bat`, `gh`, `node`, `npm`, `uv`, `pipx`, `yq`.

## Declaration rule

Public skills that call a non-baseline binary in their `Bootstrap` section
must declare it up front inside the same fenced code block with a single
comment on its own line:

```bash
# Required Tools: rg
rg --files docs skills
```

Multiple binaries list comma-separated: `# Required Tools: rg, jq`. The
declaration lives inside the fence so the deterministic gate can find it by
parsing the fence instead of scanning the whole SKILL.md body.

The skill also keeps a pointer to this reference in its `## References` block
or body text:

```markdown
- `references/binary-preflight.md`
```

Skills whose Bootstrap touches only baseline tools declare nothing.

## Failure propagation

The preflight is lazy: it fires when a command actually fails, not at the top
of Bootstrap. That means the failure signal has to survive the shell
invocation. The pattern `rg ... 2>/dev/null || true` silently eats both the
"command not found" stderr message and the exit code 127, so the agent sees
`exit 0` and an empty stdout, indistinguishable from "ran fine, no matches."

To keep failures loud:

- Do not pipe the command through `2>/dev/null || true`. If the skill needs
  to tolerate missing files inside the command's scope, tolerate those
  specifically, not the whole invocation.
- When a `|| true` is genuinely needed (e.g. an `rg` search that may return
  no matches), guard the call with an explicit preflight:

```bash
command -v rg >/dev/null || { echo "MISSING_BIN: rg" >&2; exit 127; }
rg -n "pattern" . || true
```

- `MISSING_BIN: <name>` is the canonical sentinel. When the agent sees it on
  stderr (or sees a shell `command not found` / exit 127 from a Bootstrap
  command), it enters the preflight protocol below.

## Preflight protocol

On missing-binary detection, the agent must:

1. Stop the current Bootstrap step. Do not continue subsequent steps that
   depend on the same binary as if nothing happened.
2. Tell the user plainly: which binary is missing, which skill needs it, and
   why this step needs it (one sentence).
3. Propose the install command for the detected OS using the mapping below.
   One command, one line. No autorun.
4. Wait for explicit user consent. Treat silence as "no."
5. On consent: run the proposed install command; rerun the failed step; keep
   going.
6. On refusal: respect the `CHARNESS_BINARY_PREFLIGHT` mode (see below) to
   decide whether to abort the skill or continue in degraded mode.

Auto-install without consent is forbidden in every mode. Silent skip is
forbidden in every mode.

## Operating modes

`CHARNESS_BINARY_PREFLIGHT` selects runtime behavior when a non-baseline
binary is missing. Default is `interactive`.

- `interactive` — the full protocol above. Suitable for normal agent
  sessions where a human can consent.
- `degraded` — no consent prompt; log `MISSING_BIN: <name> (degraded)` on
  stderr, skip only the affected step, and continue the rest of Bootstrap.
  The skill records the degradation in its durable artifact when it has one
  (e.g. quality's `Runtime Signals` field) so the gap is visible afterward.
  Suitable for test harnesses, scheduled evals, and CI-bound invocations.
- `fail` — log `MISSING_BIN: <name>` and abort the skill with a non-zero
  exit. Suitable for strict CI where missing tools should break the build.

Skills never select the mode themselves. The operator or host sets it in the
environment before invoking the agent.

## Install mapping

V1 scope: `apt`. Any other package manager is out of scope for direct
proposal. When the detected OS is not one of these, the agent asks the user to
install the binary themselves and paste back the command they used; the agent
records that for the session only.

| binary | apt (Debian/Ubuntu) |
| --- | --- |
| `rg` | `sudo apt-get install -y ripgrep` |
| `jq` | `sudo apt-get install -y jq` |
| `fd` | `sudo apt-get install -y fd-find` |
| `gh` | `sudo apt-get install -y gh` |
| `node` | `sudo apt-get install -y nodejs` |
| `uv` | (no apt package; propose `pipx install uv`) |
| `yq` | `sudo apt-get install -y yq` |
| `bat` | `sudo apt-get install -y bat` |

If this table drifts from upstream reality, the escape hatch above is the
cost ceiling: the user is asked to run the correct command themselves and the
session moves on. Do not expand this table without a CI check that exercises
the added entries on a matching base image.

## User prompt template

When entering the interactive protocol, use this shape so messages stay
consistent across skills:

> `quality` needs `rg` (ripgrep) for the repo-signal scan but it is not
> installed on this host. Propose to run `sudo apt-get install -y ripgrep`.
> Say `yes` to run it, `no` to skip this step and continue without it, or
> `abort` to stop the skill.

## Support-skill delegation

Some binaries are not owned by the public skill that invokes them — they
belong to a support skill the public skill dispatches to. Example:
`gather-slack` declares `command -v jq >/dev/null` in its `capability.json`,
and `gather/SKILL.md` never touches `jq` directly.

Rule: the public skill declares the *support skill*, not the binary. The
support skill's `capability.json` remains the single source of truth for its
own binary readiness. The deterministic gate for `Required Tools:` only
fires on binaries the public skill calls directly inside its own Bootstrap
fenced block.

This prevents double-enforcement and keeps the ownership honest: when
`gather-slack` changes its tooling, only its own manifest has to move.

## Migration checklist

When migrating an existing skill to this contract:

1. Read the skill's Bootstrap fences and list every non-baseline binary.
2. Add `# Required Tools: <comma list>` as the first non-blank line inside
   the affected fence.
3. Grep the fence for `2>/dev/null || true` and similar patterns around the
   non-baseline call. Rewrite each one to either (a) drop the swallow on the
   non-baseline call, or (b) guard with the `command -v` sentinel above.
4. Add a pointer to this reference somewhere in the SKILL.md body
   (`## References`, a bullet, or an inline note).
5. Run `scripts/validate-skills.py --repo-root .` to confirm the new gate
   accepts the change.
