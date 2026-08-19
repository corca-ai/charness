# Probe Record: prompt-bulk-version-refusal

Debt row 26 of slice 5. A scanner told to use the repo's declared policy scanned NOTHING
and reported clean.

Claim: `find_inline_prompt_bulk --from-adapter` refuses when the adapter declares a
  `version` this reader cannot speak, instead of scanning the charness default policy
Claim kind: change
Observable: the `source_globs` / `min_multiline_chars` the CLI echoes and the `findings`
  it reports
Source ref: scripts/adapter-consumer-classification.json
Source revision: dd5b6dee9
Source conditions: the adapter's declared version is one this reader does not speak, so
  `adapter["data"]` is the reader's inferred defaults rather than what the repo wrote
Base ref: abbcd9bff
Head ref: working tree at abbcd9bff
Base arm: base-observed
Call sites unproven: none — `_adapter_prompt_policy` is the file's only adapter read and
  the guard sits above it; it is reached only from `main()` under `--from-adapter`, and
  no other module imports this file

## Source text

Verbatim from the manifest at the pinned revision.

```
    "skills/public/quality/references/find_inline_prompt_bulk.py": {
      "verdict": "accepted-risk-unguarded",
      "reason": "main() (line 117-136) uses `adapter_policy` from `_adapter_prompt_policy` (line 71-75, reading `adapter[\"data\"].get(\"prompt_asset_policy\")`) to set source_globs/exemption_globs/min_chars unconditionally when `--from-adapter` is passed; `adapter_payload.get(\"valid\")`/`errors` are only copied into the output `adapter` block (line 179-186), never checked to change scan behavior."
```

## Stimulus

A temp repo declaring a prompt-asset policy, plus one source file holding a 60-character
multiline string — long enough to trip the DECLARED 40-character bar and NOT the charness
default of 400, so the two policies differ in the FINDINGS rather than only in the echoed
configuration.

```
mkdir -p $D/.agents $D/src
python3 -c "print('PROMPT = \"\"\"'); print('x'*60); print('\"\"\"')" > $D/src/a.py
cat > $D/.agents/quality-adapter.yaml <<'YAML'
version: 9
repo: demo
prompt_asset_policy:
  source_globs:
    - "src/**/*.py"
  min_multiline_chars: 40
  exemption_globs: []
YAML
python3 skills/public/quality/references/find_inline_prompt_bulk.py --repo-root $D --from-adapter
```

## Base observable

```
source_globs: []
exemption_globs: []
min_multiline_chars: 400
findings: []
exit 0
```

Both values are charness defaults. The repo declared neither.

## Head observable

```
`.agents/quality-adapter.yaml` declares a `version` this reader does not speak (version must be 1). Nothing the adapter declares is being honored, so this run would fall back to charness defaults rather than to what the repo declared -- refusing instead. Set `version: 1`, or upgrade the reader, then re-run.
exit 1
```

## Polarity controls

- speakable version (`version: 1`) → `source_globs: - src/**/*.py`,
  `min_multiline_chars: 40`, and a non-empty `findings` list. The findings assertion is
  what makes this control able to fail: a scanner that merely echoed its configuration
  would pass a globs-only check.
- **`--source-glob src/**/*.py` under `version: 9`** → exit 0, scanned. The explicit flags
  are why this script has flags; the guard sits only on the `--from-adapter` path.
- no adapter file at all → exit 0 with the empty default policy, which is the honest
  answer for a repo that declared none.
- ordinary-invalid (`preset_version: 3` beside a speakable version) → exit 0 AND
  `min_multiline_chars: 40` still honored.

## Non-claims

- **Only the VERSION door is live here.** Quality's resolver calls
  `adapter_lib.load_yaml_file` bare, so a parser refusal raises out of the consumer's own
  load and a silently dropped policy line leaves `errors: []` and `valid: True` with
  nothing for `declarations_dropped` to read. That is
  [#673](https://github.com/corca-ai/charness/issues/673); the announcement resolver was
  repaired for it in the same batch because its surface is a publish boundary, and
  quality's was not.
- This file lives under `references/`, not `scripts/`, so it has no skill-runtime
  bootstrap and reaches the verdict module by an ancestor walk. If that module is absent
  the guard is SKIPPED and the pre-existing behavior stands — stated rather than assumed
  away.
- The claim is about which policy the scan uses. Nothing here asserts the scanner's own
  findings are correct.
- This record establishes ONE file. Recount the rest with
  `python3 scripts/check_adapter_consumer_classification.py --repo-root .`.
