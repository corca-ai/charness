# Alias Resolution

## Problem

The fixture currently exposes `Catalog(mapping)`, where canonical keys are
looked up directly and an unknown key produces the normal `KeyError`. Consumers
need optional alternate names without changing that existing call or changing
the meaning of a canonical key. Alias input must retain order and duplicates so
bad definitions are observable and rejected rather than collapsed by a
dictionary.

## Capability Contract

The public forms in this slice are:

```python
Catalog(mapping)
Catalog(mapping, aliases=[("reading", "books"), ("listening", "music")])
```

`mapping` keeps its existing meaning: its keys are the canonical keys and its
values are the values returned by `resolve`. `aliases`, when supplied, is an
ordered list of two-item `(alias, canonical_key)` pairs. A pair's first item is
the name accepted by `resolve`; its second item must name an existing
canonical key. The required public representation is the list of pairs, not a
dictionary. An omitted or empty alias list adds no aliases.

For a valid catalog:

- `resolve(canonical_key)` continues to return the value stored under that
  canonical key.
- `resolve(alias)` returns the same value as resolving the alias's target
  canonical key. Alias targets are canonical keys only; aliases do not chain.
- Canonical keys and alias names share one namespace. An alias name equal to a
  canonical key is invalid, even when it targets that same key.
- A key that is neither a canonical key nor an accepted alias raises
  `KeyError` from `resolve`. The unknown-key behavior remains a lookup failure,
  not an alias-validation failure.

### Validation and failure shape

The constructor validates the alias list in its supplied order before a usable
`Catalog` instance is returned. It stops at the first invalid pair; later
pairs are not considered. “First” means the lowest input-list index that is
invalid, not the first error found after sorting, deduplicating, or converting
the list to a dictionary.

For a pair at that index, apply these checks in this fixed order:

1. If `alias` is a canonical key, raise `ValueError` with exactly:
   `alias <alias!r> collides with canonical key`.
2. If the same `alias` occurred in an earlier pair, raise `ValueError` with
   exactly: `duplicate alias <alias!r>`.
3. If `canonical_key` is not a key in `mapping`, raise `ValueError` with
   exactly: `alias <alias!r> targets unknown canonical key <canonical_key!r>`.

Here `<alias!r>` and `<canonical_key!r>` mean their Python `repr` in the
message, as in an f-string conversion. Every invalid alias definition in this
slice therefore raises plain `ValueError`, and every such message includes the
offending alias name. Duplicate means a repeated alias name regardless of
whether the repeated pair has the same target or a different target. There is
no last-write-wins behavior.

The semantic contract assumes the supplied alias representation is a list of
valid two-item pairs with hashable names. Acceptance does not define behavior
for a dictionary, malformed pair, or unhashable name; those inputs are outside
this bounded slice and must not be used to weaken or change any behavior above.

## Current Slice

This phase creates this implementation contract only. It does not modify
`src/catalog.py` or `tests/test_catalog.py`, and it does not add alias support.
The next phase will implement the constructor and lookup behavior, then add the
unit checks named below. The dependency-free fixture continues to use its
standard-library test command.

## Fixed Decisions

- Preserve `Catalog(mapping)` and all existing canonical-key lookup behavior.
- Add aliases as an optional `aliases` argument; the required representation is
  an ordered list of `(alias, canonical_key)` pairs.
- Validate against the canonical keys from `mapping`, not against previously
  declared aliases; alias chaining is not supported.
- Reject canonical-key collisions, missing canonical targets, and any repeated
  alias name, including a repeat of the same target.
- Scan input order and fail immediately on the first invalid pair.
- Resolve multiple invalid conditions on one pair using the precedence
  canonical collision, then duplicate alias, then unknown target.
- Use plain `ValueError` for invalid alias definitions and preserve `KeyError`
  for an unknown `resolve` key.
- Use the exact failure-message templates in the capability contract; the
  offending alias is always present in the message.
- Keep this fixture dependency-free and verify the behavior with
  `unittest`-style unit checks.

## Probe Questions

No product or API decision is left open for implementation. One small,
non-blocking implementation probe remains visible: after the first slice is
written, run the combined baseline and alias unit checks and confirm that the
normal `KeyError` path is still reached for an unknown lookup while each
`ValueError` message contains the `repr` of the alias named by its failing
pair. If that probe fails, adjust the implementation or its tests to this
contract; do not broaden the API or change the fixed precedence.

## Deferred Decisions

- Whether to accept tuple, generator, or other iterable containers in addition
  to the required list is deferred. Supporting one later must not change the
  ordered-pair validation rules.
- Whether to expose aliases or a reverse-alias index through a new public
  inspection API is deferred and out of this slice.
- Caller mutation semantics after construction are explicitly not promised:
  callers must not rely on mutating the input list changing, or not changing,
  a constructed catalog. This decision should be reopened only if a consumer
  requires a documented live/snapshot policy or a public inspection API is
  proposed. The internal storage shape is also deferred; neither deferral
  permits input reordering, silent duplicate replacement, alias chaining, or
  changed lookup failures.

## Non-Goals

- No alias chains, recursive resolution, wildcard matching, or normalization of
  names.
- No change to mapping value copying, canonical-key equality, or ordinary
  Python lookup behavior beyond the required alias branch.
- No new dependency, evaluator, validation framework, CLI, persistence layer,
  or broad repository rewrite.

## Deliberately Not Doing

The implementation will not accept a dictionary as the specified alias data
model or use dictionary overwrite order to decide which duplicate wins. It
will not add a generalized schema for malformed inputs merely to make this
small fixture appear more complete. It will not add acceptance tooling beyond
the repository's existing standard-library test command.

## Constraints

- The only public behavior being changed is construction with the required
  `aliases=[(alias, canonical_key), ...]` list and resolution of valid aliases.
- Canonical lookup is the compatibility boundary: existing callers and tests
  must remain valid without edits to their calls.
- Validation must happen before the constructor returns, so a caller cannot
  observe a partially accepted alias set.
- Tests belong at the existing `tests/test_catalog.py` unit boundary and must
  run with:

  ```text
  python3 -m unittest discover -s tests -v
  ```

- The spec is bounded to this consumer fixture. It does not prescribe a new
  evaluator or a new test dependency.

## Success Criteria

Each criterion below states an observable behavior and its concrete acceptance
check. The checks are planned for the implementation phase; this spec phase
intentionally does not add them.

| ID | Observable behavior | Concrete acceptance check |
| --- | --- | --- |
| SC-1 | Existing callers using `Catalog(mapping)` still resolve every existing canonical key to its existing value, and an unknown key still raises `KeyError`; an explicit empty alias list is equivalent to omitting aliases. | `unit`: retain and pass `CatalogTests.test_resolves_existing_canonical_keys` and `CatalogTests.test_unknown_key_raises_key_error`, and add `CatalogTests.test_empty_alias_list_preserves_canonical_behavior`; run `python3 -m unittest discover -s tests -v`. |
| SC-2 | A catalog created with an ordered alias list resolves each valid alias to the value at its canonical target, while the target's canonical lookup remains available. | `unit`: add `CatalogTests.test_resolves_alias_to_canonical_value` using at least two aliases and `CatalogTests.test_canonical_lookup_remains_available_with_aliases`; run the standard unittest command. |
| SC-3 | An alias name colliding with any canonical key is rejected during construction, including when it targets the colliding key itself; the message identifies the alias. | `unit`: add `CatalogTests.test_rejects_alias_colliding_with_canonical_key`, asserting `ValueError` and the exact `alias 'books' collides with canonical key` and `alias 'music' collides with canonical key` messages for `aliases=[('books', 'books')]` and `aliases=[('music', 'music')]`. |
| SC-4 | An alias targeting a name absent from the canonical mapping, including a name that is only another alias, is rejected during construction, and the message identifies the alias and missing target. | `unit`: add `CatalogTests.test_rejects_alias_with_unknown_target`, asserting `ValueError` and the exact message for `aliases=[('novels', 'missing')]`; also cover `aliases=[('reading', 'short'), ('short', 'books')]`, which must fail first on `reading` because `short` is not canonical. |
| SC-5 | Repeating an alias name is rejected deterministically whether the repeated target is the same or different; no definition silently overwrites another. | `unit`: add `CatalogTests.test_rejects_duplicate_alias_with_same_target` for `[('reading', 'books'), ('reading', 'books')]` and `CatalogTests.test_rejects_duplicate_alias_with_different_target` for `[('reading', 'books'), ('reading', 'music')]`, asserting `ValueError` with `duplicate alias 'reading'`. |
| SC-6 | When several pairs could fail, the error names the first invalid input pair and follows the fixed per-pair precedence, with the offending alias in the message. | `unit`: add `CatalogTests.test_reports_first_invalid_alias_pair_in_input_order` with these exact vectors and expected messages: `[('first', 'missing'), ('books', 'books')]` → `alias 'first' targets unknown canonical key 'missing'`; `[('books', 'missing'), ('later', 'missing')]` → `alias 'books' collides with canonical key`; `[('first', 'books'), ('first', 'missing')]` → `duplicate alias 'first'`. |
| SC-7 | All invalid alias definitions use `ValueError`, while an unresolved lookup on an otherwise valid catalog uses `KeyError`; construction does not silently produce a partially valid catalog. | `unit`: the rejection tests in SC-3–SC-6 use `assertRaises`/`assertRaisesRegex` around construction, and add `CatalogTests.test_unknown_key_with_aliases_raises_key_error` for a valid alias-enabled catalog; the standard unittest command is the check. |

## Acceptance Checks

The implementation handoff must add or retain the following checks at the
existing unit boundary:

1. `unit` — Run `python3 -m unittest discover -s tests -v`; the full fixture
   suite passes, including both retained baseline tests.
2. `unit` — Exercise valid aliases, canonical keys, and `aliases=[]` together,
   proving that aliases point only to canonical values, canonical access is
   retained, and an empty list adds no behavior.
3. `unit` — Exercise each invalid-definition family separately: canonical
   collision for more than one canonical key, unknown target (including an
   alias name used as a target), duplicate same target, and duplicate different
   target. Assert `ValueError`, the exact message template, and the alias name.
4. `unit` — Exercise an ordered list containing multiple potential failures and
   assert the exact first-pair messages and fixed precedence described above.
5. `unit` — Resolve an unknown key on a valid alias-enabled catalog and assert
   `KeyError`, keeping lookup failure distinct from constructor validation.

No new evaluator, dependency, or broad integration surface is needed for these
checks.

## Boundary Ownership

- `Catalog.__init__` owns validation of the ordered alias definitions and the
  decision to reject construction. It compares aliases with canonical keys,
  tracks previously seen alias names, and emits the specified `ValueError`.
- `Catalog.resolve` owns the lookup boundary. It checks canonical and accepted
  alias names and emits the ordinary `KeyError` for an unresolved key.
- `tests/test_catalog.py` owns executable acceptance of the public behavior,
  including exception types, exact messages, input-order selection, and the
  preserved baseline cases.
- This document is the source of truth for the current contract until
  implementation changes are proposed. Any implementation discovery that
  changes scope or acceptance must update this file before code proceeds.

## Critique

Pre-implementation review focus is bounded to this document and the existing
`Catalog`/unittest seam:

- Structure and framing: the contract leads from the compatibility problem to
  fixed validation behavior, then maps every success criterion to a concrete
  unit check.
- Failure semantics: ordered scanning, duplicate identity, per-pair
  precedence, exception types, and exact messages are fixed so an implementer
  does not infer last-write-wins or sort input.
- Operational fit: the acceptance surface is the existing dependency-free
  unittest command; no evaluator or broad repository mechanism is introduced.

Counterweight disposition: the exact message templates and precedence are
`Bundle Anyway` contract detail because they are cheap and prevent divergent
tests; iterable-container support and introspection are `Valid but Defer`;
general malformed-input taxonomy and alias-chain support are `Over-Worry` for
this fixture. The review also required the mutation non-claim to name its
reopen trigger, and the acceptance matrix now covers empty lists, a second
canonical collision, non-canonical alias targets, and explicit first-error
vectors. There is no `Act Before Ship` concern remaining for the bounded slice.
The Fixed/Probe/Defer split is coherent: fixed decisions fully define required
behavior, the probe only confirms the first implementation slice against that
behavior, and each deferred item names the later API need that would reopen it.
Every success criterion has a matching `unit` check.

## Canonical Artifact

`docs/alias-resolution.md` is the canonical implementation contract for this
slice. The implementation phase should read it before changing source or
tests; this file remains the place to record any scope or acceptance change.

## First Implementation Slice

1. Extend `Catalog` construction with the optional ordered alias-list input.
2. Validate pairs in input order using the fixed precedence and message
   templates, rejecting before returning an instance.
3. Add alias resolution while preserving canonical lookup and unknown-key
   `KeyError` behavior.
4. Add the named unit checks in `tests/test_catalog.py` and run the standard
   unittest command.

Ready for impl means this document is the only spec-phase change, the public
call forms and failure shape above are fixed, every rejection and compatibility
criterion has a named check, and the only remaining probe is the bounded
implementation/test confirmation. No product clarification is required before
the next context starts.
