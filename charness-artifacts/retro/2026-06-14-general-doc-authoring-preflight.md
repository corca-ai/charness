# Session Retro
Date: 2026-06-14

## Mode

session

## Context

Resolved goal `charness-artifacts/goals/2026-06-14-general-doc-authoring-preflight.md`
(#362): built `scripts/check_doc_authoring_preflight.py`, an aggregate
author-time preflight that forecasts the markdownlint + wrapped-inline-code +
doc-link + surface-length-cap constraints for one target doc in a single pass
(reusing the real validators, no fork), then wired it into the authoring flow
(authoring-preflight.md + implementation-discipline.md + a non-blocking
slice-closeout advisory) and staged the #362 closeout. Reviewing what created
rework and what should change the next run.

## Evidence Summary

- 2 commits this run: S1 `ec69f594` (tool + 8 tests), S2 `1d69bb4b` (wiring +
  drift guard); both pre-commit gate green.
- 81 tests passed across affected surfaces; fresh-eye resolution critique
  returned SHIP / no blockers (no-drift confirmed across all four classes,
  non-blocking confirmed, no crash/silent-pass paths).
- Host-log probe: `2026-06-14-general-doc-authoring-preflight-host-log.md` —
  no repeated broad gates, no repeated VCS commands.
- Off-goal finding: #362 was auto-closed COMPLETED on 2026-06-13 by commit
  `cff2ad07` whose body said "Pursue-ready draft goal to resolve #362" — the
  draft-shaping commit closed the issue before the fix existed.

## Waste

- **First S1 commit blocked by `staged-plugin-mirror-drift`.** I committed
  before running `sync_root_plugin_manifests.py`; `scripts/*.py` is part of the
  plugin install surface, so the new script needed mirroring into
  `plugins/charness/scripts/`. One blocked commit → sync → re-commit. The gate
  caught it; cost was one round, no escaped drift.
- **First no-drift tests blocked by `check-boundary-bypass-ratchet`.** I wrote
  the gate cross-checks as `subprocess.run(["python3", "scripts/check_doc_links.py", ...])`;
  the ratchet flagged them as in-process-convertible candidates. Converted to
  in-process `main()` calls. The gate caught it; one round.
- **Process-trust cost (not this run's rework):** discovering the premature
  close of #362 meant the issue-closeout posture had to be re-derived (already
  CLOSED, fix unpushed) instead of the planned "stage a fresh close."

## Critical Decisions

- **Reuse the live validators, never fork (no-drift).** Every class is forecast
  by calling the real validator (`check_doc_links` functions,
  `find_wrapped_inline_code`, markdownlint-cli2 with the repo config, the
  handoff `MAX_ARTIFACT_LINES` constant). This is the A2 lesson and the decision
  the fresh-eye reviewer stress-tested hardest — it held.
- **Surface-aware length cap, no invented floor.** The handoff resolves to its
  live 70-line cap; a general `docs/*.md` correctly resolves to *no* cap rather
  than a fabricated one — inventing a floor would itself be drift.
- **Stay a non-blocking affordance.** Kept it out of `staged_commit_gate_plan.py`
  and added a test asserting that absence, honoring the Floor-Addition Restraint
  reflex (absorb existing gates' shape up front, do not add a serial gate).

## Expert Counterfactuals

- **Michael Feathers (characterization / seams lens):** would have reached for
  the in-process `main()` seam for the no-drift cross-check from the start rather
  than a subprocess boundary — the boundary-bypass ratchet block was avoidable by
  testing at the smallest statically-visible surface first. Changed action: when
  a test needs the *verdict* of an existing entrypoint, call its `main()` (patch
  argv) before reaching for `subprocess`.
- **A release engineer's "what does the commit message DO" lens (counterfactual
  on cff2ad07):** would have caught that "resolve #362" in a *draft-shaping*
  commit body is a live GitHub close keyword, not prose. Changed action: a
  shaping/draft commit that references a tracked issue should cite it as a bare
  number or link (`#362` / the URL), never with a close verb adjacent.

## Sibling Search

- axis: contract/keyword-leakage | location: any commit body that names a tracked issue with a close verb (`close`/`fix`/`resolve` + `#N`) in a NON-fix commit (goal-shaping, handoff refresh, WIP) | decision: valid follow-up outside the slice | proof: cff2ad07 ("...draft goal to resolve #362") auto-closed #362 COMPLETED before any fix existed; no charness guard scans commit messages for premature close keywords (grep of scripts/ for close-keyword-in-commit guards finds only the issue skill's *intended* closeout carrier, not a leakage guard) | follow-up: https://github.com/corca-ai/charness/issues/363

## Next Improvements

- workflow: when authoring a draft/shaping/handoff commit that references a
  tracked issue, cite it as a bare `#N` or URL — never adjacent to a
  close/fix/resolve verb, which GitHub auto-applies on push to the default
  branch.
- capability: a pre-push/pre-commit advisory that flags a close keyword
  (`closes/fixes/resolves #N`) in a commit whose changed paths are not a
  plausible fix for #N (e.g. an artifact-only goal-shaping commit) — surfaced
  as a non-blocking advisory, per Floor-Addition Restraint. Filed as
  https://github.com/corca-ai/charness/issues/363 (one recorded instance;
  advisory before any blocking floor).
- memory: the premature-close lesson and the in-process-seam-before-subprocess
  lesson are persisted here and rolled into recent-lessons by the retro
  persister.

## Persisted

yes: charness-artifacts/retro/2026-06-14-general-doc-authoring-preflight.md
