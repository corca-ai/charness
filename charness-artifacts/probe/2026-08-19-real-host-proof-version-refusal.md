# Probe Record: real-host-proof-version-refusal

The third debt row of slice 5, and the sharpest reading so far: the refused version does
not degrade this gate's answer, it INVERTS it, toward the permissive side.

Claim: `check_real_host_proof.py` refuses when the adapter's version was not speakable,
  instead of printing its documented opt-out over a repo that opted in
Claim kind: change
Observable: the gate's one-line `real_host=` summary and its process exit code, under a
  repo that DID declare `real_host_required_path_globs` and a changed path that matches
Source ref: scripts/adapter-consumer-classification.json
Source revision: dd5b6dee9
Source conditions: the adapter's declared version is one this reader does not speak, so
  `adapter["data"]` is the reader's inferred defaults rather than what the repo wrote
Base ref: dd5b6dee9
Head ref: working tree at f7d3fb70e
Base arm: base-observed
Call sites unproven: none — the file holds ONE adapter-payload call site (`load_adapter`
  at `build_payload`), and the guard sits at that read site rather than at `main()`;
  `publish_release_cli`, `publish_release_plan` and `plan_release_run` each re-export this
  `build_payload` as `build_real_host_payload`, and a parameterized test asserts all three
  refuse

## Source text

Verbatim from the manifest at the pinned revision.

```
    "skills/public/release/scripts/check_real_host_proof.py": {
      "verdict": "accepted-risk-unguarded",
      "reason": "build_payload() (line 135-139) does `adapter = load_adapter(repo_root)` then immediately reads `adapter[\"data\"].get(\"real_host_required_surfaces\", [])` etc. with no error/valid check -- matches the already-known-unguarded description given (repo declaring `real_host_required_surfaces` gets told 'this repo declares no release-time real-host proof triggers', exit 0)."
    },
```

The source names the unguarded read and predicts the `not-configured` report. It does NOT
name the INVERSION — that a speakable version of the same repo answers `required` — which
is this probe's own measurement and is recorded in the observables below rather than
back-attributed to the row. The source also names `real_host_required_surfaces`; this
probe used `real_host_required_path_globs`, the sibling trigger the same line names, so
the stimulus would not additionally depend on a surfaces manifest.

## Stimulus

A temp repo containing only what the row's conditions name: an adapter declaring a version
this reader refuses, a real trigger glob, and a checklist. The real CLI is run against it.

```
mkdir -p $D/.agents
cat > $D/.agents/release-adapter.yaml <<'YAML'
version: 9
real_host_required_path_globs:
  - "src/**"
real_host_checklist:
  - "run the release on a real host and paste the transcript"
YAML
python3 skills/public/release/scripts/check_real_host_proof.py --repo-root $D --paths "src/a.py"
```

## Base observable

```
real_host=not-required: This repo declares no release-time real-host proof triggers (`real_host_required_surfaces` / `real_host_required_path_globs`), so no check ran.
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

- speakable version (`version: 1`), same glob, same changed path → `real_host=required:
  Changed surfaces hit configured release-time real-host proof seams.`, exit 0. This is
  also the reading that makes the base an INVERSION rather than a degradation: same repo,
  same paths, opposite verdict.
- no adapter file at all → `real_host=not-required: This repo declares no release-time
  real-host proof triggers`, exit 0. The documented opt-out survives; a repo that declared
  nothing is not a repo whose declaration could not be read.

## Non-claims

- **The guard this record measured keyed on ONE door, and a round-1 bounded review found a
  second.** `version: !!int 9` — one token added to this record's own stimulus — makes the
  parser refuse the document, and `simple_skill_adapter_lib` answers that with
  `infer_repo_defaults(...)` plus a `parse_failure_error`, the same "nothing declared is
  honored" state by a different door. At this record's `Head ref` that input still reached
  the base behavior. It is closed in a later commit, by keying
  `adapter_version_verdict` on the CONDITION rather than on one check's wording; the
  base/head pair recorded above is unaffected and was not re-measured for the second door.
- This record establishes ONE file. It says nothing about the 33 `accepted-risk-unguarded`
  rows that remain.
- The base and head observables were captured by running the CLI, not derived from the
  diff. The record cannot prove that to a reader; a distinct observer re-running the
  stimulus above can.
- `guarded` is a structural claim about the version refusal only. It does not assert the
  file is correct in any other respect, and it does not assert the adapter's other errors
  are handled — `unspeakable_version_message` reads the resolver's error strings and
  nothing else, which is that helper's own stated blind class.
- The `real_host_required_surfaces` arm named by the source row was NOT run; the glob arm
  was. Both read `adapter["data"]` on the same two lines, so the guard covers them by
  construction, but only the glob arm carries a measured base/head pair here.
