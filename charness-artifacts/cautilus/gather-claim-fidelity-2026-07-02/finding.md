# gather claim-fidelity capture — 2026-07-02 (#411 substance floor VERIFY)

## Verdict

**SUBSTANCE FLOOR PROVEN (4/4), doc-open RCF REFUTED (0/8) on a fresh real run.**
The redesigned honest floor for gather's public-URL default — the artifact/substance
instrument `evals/cautilus/gather-claim-fidelity/outcome-assertions.json` (shipped
`3b650cb6`) — grades a genuine `/charness:gather` run correctly, and the old doc-open
RCF floor is confirmed refuted (the run opens zero reference docs). This VERIFIES the
#411 hypothesis; it does not by itself flip the spec (see Remaining).

## What ran

`/charness:gather https://docs.python.org/3/library/asyncio-task.html ...` at
`HEAD`=22dba8c8 (base-commit.txt), isolated worktree, exit 0, 119209ms, 1.18M tokens,
tools Bash=11 Skill=1. A faithful committing gather: fetched the exact named source
(direct-public-fetch, no search widening), wrote the durable asset
`charness-artifacts/gather/2026-07-02-docs-python-org-3-library-asyncio-task-html-*.md`
(45758-char real page body) + refreshed `latest.md`, and **committed it** (`65b16ff7`
inside the worktree — a committing run).

## Phase B — deterministic matcher (doc-open RCF refuted)

`build-skill-execution-observation.mjs --spec spec.json` over the session tree →
`outcome=failed | coverage=0/8`, both RCF floors missing (`source-priority.md`,
`capability-contract.md`). Reproduces the 2026-07-01 slice-7 finding on a fresh run:
the doc-open floor is a refuted HYPOTHESIS (census INLINE confirmed), NOT matcher
softening.

## Phase C — substance grade (honest floor PROVEN)

`grade_skill_outcome.py --judge-cmd "python3 scripts/outcome_judge_cmd.py"` (live
independent `claude -p` judge) → **scored 4/4, pass_rate 1.0, 0 skipped, 0 errors**:

- `ran-gather` (deterministic): PASS — summary matched `Execution of /gather`.
- `primary-source-fidelity` (judge): PASS — exact URL fetched, durable record embeds
  the real page body, committed 65b16ff7, no substitution/fabrication.
- `honest-access-and-capture-accounting` (judge): PASS — names `public route` access
  mode, captured-vs-confirmation distinction, first-run degradation flagged.
- `no-search-widening-substitution` (judge): PASS — record source = named URL, no
  adjacent/cache/search substitution.

**Committing-run design validated:** the judge graded the asset the run COMMITTED
(cited `65b16ff7`), proving the transcript-reading judge assertions + base..HEAD
output extraction handle a committing run — exactly what a naive `output_glob` would
have false-failed (the recent-lessons `preserve_outputs` trap).

## Remaining (does NOT close #411's public-URL default)

The RCF flip is blocked by `claim_fidelity_lib.py:172` (at least one of RCF/RSF must
be non-empty — "a spec with no floor asserts nothing"). Dropping the refuted doc-opens
leaves empty RCF, and there is no honest RSF token for public-URL (only trivial
`public` = softening, rejected by the finding). The principled unblock is
**substance-floor-only spec support** (allow empty RCF+RSF when a sibling
`outcome-assertions.json` exists) — a contract change that also unblocks setup #413.
Queued as its own design slice; no spec flipped this session (capture-before-pin).

## Bundle

- `observed.v1.json` — phase B packet (0/8).
- `outcome-grade.md` — phase C grade (4/4).
- `transcript.txt`, `trace-digest.jsonl`, `outputs/` — evidence the judge read.
