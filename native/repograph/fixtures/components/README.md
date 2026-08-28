# Components fixture

This fixture pins topology components and bounded reverse explanations:

- `scripts/cross_a.py` and `skills/shared/scripts/cross_b.py` form a
  cross-package cycle;
- `scripts/rootless_a.py` and `scripts/rootless_b.py` are a rootless cycle;
- `tests/test_island.py` and `tests/test_island_helper.py` are a closed test
  component reached only from a test root; and
- `runtime_bootstrap.py` reaches `scripts/explain_target.py` through two typed
  import edges, which also has two direct dependents.

`scripts/boundary_violation.py` is the shared violation witness used to compare
`components` with `export-safe`.
