# Deployable Skill Packaging

When a skill is meant to ship through a Claude or Codex plugin bundle, the
skill body is not the whole product contract.

Keep these layers separate:

- public skill: user-facing trigger, concept boundary, and degradation behavior
- support skill or integration manifest: owned runtime capability metadata and
  setup/readiness seams
- plugin packaging: manifest layout, exported directories, marketplace entries,
  and host-visible discovery surface
- owning CLI: install, update, doctor, reset, and structured machine state

## What To Prove

For a deployable skill, prove these separately:

- source package exists and validates
- exported plugin tree contains the skill in the expected host-facing path
- host-visible payload change is actually observable after the documented host
  refresh step

Do not treat “the source checkout changed” as proof that the installed host
copy changed.

## Claude And Codex Lessons

- Claude and Codex both consume plugin packaging, not raw `skills/public`
  directories.
- A skill addition, removal, or description change is useful as a probe only
  when it becomes visible in the installed host copy.
- The owning CLI or packaging contract should record whether the host-visible
  copy matched the exported source, rather than forcing the public skill body
  to describe lifecycle recovery.

## Where The Contract Lives

Use `create-cli` when the repo owns:

- a bootstrap binary
- plugin install/update commands
- doctor or recovery state
- structured output that later agents read

Keep `create-skill` focused on the skill package boundary itself:

- is this one user-facing concept?
- does it stay portable after host behavior is removed?
- are runtime capabilities modeled in manifests instead of hidden prose?
