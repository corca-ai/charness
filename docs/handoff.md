# Charness Handoff

## Workflow Trigger

- Run `python3 scripts/open_lesson_session.py --repo-root . --session-id <date-slug> --seed <same>`
  BEFORE any brief or reviewer spawn, then
  `grep -rl <concept> charness-artifacts/spec charness-artifacts/goals docs/`
  for the concepts you will touch. Both flags are REQUIRED — this line named the
  command bare until 2026-08-14, when following it produced a usage error.
- Then invoke `release`: the prepared release is blocked on item 1 below.

## Continuation Capability

- Four false claims found in the notes by a DO-NOT-PUBLISH pre-release round:
  [release critique](../charness-artifacts/critique/2026-08-14-v6-0-0-release.md).
- Three review rounds, including the repair that re-shipped the class it fixed:
  [closeout critique](../charness-artifacts/critique/2026-08-14-issue-618-628-closeout.md).
- Breaking changes, the migration cost, and the known-weak surfaces a consumer
  inherits: [release notes](../charness-artifacts/release/2026-08-14-v6.0.0-notes.md).
- The digest a session reads before work, distinct from the ledger that scores it:
  [recent lessons](../charness-artifacts/retro/recent-lessons.md). Selection and the
  Eighth Slice superseding "archive is automatic":
  [ledger and register spec](../charness-artifacts/spec/2026-08-12-lesson-ledger-and-contract-register.md).

## Current State

- The pushed set is on `origin/main`; confirm with `git ls-remote origin main`
  against `git rev-parse HEAD`. Broad lane green at 9270.
- The release is PREPARED, not published: no bump, tag, or publish has run, and
  every version surface still reads the shipped one. Confirm with
  `python3 skills/public/release/scripts/current_release.py --repo-root .`. The
  publish gate is satisfied except for item 1.
- [#618](https://github.com/corca-ai/charness/issues/618)-[#627](https://github.com/corca-ai/charness/issues/627)
  carry closeout evidence and stay OPEN; the push they were blocked on has landed,
  so they are closable now.
- The lesson session is claimed and its retro is written; continuity reports
  `violations=0` via `python3 scripts/check_lesson_evaluation_continuity.py --repo-root .`.

Non-claims: no tag, version bump, release publish, hosted CI, installed-consumer
readback, or issue closure.

## Next Session

1. **Finish the `--json` removal and make CLI output unconditionally YAML.** The
   owner's decision is total removal including backward compatibility, and it
   blocks the publish. Scope is ~95 declaring scripts and 140 JSON-printing files;
   recount with
   `grep -rl 'add_argument("--json"' scripts/*.py skills/public/*/scripts/*.py`.
   `json.loads` consumers all break, YAML readers do not.
   [Flag conventions](../charness-artifacts/spec/cli-command-flag-conventions.md)
   line 27 still blesses `--json` and retires with it — that stale line is what
   misled this session into calling the survivors intentional.
2. Close [#618](https://github.com/corca-ai/charness/issues/618)-[#627](https://github.com/corca-ai/charness/issues/627)
   with a `Closes #N` carrier plus the classification ledger, then
   `verify-closeout --expect-state CLOSED`. The comment bodies are already posted
   and reusable. #626/#627 need a scope decision first — their titles name outcomes
   the code does not deliver. [#608](https://github.com/corca-ai/charness/issues/608)
   was already fixed by `f149ad0bc` and only needs closing.
3. **Drive `link_only_lines` to 0 and make the gate hold it there.** Fix
   [#629](https://github.com/corca-ai/charness/issues/629) at the
   [scaffold](../skills/public/handoff/scripts/scaffold_handoff_artifact.py), whose
   `## References` placeholder teaches bare links while its siblings carry prose;
   this file now models the repaired shape. Then clear this repo's own count —
   `awiki lint -root docs` exits 1 with `link_only_lines=196` while
   `scripts/check_docs_graph.py:12-18` deliberately reads only `orphans`/`islands`.
   Assert the count the gate ALREADY parses, or 196 becomes 0 once and silently
   returns: item 5's class, inside the surface that would measure it. Design for
   item 4 is decided and written:
   [score outcome vocabulary](../charness-artifacts/spec/2026-08-14-lesson-score-outcome-vocabulary.md).
4. **Repair the lesson score signal — three coupled defects, all measured.** One
   number carries both "this lesson pushed a wrong action" and "this lesson was
   fine and did not transfer", which is exactly the distinction
   [#626](https://github.com/corca-ai/charness/issues/626)'s dispositions must
   make; a positive cannot be cited at all (`lesson_ledger_lib.py:375` needs a
   recurrence tag, so crediting a lesson that worked means declaring it recurred);
   and the review sorts sign-blind. The ledger had zero negatives until today
   because the signal had no path in, not because nothing failed. Worked example,
   including three positives this session could not record:
   [session retro](../charness-artifacts/retro/2026-08-14-closeout-618-628-release-prep.md).
5. Treat `rule-exists-but-does-not-bind` as a class, not as instances. Five hits,
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
