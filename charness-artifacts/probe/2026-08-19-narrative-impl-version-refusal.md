# Probe Record: narrative-impl-version-refusal

Debt rows 19-20 of slice 5. One surveys the wrong document set; the other prints the flag
that would have stopped it and does not read it.

Claim: `map_sources` and `survey_verification` refuse when the reader honored nothing the
  adapter declared, instead of surveying the reader's own defaults and reporting the
  result as fact
Claim kind: change
Observable: the `source_documents` list `map_sources` prints, the `tool_checks` list and
  `adapter_valid` flag `survey_verification` prints, and each process exit code
Source ref: scripts/adapter-consumer-classification.json
Source revision: dd5b6dee9
Source conditions: the adapter's declared version is one this reader does not speak, so
  `adapter["data"]` is the reader's inferred defaults rather than what the repo wrote
Base ref: 724fe8a55
Head ref: working tree at 724fe8a55
Base arm: base-observed
Call sites unproven: none — each file holds ONE adapter read, in `main()`, and the guard
  sits above it; neither module is imported by any other module under `scripts/` or
  `skills/`, so `main()` and the read site coincide

## Source text

Verbatim from the manifest at the pinned revision.

```
    "skills/public/impl/scripts/survey_verification.py": {
      "verdict": "accepted-risk-unguarded",
      "reason": "main() (line 265-296) calls `_group_specs(adapter[\"data\"])` and reads `adapter[\"data\"].get(\"verification_install_proposals\")` unconditionally; `adapter[\"valid\"]` is only echoed into the output dict (line 291) and never branched on to change behavior or add a warning."
    },
```

The source states the row exactly, and the measurement below is the same fact at runtime:
`adapter_valid: false` printed beside `tool_checks: []`.

## Stimulus

Two temp repos, each declaring a value in the shape its contract reads
(`optional_string_list` in both cases — an earlier stimulus in this slice guessed richer
mapping forms twice and produced controls that could not fail).

```
mkdir -p $D/.agents
cat > $D/.agents/narrative-adapter.yaml <<'YAML'
version: 9
repo: demo
remote_name: upstream
source_documents: [docs/mine-narrative.md]
mutable_documents: [docs/mine-narrative.md]
YAML
cat > $D/.agents/impl-adapter.yaml <<'YAML'
version: 9
repo: demo
verification_tools: [mytool]
YAML
python3 skills/public/narrative/scripts/map_sources.py --repo-root $D
python3 skills/public/impl/scripts/survey_verification.py --repo-root $D
```

## Base observable

```
map_sources           source_documents:
                      - path: README.md
                        exists: false
                        mutable: true
                      exit 0

survey_verification   adapter_found: true
                      adapter_valid: false
                      tool_checks: []
                      exit 0
```

`README.md` is the inferred default; the repo declared `docs/mine-narrative.md`. And
`adapter_valid: false` sits in the same payload as an empty survey — the flag that would
have stopped the run, printed and not read.

## Head observable

```
`.agents/narrative-adapter.yaml` declares a `version` this reader does not speak (version must be 1). Nothing the adapter declares is being honored, so this run would fall back to charness defaults rather than to what the repo declared -- refusing instead. Set `version: 1`, or upgrade the reader, then re-run.
exit 1
```

Measured on both, each naming its own adapter file.

## Polarity controls

- speakable version (`version: 1`), same declarations → `map_sources` reports
  `path: docs/mine-narrative.md` and NOT `README.md`; `survey_verification` reports
  `spec: mytool` and `adapter_valid: true`. Both exit 0.
- no adapter file at all → both exit 0. `map_sources` inferring a default document set is
  the correct answer for a repo that declared none; it is only wrong over a repo that
  declared something else.

## Non-claims

- **The parse door behaves differently for these two, and the difference is the
  RESOLVER's, not the guard's.** Measured across all sixteen public resolvers with
  `version: !!int 9`: ten record the failure in `errors` (debug, gather, handoff, hitl,
  hotl, impl, issue, release, retro, setup) and SIX let the `ValueError` out as a raw
  traceback (achieve, announcement, create-skill, critique, narrative, quality). So
  `survey_verification` renders the refusal on both doors and `map_sources` renders a
  traceback on the second. Both stop. Filed as
  [#673](https://github.com/corca-ai/charness/issues/673) rather than fixed here, because
  changing six resolvers is a different change than guarding a consumer — and because
  `adapter_version_verdict.parse_refused` is UNREACHABLE for those six, which is a real
  blind arm in every consumer guard on that side.
- This record establishes TWO files. Recount the rest with
  `python3 scripts/check_adapter_consumer_classification.py --repo-root .`.
- The base and head observables were captured by running the CLIs, not derived from the
  diff. A distinct observer re-running the stimulus above can check that.
- The claim is about what each command surveys. Nothing here asserts either is correct in
  any other respect.
