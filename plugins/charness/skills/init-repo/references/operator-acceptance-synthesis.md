# Operator Acceptance Synthesis

When `<repo-root>/docs/operator-acceptance.md` is missing in a repo that already has real
checks, derive it from the repo's current command and takeover surface instead
of inventing a parallel ritual.

## Synthesis Rule

Start from:

- standing repo-owned gates
- repo-owned install, update, doctor, or reset commands
- the repo's named probe surface when install and health/readiness semantics
  are split across multiple commands
- remaining roadmap or deferred-decision items
- known human-only takeover steps

Then classify each item explicitly:

- `machine-local`: runnable in a normal local clone without extra systems
- `machine-external`: runnable, but depends on credentials, services, seeded
  data, or another host state
- `human-judgment`: requires reading, approval, comparison, or a product call

Also tag cost and order:

- `cheap-first`: the first bounded checks an operator should run
- `expensive-later`: fuller validation or host-visible proof after the cheap pass

## Good Shape

A good operator-acceptance section usually contains:

- shared start commands
- prerequisites for external or privileged steps
- remaining items with read-first pointers
- acceptance bullets that say what proves completion

Use `<repo-root>/scripts/synthesize_operator_acceptance.py` when the repo already has
functional-check style Markdown specs or repo-owned command surfaces and needs
the first honest draft before manual tightening.

## Avoid

- copying the roadmap verbatim without runnable or reviewable acceptance steps
- hiding environment prerequisites inside command prose
- mixing human judgment and machine checks into one indistinguishable list
- forcing an operator to rediscover which command is cheap smoke versus costly proof
