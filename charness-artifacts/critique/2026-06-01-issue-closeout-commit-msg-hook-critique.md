# Critique - Issue Closeout Commit-Message Hook

Fresh-Eye Satisfaction: parent-delegated
Reviewers: Meitner (`019e8006-1009-7a43-b58e-3a0fab7a38a8`), Singer (`019e800b-8520-7b23-ad40-2ffce47d110f`)
Target: commit-message hook implementation for issue closeout carriers

## Scope

Add a repo-owned `commit-msg` hook that blocks commits staging
`charness-artifacts/issue/*.md` closeout artifacts with `Close #N` keywords
unless the final commit message carries matching close keywords and required
closeout ledger fields.

Also make the hook available to Charness-using repos through
`scripts/install-git-hooks.sh --repo-root <consumer>`.

## Fresh-Eye Findings

### First Review

Verdict: no-go as-is.

Blockers:

- The checker hardcoded the authoring layout
  `skills/public/issue/scripts/issue_verify_closeout.py`, which fails from the
  exported plugin layout (`skills/issue/scripts/...`).
- Consumer repos did not actually receive a hook; the installer only pointed at
  an existing `.githooks` directory.

Resolution:

- The checker now resolves both authoring and exported plugin issue-skill
  layouts.
- `install-git-hooks.sh --repo-root <consumer>` materializes a consumer
  `.githooks/commit-msg` hook that calls the installed checker.

### Second Review

Verdict: no-go as-is.

Blockers:

- The plugin-export installer still required source `.githooks` before reaching
  the consumer materialization branch.
- The maintainer setup validator required the full Charness source hook set
  (`pre-commit`, `commit-msg`, `pre-push`) even for consumer repos where the
  installer intentionally materializes only `commit-msg`.

Resolution:

- Consumer installs no longer require source `.githooks`; only self-installs of
  the Charness source repo require the checked-in hook directory.
- `validate_maintainer_setup.py` requires the full hook set only for the
  Charness source repo. Consumer repos with only Charness' generated
  `commit-msg` hook can pass.
- The consumer hook smoke test now uses `plugins/charness/scripts/install-git-hooks.sh`
  and proves a bad issue closeout commit is blocked.

## Residual Risks

- The hook only triggers from staged issue closeout artifacts that contain
  close keywords outside code fences. That is the first enforceable slice, not
  full inference of all issue-resolving commits.
- The commit message ledger is validated for required fields, not deep semantic
  equality with the artifact body.

## Verification

- `pytest -q tests/quality_gates/test_issue_closeout_commit_msg_hook.py tests/quality_gates/test_quality_runner.py::test_install_git_hooks_materializes_consumer_commit_msg_hook tests/quality_gates/test_quality_runner.py::test_install_git_hooks_sets_core_hookspath tests/quality_gates/test_quality_runner.py::test_validate_maintainer_setup_requires_installed_hookspath`
- consumer smoke: `plugins/charness/scripts/install-git-hooks.sh --repo-root <tmprepo>` then `git commit -m 'bad carrier'` blocked by generated `commit-msg`
- `python3 scripts/validate_packaging_committed.py --repo-root .`
- `python3 scripts/validate_maintainer_setup.py --repo-root .`
- `./scripts/run-quality.sh --read-only` passed with 68 checks

## Verdict

Go after the listed fixes. The current implementation enforces the commit
carrier invariant in the Charness source repo and materializes the hook for
Charness-using consumer repos.
