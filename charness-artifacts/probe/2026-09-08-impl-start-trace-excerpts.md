# Consumer trace excerpts

Executed command/result excerpts only; absolute runtime roots are replaced by logical labels. Raw trace digests and total line counts are retained in the observation JSON. These excerpts illustrate the claims; they are not a complete trace or a proof of absent events by themselves.

## baseline

Original trace lines 421–453:

```text
421: exec
422: /usr/bin/zsh -lc "printf '%s\\n' '--- required consumer doc ---'; if test -f docs/index.md; then sed -n '1,240p' docs/index.md; else printf '%s\\n' 'MISSING docs/index.md'; fi; printf '%s\\n' '--- exported referenced files ---'; for f in \\
423:   skills/spec/references/fixed-probe-defer.md \\
424:   skills/spec/references/success-criteria.md \\
425:   skills/spec/references/acceptance-checks.md \\
426:   skills/spec/references/evidence-durability.md \\
427:   skills/spec/references/public-executable-contracts.md \\
428:   skills/spec/references/executable-spec-cost.md \\
429:   skills/spec/references/design-lenses.md \\
430:   skills/spec/references/taxonomy-axis-checkpoint.md \\
431:   skills/prove/SKILL.md \\
432:   skills/shared/references/agent-assessment-invariant.md \\
433:   skills/shared/references/success-criteria-review.md \\
434:   skills/shared/references/source-bound-records.md \\
435:   skills/shared/references/fresh-eye-subagent-review.md \\
436:   skills/impl/references/adapter-contract.md \\
437:   skills/impl/references/contract-consumption.md \\
438:   skills/impl/references/design-lenses.md \\
439:   skills/impl/references/sequence-discipline.md \\
440:   skills/impl/references/external-api-contract.md \\
441:   skills/shared/references/prescribed-path-self-test.md; do
442:   p=\""'$CHARNESS_FIXTURE_PLUGIN_ROOT/$f"
443:   if test -f "$p"; then
444:     printf '"'\\n--- %s ---\\n' \""'$f"
445:     sed -n '"'1,240p' \""'$p"
446:   else
447:     printf '"'\\n--- %s: MISSING ---\\n' \""'$f"
448:   fi
449: done' in <consumer-task-root>/impl-routing-baseline/worktree
450:  succeeded in 4ms:
451: exec
452: /usr/bin/zsh -lc "printf '%s\\n' '--- exported skill tree ---'; rg --files \""'$CHARNESS_FIXTURE_PLUGIN_ROOT/skills" | sed -n '"'1,260p'; printf '%s\\n' '--- current contract and targets ---'; sed -n '1,240p' docs/alias-resolution.md; sed -n '1,240p' src/catalog.py; sed -n '1,280p' tests/test_catalog.py; printf '%s\\n' '--- README ---'; sed -n '1,220p' README.md; printf '%s\\n' '--- status ---'; git status --short --ignored" in <consumer-task-root>/impl-routing-baseline/worktree
453:  succeeded in 7ms:
```

## candidate

Original trace lines 414–418:

```text
414: exec
415: /usr/bin/zsh -lc "printf '%s\\n' '--- impl contract-consumption reference ---' && sed -n '1,260p' \""'$CHARNESS_FIXTURE_PLUGIN_ROOT/skills/impl/references/contract-consumption.md" && printf '"'%s\\n' '--- repository state/files ---' && git status --short --untracked-files=all && rg --files -g '"'!__pycache__'"' | sort && printf '%s\\n' '--- docs/index.md ---' && sed -n '1,220p' docs/index.md && printf '%s\\n' '--- docs/alias-resolution.md ---' && sed -n '1,260p' docs/alias-resolution.md && printf '%s\\n' '--- src/catalog.py ---' && sed -n '1,260p' src/catalog.py && printf '%s\\n' '--- tests/test_catalog.py ---' && sed -n '1,320p' tests/test_catalog.py && printf '%s\\n' '--- README.md ---' && sed -n '1,220p' README.md" in <consumer-task-root>/impl-routing-candidate/worktree
416:  exited 2 in 0ms:
417: --- impl contract-consumption reference ---
418: # Contract Consumption
```

Original trace lines 455–470:

```text
455: AGENTS.md
456: README.md
457: docs/alias-resolution.md
458: src/__init__.py
459: src/catalog.py
460: tests/test_catalog.py
461: --- docs/index.md ---
462: sed: can't read docs/index.md: No such file or directory
463:
464: codex
465: The exported package is Charness `8.6.0`; the consumed implementation skill is `<probe-root>/exports/candidate/skills/impl/SKILL.md` (with its contract-consumption reference resolved from that same export). The repository has no `docs/index.md`, so I’m treating the existing `docs/alias-resolution.md` as the canonical contract and will note that missing index as a non-claim rather than creating unrelated fixture files.
466: exec
467: /usr/bin/zsh -lc "printf '%s\\n' '--- docs/alias-resolution.md ---' && sed -n '1,300p' docs/alias-resolution.md" in <consumer-task-root>/impl-routing-candidate/worktree
468:  succeeded in 0ms:
469: --- docs/alias-resolution.md ---
470: # Alias Resolution
```

## final-candidate

Original trace lines 414–425:

```text
414: exec
415: /usr/bin/zsh -lc "printf '%s\\n' '--- docs/index.md ---' && sed -n '1,240p' docs/index.md && printf '%s\\n' '--- docs/alias-resolution.md ---' && sed -n '1,280p' docs/alias-resolution.md && printf '%s\\n' '--- README.md ---' && sed -n '1,220p' README.md && printf '%s\\n' '--- tree ---' && rg --files -g '"'!*.pyc'"' | sort && printf '%s\\n' '--- git status ---' && git status --short && printf '%s\\n' '--- adapter presence ---' && if test -f .agents/impl-adapter.yaml; then sed -n '1,240p' .agents/impl-adapter.yaml; else echo none; fi" in <consumer-task-root>/impl-routing-final-candidate/worktree
416:  exited 2 in 0ms:
417: --- docs/index.md ---
418: sed: can't read docs/index.md: No such file or directory
419:
420: codex
421: The exported skill requires `docs/index.md`, but this consumer checkout does not currently contain that path; the initial read stopped there. I’m checking the repository contents and worktree state now, then I’ll use the exact alias-resolution contract if present and preserve any pre-existing changes.
422: exec
423: /usr/bin/zsh -lc "printf '%s\\n' '--- top-level ---' && ls -la && printf '%s\\n' '--- files ---' && rg --files -g '"'!*.pyc'"' | sort || true && printf '%s\\n' '--- docs candidates ---' && find . -maxdepth 3 -type f -print | sort && printf '%s\\n' '--- git status ---' && git status --short && printf '%s\\n' '--- git log ---' && git log -5 --oneline --decorate" in <consumer-task-root>/impl-routing-final-candidate/worktree
424:  succeeded in 0ms:
425: --- top-level ---
```

Original trace lines 1020–1023:

```text
1020: exec
1021: /usr/bin/zsh -lc "printf '%s\\n' '--- exported skills files ---' && rg --files \""'$CHARNESS_FIXTURE_PLUGIN_ROOT/skills" | sort && printf '"'%s\\n' '--- exported impl references ---' && for ref_file in \""'$CHARNESS_FIXTURE_PLUGIN_ROOT/skills/impl/references/"*.md; do printf '"'\\n--- %s ---\\n' \""'$ref_file"; sed -n '"'1,300p' \""'$ref_file"; done && printf '"'%s\\n' '--- exported spec references ---' && for ref_file in \""'$CHARNESS_FIXTURE_PLUGIN_ROOT/skills/spec/references/"*.md; do printf '"'\\n--- %s ---\\n' \""'$ref_file"; sed -n '"'1,300p' \""'$ref_file"; done' in <consumer-task-root>/impl-routing-final-candidate/worktree
1022:  succeeded in 0ms:
1023: --- exported skills files ---
```

Original trace lines 2306–2309:

```text
2306: exec
2307: /usr/bin/zsh -lc "printf '%s\\n' '--- impl reference metadata ---' && ls -l \""'$CHARNESS_FIXTURE_PLUGIN_ROOT/skills/impl/references" && printf '"'%s\\n' '--- impl contract-consumption ---' && sed -n '1,320p' \""'$CHARNESS_FIXTURE_PLUGIN_ROOT/skills/impl/references/contract-consumption.md" && printf '"'%s\\n' '--- impl adapter-contract ---' && sed -n '1,320p' \""'$CHARNESS_FIXTURE_PLUGIN_ROOT/skills/impl/references/adapter-contract.md" && printf '"'%s\\n' '--- impl external-api-contract ---' && sed -n '1,320p' \""'$CHARNESS_FIXTURE_PLUGIN_ROOT/skills/impl/references/external-api-contract.md" && printf '"'%s\\n' '--- impl sequence-discipline ---' && sed -n '1,240p' \""'$CHARNESS_FIXTURE_PLUGIN_ROOT/skills/impl/references/sequence-discipline.md"' in <consumer-task-root>/impl-routing-final-candidate/worktree
2308:  succeeded in 0ms:
2309: --- impl reference metadata ---
```

Original trace lines 2536–2539:

```text
2536: exec
2537: /usr/bin/zsh -lc "printf '%s\\n' '--- impl design-lenses ---' && sed -n '1,240p' \""'$CHARNESS_FIXTURE_PLUGIN_ROOT/skills/impl/references/design-lenses.md" && printf '"'%s\\n' '--- spec-boundary availability ---' && if test -f \""'$CHARNESS_FIXTURE_PLUGIN_ROOT/skills/ideation/references/spec-boundary.md"; then sed -n '"'1,240p' \""'$CHARNESS_FIXTURE_PLUGIN_ROOT/skills/ideation/references/spec-boundary.md"; else echo '"'[not present]'; fi && printf '%s\\n' '--- referenced shared paths availability ---' && for ref_file in \\
2538:   \""'$CHARNESS_FIXTURE_PLUGIN_ROOT/skills/shared/references/bootstrap-resolution.md" '"\\
2539:   \""'$CHARNESS_FIXTURE_PLUGIN_ROOT/skills/shared/references/binary-preflight.md" '"\\
```

## index

Original trace lines 44–49:

```text
44: exec
45: /usr/bin/zsh -lc "printf 'PLUGIN_ROOT=%s\\n' \""'$CHARNESS_FIXTURE_PLUGIN_ROOT"; pwd; printf '"'%s\\n' '--- AGENTS.md ---'; sed -n '1,240p' AGENTS.md; printf '%s\\n' '--- files ---'; rg --files -g '"'!*.pyc'"' | sort; printf '%s\\n' '--- installed manifests ---'; if [ -f \""'$CHARNESS_FIXTURE_PLUGIN_ROOT/.codex-plugin/plugin.json" ]; then sed -n '"'1,160p' \""'$CHARNESS_FIXTURE_PLUGIN_ROOT/.codex-plugin/plugin.json"; elif [ -f "$CHARNESS_FIXTURE_PLUGIN_ROOT/.claude-plugin/plugin.json" ]; then sed -n '"'1,160p' \""'$CHARNESS_FIXTURE_PLUGIN_ROOT/.claude-plugin/plugin.json"; fi; printf '"'%s\\n' '--- spec skill ---'; sed -n '1,260p' \""'$CHARNESS_FIXTURE_PLUGIN_ROOT/skills/spec/SKILL.md"; printf '"'%s\\n' '--- impl skill ---'; sed -n '1,320p' \""'$CHARNESS_FIXTURE_PLUGIN_ROOT/skills/impl/SKILL.md"' in <consumer-task-root>/impl-optional-index/worktree
46:  succeeded in 0ms:
47: PLUGIN_ROOT=<probe-root>/exports/optional-index
48: <consumer-task-root>/impl-optional-index/worktree
49: --- AGENTS.md ---
```

Original trace lines 69–79:

```text
69: The seed is the baseline input. Do not put acceptance results, candidate
70: patches, or copied plugin/skills trees in it.
71: --- files ---
72: AGENTS.md
73: README.md
74: docs/alias-resolution.md
75: src/__init__.py
76: src/catalog.py
77: tests/test_catalog.py
78: --- installed manifests ---
79: {
```

Original trace lines 309–320:

```text
309: evidence that the next decision does not require rework.
310:
311: ## Start
312:
313: 1. Read `AGENTS.md`, then `<repo-root>/docs/index.md` when present <!-- not vendored: consumer-repo path --> and only the pages that own the
314:    current surface. If an active `/goal #N` exists, read the parent body and
315:    the selected child only; do not rescan the whole issue graph on routine
316:    pickup.
317: 2. Read the current implementation contract. If none exists, write a small
318:    working contract in the task context: intended behavior, acceptance check,
319:    and explicit non-claims.
320: 3. Inspect the exact target paths and current diff. Preserve unrelated parent
```

Original trace lines 417–430:

```text
417: exec
418: /usr/bin/zsh -lc "printf '%s\\n' '--- contract ---'; sed -n '1,260p' docs/alias-resolution.md; printf '%s\\n' '--- README ---'; sed -n '1,220p' README.md; printf '%s\\n' '--- src/catalog.py ---'; sed -n '1,260p' src/catalog.py; printf '%s\\n' '--- tests/test_catalog.py ---'; sed -n '1,320p' tests/test_catalog.py; printf '%s\\n' '--- status/diff ---'; git status --short; git diff -- src/catalog.py tests/test_catalog.py docs/alias-resolution.md; printf '%s\\n' '--- impl references ---'; for f in \""'$CHARNESS_FIXTURE_PLUGIN_ROOT/skills/impl/references/adapter-contract.md" "$CHARNESS_FIXTURE_PLUGIN_ROOT/skills/impl/references/contract-consumption.md" "$CHARNESS_FIXTURE_PLUGIN_ROOT/skills/impl/references/design-lenses.md" "$CHARNESS_FIXTURE_PLUGIN_ROOT/skills/impl/references/sequence-discipline.md"; do printf '"'\\n### %s\\n' \""'$f"; sed -n '"'1,260p' \""'$f"; done' in <consumer-task-root>/impl-optional-index/worktree
419:  succeeded in 0ms:
420: --- contract ---
421: # Alias Resolution
422:
423: ## Problem
424:
425: The fixture currently exposes `Catalog(mapping)`, where canonical keys are
426: looked up directly and an unknown key produces the normal `KeyError`. Consumers
427: need optional alternate names without changing that existing call or changing
428: the meaning of a canonical key. Alias input must retain order and duplicates so
429: bad definitions are observable and rejected rather than collapsed by a
430: dictionary.
```

## index-present

Original trace lines 36–47:

```text
36: exec
37: /usr/bin/zsh -lc "printf '%s\\n' '--- docs/index.md ---'; sed -n '1,260p' docs/index.md; printf '%s\\n' '--- docs/alias-resolution.md ---'; sed -n '1,320p' docs/alias-resolution.md; printf '%s\\n' '--- impl references ---'; for f in \""'$CHARNESS_FIXTURE_PLUGIN_ROOT"/skills/impl/references/*.md; do printf '"'\\n### %s\\n' \""'$f"; sed -n '"'1,260p' \""'$f"; done; printf '"'%s\\n' '--- spec references ---'; for f in \""'$CHARNESS_FIXTURE_PLUGIN_ROOT"/skills/spec/references/*.md; do printf '"'\\n### %s\\n' \""'$f"; sed -n '"'1,220p' \""'$f"; done' in <index-present-task-root>/impl-index-present-plan/worktree
38:  succeeded in 0ms:
39: --- docs/index.md ---
40: # Consumer documentation
41:
42: [Alias resolution](alias-resolution.md) owns the current implementation contract, rejection messages, acceptance checks, and deferred decisions.
43: --- docs/alias-resolution.md ---
44: # Alias Resolution
45:
46: ## Problem
47:
```
