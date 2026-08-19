# Probe Record: web-fetch-route-version-refusal

Debt row 23 of slice 5, and the first whose flip runs in the PERMISSIVE direction on an
external boundary: the repo said it had no GitHub path, and the router offered to take
one.

Claim: `route_public_fetch_routes.resolve_github_mode` refuses when the adapter declares a
  `version` this reader cannot speak, instead of routing `github.com` by a mode the repo
  did not declare
Claim kind: change
Observable: the mode string `resolve_github_mode` returns and the route id
  `route_id_for_host("github.com", github_mode=...)` derives from it
Source ref: scripts/adapter-consumer-classification.json
Source revision: dd5b6dee9
Source conditions: the adapter's declared version is one this reader does not speak, so
  the resolved payload is the reader's inferred defaults rather than what the repo wrote
Base ref: e1c93ba17
Head ref: working tree at e1c93ba17
Base arm: base-observed
Call sites unproven: none — `resolve_github_mode` holds the file's only adapter read, and
  the guard sits between the load and the first use of `gather_provider`. CORRECTED after
  a bounded review: an earlier draft said "its one production caller is
  `route_public_fetch.py:58`", which understated the blast radius by two entrypoints. That
  call sits inside `route_for_url`, which THREE production entrypoints traverse —
  `route_public_fetch.py` (its own CLI), `acquire_public_url.py` (the fetch executor), and
  `gather_plan.py` in a DIFFERENT SKILL. The refusal now surfaces as `SystemExit` in all
  three, which is a behavior change to two of them and is recorded in the non-claims
  rather than left implied. Line 58 is also a BYPASS (`github_mode if github_mode in
  GITHUB_ROUTE_FOR_MODE else resolve_github_mode(...)`), unreachable today because no
  production caller passes `github_mode` — citing it as evidence of coverage was exactly
  backwards

## Source text

Verbatim from the manifest at the pinned revision.

```
    "skills/support/web-fetch/scripts/route_public_fetch_routes.py": {
      "verdict": "accepted-risk-unguarded",
      "reason": "`resolve_github_mode` (lines 184-202) does `payload = module.load_adapter(repo_root)` then `provider = payload.get(\"data\", {}).get(\"gather_provider\") or {}` with no check of `payload.get(\"valid\")` or `payload.get(\"errors\")` \u2014 only a bare `except Exception` around the import/call, which a version-refused adapter does not raise (load_adapter returns a normal dict with valid=False)."
```

The source names the unguarded read and the bare `except`. It does NOT name the DIRECTION:
that the fallback is `direct-cli`, which is more permissive than either declarable mode.
That is this probe's own measurement.

## Stimulus

A temp repo declaring the mode whose refusal is most consequential — `none`, meaning the
repo has no GitHub path at all.

```
mkdir -p $D/.agents
cat > $D/.agents/gather-adapter.yaml <<'YAML'
version: 9
repo: demo
gather_provider:
  github:
    mode: none
YAML
python3 -c "
import sys, pathlib; sys.path.insert(0, '.')
from tests.script_main import load_script_module
m = load_script_module('wf', pathlib.Path('skills/support/web-fetch/scripts/route_public_fetch_routes.py'))
mode = m.resolve_github_mode(pathlib.Path('$D'))
print(mode, m.route_id_for_host('github.com', github_mode=mode))
"
```

Two-space indent at both nested levels is load-bearing: `adapter_lib._parse_empty_value`
recurses on `current_indent + 2` rather than on the observed indent, so the same document
at four-space indent has the whole `gather_provider` block dropped and the control cannot
fail. A bounded review established that for the sibling record; this stimulus is written
to the same rule.

## Base observable

```
declared mode: none      ->  resolved: direct-cli   route: github-grant-or-cli
declared mode: host-mediated ->  resolved: direct-cli   route: github-grant-or-cli
```

Both at exit 0, no diagnostic. The first line is the one that matters: a repo that
declared it has NO GitHub capability is routed to a path that asks for a grant or uses the
CLI.

## Head observable

```
`.agents/gather-adapter.yaml` declares a `version` this reader does not speak (version must be 1). Nothing the adapter declares is being honored, so this run would fall back to charness defaults rather than to what the repo declared -- refusing instead. Set `version: 1`, or upgrade the reader, then re-run.
```

raised as `SystemExit`, for both declared modes. The PARSE door renders different text
and is quoted rather than folded in, after a bounded review noted the two doors do not
share a message and `Observable:` names the message:

```
`.agents/gather-adapter.yaml` could not be parsed (adapter could not be parsed: unsupported YAML construct in scalar: '!!int 9'). Nothing the adapter declares is being honored, so this run would fall back to charness defaults rather than to what the repo declared -- refusing instead. Fix the YAML so the document parses, then re-run.
```

## Polarity controls

- speakable version (`version: 1`), `mode: none` → `none` /
  `github-missing-capability`.
- speakable version, `mode: host-mediated` → `host-mediated` /
  `github-host-mediated`.
- **no adapter file at all** → `direct-cli`, no refusal. A repo that declared nothing has
  dishonored nothing, and web fetch has to keep working in a checkout that ships no gather
  skill.
- `resolve_github_mode(None)` → `direct-cli`, unchanged; the guard sits after that early
  return.
- ordinary-invalid (`preset_version: 3` beside a speakable version) → `none` still
  resolved. Asserting the honored value, not merely the absence of an exception.

## Non-claims

- **THREE ENTRYPOINTS now stop where two used to route.** `route_for_url` is traversed by
  `route_public_fetch.py`, `acquire_public_url.py` and — in a different skill —
  `gather_plan.py`. `unspeakable_version_message` returns a message rather than raising
  precisely so callers keep their own exit paths, and this row converts it to a bare
  `SystemExit` inside that chain. Two consequences, named rather than discovered later:
  `acquire_public_url.acquire` now stops before appending an acquisition attempt, so no
  trace record is emitted; and `gather_plan.build_plan`, which already loads the gather
  adapter itself, now exits on a raise from a helper module it did not expect. This is the
  same collateral-change class an earlier round of this slice found in two planners, and
  it is disclosed here rather than left for a reader to hit.
- **An ordinary validation error ON `gather_provider` ITSELF still resolves to the
  permissive default, and the guard deliberately does not cover it.** A non-mapping entry,
  an unrecognized mode, or flow-style YAML this parser does not support
  (`github: {mode: none}` parses as a STRING) makes `_parse_gather_provider` append an
  error and leave `mode` at `direct-cli` — `github-grant-or-cli`, exit 0, no version
  manipulation needed. `adapter_version_verdict` forbids refusing on ordinary invalidity
  and that is the right rule, so this is an accepted arm rather than a gap in the guard.
  The record's ordinary-invalid CONTROL uses `preset_version`, an unrelated string field,
  which demonstrates the benign case and is structurally incapable of showing this one.
- **The `except Exception -> "direct-cli"` fallback is DELIBERATELY LEFT.** A missing
  gather resolver or an unloadable module is not "the repo declared something this reader
  ignored"; degrading there keeps web fetch working in a checkout that ships no gather
  skill. This guard fires only where a declaration exists and was not honored. That means
  a repo whose gather skill is absent still routes by charness's default — recorded as the
  accepted arm, not as coverage.
- This module has no skill-runtime bootstrap, so it reaches
  `scripts/adapter_version_verdict.py` by the same ancestor walk it already uses to find
  the gather resolver. If neither is found, the guard is skipped and the pre-existing
  fallback stands — an availability gap that is stated rather than assumed away.
- The claim is about the MODE and the route id it selects. Nothing here asserts any route
  is implemented correctly, or that `github-grant-or-cli` performs an unauthorized fetch —
  only that the repo's declaration stopped selecting the route.
- This record establishes ONE file. Recount the rest with
  `python3 scripts/check_adapter_consumer_classification.py --repo-root .`.
