# Maintainer-Local Enforcement

This reference expands the SKILL.md rule that maintainer-local enforcement is
not optional when the repo depends on it. It exists because first-use quality
passes were stopping after they found one canonical final gate such as
`npm run verify` or `make verify`, without forcing an explicit judgment on how
that gate is actually enforced in maintainer clones.

## The bias to watch for

`quality` should not drift into the pattern where:

- the repo has one obvious final stop-before-finish command
- that command passes in the current clone
- there is no checked-in pre-push hook, no repo-owned hook installer, no clone
  validator that proves the hook is active, and no documented decision that
  hooks are intentionally omitted from the quality bar
- the quality artifact stays quiet about that gap

That shape is not "healthy posture". It is an enforcement gap that happens to
compile. Name it plainly.

## Forced question

When the repo has an obvious final stop-before-finish gate, ask one explicit
question before classifying anything as healthy:

> How is this enforced before push in maintainer clones?

Acceptable answers:

- a checked-in `pre-push` hook (or equivalent Husky, simple-git-hooks,
  lefthook, or `core.hooksPath` wiring) plus a deterministic validator that
  proves the current clone uses it
- an explicit documented decision that hooks are intentionally not part of the
  quality bar, with a named owner for the CI-side enforcement
- a repo-owned installer or onboarding step that provably wires the hook in

If none of these hold, the gap is `missing`, not implicit.

When all three exist together, treat that as a strong positive pattern:

- checked-in hook config
- repo-owned hook installer or clone validator
- repo-owned install path for extra quality binaries the local bar depends on

## Probe commands

Run these during `quality` bootstrap whenever the repo has, or is likely to
have, a canonical final local gate:

```bash
rg -n "pre-push|prepush|githook|githooks|core\.hooksPath|husky|simple-git-hooks|lefthook" .
git config --get core.hooksPath || true
find .git/hooks -maxdepth 1 -type f 2>/dev/null | sort
```

These are cheap and answer three questions at once:

1. does the repo ship any hook-related config, script, or docs
2. does the current clone point at a custom hook directory
3. what hooks are actually installed in this clone

Read the three answers together. A repo that ships `husky` config but whose
clone shows no files under `.git/hooks/` (or an empty `core.hooksPath`) is a
broken install, not a healthy gate.

## Classification rule

If the repo has one canonical final local gate such as `npm run verify`,
`make verify`, or an equivalent checked-in validation command, and there is
no repo-owned pre-push hook, hook installer/checker, or explicit documented
decision to omit local hook enforcement, classify that as `missing` rather
than leaving it implicit.

This rule applies even when the command itself is healthy and fast. The gap
is not the command; the gap is that maintainer clones can push without running
it.

## Automation promotion

When the missing enforcement is maintainer-local and repo-owned, prefer
implementing a checked-in hook plus a deterministic validator in the same turn
over leaving a prose recommendation. The smallest honest slice is usually:

- a checked-in `<repo-root>/scripts/hooks/pre-push` (or equivalent) that runs the final
  gate command
- a tiny Python or shell validator script that confirms the current clone's
  active hook matches the repo-owned one, runnable as part of `verify`
- a one-line note in the onboarding doc explaining how the hook gets wired

Leave it as a recommendation only when hook installation cannot be owned
honestly by the repo (for example, because maintainers deliberately run a
shared team tool that owns this concern).

When the repo already owns that full pattern, say so explicitly in the
artifact instead of only staying silent because no missing gap was found.

## Artifact output expectation

The durable quality artifact should carry one explicit field:

- `Maintainer-Local Enforcement`: whether the current clone is proven to use
  the checked-in final gate before push, whether that proof is missing, or
  whether hook omission is intentional documented policy

"Unclear" is not an acceptable value. If the state is unclear, the field value
is `missing` until the gap is either closed or explicitly deferred with a
reason.

## Operability wiring

When inspecting the `operability` lens, ask whether the repo's claimed final
local gate is actually wired into clone setup through a checked-in hook, a
repo-owned installer or checker, a CI parity note, or an explicit decision
not to do so. If none of those are true, the operability lens alone is enough
to classify the gap as `missing`.
