# Adapter Contract

`find-skills` is local-first by default, but hosts can widen the discovery
surface without forking the skill body.

## Required Fields

- `version`
- `repo`
- `language`
- `output_dir`

## Optional Fields

- `preset_id`
- `preset_version`
- `customized_from`
- `official_skill_roots`
  - additional skill roots the host treats as trusted official inventory
  - a downstream host can point this at its official skill directory
- `prefer_local_first`
  - keep local `charness` skills ahead of official roots
- `allow_external_registry`
  - whether a generic external skill ecosystem can be proposed at all

## Default Behavior

Without an adapter, `find-skills` should:

- search local public skills
- search local support skills
- search local integration manifests
- classify the remaining gap honestly

Without host approval, it should not pretend that a generic external skill
registry is part of the harness.

## Official Skill Roots

Official skill roots are not the same thing as local public skills.

Use them when:

- the current host ships an official skill pack outside `charness`
- that pack is still part of the trusted workflow surface
- the host wants `find-skills` to discover it before proposing new work

Do not use them to turn random third-party folders into first-class shipped
capabilities.
