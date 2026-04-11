# Design Lenses

Use these lenses only when they sharpen the current contract choice.

## Kent Beck

- prefer a slice small enough to learn quickly
- let fast feedback carry as much confidence load as possible
- avoid freezing detail early when a thinner slice can answer the question

## John Ousterhout

- push complexity behind a smaller, clearer interface when possible
- prefer one deeper seam over many shallow coordination surfaces
- treat duplicated low-level acceptance detail as a sign the contract boundary
  may be wrong

## Translation For Spec

- use Beck when deciding how small the first probe or slice can honestly be
- use Ousterhout when the contract is getting noisy because interfaces or
  responsibilities are split too shallowly
