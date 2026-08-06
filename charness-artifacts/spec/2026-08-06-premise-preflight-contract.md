# Slice 2 Implementation Contract: Premise Preflight

## Problem

Implementation slices currently begin by manually reconstructing whether an
issue premise is still live, whether the relevant tree has moved, and whether
the same work was already accepted. That reconstruction permits a stale issue
read, a duplicate slice, an already-shipped premise, or a partial local repair
to enter design as if it were new.

## Capability Contract

An operator can run one source-checkout command against a captured issue
readback and a candidate premise record. The command compares the issue
identity and the protected tree identity, refuses stale/duplicate/
already-shipped/partial-repair premises with named machine-readable reasons,
and persists the accepted or refused decision as a durable JSONL record.

The preflight consumes an issue readback produced by the issue adapter. It does
not call GitHub, mutate issue state, execute the proposed repair, or claim that
a local readback is provider/runtime proof.

## Current Slice

Add `scripts/premise_preflight_lib.py` and the thin CLI
`scripts/check_premise_preflight.py`, plus the checked-in plugin mirror and
focused fixture tests. The command is an offline coherence check over two
captured inputs: an exact `issue_tool.py read` envelope and a candidate premise
record. The workflow obtains a fresh provider read before invoking this command;
the command itself cannot establish provider freshness.

The candidate record has this schema (`charness.premise-preflight`, version 1):

```json
{
  "kind": "charness.premise-preflight",
  "schema_version": 1,
  "premise_id": "issue-510-slice-2",
  "repository": "owner/repo",
  "goal_path": "charness-artifacts/goals/example.md",
  "slice_id": "slice-2-premise-preflight",
  "decision_log": "charness-artifacts/goals/premise-decisions.jsonl",
  "issue": {
    "number": 510,
    "expected_state": "OPEN",
    "captured": {
      "body_sha256": "<sha256 of issue.body UTF-8 bytes>",
      "comments_sha256": "<sha256 of canonical comments JSON>",
      "comment_count": 0,
      "updated_at": "2026-08-06T01:20:31Z"
    }
  },
  "tree": {
    "captured_head_sha": "<40 lowercase hex SHA>",
    "protected": [
      {"path": "scripts/example.py", "sha256": "<HEAD blob bytes>"}
    ],
    "expected_missing": ["scripts/not-yet-created.py"]
  }
}
```

`protected` is non-empty and unique. Each entry must be a regular tracked blob
at `captured_head_sha`; its hash is SHA-256 over the blob bytes at that commit.
The preflight compares both the index blob and the regular worktree file to
that captured hash. `expected_missing` paths must be absent from the captured
commit, current worktree (including symlinks), and current index. An indexed
descendant below an expected-missing directory is also a partial repair. All
paths use the same safe repository-relative POSIX rules as the Slice 1
manifest.

The accepted issue input is the exact envelope emitted by
`skills/public/issue/scripts/issue_read.py`: `ok: true`, top-level `repo`,
`number`, `comments_read: true`, `comment_count`, and nested `issue` fields
`number`, `body`, `comments`, `state`, and `updatedAt`. The outer repository is
authoritative because the current producer does not emit `issue.repo`; outer
and inner numbers must agree. `comments` must be a list and its length must
equal the outer count. `comments_sha256` hashes the ordered comments list as UTF-8 JSON
with sorted object keys and compact separators. No captured file authenticity
is claimed.

The CLI checks current `HEAD`, protected index/worktree bytes, expected-missing
paths, prior accepted decisions, and the exact full-line marker
`Charness-Premise-ID: <premise_id>` in commit bodies reachable from current
`HEAD` only. It appends one decision record for every semantically valid run;
structural input or malformed-history refusals are emitted but are not appended
because they cannot preserve an auditable JSONL stream.

## Fixed Decisions

- The issue readback is an input file, not an implicit provider call. This
  keeps the preflight deterministic and leaves the provider read as a distinct
  observer-owned step. `stale_issue` means captured-candidate/readback
  incoherence only; it never means the provider changed after capture.
- The expected issue state is `OPEN`. A readback state of `CLOSED` always emits
  `already_shipped`, never `stale_issue`; any other state is invalid input.
  Body, ordered comments, update timestamp, outer/inner repository, number, or
  completeness mismatches emit `stale_issue` only after the envelope shape is
  valid.
- A moved current `HEAD` emits `stale_tree` only and skips path drift
  classification. When `HEAD` still matches, a changed index blob, changed
  regular worktree file, missing protected file, newly present expected-
  missing path, or inaccessible protected file emits `partial_repair`.
  Detection is limited to the declared protected/missing set.
- A prior `accepted` decision with the same stable `premise_id` emits
  `duplicate_premise`; prior refused decisions are retained but do not block a
  retry. The decision record carries a generated `attempt_id` so retries remain
  distinguishable without allowing a new premise ID to evade the duplicate
  check.
- The shipped marker is generated from the stable premise ID, matched as an
  exact full line in commit bodies reachable from current `HEAD`; a match emits
  `already_shipped`. No arbitrary local ref or unreachable object is searched.
- Semantic reason codes are additive in this exact order:
  `already_shipped`, `duplicate_premise`, `stale_issue`, `stale_tree`,
  `partial_repair`. `stale_issue` is not emitted for a closed issue, and
  `partial_repair` is not emitted when `stale_tree` is present.
- The JSONL log is append-only by one local process, with no concurrency/locking
  promise in this slice. Every structurally valid run appends an accepted or
  refused record. A malformed existing log emits `invalid_decision_history`,
  does not append, and must be repaired before retrying.
- A decision log must be a regular non-symlink file when it exists. A dangling
  or resolved symlink is a structural refusal and is never followed for reads
  or writes.
- The CLI emits sorted JSON, exits `0` for accepted, `1` for a semantically
  refused but persisted decision, and `2` for structural/history or append
  errors. It emits a non-claim that this is offline coherence evidence only.

## Probe Questions

- Does the CLI preserve all distinct semantic refusal reasons when more than
  one identity has drifted, while obeying the stale-tree precedence? Acceptance:
  a fixture asserts the exact ordered reason list and persisted record.
- Does the actual issue-tool envelope reject missing comments, inconsistent
  outer/inner fields, same-count/different-content comments, and invalid
  timestamps before semantic comparison? Acceptance: adapter-shaped fixtures
  refuse with `invalid_issue_readback` or `stale_issue` as appropriate.
- Does a clean valid premise survive source and checked-in plugin subprocess
  invocation, while an index-only or worktree-only edit is classified as
  `partial_repair`? Acceptance: a temporary git fixture and parity check pass.

## Deferred Decisions

- Live provider invocation belongs to a later publish/ledger bundle; this slice
  accepts the issue adapter's captured output only.
- Commit-marker conventions for release or PR carriers belong to the publish
  ledger slice; this slice uses one explicit premise marker only.
- A universal prose or semantic duplicate detector is deferred. Duplicate
  identity is limited to the structured premise ID and the persisted decision
  log.

## Non-Goals

- Do not close, reopen, label, or otherwise write a GitHub issue.
- Do not infer behavior proof from issue state, git history, or a passing local
  validator.
- Do not inspect arbitrary prose to decide that two different issues are
  semantically duplicates.
- Do not add a closeout gate or change the runtime floor in this slice.

## Deliberately Not Doing

The preflight does not own the issue body, the issue adapter, the final bundle,
or the publish ledger. It records the identity decision needed by those later
surfaces and leaves their ownership unchanged.

## Constraints

- JSON input/output must be stable, sorted, and safe for shell-free callers.
  Structural errors do not write the decision log.
- Repository paths are relative POSIX paths and may not escape the repository;
  protected paths must be regular tracked blobs, not symlinks. Expected-missing
  index checks include descendants because Git stores files, not directory
  entries, in the index.
- Git identity comparisons use exact lowercase 40-character commit SHAs and
  SHA-256 file hashes. `HEAD` must resolve to a commit; unborn or ambiguous
  repositories refuse with `invalid_git_state`.
- Issue timestamps must be non-empty RFC3339 UTC strings ending in `Z`; body
  and comment hashes use exact UTF-8 bytes and the canonical JSON projection
  above.
- The source and checked-in plugin scripts must remain byte-identical.
- Existing decision logs with malformed JSON or invalid decision records are a
  refusal, not silently ignored history.
- Goal and slice identifiers are audit bindings; the preflight does not parse
  the goal prose or become its source of truth.

## Success Criteria

1. A valid captured issue/tree premise returns `accepted` and appends a
   versioned decision record containing the stable premise ID, generated
   attempt ID, issue/tree observations, ordered empty reason codes, and the
   offline non-claim.
2. A valid but changed issue envelope returns `stale_issue`; a malformed or
   incomplete envelope returns `invalid_issue_readback` without appending.
3. A moved `HEAD` returns only `stale_tree`; a matching `HEAD` with an index,
   worktree, protected-file, or expected-missing drift returns `partial_repair`.
4. A prior accepted premise returns `duplicate_premise`; a closed issue or
   exact reachable marker returns `already_shipped`.
5. Malformed decision history, unsafe/untracked protected paths, invalid git
   state, and mismatched repository/issue identity produce structured refusal
   output and do not append.
6. The source and plugin CLI/lib copies are byte-identical and focused
   regression tests cover positive, negative, persistence, retry, marker
   reachability, and shell-free subprocess paths.

## Acceptance Checks

- `unit`: focused tests exercise each refusal class, stable reason ordering,
  exact envelope/hash semantics, JSONL persistence/retry, and shell-free
  subprocess output.
- `integration`: a temporary git fixture runs the source CLI against a captured
  issue-tool envelope and protected tree, then mutates issue content, HEAD,
  index, worktree, expected-missing paths, and decision history one at a time.
- `manual`: inspect one emitted decision record and confirm it names captured
  issue/tree evidence while making no provider/runtime claim.
- `specdown`: `python3 scripts/check_spec_evidence_durability.py --repo-root .
  --require-git-file-listing` validates this contract's durable references.

## Boundary Ownership

- `issue_tool.py read` owns provider/backend reads and comments completeness.
- `premise_preflight_lib.py` owns structured premise identity comparison and
  refusal reasons.
- The JSONL decision log owns the preflight decision history only.
- GitHub remains the source of truth for issue state; the goal manifest remains
  the source of truth for published proof identity.

## Critique

Delegated spec and implementation critiques are recorded in
`charness-artifacts/critique/2026-08-06-slice-2-premise-contract.md` and
`charness-artifacts/critique/2026-08-06-slice-2-premise-implementation-review.md`.
The implementation review's second round found and bound repairs to the
remaining proof-surface escapes; those repairs are explicitly
accepted-unreviewed under the two-round cap.

## Canonical Artifact

`charness-artifacts/spec/2026-08-06-premise-preflight-contract.md`

## First Implementation Slice

Implement the library and CLI, add the temporary-git and issue-envelope
fixtures, sync the plugin mirror, and run the focused proof before any broad
closeout or publish action.
