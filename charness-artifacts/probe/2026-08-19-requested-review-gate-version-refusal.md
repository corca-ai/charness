# Probe Record: requested-review-gate-version-refusal

The first debt row of slice 5, and the pattern the remaining rows are measured by.

Claim: `check_requested_review_gate.py` refuses when the adapter's version was not
  speakable, instead of reporting the charness default as the repo's own declaration
Claim kind: change
Observable: the gate's `configuration status` line and its process exit code, under a
  repo that DID declare `requested_review_commands`
Source ref: scripts/adapter-consumer-classification.json
Source revision: dd5b6dee9
Source conditions: the adapter's declared version is one this reader does not speak, so
  the resolved payload is the reader's inferred defaults rather than what the repo wrote
Base ref: dd5b6dee9
Head ref: 90348df50
Base arm: base-observed
Call sites unproven: none — the file holds ONE adapter-payload call site (`load_adapter`
  at `build_payload`), and the guard sits at that read site rather than at `main()`, so
  the three entrypoints that reach it (its own CLI, `plan_release_run`, and
  `publish_release_cli`, the latter two importing `build_payload` directly) inherit it by
  construction; a parameterized test asserts each importer refuses

## Source text

Verbatim from the manifest at the pinned revision. The FIRST draft of this record
paraphrased it and invented a tail asserting the `not_configured` consequence — the
consequence I had measured, attributed to a source that never said it. This record's own
resolver refused it (`stimulus provenance is unverified`), which is the `#528` generator
caught on this mechanism's first real debt row.

```
    "skills/public/release/scripts/check_requested_review_gate.py": {
      "verdict": "accepted-risk-unguarded",
      "reason": "build_payload() (line 64-75) does `adapter = load_adapter(repo_root); data = adapter[\"data\"]` with no error/valid check anywhere in the file, then reads `data.get(\"requested_review_commands\", [])` and executes them via `_run_review_commands` (subprocess.run with shell=True) at line 75."
    },
```

The source names the unguarded read and the shell execution. It does NOT name the
`not_configured` report — that is this probe's own measurement, recorded in the
observables below rather than back-attributed to the row.

## Stimulus

A temp repo containing only what the row's conditions name: an adapter declaring a
version this reader refuses, a real `requested_review_commands` entry, and a
`block-if-unconfigured` policy. The real CLI is run against it — not imported, not
mocked.

```
mkdir -p $D/.agents $D/charness-artifacts/release
cat > $D/.agents/release-adapter.yaml <<'YAML'
version: 9
requested_review_commands:
  - echo "the repo DID declare a requested-review command"
requested_review_policy: block-if-unconfigured
YAML
echo "# release" > $D/charness-artifacts/release/latest.md
python3 skills/public/release/scripts/check_requested_review_gate.py --repo-root $D
```

## Base observable

```
requested release review gate: ok
configuration status: not_configured
WARNING: requested_review_commands is empty; requested-review enforcement is advisory-only for this release.
exit 0
```

## Head observable

```
`.agents/release-adapter.yaml` declares a `version` this reader does not speak (version must be 1). Nothing the adapter declares is being honored, so this run would fall back to charness defaults rather than to what the repo declared -- refusing instead. Set `version: 1`, or upgrade the reader, then re-run.
exit 1
```

## Polarity controls

Every assertion above is satisfied by a gate that refuses everything, so both controls
were run on the same HEAD and both are part of the evidence:

- speakable version (`version: 1`) with the same declared command → `configuration
  status: configured`, exit 0. The guard does not fire on good input.
- no adapter file at all → `configuration status: not_configured` advisory, exit 0. The
  opt-in design survives: a repo that declared nothing is not a repo whose declaration
  could not be read, and conflating the two would refuse every consumer that never opted
  in.

## Non-claims

- This record establishes ONE file. It says nothing about the other 36
  `accepted-risk-unguarded` rows, which share a class but not a call-site shape.
- The base and head observables were captured by running the CLI, not derived from the
  diff. The record cannot prove that to a reader; a distinct observer re-running the
  stimulus above can.
- `guarded` is a structural claim about the version refusal only. It does not assert the
  file is correct in any other respect, and it does not assert the adapter's other
  errors are handled — `version_refused` reads the resolver's error strings and nothing
  else, which is that helper's own stated blind class.
