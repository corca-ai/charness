# Probe Record: scaffold-family-version-refusal

Debt rows 6-10 of slice 5. Five files, one harm shape, and FIVE separately measured
base/head pairs — the shared shape is why they are in one record, not a reason to measure
one and assert four.

Claim: the five artifact scaffolds refuse when the reader honored nothing the adapter
  declared, instead of returning the charness default write target
Claim kind: change
Observable: the `artifact_path` / `write_artifact_path` each scaffold CLI prints, and its
  process exit code, under a repo that declared its own `output_dir`
Source ref: scripts/adapter-consumer-classification.json
Source revision: dd5b6dee9
Source conditions: the adapter's declared version is one this reader does not speak, so
  `adapter["data"]` is the reader's inferred defaults rather than what the repo wrote
Base ref: 0bcb6b227
Head ref: working tree at 0bcb6b227
Base arm: base-observed
Call sites unproven: none — each file holds ONE adapter-payload call site, in
  `payload_for`, and the guard sits above it; `payload_for` is the imported symbol in each
  of these skills, so a refusal at `main()` would cover the CLI and leave the importers

## Source text

Verbatim from the manifest at the pinned revision, for the row whose reason is the most
specific of the five.

```
    "skills/public/quality/scripts/scaffold_quality_artifact.py": {
      "verdict": "accepted-risk-unguarded",
      "reason": "payload_for() (line 246-248) does `adapter = load_adapter(repo_root); output_dir = Path(adapter[\"data\"][\"output_dir\"])` with no error/valid check anywhere in the file -- matches the already-known-unguarded classification given for this file."
    },
```

The other four rows say the same thing about their own `payload_for`, and each was read
before its guard was placed. Two of those rows are weaker as SOURCES and this record says
so rather than quoting them as if they were equal: `scaffold_critique_artifact.py`'s
reason is `"Already reported/known per task background as unguarded+consequential; not
re-derived here"`, and `scaffold_handoff_artifact.py`'s cites the same pre-listed set. The
census row is not the evidence for those two — the measurement below is.

## Stimulus

One temp repo per skill, each declaring its own `output_dir` — a value that differs from
the reader's default, so "honored" and "fell back" are distinguishable. Each real CLI is
run against its own repo.

```
mkdir -p $D/.agents
cat > $D/.agents/<skill>-adapter.yaml <<'YAML'
version: 9
repo: demo
output_dir: docs/mine-<skill>
YAML
python3 skills/public/<skill>/scripts/scaffold_<skill>_artifact.py --repo-root $D --title probe
```

`handoff` uses `output_dir: docs/mine`; its adapter derives the path from a directory plus
a fixed `handoff.md`.

## Base observable

Five runs, five captures, excerpted at the one field this row is about:

```
quality    artifact_path: charness-artifacts/quality/latest.md          exit 0
retro      artifact_path: charness-artifacts/retro/2026-08-19-probe.md  exit 0
debug      artifact_path: charness-artifacts/debug/latest.md            exit 0
critique   artifact_path: charness-artifacts/critique/2026-08-19-probe.md exit 0
handoff    artifact_path: docs/handoff.md                               exit 0
```

Every one is the charness default. Every one of those repos declared something else.

## Head observable

```
`.agents/<skill>-adapter.yaml` declares a `version` this reader does not speak (version must be 1). Nothing the adapter declares is being honored, so this run would fall back to charness defaults rather than to what the repo declared -- refusing instead. Set `version: 1`, or upgrade the reader, then re-run.
exit 1
```

Measured on all five, each with its own adapter name in the message.

## Polarity controls

- speakable version (`version: 1`), same declared `output_dir` → each returns its own
  path: `docs/mine-quality/latest.md`, `docs/mine-retro/2026-08-19-probe.md`,
  `docs/mine-debug/latest.md`, `docs/mine-critique/2026-08-19-probe.md`,
  `docs/mine/handoff.md`. Exit 0.
- no adapter file at all → each returns its charness default at exit 0. These are opt-in
  surfaces; refusing a repo that declared nothing would break every consumer that never
  wrote an adapter.
- **A control that could not fail, found and re-measured.** The `handoff` stimulus first
  declared `artifact_path: docs/mine/handoff.md`. That resolver ignores the field — it
  builds the path from `output_dir` plus a fixed filename — so the speakable-version
  control ALSO returned `docs/handoff.md` and could not distinguish "honored" from "fell
  back". Both the base and the control were re-run on `output_dir`, which is the field the
  contract reads.

## Non-claims

- **Two of the five refuse a PARSER refusal with a raw traceback, not a rendered verdict.**
  `quality` and `critique` reach a resolver that lets the `ValueError` out. They stop the
  run and they do not relocate the artifact, which is this row's claim, but the operator
  sees a stack trace instead of an instruction. That is a real residual, named here rather
  than absorbed; fixing that resolver is a different change than the one these rows make.
- This record establishes FIVE files. It says nothing about the 27
  `accepted-risk-unguarded` rows that remain.
- The claim is about the write TARGET only. Nothing here asserts the scaffolds are correct
  in any other respect, or that the artifacts they produce are well-formed.
- Two of the five census rows quoted above did not derive their own finding
  (`critique`, `handoff` — both say "already known", one explicitly "not re-derived
  here"). The measurement is the evidence for those two, not the row.
- The base and head observables were captured by running the CLIs, not derived from the
  diff. The record cannot prove that to a reader; a distinct observer re-running the
  stimuli above can.
