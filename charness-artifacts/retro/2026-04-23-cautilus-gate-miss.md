# Cautilus Gate Miss

## Context

Unit of work: issue #62 init-repo AGENTS normalization drift. The implementation
was committed as `043b1fb` after pytest and slice closeout passed.

## Evidence Summary

- `python3 scripts/run_slice_closeout.py --repo-root .` passed before commit.
- `python3 scripts/plan_cautilus_proof.py --repo-root . --json` on a clean tree
  reported no current proof requirement because the diff was empty.
- `python3 scripts/plan_cautilus_proof.py --repo-root . --json --paths ...`
  for the #62 commit paths reported `changed_public_skills: ["init-repo"]` and
  recommended init-repo dogfood/scenario review, while still not requiring a
  Cautilus instruction-surface run.
- `python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id init-repo --json`
  matched the existing dogfood case.

## Waste

I answered the implementation closeout as if slice closeout fully covered the
public-skill semantic gate. Because the tree was clean after commit, the default
Cautilus planner invocation could no longer see the just-committed paths.

## Critical Decisions

- Keep the #62 behavioral proof as deterministic pytest coverage; the changed
  behavior is an inspector payload contract, not an instruction-surface routing
  case.
- Treat the Cautilus planner's explicit-path mode as required after committing a
  public-skill semantic change before claiming evaluator coverage is settled.

## Expert Counterfactuals

- A release engineer would have rerun proof planning from `git show --name-only
  HEAD` after the commit, not only from the working tree.
- A test maintainer would separate "Cautilus binary was run" from "Cautilus
  planner says no binary run is required but dogfood/scenario review was
  checked."

## Next Improvements

- `workflow`: for public-skill changes, run `plan_cautilus_proof.py --paths`
  with the commit paths if the worktree is already clean.
- `memory`: keep this as a repeat trap in recent lessons until the closeout
  script or commit workflow carries explicit-path Cautilus planning.

## Persisted

yes
