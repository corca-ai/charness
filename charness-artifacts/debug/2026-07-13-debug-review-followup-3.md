# Capability Catalog Invalid Repo Root Debug
Date: 2026-07-13

## Problem

`charness catalog refresh --repo-root <missing-path>` exits zero and creates a
new directory tree plus two catalog artifacts at the typo path. A regular-file
root reaches the same writer and crashes with an unhandled traceback.

## Correct Behavior

Given an explicit catalog refresh root that is not an existing directory, when
the public or direct CLI runs, then it returns a clean nonzero error before
inventory construction or filesystem mutation. Existing directories remain
valid because a consumer directory need not be a Git checkout.

## Observed Facts

- Missing-root repro returned rc=0, created the supplied directory, and wrote
  `latest.md` plus `latest.json`.
- Regular-file repro returned rc=1 with `NotADirectoryError` from
  `output_dir.mkdir`, exposed as a traceback by the public CLI.
- `_repo_root` only expands/resolves. `refresh_catalog` calls `build_inventory`
  and then `persist_catalog`; `persist_catalog` creates parents unconditionally.
- Existing tests refresh an already-existing `tmp_path`; none covers a missing
  or non-directory root. `resolve-skill-path` deliberately accepts a missing
  repo root for cache recovery, so validation must stay refresh-specific.

## Reproduction

- `tmp=$(mktemp -d); ./charness catalog refresh --repo-root "$tmp/typo" --json
  >/dev/null; echo $?; find "$tmp/typo" -type f` returned rc=0 and two files.
- Replacing the root with a regular file returned rc=1 plus a Python traceback.

## Candidate Causes

- Control flow: no refresh-specific existing-directory precondition runs before
  the writer.
- Contract: catalog refresh may intentionally initialize arbitrary new roots,
  like `capability init`.
- Layering: inventory discovery may require a missing root so validation cannot
  live in the shared `_repo_root` resolver.

## Hypothesis

- Falsifiable claim: refresh alone lacks an existing-directory guard, while
  list/resolve intentionally tolerate sparse or missing roots; a shared backend
  refresh guard plus entrypoint error translation will prevent writes and
  tracebacks without narrowing the read-only commands. | disconfirmer: find a
  documented/tested refresh-init contract or an existing missing-root refresh
  test that expects artifact creation.

## Verification

- resolved — help describes refresh as writing canonical current pointers, not
  initializing a repository; searches found no refresh-init contract. A typed
  backend guard now runs before inventory/persistence and both entrypoints
  translate it. The two focused modules passed 21 tests in 14.06s; a durable
  public-process regression and separate shell roundtrips returned rc=2 for
  missing/file roots, created no missing path, and emitted no traceback. Ruff,
  source/plugin byte parity, and the bounded code critique passed.

## Root Cause

The backend treats `repo_root` as an artifact destination without first
classifying whether the caller supplied a valid destination. Parent creation in
the current-pointer writer then silently turns an operator typo into a new
repository-shaped tree, and the two CLI entrypoints have no shared error
translation for the corresponding file-path failure.

## Invariant Proof

- Invariant: when catalog refresh receives a non-directory root, the backend
  must reject it before the current-pointer producer can write, and both final
  CLI consumers must return a clean nonzero diagnostic.
- Producer Proof: missing and regular-file roots reach `persist_catalog` before
  any validation; the former writes and the latter raises from `mkdir`.
- Final-Consumer Proof: backend no-write, direct-script rc/stderr+JSON, and
  public `charness` rc/stderr+JSON regressions pass; a separate shell roundtrip
  observed rc=2 for both invalid root classes and no created missing path.
- Interface-Shape Sibling Scan: inspect list, resolve-skill-path, capability
  init, and public catalog dispatch before making the guard generic.
- Non-Claims: no claim that every `--repo-root` command requires a Git checkout
  or that read-only catalog resolution must reject a missing root.

## Detection Gap

- `tests/test_capability_catalog.py` and public catalog dispatcher test | only
  existing-directory success/noop paths ran | add missing-directory and file-root
  refusal assertions that prove rc plus no filesystem creation/traceback.

## Sibling Search

- Mental model: a path accepted as a writer destination was treated as authority
  to create all missing parents.
- same layer: `scripts/capability_catalog.py` direct refresh CLI | decision: same
  bug, fix now | proof: local payload proof.
- abstraction up: public `charness cmd_catalog_refresh` | decision: same bug,
  fix now | proof: runtime public-CLI roundtrip.
- specialization down: catalog list/resolve-skill-path | decision: intentional
  plain-text or non-rendering boundary | proof: list is read-only and resolver
  has a focused missing-repo cache-recovery test.
- mental-model sibling: capability init | decision: intentional plain-text or
  non-rendering boundary | proof: it is explicitly an initialization command.
- cross-file: `charness` public dispatcher and
  `scripts/capability_catalog_artifact.py` final writer share the failing path.

## Seam Risk

- Interrupt ID: catalog-refresh-invalid-repo-root
- Risk Class: none
- Seam: parsed CLI path to repo-owned current-pointer writer
- Disproving Observation: a missing root is created and a file root leaks a
  traceback before either entrypoint can report a usage error.
- What Local Reasoning Cannot Prove: whether third-party callers import
  `refresh_catalog`; the backend exception keeps that failure explicit.
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: impl
- Handoff Artifact: none

## Prevention

Validate the destination once in the backend before inventory or persistence,
translate that typed failure in both CLI consumers, and retain focused no-write
regressions. Do not broaden the guard to read-only/cache-recovery commands.
