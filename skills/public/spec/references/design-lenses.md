# Design Lenses

This reference captures the Beck and Ousterhout moves that matter to `spec`.

## Kent Beck

- prefer a slice small enough to learn quickly
- let fast feedback carry as much confidence load as possible
- avoid freezing detail early when a thinner slice can answer the question

## John Ousterhout

- push complexity behind a smaller, clearer interface when possible
- prefer one deeper seam over many shallow coordination surfaces
- treat duplicated low-level acceptance detail as a sign the contract boundary
  may be wrong

## Boundary ownership

- when the contract places a fact, some state, or a behavior on a surface, run
  the [boundary ownership brief](../../../shared/references/boundary-ownership-brief.md)
  producer/consumer questions so a mislocated owner is caught in the contract
  rather than after `impl` encodes it — Ousterhout's "wrong contract boundary"
  smell and the brief's producer/consumer question are the same move seen from
  two sides
- the disposition this lens produces is carried by the bounded `critique` this
  skill runs before finalizing (step 7); `spec` records it as an emit-only
  `Boundary Ownership` closeout token, not a separate validator

## Translation For Spec

- use Beck when deciding how small the first probe or slice can honestly be
- use Ousterhout when the contract is getting noisy because interfaces or
  responsibilities are split too shallowly
