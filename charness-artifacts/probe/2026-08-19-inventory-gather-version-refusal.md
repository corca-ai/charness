# Probe Record: inventory-gather-version-refusal

Debt rows 21-22 of slice 5. One clears the wrong file; the other denies a capability the
repo enabled.

Claim: `inventory_quality_handoff` and `advise_google_workspace_path` refuse when the
  adapter declares a `version` this reader cannot speak, instead of answering about the
  reader's own defaults
Claim kind: change
Observable: the `artifact:` path the inventory reports beside its `status`/`findings`, the
  `provider_mode` the advisor reports, and each process exit code
Source ref: scripts/adapter-consumer-classification.json
Source revision: dd5b6dee9
Source conditions: the adapter's declared version is one this reader does not speak, so
  `adapter["data"]` is the reader's inferred defaults rather than what the repo wrote
Base ref: 1465689ac
Head ref: working tree at 1465689ac
Base arm: base-observed
Call sites unproven: none — each file makes ONE `load_adapter` call and the guard sits
  above it. `inventory_quality_handoff`'s guard sits INSIDE the `args.artifact is None`
  branch, because the `--artifact` arm asks the adapter nothing; a control asserts that
  arm still works under a refused version. Neither module is imported by another module
  under `scripts/` or `skills/`

## Source text

Verbatim from the manifest at the pinned revision.

```
    "scripts/inventory_quality_handoff.py": {
      "verdict": "accepted-risk-unguarded",
      "reason": "main() (lines 117-119) calls `adapter = load_adapter(repo_root)` (the quality resolve_adapter.py -> quality_adapter_lib.load_quality_adapter) and immediately does `artifact_path = repo_root / adapter['artifact_path']` with no check of `adapter['valid']`/`adapter['errors']`."
    },
```

A bounded review noted that this record establishes TWO files and quotes ONE. The second
row's text is below, and it is deliberately OUTSIDE the fence — which is itself the
finding worth keeping:

> `skills/public/gather/scripts/advise_google_workspace_path.py`,
> `accepted-risk-unguarded`: "L45 `load_gather_adapter(repo_root)["data"]` with no
> `errors` check: on a refused version the advice is computed from gather's shipped
> defaults rather than the repo's declaration."

`probe_record_parse` CONCATENATES every fence in this section and requires the result to
appear as one contiguous block in the source. Two rows that are not adjacent in the
manifest — and these are far apart under JSON key ordering — cannot both be verbatim-
verified by that mechanism. Quoting both inside fences turns `verified` into `absent` and
the record into `not-established`, which was measured before writing this. So the second
row is transcribed and labelled unverified rather than smuggled into a block the checker
would then wrongly refuse. The mechanism limit is real and is the honest thing to record;
the alternative is a record that quotes one row while claiming two.

## Stimulus

One temp repo, with a quality review at BOTH the declared and the default location
carrying different bodies, so "inventoried the declared one" and "inventoried ours" are
distinguishable beyond the path. Block shapes throughout — four probe records in this
slice shipped a control that could not fail because a published stimulus used a form
`adapter_lib` does not parse into the type its validator needs.

```
mkdir -p $D/.agents $D/docs/mine-q $D/charness-artifacts/quality
cat > $D/.agents/quality-adapter.yaml <<'YAML'
version: 9
repo: demo
output_dir: docs/mine-q
YAML
cat > $D/.agents/gather-adapter.yaml <<'YAML'
version: 9
repo: demo
gather_provider:
  google_workspace:
    mode: host-mediated
YAML
printf '# Quality Review\n\nthe declared one\n' > $D/docs/mine-q/latest.md
printf '# Quality Review\n\nthe charness default one\n' > $D/charness-artifacts/quality/latest.md

python3 scripts/inventory_quality_handoff.py --repo-root $D
python3 skills/public/gather/scripts/advise_google_workspace_path.py --repo-root $D
```

## Base observable

```
inventory_quality_handoff   status: advisory
                            artifact: charness-artifacts/quality/latest.md
                            findings: []
                            exit 0

advise_google_workspace_path   provider_mode: none
                               summary: Google Workspace gather has no repo-owned direct
                                        CLI provider.
                               operator_prompt: Adapter declares
                                        gather_provider.google_workspace.mode=none. Stop
                                        with a missing-capability explanation.
                               exit 0
```

The first is a clean bill of health on a file the repo does not keep its review in. The
second tells the operator to STOP for a missing capability, quoting a `mode=none` the
adapter does not contain.

## Head observable

```
`.agents/quality-adapter.yaml` declares a `version` this reader does not speak (version must be 1). Nothing the adapter declares is being honored, so this run would fall back to charness defaults rather than to what the repo declared -- refusing instead. Set `version: 1`, or upgrade the reader, then re-run.
exit 1
```

Measured on both, each naming its own adapter file.

## Polarity controls

- speakable version (`version: 1`), same declarations → `artifact: docs/mine-q/latest.md`
  and `provider_mode: host-mediated`. Both exit 0.
- **`--artifact docs/mine-q/latest.md` under `version: 9`** → exit 0, the named file
  inventoried. The guard sits inside the branch that resolves the path FROM the adapter,
  so a caller that named the file is unaffected.
- ordinary-invalid (`preset_version: 3` beside a speakable version) → both exit 0 AND both
  still report the declared value. Asserting the honored value matters: an exit-0-only
  control passes equally for a guard that refuses nothing beside a resolver that honors
  nothing.
- no adapter file at all → both exit 0.

## Non-claims

- **`guarded` is ONE token for two materially different coverages here, and the census
  gate cannot tell them apart.** Row 22 (`gather`) is covered on all three doors. Row 21
  (`inventory_quality_handoff`, reading the quality adapter) is covered on ONE: the
  cheapest input that still reaches a charness default at HEAD is
  `version: 1` / `repo: demo` / one over-indented `output_dir` line — `errors: []`,
  `valid: True`, `artifact: charness-artifacts/quality/latest.md`, `findings: []`, exit 0.
  That is the pre-repair harm at one keystroke instead of `version: 9`. The gate's
  `GUARDED_WITNESSES` is a per-file name check and sees only that the file calls the
  helper. Recorded here because a reader comparing the two rows' verdicts would otherwise
  read them as equal. #673 is the closure.
- **The claim is the narrow one.** These guards ask
  `adapter_version_verdict.unspeakable_version_message`, which refuses on a refused
  `version`, a refused parse, and — since `1465689ac` — a line the resolver reports as
  uninterpreted. Quality's resolver reports NONE of the last two: it calls
  `adapter_lib.load_yaml_file` bare. A bounded review corrected the mechanism this record
  first stated: a parser refusal does NOT raise before the guard. The guard's own load
  raises, `unspeakable_version_message` swallows it and answers `None`, and the run stops
  on the CONSUMER's second, unguarded load — a traceback, not a refusal. That matters
  because wrapping that second load in a `try` would make the door silent while this
  record's original wording implied the guard was never involved. A silently dropped line
  likewise leaves `errors: []` and `valid: True` with no warning for `declarations_dropped`
  to read. `gather` routes through
  `simple_skill_adapter_lib` and is covered on all three. That split is
  [#673](https://github.com/corca-ai/charness/issues/673) and is why the Claim above says
  `version` rather than "honored nothing the repo declared".
- This record establishes TWO files. Recount the rest with
  `python3 scripts/check_adapter_consumer_classification.py --repo-root .`.
- The base and head observables were captured by running the CLIs, not derived from the
  diff. A distinct observer re-running the stimulus above can check that.
- `guarded` is a structural claim about the version refusal only. Nothing here asserts
  either command's own analysis is correct.
