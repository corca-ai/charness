# Debug Review
Date: 2026-04-11

## Problem

`tests/test_charness_cli.py::test_charness_update_reports_codex_version_drift`
failed because `charness update` stopped at `managed checkout ... has local
changes` instead of reporting Codex cache drift.

## Correct Behavior

Given a fresh managed checkout created by `charness init`, when `charness
update` runs immediately afterward, then the checkout should remain clean and
the command should report Codex source/cache version drift rather than fail on
repo dirt.

## Observed Facts

- A test-style repro (`init` into a temp home, then `git status --short` inside
  the managed checkout) showed dirty files immediately after init.
- The dirty paths were all under `plugins/charness/`, including an untracked
  `plugins/charness/scripts/install_tools.py`.
- `install_surface()` runs `scripts/sync_root_plugin_manifests.py` before
  exporting the machine-local plugin root.

## Reproduction

```bash
python3 - <<'PY'
import os, subprocess, tempfile
from pathlib import Path
from tests.test_charness_cli import make_fake_claude, run_cli

tmp = Path(tempfile.mkdtemp(prefix='charness-debug-'))
home_root = tmp / 'home'
fake_claude = make_fake_claude(tmp)
env = os.environ.copy()
env['HOME'] = str(home_root)
env['PATH'] = f"{fake_claude.parent}:{env.get('PATH', '')}"
run_cli('init', '--home-root', str(home_root), env=env)
repo = home_root / '.agents' / 'src' / 'charness'
print(subprocess.run(['git', 'status', '--short'], cwd=repo, capture_output=True, text=True).stdout)
PY
```

## Candidate Causes

- checked-in `plugins/charness/` export drifted from the source checkout
- `charness init` wrote host-local files into the source checkout by mistake
- git dirty detection was counting harmless generated cache files that should be
  ignored

## Hypothesis

If the checked-in plugin surface is stale, then `sync_root_plugin_manifests.py`
will rewrite `plugins/charness/` during init/update, and a fresh git clone of
the repo will become dirty before `git pull --ff-only`.

## Verification

- Running `scripts/sync_root_plugin_manifests.py --repo-root .` reproduced the
  same `plugins/charness/` changes in the current checkout.
- After committing the refreshed `plugins/charness/` surface, the failing
  managed-checkout drift test no longer depends on uncommitted local files.

## Root Cause

The repo's checked-in plugin export surface had drifted behind the source
checkout. `charness init` correctly re-synced that surface, which made a fresh
managed clone dirty and caused `charness update` to fail before reporting Codex
cache drift.

## Prevention

- Commit refreshed `plugins/charness/` export changes whenever source packaging
  surfaces change.
- Keep the managed-checkout init/update test in the normal quality path because
  it catches HEAD-vs-worktree export drift that repo-local validators can miss.
