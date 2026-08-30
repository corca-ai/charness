# Probe Record: current-release-version-refusal

Slice 5, debt row 2. The release IDENTITY surface: which package this release is, and
where it lives.

Claim: `current_release.py` refuses when the adapter's version was not speakable, instead
  of resolving the package id and both release paths from charness defaults
Claim kind: change
Observable: the `package_id`, `packaging_manifest_path` and current
  `materialized_plugin_root` equivalent the
  CLI prints, and its process exit code, under a repo that declared all three
Source ref: scripts/adapter-consumer-classification.json
Source revision: bda87440c
Source conditions: the adapter's declared version is one this reader does not speak, so
  every field the repo declared is replaced by the reader's inferred defaults
Base ref: bda87440c
Head ref: f7d3fb70e
Base arm: base-observed
Call sites unproven: none — one adapter-payload call site (`load_adapter` in
  `build_payload`), guarded at that read site, so the three modules importing
  `build_payload` directly (`publish_release_cli`, `publish_release_plan`,
  `plan_release_run`) inherit it rather than each needing their own guard; a round-1
  bounded review verified all three importers and refuted the harm claim recorded in the
  non-claims below, not the coverage claim recorded here

## Source text

Verbatim from the manifest at the pinned revision.

```
    "skills/public/release/scripts/current_release.py": {
      "verdict": "accepted-risk-unguarded",
      "reason": "build_payload() (line 169-174) does `adapter = load_adapter(repo_root); data = adapter[\"data\"]` with no error/valid check gating any of the path resolution, then computes `manifest_path`, `package_id`, `plugin_root` from `data[\"packaging_manifest_path\"]`, `data[\"package_id\"]`, `data[\"checked_in_plugin_root\"]` and later the `drift`/`absence_corroboration` verdict at line 245-286 that `plan_release_run.py` routes on (per the file's own comment at line 209: \"drift is the gate ... plan_release_run_packets routes on\")."
    },
```

The source names the unguarded path resolution and the downstream `drift` verdict that
`plan_release_run` routes on. The specific defaults observed below are this probe's
measurement, not the row's claim.

## Stimulus

A temp repo declaring a package id and both release paths that differ from anything
charness would infer, under a version this reader refuses. The real CLI is run against
it.

```
mkdir -p $D/.agents $D/vendor/mypkg/.claude-plugin
cat > $D/.agents/release-adapter.yaml <<'YAML'
version: 9
package_id: acme-harness
packaging_manifest_path: vendor/mypkg/manifest.json
materialized_plugin_root: vendor/mypkg
YAML
echo '{"version": "7.7.7"}' > $D/vendor/mypkg/manifest.json
echo '{"version": "7.7.7"}' > $D/vendor/mypkg/.claude-plugin/plugin.json
python3 skills/public/release/scripts/current_release.py --repo-root $D
```

## Base observable

The repo declared `acme-harness` and `vendor/mypkg`. EXCERPTED at the four fields this
row is about — the full payload carries ~12 top-level keys, and the omitted ones are not
evidence either way:

```
  valid: false
package_id: probe-cr-EsjAMq
packaging_manifest_path: /tmp/probe-cr-EsjAMq/packaging/probe-cr-EsjAMq.json
checked_in_plugin_root: /tmp/probe-cr-EsjAMq/plugins/probe-cr-EsjAMq
exit 0
```

`package_id` is the repo's own DIRECTORY NAME, and neither path exists. `valid: false` is
printed in the same payload and acted on by nothing — a read is not a check.

## Head observable

```
`.agents/release-adapter.yaml` declares a `version` this reader does not speak (version must be 1). Nothing the adapter declares is being honored, so this run would fall back to charness defaults rather than to what the repo declared -- refusing instead. Set `version: 1`, or upgrade the reader, then re-run.
exit 1
```

## Polarity controls

- speakable version (`version: 1`), same declarations → `package_id: acme-harness`,
  `materialized_plugin_root: .../vendor/mypkg`, exit 0. The guard does not fire on good
  input, and the surface now reports what the repo actually said.
- no adapter file at all → a payload with an inferred `package_id`, exit 0. The opt-in
  design survives: declaring nothing is not the same as declaring something unreadable.

## Non-claims

- **The guard this record measured keyed on ONE door, and a round-1 bounded review found a
  second.** `version: !!int 9` — one token added to this record's own stimulus — makes the
  parser refuse the document, and `simple_skill_adapter_lib` answers that with
  `infer_repo_defaults(...)` plus a `parse_failure_error`, the same "nothing declared is
  honored" state by a different door. At this record's `Head ref` that input still reached
  the base behavior. It is closed in a later commit, by keying
  `adapter_version_verdict` on the CONDITION rather than on one check's wording; the
  base/head pair recorded above is unaffected and was not re-measured for the second door.
- **The read-site rationale is narrower than this record first implied, corrected after a
  round-1 bounded review.** Under an unhonored declaration `publish_release_cli` and
  `publish_release_plan` stop earlier, at `_valid_adapter_data`. ONE importer genuinely
  reached a charness default here: `plan_release_run`, which calls `build_payload`
  unconditionally ahead of its own validity gates. So read-site placement removed one
  measured live harm and bought positional independence for the other two — not three
  live harms.

- One file. It says nothing about the other 35 `accepted-risk-unguarded` rows.
- Captured by running the CLI, not read off the diff. A distinct observer re-running the
  stimulus can confirm it; this record cannot prove it.
- `guarded` is a claim about the version refusal only. The `drift`/`absence_corroboration`
  verdict the source names is downstream of the same payload and is not separately
  asserted here.
