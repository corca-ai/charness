# Charness Handoff

## Workflow Trigger

- Run `python3 scripts/open_lesson_session.py --repo-root . --session-id <date-slug> --seed <same>`
  BEFORE any brief or reviewer spawn, then
  `grep -rl <concept> charness-artifacts/spec charness-artifacts/goals docs/`
  for the concepts you will touch. Both flags are REQUIRED — this line named the
  command bare until 2026-08-14, when following it produced a usage error.
- Then invoke `release`: the prepared release is blocked on item 1 below.

## Continuation Capability

- The release critique that returned DO-NOT-PUBLISH, and the four false claims it
  found in the notes:
  [release critique](../charness-artifacts/critique/2026-08-14-v6-0-0-release.md).
- The closeout slice's three review rounds, including the repair that re-shipped
  the class it fixed:
  [issue 618-628 closeout critique](../charness-artifacts/critique/2026-08-14-issue-618-628-closeout.md).
- Breaking changes, the migration cost, and the known-weak surfaces a consumer
  inherits: [release notes](../charness-artifacts/release/2026-08-14-v6.0.0-notes.md).
- Selection, archive/graduation asymmetry, and the Eighth Slice that supersedes
  "archive is automatic":
  [ledger and register spec](../charness-artifacts/spec/2026-08-12-lesson-ledger-and-contract-register.md).

## Current State

- `origin/main` is `0a1a53405`; the 20-commit set IS pushed, verified by
  `git ls-remote`. Broad lane was green at 9237 before the last three commits.
- The release is PREPARED, not published: no bump, tag, or publish has run, and
  every version surface still reads the shipped one. Confirm with
  `python3 skills/public/release/scripts/current_release.py --repo-root .`. The
  publish gate is satisfied except for item 1.
- [#618](https://github.com/corca-ai/charness/issues/618)-[#627](https://github.com/corca-ai/charness/issues/627)
  carry closeout evidence and stay OPEN; the push they were blocked on has landed,
  so they are closable now.
- A lesson session `2026-08-14-closeout-618-628` was opened and is UNCLAIMED — it
  owes a retro disposition; check with
  `python3 scripts/check_lesson_evaluation_continuity.py --repo-root .`.

Non-claims: no tag, version bump, release publish, hosted CI, installed-consumer
readback, or issue closure. No retro was written for this session.

## Next Session

1. **Finish the `--json` removal and make CLI output unconditionally YAML.** The
   owner's decision is total removal including backward compatibility, and it
   blocks the publish. Measured scope: 12 public skill scripts and 83 repo
   scripts declare `--json`, 72 of those branch on it to emit `json.dumps`, and 140
   files print JSON to stdout. Consumers using `json.loads` all break; YAML readers
   do not, since JSON is valid YAML. Recount with
   `grep -rl 'add_argument("--json"' scripts/*.py skills/public/*/scripts/*.py`.
   `charness-artifacts/spec/cli-command-flag-conventions.md:27` still blesses
   `--json` as a convention and must be retired with it — that stale line is what
   misled this session into calling the survivors intentional.
2. Close [#618](https://github.com/corca-ai/charness/issues/618)-[#627](https://github.com/corca-ai/charness/issues/627)
   with a `Closes #N` carrier plus the classification ledger, then
   `verify-closeout --expect-state CLOSED`. The comment bodies are already posted
   and reusable. #626/#627 need a scope decision first — their titles name outcomes
   the code does not deliver. [#608](https://github.com/corca-ai/charness/issues/608)
   was already fixed by `f149ad0bc` and only needs closing.
3. **Drive `link_only_lines` to 0 and make the gate hold it there.** Two halves.
   Fix [#629](https://github.com/corca-ai/charness/issues/629) at the source: the
   handoff scaffold's `## References` placeholder teaches bare links while its two
   sibling placeholders carry prose
   ([scaffold](../skills/public/handoff/scripts/scaffold_handoff_artifact.py)); the validator
   also requires a link there while exempting the section from the content ceiling,
   so links pool exactly where nothing is measured. This file now models the
   repaired shape. Then clear this repo's own count: `awiki lint -root docs` reports
   `link_only_lines=196` and exit 1 today, and `scripts/check_docs_graph.py:12-18`
   deliberately reads only `orphans`/`islands` and discards that exit code. Adopting
   the rule means asserting the `link_only_lines=N` figure the gate ALREADY parses
   from the summary — otherwise 196 becomes 0 once and silently regresses, which is
   item 4's class in the surface that would be measuring it.
4. Treat `rule-exists-but-does-not-bind` as a class, not as instances. Five hits,
   two of them found by FOLLOWING this file rather than auditing it. Cheapest
   probe: `grep -rn seed_lesson_transitions skills/public/retro/scripts/` still
   returns no caller.

## Discuss

- DECIDED by the owner, recorded so it is not relitigated: the YAML migration and
  the `link_only_lines` cleanup both ride in this release, and cost is not the
  constraint —
  doing it properly outranks doing it cheaply. Waste is still worth cutting; scope
  is not. The open question is only sequencing and review depth, given this session
  needed three rounds to stop shipping the class it was fixing.
- Whether to extract the ledger write transaction shared by four writers; see
  [dup-review](../charness-artifacts/quality/dup-review.json) family `d3fea2dbc2463d22`.

## References

- [Design north star](./design-north-star.md) — the P4 rule this session leaned on
  most: a passing gate is a claim, not a conclusion.
- [Operating contract](./conventions/operating-contract.md) — the closeout,
  critique-round, and external-boundary floors every item above is measured by.
- [Parallel execution](./conventions/parallel-execution.md) — the disjoint-writer
  rule, and why an isolated worktree branches from `origin/main` rather than HEAD.
