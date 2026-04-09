# Verification Ladder

Use the strongest honest verification capability that is reasonably available.

## Capability-Seeking Rule

Do not anchor on one kind of verification.

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
- if a branch matters to user-visible behavior, symbol existence is not enough
- if stronger verification needs setup or permission, ask for it explicitly
- when a check is missing, add the smallest one that prevents the branch from
  going unproven

## Closeout

At the end of the slice, state:

- what was verified directly
- what capability was used to verify it
- what stronger verification was unavailable and why
- what remains unverified
