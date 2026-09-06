# Catalog Alias Resolution

## Problem

The fixture currently resolves only canonical keys through `Catalog(mapping)`.
Consumers need alternate names that resolve to an existing canonical entry,
while existing constructor calls, canonical lookup, and unknown-key behavior
remain unchanged. Alias input must preserve duplicate definitions long enough
for the constructor to reject them; a dictionary is therefore not the public
alias representation.

## Capability Contract

`Catalog` gains an optional `aliases` argument:

```python
Catalog(mapping, aliases=[("reading", "books"), ("listening", "music")])
```

The supplied alias representation is an ordered list of two-item pairs
`(alias, canonical_key)`. Omitting `aliases` is exactly the no-alias case and
behaves as if an empty list had been supplied. The contract promises the
keyword form shown above; it does not add a separate requirement for passing
aliases positionally or for supplying a dictionary.

Canonical keys continue to be the keys of `mapping`, with the existing
canonical mapping and value behavior. An alias resolves to the value of its
target canonical key. An alias target must be a canonical key, not another
alias; alias chains and cycles are not part of this capability.

### Validation and failure shape

Alias definitions are validated during construction, before a successful
`Catalog` can be returned. Validation scans the list from left to right and
stops at the first invalid pair. For each pair, checks occur in this fixed
order:

1. If `alias` is a canonical key, raise `ValueError` with the exact message
   `alias <alias!r> collides with canonical key`.
2. If `canonical_key` is not a canonical key, raise `ValueError` with the
   exact message `alias <alias!r> targets unknown canonical key <canonical_key!r>`.
3. If the alias name has already appeared in an earlier pair, raise
   `ValueError` with the exact message `duplicate alias <alias!r>`.
4. Otherwise accept the pair and record its alias name as seen.

Here `<alias!r>` and `<canonical_key!r>` mean their normal Python `repr`
rendering in the message. For the string keys used by this fixture, for
example, the messages are `alias 'books' collides with canonical key`,
`alias 'missing' targets unknown canonical key 'archive'`, and
`duplicate alias 'reading'`.

Duplicate means the alias name is repeated, regardless of whether the target
is the same or different. Thus both
`[("reading", "books"), ("reading", "books")]` and
`[("reading", "books"), ("reading", "music")]` are rejected; no
last-write-wins behavior is allowed. The second occurrence is the offending
pair. If several different pairs are invalid, only the earliest invalid pair
in input order determines the exception. Its alias name must appear in the
exception message.

Unknown lookup remains the baseline behavior: `resolve(key)` raises
`KeyError(key)` for a key that is neither canonical nor a valid alias. Alias
validation errors are `ValueError` at construction time, not `KeyError` during
lookup. Canonical names cannot be aliases, so lookup has no canonical/alias
precedence ambiguity.

## Current Slice

Implement the optional constructor argument and ordered validation in
`src/catalog.py`, then add focused unit coverage to the existing standard
library test surface in `tests/test_catalog.py`. This spec phase changes only
this document; it does not implement the feature or add tests.

## Fixed Decisions

- `Catalog(mapping)` remains a supported call with unchanged canonical lookup.
- Omitted `aliases` means no aliases.
- The supported supplied representation is a list of ordered `(alias,
  canonical_key)` pairs, not a dictionary.
- An alias resolves to the value for its canonical target.
- A canonical key cannot also be an alias name.
- Every alias target must be an existing canonical key; an alias cannot target
  another alias.
- Repeated alias names are invalid, including repeated pairs with the same
  target and repeated names with different targets.
- Construction rejects every specified invalid alias definition with
  `ValueError`; unknown `resolve` keys continue to raise `KeyError`.
- Validation is left-to-right, stops at the first invalid pair, and uses the
  collision/unknown-target/duplicate precedence stated in the failure-shape
  contract above.
- The exception messages and alias-name inclusion described above are public
  behavior, not implementation suggestions.

## Probe Questions

- **Malformed input outside the pair contract:** During the first
  implementation slice, run a narrow probe for a dictionary container,
  `None`, a non-two-item entry, and an unhashable alias or target. The signal
  is whether the implementation needs a stable, user-facing rejection for
  malformed input. Record any newly supported error shape here before
  expanding acceptance; this probe must not change the fixed behavior for
   well-formed pairs and the specified rejection classes.

## Deferred Decisions

- Alias introspection, serialization, and a public aliases property are
  deferred until a consumer needs metadata beyond `resolve`; that request is
  the trigger to reopen this spec.
- Alias-to-alias chains, cycles, and normalization such as case folding are
  deferred until a caller explicitly requests alternate-name composition;
  this slice continues to require canonical targets.
- Behavior after a caller mutates its original aliases list, and any catalog
  mutation API, are deferred until the fixture exposes post-construction
  mutation; they do not affect construction-time validation or lookup here.

## Non-Goals

- Changing canonical key names, canonical values, or the normal unknown-key
  exception.
- Silently dropping invalid aliases, overwriting duplicate definitions, or
  using last-write-wins semantics.
- Supporting a dictionary as the alias input contract, alias chains, cycles,
  case-insensitive matching, or automatic alias normalization.
- Adding dependencies, a new evaluator, a new test framework, or a broad
  repository rewrite.

## Deliberately Not Doing

The implementation will not infer a conflict policy from dictionary ordering
or choose a later duplicate as authoritative. It will not make aliases a
second canonical namespace with different error behavior. Those alternatives
would make duplicate definitions unobservable or make a caller unable to
distinguish invalid configuration (`ValueError`) from an unknown lookup
(`KeyError`).

## Constraints

- Stay within this dependency-free consumer fixture and its existing
  `src/catalog.py` plus `tests/test_catalog.py` surfaces.
- Preserve the baseline standard-library test command:
  `python3 -m unittest discover -s tests -v`.
- Keep validation deterministic and independent of hash/dictionary insertion
  order: list position determines the offending pair, and the fixed per-pair
  precedence determines its failure class.
- Do not claim implementation or acceptance results in this spec phase.

## Success Criteria and Acceptance Checks

Each criterion is an observable contract and has a concrete check for the
implementation phase. All checks are `unit` checks run with
`python3 -m unittest discover -s tests -v`.

| ID | Fixed success criterion | Concrete acceptance check |
| --- | --- | --- |
| SC-1 | A caller can continue to construct `Catalog(mapping)` and resolve every existing canonical key to its existing value. | Preserve and pass `CatalogTests.test_resolves_existing_canonical_keys` using the existing no-alias setup. |
| SC-2 | An unknown key in the no-alias form still raises `KeyError`, with no new `ValueError` or silent miss. | Preserve and pass `CatalogTests.test_unknown_key_raises_key_error`. |
| SC-3 | A valid list of alias pairs lets each alias resolve to the value of its canonical target. | Add `CatalogTests.test_resolves_alias_to_canonical_value` with at least two aliases and assert alias results equal their canonical results. |
| SC-4 | Canonical lookup remains available and unambiguous when valid aliases are configured. | Add `CatalogTests.test_canonical_lookup_with_aliases` and resolve both a canonical key and its alias. |
| SC-5 | An alias name colliding with a canonical key is rejected at construction with `ValueError`, and the colliding alias name appears in the message. | Add `CatalogTests.test_rejects_alias_canonical_collision`; construct with `[("books", "music")]` and assert the exception type and message contain `books`. |
| SC-6 | An alias targeting a missing key is rejected at construction with `ValueError`, and that alias name appears in the message. | Add `CatalogTests.test_rejects_unknown_alias_target`; construct with `[("reading", "archive")]` and assert the exception type and message contain `reading`. |
| SC-7 | A repeated alias definition with the same target is rejected with `ValueError`; the second pair is not silently accepted. | Add `CatalogTests.test_rejects_duplicate_alias_same_target` with `[("reading", "books"), ("reading", "books")]` and assert the message contains `reading`. |
| SC-8 | A repeated alias name with a different target is also rejected with `ValueError`; no last-write-wins behavior occurs. | Add `CatalogTests.test_rejects_duplicate_alias_different_target` with `[("reading", "books"), ("reading", "music")]` and assert the message contains `reading`. |
| SC-9 | When multiple pairs are invalid, the first invalid pair in list order controls the failure, including the alias named in the message. | Add `CatalogTests.test_reports_first_invalid_pair_in_input_order` with `[("reading", "archive"), ("books", "music")]`; assert construction raises `ValueError`, the message contains `reading`, and it does not select the later `books` collision. |
| SC-10 | An unknown lookup remains `KeyError` even when valid aliases are configured. | Add `CatalogTests.test_unknown_key_with_aliases_raises_key_error`; configure a valid alias and assert `resolve("missing")` raises `KeyError`. |

The rejection checks must use `assertRaises`/`assertRaisesRegex` around
construction, not around `resolve`, so the public failure timing is tested as
well as the exception type. SC-5 through SC-9 cover every specified invalid
alias class and deterministic offending-entry rule.

## Tripwires

The implementation is off-contract if any test converts aliases to a
dictionary before duplicate validation, reports a later invalid pair instead
of the first one, raises `KeyError` for invalid configuration, or allows an
alias to shadow a canonical key. A focused test should fail immediately for
each of those signals.

## Boundary Ownership

- **Producer:** `Catalog` construction owns the canonical snapshot, alias
  validation, and alias-to-canonical resolution relationship.
- **Consumer:** callers of `Catalog.resolve` and the fixture's unit tests
  observe the successful values and failure types/messages.
- **Owning surface:** the `Catalog` public API in `src/catalog.py`, with
  `tests/test_catalog.py` as its executable acceptance surface.
- **Verdict:** `single-surface`; this bounded change does not move state across
  an external provider, package boundary, or separate evaluator.

## Critique

### Fixed/Probe/Defer Coherence Result

Pass. The constructor, lookup, validation order, exception shape, and
offending-entry rule are fixed. The only probe concerns malformed inputs
outside the explicitly supported list-of-pairs representation, and each
deferred item has a concrete consumer request that would reopen it.

### Acceptance Check Coverage Result

Pass. SC-1 and SC-2 preserve the two existing baseline tests; SC-3 and SC-4
cover successful alias/canonical lookup; SC-5 through SC-8 cover every
rejection; SC-9 covers first-invalid ordering; and SC-10 covers unknown lookup
with aliases. Every criterion maps to a named unit check and the documented
standard-library command.

### Counterweight Triage

- **Act Before Ship:** none after fixing per-pair precedence, exact failure
  messages, and the first-invalid stop rule.
- **Bundle Anyway:** keep the focused negative tests at the existing unit-test
  boundary so duplicate handling cannot regress into dictionary overwrite.
- **Over-Worry:** recursive alias graphs, serializer design, and broad key-type
  taxonomies are unsupported future shapes, not blockers for this fixture.
- **Valid but Defer:** malformed alias-container/entry behavior and
  post-construction mutation semantics remain visible in Probe Questions and
  Deferred Decisions.

### Fresh-Eye Satisfaction

No fresh-eye approval is claimed. The exported delegation resolver found no
repo-owned grant and returned `ask`; this spec phase is limited to the single
requested document, so the contract records the bounded inline review and
leaves external reviewer authorization to the owning workflow.

## Canonical Artifact

This file, `docs/alias-resolution.md`, is the source of truth for the next
implementation context. If implementation discovers a fact that changes a
fixed decision or acceptance check, update this document before relying on the
new behavior.

## Ready for Impl

This contract is ready when the next context can implement the `Current Slice`
without choosing any public behavior: it has the exact constructor form,
ordered list representation, validation precedence, exception types/messages,
first-invalid rule, preserved `KeyError` behavior, and a named check for every
success criterion. The malformed-input probe and deferred items do not block
the first slice and must remain visible if they are not resolved.

## First Implementation Slice

1. Extend `Catalog` to accept omitted or supplied `aliases` while retaining
   canonical mapping behavior.
2. Validate the ordered pairs exactly in the specified order before exposing a
   usable catalog; retain aliases only after validation so duplicates cannot be
   overwritten first.
3. Resolve aliases through their canonical targets and preserve native
   `KeyError` for unknown lookups.
4. Add the SC-3 through SC-10 focused tests while keeping SC-1 and SC-2 green,
   then run the documented standard-library command.

The implementation handoff is complete when this slice satisfies all fixed
criteria and reports any malformed-input probe result without expanding the
fixture's scope.
