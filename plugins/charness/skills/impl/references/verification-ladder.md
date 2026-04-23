# Verification Ladder

Use the strongest honest verification capability that is reasonably available.

## Capability-Seeking Rule

Do not anchor on one kind of verification.

Start by surveying the repo's best available self-verification tools:

- adapter-defined preferred tools
- installed support skills
- local binaries and CLIs
- repo-local scripts, fixtures, and harnesses

When the task is shaped as review, evaluation, closeout, an operator reading
test, `검증`, `평가`, or `리뷰`, query `find-skills` for validation
recommendations before treating same-agent/manual review as the best available
path.

Actively look for the best available way to prove the slice, including:

- local tests
- support skills
- integration tools or external binaries
- CLI or API checks
- browser paths
- evals or scenarios
- read-only reasoning only when stronger proof is genuinely unavailable

## Browser-Facing Output

For HTML, CSS, static reports, screenshots, browser-readable artifacts, or UI
surfaces, code-level checks and fixture renders are partial proof by default.
Prefer a real browser/runtime pass when a host or support seam exists. If that
capability may be hidden behind support-skill discovery, route through
`find-skills` before improvising local search or stopping at tests.

If an equivalent local browser seam is used instead, name it explicitly. If no
browser/runtime pass ran, say the UI or rendered surface was not visually
verified.

## Rules

- prefer executed proof over a claim whenever an executable path exists
- when UI, rendered artifacts, screenshots, or browser paths matter, inspect a
  real render if a browser path exists
- when validation-shaped review or closeout work matters, use the validation
  recommendation route before settling for same-agent manual review
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
- whether code/fixture, browser/runtime, and evaluator-backed proof did or did
  not run when relevant
- what stronger verification was unavailable and why
- what remains unverified
