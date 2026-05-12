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

Ask one more question before calling the gate local:

> Does this local or pre-push gate hide network, external-repo fetch, latest
> release, or supply-chain refresh work that should be an explicit refresh,
> update, or release action instead?

Acceptable answers:

- a checked-in `pre-push` hook (or equivalent Husky, simple-git-hooks,
  lefthook, or `core.hooksPath` wiring) plus a deterministic validator that
  proves the current clone uses it
- an explicit documented decision that hooks are intentionally not part of the
  quality bar, with a named owner for the CI-side enforcement
- a repo-owned installer or onboarding step that provably wires the hook in

If none of these hold, the gap is `missing`, not implicit.

The default local/pre-push gate should prove local invariants. Network,
external-repo fetch, and upstream freshness work should be explicit unless the
user's quality question is specifically about those external boundaries.

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

## CI/local gate parity

Maintainer-local enforcement closes "the local clone can push without running
the gate". `CI/local gate parity` closes the adjacent failure mode: the local
clone runs the gate, the CI workflow runs the same gate, **and** the CI
workflow appends required `run:` steps after the canonical gate that the
local gate graph does not enforce. The local gate stays green while CI fails
on a step that should have been part of the local bar.

This is an enforcement gap even when each individual step is healthy. If a
required CI step lives outside the canonical local gate, classify it as
`weak` or `missing` unless one of these holds:

- the step is also represented inside the canonical local gate (e.g., the
  step's `run:` line is also one of the phases that the local gate
  invokes);
- the step belongs to an explicit local release, update, or refresh gate
  that maintainers run before the corresponding operation; this is not a
  CI-only waiver, and the local command must be named in the repo contract;
- the step is setup or provisioning (e.g., `actions/checkout`,
  `actions/setup-*`, `npm ci`, `pip install`, package cache restore) rather
  than a required quality assertion.

Treat `CI-only`, `ci only`, and equivalent phrasing on quality gates as a
strong warning, not as documentation that makes the split acceptable. CI may
repeat local proof, but CI must not be the first place a required quality
failure can appear.

Use `skills/public/quality/scripts/inventory_ci_local_gate_parity.py` to
inventory parity. The helper takes `--workflow-glob`,
`--canonical-gate-pattern` (repeatable), and `--ci-only-marker` for detecting
forbidden CI-only language. With `--require-empty-parity-issues` it returns
exit 1 when any subsequent step is classified as `parity-issue` or
`ci-only-violation`, which is the right shape for a standing gate or pre-push
hook in repos where the parity contract is intentional.

The default canonical-gate patterns cover `npm run verify`, `make verify`,
`bash scripts/run-quality.sh`, `bash scripts/run-verify.{mjs,sh}`, and
`charness verify`. Repos with custom local-gate names should pass
`--canonical-gate-pattern` to surface their own shape.
