# Design Lenses

This reference captures the Beck and Ousterhout moves that matter to `impl`.

## Kent Beck

- keep slices small enough that feedback arrives quickly
- let the next test, check, or real invocation answer one question at a time
- avoid bundling several uncertainties into one large change

## John Ousterhout

- prefer a simpler interface that hides complexity behind a deeper seam
- treat copied coordination code as a signal that the seam is too shallow
- simplify the ownership boundary before adding more verification ceremony

## Translation For Impl

- use Beck when choosing the smallest honest slice and the next proof step
- use Ousterhout when interface sprawl or copied helper seams are the real
  source of risk
- if the real question is command-surface shape for an agent-facing CLI, not
  slice discipline, see `../../create-cli/references/command-surface.md`
  prep/execute split section instead
