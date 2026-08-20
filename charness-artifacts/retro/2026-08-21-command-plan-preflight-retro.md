# Session Retro: command-plan failure-smell repair

Date: 2026-08-21
Goal: charness-artifacts/goals/2026-08-20-repairs-that-carry-their-class.md
Mode: session

## Context

The semantic-candidate review identified a procedural fan-out seam: operators were told to resolve paths, refs, and owner flags before parallel work, but no executable command checked those premises. The implementation added a repo-local command-plan preflight, then its first fresh-eye review found that the new gate did not actually stop after ref/help/flag failures and did not recognize short flags. Those findings were repaired and a second bounded review read the repaired verdict surface.

## Window

Working tree from `de1b3bf3a9dc043c018c97c68f85271b4a69441c` through the pending command-plan slice. No version mutation, tag, push, publication, hosted readback, Cautilus run, or issue closeout occurred.

## Evidence Summary

- `scripts/command_plan_preflight.py` resolves targets through `rg --files`, verifies refs through `git rev-parse --verify`, and probes only owner `--help` surfaces before fan-out.
- Focused command-plan tests cover wrong paths, ambiguous basenames, missing long and short flags, owner/flag fail-fast, and missing refs with later commands suppressed.
- Fresh-eye round 1 found the fail-fast and short-flag defects; round 2 read the repaired surface and found no blocker or false-green path. Round-2 test additions were accepted-unreviewed under the two-round cap.
- The first lesson continuity gate failure named the unclaimed receipt `2026-08-21-goal-codex-review`; this retro now binds that receipt to an explicit disposition.

## Waste

The main waste was trusting a command plan because its prose described a stop condition that the implementation had not enforced. A second waste was invoking the round recorder with an out-of-repo `/tmp` snapshot path; the refusal was correct, but the workflow had not made the repository-local evidence boundary obvious at the call site. Earlier investigation also tried guessed validator paths before resolving the actual repo-owned paths with `rg --files`. These are one class: a wrong path or wrong command surface is itself a premise failure, not a harmless typo.

The broad lane was run before source/export sync and exposed six structural failures: missing plugin mirror, unclaimed lesson emission, stale critique metadata, packaging-dependent test failures, changed-line proof fallout, and duplicate families. The failures were useful evidence, but the sequencing cost a long rerun.

## Critical Decisions

- Keep target, ref, and owner-help resolution as one fail-closed preflight contract. A plan that cannot resolve any one premise must not start later probes.
- Share repo-relative resolution through `path_portability_lib`; do not add another path normalizer with a different outside-root behavior.
- Treat the standard import family as intentional standalone-CLI boilerplate, with a rationale-bearing overlay entry, while repairing the duplicated semantic helpers.
- Preserve the lesson receipt and write a durable retro disposition rather than deleting evidence to make continuity green.
- Keep release mutation deferred until the repaired source/export tree is committed, the semantic packet is rebuilt against that exact identity, and integrated verification is rerun.

## Trends vs Last Retro

The recurring class is now explicit: a repair to a proof or orchestration surface can carry the failure class it was meant to close. This slice caught it twice — the implementation's claimed fail-fast behavior and the workflow's guessed evidence/validator paths. The new command-plan seam reduces the class for future parallel work, while the retro records the remaining non-claims instead of treating a green focused test as broad proof.

## North Star Alignment

- Brief a capable judge: the preflight emits structured target, ref, command, error, and non-claim state so an operator can inspect why fan-out was refused.
- Keep teeth where a wrong answer escapes: missing/ambiguous paths, unresolved refs, owner-help failure, and unsupported flags are blocking premises; runtime behavior and hosted truth remain outside this checker.
- Confirm irreversible boundaries through a different observer: two bounded fresh-eye rounds read the command-plan verdict surface, with boundary snapshots verified clean.
- Failure signature: wrong path, wrong ref, and wrong flag are not incidental invocation mistakes; each is a smell that the producer/consumer contract is not bound.

## Expert Counterfactuals

An Ousterhout-style counterfactual would ask whether the command-plan contract is deep enough to own the premise checks. The first version was shallow because it documented fail-fast without enforcing it. The repaired owner now has one structured refusal path and tests that distinguish target/ref refusal from owner-help/flag refusal. An Engelbart-style counterfactual would ask whether the workflow learns from the refusal; the durable plan, round artifacts, and retro now carry the exact failure class forward.

## Lesson Evaluation

The harmful question first: the selected lessons did not cause a wrong action; the misses came from failing to apply the path/premise lesson early enough. The receipt proves that a lesson bundle was issued, but this retro does not claim host-level presentation/readback, so no score event is attributed to it. Other selected lessons had no observable occasion and were not scored.

Lesson evaluation: {"score_event_count":0,"session_id":"2026-08-21-goal-codex-review","status":"not-evaluated","reason":"presentation-unproven"}

## Next Improvements

- workflow: run command-plan preflight before every independent fan-out, including validator and artifact paths; recurrence-class: command-plan-premise-before-fanout
- workflow: resolve repo-owned command paths with `rg --files` before invoking a gate; recurrence-class: wrong-path-is-premise-failure
- capability: make the parallel-execution workflow consume the preflight report as its input contract, so an unresolved target cannot be silently replaced by a sibling path.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-21-command-plan-preflight-retro.md
