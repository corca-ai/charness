# Dual-Implementation Parity

Sometimes a repo ships one implementation and keeps another historical path
alive beside it. That is not automatically wrong, but it is a quality smell
until the relationship is explicit.

Signals worth inventorying:

- the same schema id or packet id appears in code across multiple language
  groups
- both paths are exported or still runnable
- tests exist for each side independently, but no parity harness feeds the same
  input through both and diffs the output
- docs or specs still call one side "the helper" even though the shipped path
  is elsewhere

`inventory_dual_implementation.py` stays intentionally advisory.
It can surface likely candidates when the same schema id appears across
languages and can point at doc-identity leakage when markdown mentions only one
of those paths.
It can still miss repos where the shipped path collapses multiple schema or
packet boundaries into one canonical source file and only the legacy wrapper
files carry the schema constants. Treat a clean report as "no weak-heuristic
hit", not proof that no dual-implementation drift exists.

When the smell is real, `quality` should recommend one of:

- add a parity harness
- choose one side canonical and delete or wrap the other
- document the divergence as intentional and add a test asserting it

Do not celebrate a duplicate implementation as a "free oracle" unless the repo
is also willing to pay the permanent alignment cost.
