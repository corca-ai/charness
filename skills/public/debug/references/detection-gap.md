# Detection Gap

`debug` step 6 (resolve and preserve the learning) walks the structural cause
through the existing detection surface to find which gate did not fire and the
smallest change that would have fired it. The scaffold seeds the shape
(`surface | what did not fire | smallest change to fire it`); this reference owns
the depth — how to enumerate surfaces, classify the gap, and choose the
prevention move.

`debug` is callable directly when no GitHub issue exists; bug-class
`issue resolve` invokes the same substrate through
`../../issue/references/causal-review.md` Lens 2 without re-deriving this body.

## Enumerate detection surfaces

Bug-class incidents reach `debug` because some detection surface failed. Walk the
existing surfaces and name the failure mode against each one: which tests, gates,
lints, type checks, or evals existed but did not fire; what would have had to
change for them to fire (a different assertion, fixture, or sample — the smaller
the change, the more the gap is a missing invariant than missing scope); whether
monitoring or runtime observability would have surfaced this and was absent or
noisy; whether a human-only review path is the only realistic detection (flag
those honestly). Produce a short list with `file:line` evidence per surface and
map the chosen move to the artifact `## Prevention` section.

## Common shapes

- **missing invariant** — a single-line assertion change would have caught it
- **missing scope** — a fixture or input class was not sampled
- **noisy observability** — the signal existed but was buried in noise
- **human-only detection** — the failure class is judgment-bound and an automated
  gate would either over-fire or miss the real concern

## Trivial-bug short-circuit

When the fix is a single-file typo, rename, or comment correction with no
plausible automated gate, record `n/a — trivial fix` and keep going —
scope-bounded and reviewer-visible, not a default escape.

## Over-reach check

State the simplest evidence that the listed gap is real, not "no test exists in
this corner." A detection gap that names a surface but cannot describe the
smallest change to fire it is usually over-reach.
