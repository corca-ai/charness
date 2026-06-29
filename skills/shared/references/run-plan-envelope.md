# Run-Plan Envelope (canonical planner contract)

Every charness skill that ships a deterministic planner (`plan_*` /
`*_plan.py`) emits ONE envelope shape so an agent learns a single protocol, not
one bespoke bootstrap per skill. The shared builders and validator live in
[`skills/shared/scripts/run_plan_envelope.py`](../scripts/run_plan_envelope.py)
(mirrored to `plugins/<pkg>/shared/scripts/`).

## Minimal Vocabulary

Three keys carry the shared meaning; everything else is a per-skill extension:

- `required_reads` — list of `read()` items to open before broad work. Each item
  is `{path, why}` plus optional `kind` / `base` (debug/handoff/retro),
  `trigger` (gather/issue), `role` (issue/quality).
- `next_action` — a single `next_action()` dict, ALWAYS carrying a string
  `kind`. `command` / `instruction` / `reason` / `why` / `redirect` /
  artifact pointers ride as extensions. It is never a bare string.
- `gate_packets` — list of `gate_packet()` deterministic evidence packets. Core
  keys are `id` / `trust_model` / `cost_tier`; `status` / `command` /
  `available` / `path` / `parallel_group` / `run_when` / `purpose` are
  extensions.

Plus two markers: `schema_version` (the skill's own dialect, e.g.
`debug.run_plan.v1`) and `envelope_version` (`charness.run_plan_envelope.v1`,
stamped by `build_envelope`). Skill structure (`adapter`, `artifact`, `mode`,
`on_demand_reads`, `phase_barriers`, `lens_brief`, ...) stays as extensions —
the envelope unifies vocabulary, it does not flatten real per-skill shape.

## How A Planner Uses It

Load the lib with the uniform snippet (the existing
`SimpleNamespace(**runpy.run_path(...))` bootstrap idiom):

```python
ENVELOPE = SimpleNamespace(
    **runpy.run_path(
        str(Path(__file__).resolve().parents[3] / "shared" / "scripts" / "run_plan_envelope.py")
    )
)
```

For a planner at `.../skills/<skill>/scripts/<planner>.py`, `parents[3]` is the
skills container root in both the source tree and the exported plugin mirror —
the same portable scheme gather uses (as `SCRIPT_DIR.parents[2]`) to reach
`support/web-fetch`. Build items with `ENVELOPE.read(...)`,
`ENVELOPE.gate_packet(...)`, `ENVELOPE.next_action(...)`, then assemble and
self-validate the payload with `ENVELOPE.build_envelope(...)`, passing
`schema_version`, the three vocabulary lists, and any skill `**extensions`:

```python
return ENVELOPE.build_envelope(
    schema_version="myskill.run_plan.v1",
    required_reads=reads,
    next_action=action,
    gate_packets=packets,
    repo_root=str(repo_root),  # any skill-specific extension rides through
)
```

## Linear Skills

A skill with no real branching briefing decision uses
`ENVELOPE.build_linear_envelope(...)`: `required_reads` + one fixed
`next_action` + (optionally empty) `gate_packets`, and NO fabricated
mode/branch fields. Do not cargo-cult branches a skill does not have
(Floor-Addition Restraint); a planner on a skill with no briefing decision is
boilerplate that adds concepts.

## Why A Validator, Not A New Floor

`build_envelope` calls `validate_envelope`, which raises `EnvelopeError` on a
non-canonical payload. This is a correctness check on planner *output* (a
type-check that replaces seven ad hoc shapes with one), not a new
closeout/commit gate or a new authoring field an operator satisfies by hand — it
lowers contract weight rather than raising it.
