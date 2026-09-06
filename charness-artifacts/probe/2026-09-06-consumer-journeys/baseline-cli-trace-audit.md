# Baseline CLI Trace Duplicate Audit

> Date: 2026-09-06
> Goal: 798
> Status: parent-delegated read-only judgment; not configured worker approval

## Source identity

- Raw trace:
  `/home/hwidong/.cache/tmp/charness/runtime/3f551f6cbcc26b40/task-run/goal798-cli-baseline/codex.stderr.log`
- Raw trace SHA256:
  `b933b9e79c8794adbc0e29cd821de2bb2e1c7379292e4945f0190de5a144d539`
- Exported plugin root:
  `/tmp/charness-goal798.qWglDo/baseline-export/plugins/charness`
- Exported plugin version: `8.4.3`
- Consumer worktree:
  `/home/hwidong/.cache/tmp/charness/runtime/3f551f6cbcc26b40/task-run/goal798-cli-baseline/worktree`
- Frozen consumer seed commit: `dbb6831` (trace lines 1159-1161)
- Produced repository commit after capture:
  `5cf9b39fb50ef0a77c245a569c4bcf92bbb95f4f`

The raw trace is ephemeral. This artifact preserves the normalized commands,
line references, change chronology, and counting judgment needed to reproduce
the audit without treating the runtime log as the sole evidence.

## Counting rule

A strict duplicate is the same-purpose operation on unchanged input after a
usable result already exists. Changed code or tests invalidate their earlier
checks. Independent review, required handoff reading, direct acceptance smoke,
and diff/status checks are not duplicates merely because a unit suite passed.

Strict total: **11 operations**: nine file reads, one test-suite invocation,
and one source compilation.

## 1. Four immediate reference re-reads

Trace lines 520-522 first read every `skills/create-cli/references/*.md` file,
including the four below. With the exported package unchanged, lines 695-697
read the same content again:

```sh
sed -n '1,280p' "$PLUGIN/skills/create-cli/references/intent-first-grammar.md"
sed -n '1,220p' "$PLUGIN/skills/create-cli/references/machine-readable-state.md"
sed -n '1,320p' "$PLUGIN/skills/create-cli/references/install-update.md"
sed -n '1,320p' "$PLUGIN/skills/create-cli/references/quality-gates.md"
```

Count: **4 duplicated file reads**.

## 2. Repeated install/update tail

After the file was read at lines 520-522 and again at lines 695-697, the
closeout discovery command at lines 8910-8920 reads its tail a third time:

```sh
sed -n '100,280p' "$PLUGIN/skills/create-cli/references/install-update.md"
```

Count: **1 duplicated file read**.

The same command first reads `impl/references/external-api-contract.md` and all
20 exported `shared/references/*.md` files (headers at lines 9041-10947) after
the green run at lines 8448-8464 and the explicit green statement at line
8909. That is avoidable broad discovery—18 shared references and the external
API reference are clearly inapplicable—but first-time reads are excluded from
the strict same-input duplicate total.

## 3. Four shared-reference re-reads

The 20-file sweep at lines 8911-8920 already reads these four files. Lines
11441-11449 read their unchanged contents again:

```sh
for file in \
  "$PLUGIN/shared/references/binary-preflight.md" \
  "$PLUGIN/shared/references/external-capability-proof-ladder.md" \
  "$PLUGIN/shared/references/prescribed-path-self-test.md" \
  "$PLUGIN/shared/references/source-bound-records.md"
do
  sed -n '1,260p' "$file"
done
```

Count: **4 duplicated file reads**.

## 4. Executable checks after a README-only change

The file-change and verification chronology is:

- Lines 1166-1170: initial `README.md`, `repoctl`, and test changes.
- Lines 2410-2425: unit suite fails; lines 2848-2850 change `repoctl`.
- Lines 3687-3703: first justified green suite.
- Lines 6689-6692 change README/tests; lines 7567-7569 change `repoctl`.
- Lines 8448-8464: justified green suite and successful `repoctl` compile.
- Lines 12309-12311 change tests.
- Lines 13212-13231: justified nine-test green suite after that test change.
- Lines 13685-13687: only `README.md` changes.
- Lines 14590-14609: final composite verification.

Normalized final command from line 14591:

```sh
python3 -m unittest discover -s tests -v &&
PYTHONDONTWRITEBYTECODE=1 python3 -c \
  'from pathlib import Path; compile(Path("repoctl").read_text(), "repoctl", "exec")' &&
git diff --check && git status --short --ignored && git diff --summary
```

Neither the test inputs nor `repoctl` changed after their usable checks. The
README-only patch does not invalidate these executable-only checks.

Count: **2 duplicated operations**: one nine-test suite invocation and one
`repoctl` compilation. The three diff/status operations remain appropriate
closeout evidence and are not counted.

## Disposition

The smallest owner correction belongs in `skills/public/impl/SKILL.md`, after
“Run the narrowest evidence that answers the changed behavior”:

> Reuse already-read guidance and passing checks while their inputs are
> unchanged. Re-read or rerun only when a changed input or unresolved question
> can alter the next decision; a docs-only edit does not invalidate checks whose
> inputs exclude docs.

This preserves acceptance, configured lint, direct smoke, review, and handoff
checks while preventing the two demonstrated rework classes.
