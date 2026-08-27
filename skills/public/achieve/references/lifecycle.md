# Achieve Planning and Pickup

Achieve has two durable boundaries: the planning record becomes immutable at
Goal Binding, and execution resumes through the provider-backed Goal Run. It
does not maintain a local lifecycle or progress ledger.

- `goal-artifact.md` — planning-record shape and writer.
- `adapter-contract.md` — interview ceiling and planning adapter fields.
- `../SKILL.md` — approval, binding, and exact `/goal #N` pickup.

The issue skill owns provider bootstrap, graph mutation, child proof, and
Goal Run closeout. Achieve only supplies the frozen draft identity and pickup
entry point.
