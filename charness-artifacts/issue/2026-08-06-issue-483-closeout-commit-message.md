Closes #483

Classification: deferred-work
JTBD: Shipped JSON/YAML/YML assets must not carry commands that only resolve in
the authoring skills/public or skills/support tree and therefore disappear in a
consumer's installed plugin.
Boundary: In scope is typed structured-asset traversal, source-to-shipped path
mapping, source/export/layout fail-closed reporting, interpreter-option coverage,
the two live asset repairs, source/plugin parity, and the run-quality bundle gate.
Out of scope is arbitrary string classification, general shell parsing, installed
consumer execution, and remote CI.
Resolution brief: inline (no pause) — add one typed asset gate over tracked plugin
JSON/YAML/YML values, reject authoring-layout carriers even when source or export
is missing, and require plugin-relative paths in shipped assets.
Implementation: Added scripts/check_plugin_asset_command_carriers.py and its generated
plugin mirror, added seven focused regression tests, repaired the vulture host note
and achieve adapter command template, synchronized source/plugin manifests, queued
the gate in scripts/run-quality.sh, and recorded the quality and critique artifacts.
Prevention: The gate fails on malformed assets, unsupported package layout, missing
authoring source, missing export, and interpreter options that precede a carrier;
source/plugin parity and the timing-layer completeness meta-gate remain enforced.
Critique #483: charness-artifacts/critique/2026-08-06-issue-483-non-markdown-command-carrier-resolution-critique.md
Behavior #483: local-only-by-contract — the focused structured-asset suite passed
7 tests, the direct gate validated 62 tracked shipped assets with no findings,
the timing meta-gate classified all 89 run-quality validators, and source/plugin
copies were synchronized. Installed-consumer execution, provider behavior, remote
CI, and GitHub state are not claimed by this local verdict.
Fresh-Eye Satisfaction: parent-delegated; round 1 found timing/source/layout
fail-open defects and round 2 found interpreter-option bypass. All round-1 repairs
were verified; the final round-2 repair is accepted-unreviewed under the two-round cap.
AI-provenance: Agent-authored direct-commit carrier; implementation, focused evidence,
source/plugin sync, bounded fresh-eye findings, accepted-unreviewed disposition, and
non-claims are recorded in the linked artifacts.
