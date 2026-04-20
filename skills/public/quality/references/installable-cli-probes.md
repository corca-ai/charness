# Installable CLI Probe Contracts

When a repo ships an installable CLI, bootstrap script, or host-visible plugin
surface, `quality` should inspect probe layers as separate seams instead of
treating one `doctor` or one passing smoke command as generic proof.

Check these seams explicitly:

- help probes such as `--help`
- machine-readable command discovery when wrappers or agents depend on it
- binary/runtime health
- repo/install readiness
- local discoverability such as support-skill materialization or host-visible
  plugin state
- lifecycle ownership: one canonical target vs explicit multi-target registry or
  manifest, plus who owns cleanup

Review docs and runtime together:

- README / INSTALL / operator docs should describe install, update, doctor,
  reset, and uninstall behavior without conflating them
- readiness and discoverability should not be reported as generic binary health
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
