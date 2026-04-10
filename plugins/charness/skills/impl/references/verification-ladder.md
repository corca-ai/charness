# Verification Ladder

Use the strongest honest verification capability that is reasonably available.

## Capability-Seeking Rule

Do not anchor on one kind of verification.

Start by surveying the repo's best available self-verification tools:

- adapter-defined preferred tools
- installed support skills
- local binaries and CLIs
- repo-local scripts, fixtures, and harnesses

Actively look for the best available way to prove the slice, including:

- local tests
- support skills
- integration tools or external binaries
- CLI or API checks
- browser paths
- evals or scenarios
- read-only reasoning only when stronger proof is genuinely unavailable

## Rules

- prefer executed proof over a claim whenever an executable path exists
- when UI, rendered artifacts, screenshots, or browser paths matter, inspect a
  real render if a browser path exists
- when user-visible agent or tool invocation matters, run a real invocation if
  the repo exposes one
- if a branch matters to user-visible behavior, symbol existence is not enough
- if stronger verification needs setup or permission, ask for it explicitly
- if the repo has preferred verification tools configured but they are missing,
  propose installation or setup before silently downgrading the claim
- when a check is missing, add the smallest one that prevents the branch from
  going unproven

## Closeout

At the end of the slice, state:

- what was verified directly
- what capability was used to verify it
- what stronger verification was unavailable and why
- what remains unverified
