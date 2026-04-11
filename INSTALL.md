# charness — Installation Instructions for Operators and AI Agents

This file is the canonical installation contract for `charness`.

Use it when a human or an AI agent needs to install, verify, or refresh the
checked-in `charness` plugin surface for Claude or Codex.

`charness` installs as one plugin bundle. Do not install individual public
skills à la carte.

## Guardrails

- treat [packaging/charness.json](/home/ubuntu/charness/packaging/charness.json)
  as the source of truth
- treat checked-in plugin manifests and marketplace files as derived artifacts
- do not add runtime self-update behavior to skills
- prefer proving the documented install surface over inventing a fallback
- if a host behavior differs from the docs, record the exact behavior instead of
  silently changing the contract

## Prerequisites

- the user asked to install or verify `charness`
- you have a local checkout of this repository or a generated export root
- you can run shell commands and read local files
- for repo-checkout installs, you are working from the checkout root

## Step 1: Verify And Refresh The Install Surface

From the repo root, run:

```bash
python3 scripts/validate-packaging.py --repo-root .
python3 scripts/sync_root_plugin_manifests.py --repo-root .
python3 scripts/plugin_preamble.py --repo-root .
```

Expected checked-in install-surface paths:

- `plugins/charness/.claude-plugin/plugin.json`
- `plugins/charness/.codex-plugin/plugin.json`
- `.claude-plugin/marketplace.json`
- `.agents/plugins/marketplace.json`

If `validate-packaging.py` fails, stop and fix the packaging drift before
continuing.

## Step 2: Choose The Host Install Path

Pick the smallest honest path that matches the user's host:

- Claude Code local checkout: `plugins/charness` plugin root, locally verified
- Claude Code shared marketplace: `corca-ai/charness`, documented and supported
- Codex machine-local personal marketplace: `~/.agents/plugins/marketplace.json`
  backed by `~/.agents/plugins/charness`, preferred operator path
- Codex repo-scoped marketplace: `.agents/plugins/marketplace.json`, documented
  path with continued real-host proof still needed

## Step 3: Claude Code

### Local checkout install

Use the checked-in plugin root directly:

```bash
claude --plugin-dir /absolute/path/to/charness/plugins/charness
```

Smoke check:

```bash
claude --print --plugin-dir /absolute/path/to/charness/plugins/charness \
  "Return exactly one line: charness-smoke"
```

If you need to prove skill runtime from the installed surface, prefer an actual
skill invocation such as:

```bash
claude --print --plugin-dir /absolute/path/to/charness/plugins/charness \
  "/gather Read plugins/charness/README.md and return exactly TITLE:charness if the title is '# charness'."
```

### Shared marketplace install

Use Claude's marketplace flow:

```text
/plugin marketplace add corca-ai/charness
/plugin install charness@corca-charness
```

Update path for a marketplace install:

```text
/plugin update charness@corca-charness
```

## Step 4: Codex

Prefer the machine-local personal marketplace path for operator installs.

### Machine-local personal install

Recommended source checkout location:

```bash
mkdir -p ~/.agents/src
if [ -d ~/.agents/src/charness/.git ]; then
  git -C ~/.agents/src/charness pull --ff-only
else
  git clone https://github.com/corca-ai/charness ~/.agents/src/charness
fi
cd ~/.agents/src/charness
```

Refresh the checked-in install surface, then export the machine-local install:

```bash
python3 scripts/validate-packaging.py --repo-root .
python3 scripts/sync_root_plugin_manifests.py --repo-root .
python3 scripts/install-machine-local.py --repo-root .
```

Expected machine-local result:

- source checkout at `~/.agents/src/charness`
- exported plugin root at `~/.agents/plugins/charness`
- personal Codex marketplace at `~/.agents/plugins/marketplace.json`
- Codex marketplace `source.path` pointing at `./.agents/plugins/charness`

Recommended verification steps:

1. Restart Codex from the home directory that owns
   `~/.agents/plugins/marketplace.json`.
2. Confirm that discovery or install visibility comes from the exported
   `~/.agents/plugins/charness` surface, not from the source checkout tree.
3. If the behavior is ambiguous, record the exact host output and treat that as
   a proof gap to close, not as silent success.

Claude can use the same exported surface:

```bash
claude --plugin-dir ~/.agents/plugins/charness
```

### Repo-scoped development install

`charness` still keeps the repo-scoped marketplace path for local development
and packaging proof.

Required local surface:

- keep `.agents/plugins/marketplace.json` in the checkout
- keep `source.path` pointing at `./plugins/charness`
- reload or restart Codex after updating the checkout

Recommended verification steps:

1. Start Codex from the checkout root that contains `.agents/plugins/marketplace.json`.
2. Confirm that discovery or install visibility comes from the checked-in plugin
   surface, not from the source `skills/` tree.
3. If the behavior is ambiguous, record the exact host output and treat that as
   a proof gap to close, not as silent success.

Current honesty note:

- machine-local personal marketplace is the preferred operator path
- repo-scoped marketplace usage remains the documented development path
- public GitHub-backed install proof is still pending
- `codex exec` alone may not be sufficient proof of local plugin discovery

## Step 5: Update Model

- machine-local install: update `~/.agents/src/charness`, then rerun
  `python3 scripts/install-machine-local.py --repo-root ~/.agents/src/charness`
- local checkout install: update the checkout, then rerun
  `python3 scripts/sync_root_plugin_manifests.py --repo-root .`
- Claude marketplace install: use `/plugin update charness@corca-charness`
- Codex repo-scoped marketplace install: update the checkout behind
  `.agents/plugins/marketplace.json`, then reload Codex
- skill execution must stay read-only with respect to install/update state

## Step 6: Report Back

After installation or verification, report:

1. which host path you used
2. which install surface was exercised
3. which smoke or runtime proof passed
4. whether this was a fresh install, a refresh, or a proof-only check
5. any unresolved host-specific gaps
