# Installable CLI Probe Contracts

When a repo ships an installable CLI, bootstrap script, or host-visible plugin
surface, `quality` should inspect probe layers as separate seams instead of
treating one `doctor` or one passing smoke command as generic proof.

Check these seams explicitly:

- cheap startup probes such as `version`, `--version`, or lightweight
  `doctor --json`
- help probes such as `--help`
- mutating subcommand help probes that prove `cmd mutate --help` is read-only
- option-looking positional probes such as `--help` or `--not-an-instance`
  that must be rejected before any mutation
- machine-readable command discovery when wrappers or agents depend on it
- binary/runtime health
- repo/install readiness
- local discoverability such as support-skill materialization or host-visible
  plugin state
- lifecycle ownership: one canonical target vs explicit multi-target registry or
  manifest, plus who owns cleanup

Review docs and runtime together:

- startup latency claims should point at explicit measured probes, not generic
  "CLI works" prose
- first-touch docs such as README and operator docs should describe install,
  update, doctor, reset, and uninstall behavior without conflating them
- when one canonical bootstrap exists, prefer a pasteable README-first contract
  and a repo-owned next-action surface over telling an agent to fetch a remote
  install doc
- readiness and discoverability should not be reported as generic binary health
- mutating lifecycle commands should expose a dry-run or plan path, or carry an
  explicit waiver that explains why preview is not meaningful
- probe fixtures should watch the actual side-effect seams the CLI owns:
  filesystem roots, service/unit materialization, subprocess runners, or
  persisted manifests
- a missing `cli-side-effect-probes.json` contract is itself a quality finding
  when mutating operator CLI commands are in scope
- executable probe fixtures should opt in explicitly with `safe_to_execute` and
  run through `inventory_cli_side_effect_probes.py --execute-probes`
- if one installed copy is canonical, docs and machine-readable state should
  point at that target directly instead of hiding it behind a registry story
- if multiple managed targets exist, docs should say how they are tracked and
  how stale entries or orphaned copies get cleaned up
- a repo-local install surface should not fail closed on gitignored runtime
  artifacts unless that exact seam is the point of the check

When deeper proof depends on an external binary or evaluator:

- say whether the tool is currently installed, healthy, and ready
- prefer a repo-owned recommendation or doctor helper when one exists
- surface the exact install route and post-install verification command instead
  of telling the operator to rediscover them manually
