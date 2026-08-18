# Probe Record: hitl-bootstrap-version-refusal

The fifth debt row of slice 5, and the first that WRITES. It is also the first whose harm
runs in the SAFE direction, which is recorded rather than dressed up.

Claim: `bootstrap_review.py` refuses when the adapter's version was not speakable, instead
  of writing a charness apply policy into `state.yaml` as if the repo had declared it
Claim kind: change
Observable: the `require_explicit_apply` value the CLI prints and writes into
  `state.yaml`, the process exit code, and whether the session directory exists afterward
Source ref: scripts/adapter-consumer-classification.json
Source revision: dd5b6dee9
Source conditions: the adapter's declared version is one this reader does not speak, so
  `adapter["data"]` is the reader's inferred defaults rather than what the repo wrote
Base ref: dd5b6dee9
Head ref: working tree at 529486982
Base arm: base-observed
Call sites unproven: none — `bootstrap_review` is not imported by any module (`grep` over
  `scripts/`, `skills/` and `tests/` finds no importer), and the file holds ONE
  adapter-payload call site; the guard sits above it and above the `mkdir`, so no write in
  this function is reachable under a refused version

## Source text

Verbatim from the manifest at the pinned revision.

```
    "skills/public/hitl/scripts/bootstrap_review.py": {
      "verdict": "accepted-risk-unguarded",
      "reason": "bootstrap_review (line 98-99) reads `adapter[\"data\"].get(\"require_explicit_apply\", True)` and writes it straight into state.yaml/queue.json (lines 110-168) with no reference anywhere in the file to adapter[\"errors\"] or adapter[\"valid\"]."
    },
```

The source names the unguarded read and the write. It does NOT name the DIRECTION of the
harm — that the reader's `True` fallback means an unspeakable version always lands on the
stricter apply policy and so cannot weaken this control. That is this probe's own
measurement and is recorded in the non-claims rather than back-attributed to the row.

## Stimulus

A temp repo containing only what the row's conditions name: an adapter declaring a version
this reader refuses, and a real `require_explicit_apply: false` declaration — the value
that differs from the reader's fallback, so the two are distinguishable in the output.

```
mkdir -p $D/.agents
cat > $D/.agents/hitl-adapter.yaml <<'YAML'
version: 9
require_explicit_apply: false
YAML
python3 skills/public/hitl/scripts/bootstrap_review.py --repo-root $D --session-id probe --target README.md
cat $D/.charness/hitl/runtime/probe/state.yaml
```

## Base observable

EXCERPTED, and labelled as such after a round-1 bounded review caught it presented as a
verbatim capture: the capture command piped stdout through `head -5`, so the sixth key the
CLI prints (`apply_mode: explicit-after-all-chunks`, the same value the written
`state.yaml` carries below) was cut off. Nothing else is omitted.

```
session_dir: .charness/hitl/runtime/probe
scratchpad: .charness/hitl/runtime/probe/hitl-scratchpad.md
state_file: .charness/hitl/runtime/probe/state.yaml
queue_file: .charness/hitl/runtime/probe/queue.json
require_explicit_apply: true
[apply_mode: explicit-after-all-chunks — cut off by the capture's own `head -5`]
exit 0
```

and in the written `state.yaml`:

```
require_explicit_apply: true
apply_mode: explicit-after-all-chunks
```

## Head observable

```
`.agents/hitl-adapter.yaml` declares a `version` this reader does not speak (version must be 1). Nothing the adapter declares is being honored, so this run would fall back to charness defaults rather than to what the repo declared -- refusing instead. Set `version: 1`, or upgrade the reader, then re-run.
exit 1
```

and the session directory `.charness/hitl/runtime/probe` does not exist. The guard is
placed above the `mkdir`, which is earlier than the four gate rows of this slice needed:
everything below that line writes, and a refusal after it would leave a half-bootstrapped
session an operator has to tell apart from a real one.

## Polarity controls

- speakable version (`version: 1`), same `require_explicit_apply: false` → `state.yaml`
  carries `require_explicit_apply: false` and `apply_mode:
  accepted-chunk-or-final-apply-boundary`, exit 0. This is the reading that makes the base
  a written INVERSION of the declaration rather than an omission.
- no adapter file at all → `require_explicit_apply: true`, exit 0. The documented default
  survives for a repo that never opted in, and nothing claims that value came from a
  declaration.

## Non-claims

- **The guard this record measured keyed on ONE door, and a round-1 bounded review found a
  second.** `version: !!int 9` — one token added to this record's own stimulus — makes the
  parser refuse the document, and `simple_skill_adapter_lib` answers that with
  `infer_repo_defaults(...)` plus a `parse_failure_error`, the same "nothing declared is
  honored" state by a different door. At this record's `Head ref` that input still reached
  the base behavior. It is closed in a later commit, by keying
  `adapter_version_verdict` on the CONDITION rather than on one check's wording; the
  base/head pair recorded above is unaffected and was not re-measured for the second door.
- **This row's harm runs in the SAFE direction and the record does not pretend otherwise.**
  The read is `.get("require_explicit_apply", True)`, so an unspeakable version always
  lands on the STRICTER apply policy. It cannot weaken this control. What it does is
  persist a policy the repo never declared into a durable artifact that an operator and
  later runs read as the repo's own contract, and silently run a workflow other than the
  one the repo asked for. That is a false-claim defect, not a safety-bypass defect.
- This record establishes ONE file. It says nothing about the 32 `accepted-risk-unguarded`
  rows that remain.
- The base and head observables were captured by running the CLI, not derived from the
  diff. The record cannot prove that to a reader; a distinct observer re-running the
  stimulus above can.
- `queue.json` is named by the source row as a second write target. Its contents were NOT
  read in this probe; only `state.yaml` was. Both are written after the guard, so the
  guard covers them by construction, but only `state.yaml` carries a measured base/head
  pair here.
- `guarded` is a structural claim about the version refusal only. It does not assert the
  file is correct in any other respect.
