# GitHub Actions Defaults

When `init-repo` scaffolds or normalizes GitHub-hosted workflows, prefer the
current documented majors for first-party JavaScript actions instead of older
pins that only fail later through hosted-runner warnings.

Current baseline as of 2026-04-13:

- `actions/checkout@v6` (`v5` was the first Node 24-ready major)
- `actions/setup-node@v6` (`v5` was the first Node 24-ready major)
- `actions/setup-go@v6`
- `actions/setup-python@v6`
- `actions/cache@v5`
- `actions/github-script@v8`

Prefer direct upgrades in workflow YAML.

Compatibility env vars are temporary rollout tools, not scaffold defaults:

- `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24=true` is acceptable only as a short-lived
  runner-readiness check while validating or staging the upgrade.
- `ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION=true` is an emergency escape hatch
  while removing old action majors, not a durable fix.

If the repo uses self-hosted runners, verify the runner floor before upgrading.
Current Node 24 GitHub JavaScript actions generally require Actions Runner
`v2.327.1` or newer.

Official references:

- `actions/checkout`: <https://raw.githubusercontent.com/actions/checkout/main/README.md>
- `actions/setup-node`: <https://raw.githubusercontent.com/actions/setup-node/main/README.md>
- `actions/setup-go`: <https://raw.githubusercontent.com/actions/setup-go/main/README.md>
- `actions/setup-python`: <https://raw.githubusercontent.com/actions/setup-python/main/README.md>
- `actions/cache`: <https://raw.githubusercontent.com/actions/cache/main/README.md>
- `actions/github-script`: <https://raw.githubusercontent.com/actions/github-script/main/README.md>
