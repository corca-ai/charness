# Unit-Test Quality (per-test-body authoring)

A per-test-body authoring lens. The rest of `quality`'s test surface is
suite-level (economics, mutation, dup-ratchet, selection); this is the layer
*inside* one test. Sits **below** [`testability-and-selection.md`](./testability-and-selection.md):
that file owns the test-DSL **review** lens (is the DSL hiding untestable
structure? are assertions still visible at the `.test` site?) and is stronger
there — keep it. This file grafts only the *authoring* principles, stack-neutral;
`quality` still ships no stack-specific DSL (consumer repos build their own).

Each pattern is a principle plus one worked example, not a do-not list — derive
the next case from the example. Apply the no-op deletion test to this reference
too: a line that a competent test author would already follow without it should
go.

## 1. Determinism harness

A test that can fail on a different clock, locale, machine, or run order is not
testing the behavior — it is testing the environment. Pin the ambient inputs
(clock, randomness, timezone, locale, generated ids, iteration order) at the test
seam; prefer a fake clock over `sleep`; isolate state in-memory or in a temp dir;
assert on sets/sorted views when order is not part of the contract.

> A token-expiry test that does `sleep(2)` and checks "expired" is slow and
> flaky. Inject the clock: `clock.advance(ttl + 1s)` then assert expired — fast,
> deterministic, and it actually pins the boundary.

## 2. Properties and invariants in the test

A property the code must hold for *all* inputs is worth more than one example
row. Encode the invariant: idempotence (`f(f(x)) == f(x)`), round-trips
(`decode(encode(x)) == x`), normalization, immutability (the input the caller
owns is unchanged), and preservation of unrelated fields.

> A `redact(record)` test that checks one masked field can pass while silently
> dropping every other field. Assert the invariant instead: the secret field is
> masked AND every other field round-trips unchanged — now the "drops siblings"
> bug fails the test.

## 3. Observable contract over private mechanics

Test what a caller can observe (return value, emitted event, persisted row,
raised error), not a private helper or call count. One reason to fail per test:
the assertion names the behavior, so a green-to-red flip points at one cause.
Prefer explicit assertions over a whole-object snapshot that re-fails on every
unrelated change.

> Asserting `_parse` was called once couples the test to structure and stays
> green when `_parse`'s result is dropped. Assert the parsed value reached the
> output instead — the contract, not the mechanic.

## 4. Real collaborators by default (in-process)

For in-process code, use the real collaborator; reach for a double only at a
genuine boundary (network, clock, external provider, nondeterministic source).
A mock of your own pure function tests the mock. (`quality` already states this
for external provider APIs; this extends it to in-process code.)

> A pricing test that stubs the real in-process `tax_table` asserts the stub.
> Use the real table and stub only the currency-rate *fetch* (the network edge).

## 5. Map behavior before testing

List the behavior's branches and edge cases before writing assertions, then write
the negative and boundary cases first — they catch the regressions the happy path
hides. Empty, one, many; zero/negative; null/missing; duplicate; over-limit;
malformed.

> Before testing `split_invoice`, map: 0 line items, 1, many; a zero-amount item;
> a rounding remainder. The remainder case is where the money bug lives — write
> it first, not last.

## 6. Fixture / DSL authoring

Build test data the reader can see. Plain literals until repetition genuinely
hides intent; a builder's defaults valid, minimal, and visible, with the test
overriding only the scenario-relevant field; avoid fluent chains that bury
cause and effect; prefer a small named helper over a clever grammar.

> `order(items=[item(qty=0)])` shows the scenario — the zero quantity — at a
> glance. `OrderBuilder().withDefaults().withItem(...).build()` hides which field
> the test actually turns on. Name the variation; default the rest.
