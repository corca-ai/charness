## Three closeout gates got stricter and can refuse work that passed on 2.11.2

This is a patch release, but it can turn a green repo red with no change of your
own. All three tightenings fix gates that were reporting PASS over something they
had not established, on the boundary where a wrong answer closes a real GitHub
issue. Each has a one-line remedy.

**1. A bare `N/A` is now a placeholder, like `TBD` always was.**
The placeholder set declared `n/a` all along, but the value was normalized before
the comparison in a way that made that entry unreachable — so an entire closeout
ledger of `N/A` passed every floor. Write a real value, or a dismissal *with a
reason*: `N/A — issue was context only` still passes. Only the bare token is
refused.

**2. A blocked-critique signal needs at least 20 characters that you wrote.**
The skill prepends the `host-blocked-subagent:` head itself — 23 characters — and
those were paying down the 40-character floor, so a 17-character excuse was
enough to skip a mandatory fresh-eye critique. The floor now measures only your
text. **This is a shared predicate**: it applies to `achieve` goal `complete`
flips and `publish_release --critique-blocked`, not just issue closes. It can
also fire retroactively — an existing goal artifact whose skip reason cleared 40
total with a short detail will fail the next time it is re-checked.

**3. The word `Answer:` no longer infers the floor-exempt `question` class.**
Any staged issue artifact containing `Answer:` or `decision:` anywhere — a quoted
log, a prose sentence — was classified `question`, which switches off the
behavioral-verdict, AI-provenance and resolution-critique floors entirely. That
exemption is now reachable only by declaring `Classification: question` (or
`decision-needed`) explicitly. An artifact that does not is checked as a `bug`
and owes the full bug ledger. The failure output now names the classification it
checked against and tells you how to declare one.

## What the critique-skip fix does and does not buy

**A fluent excuse of sufficient length still passes, and no length floor can
refuse one.** The enum head on that carrier is manufactured by the caller, so the
enum check validates a constant and cannot be fixed at this layer. What changed
is that a skipped critique is no longer byte-identical to an executed one: every
issue carrier now emits a non-blocking `REVIEW: … was SKIPPED` line naming the
recorded host signal. Whether that skip was honest remains a human judgment.
The bug-hunt record carries this as `FIXED (narrowed)`, not closed.

One thing loosened, deliberately: `Source origin: N/A` now reads as "no external
source" and is exempt from the source-preservation forms, where it previously
failed. That floor uses the same predicate as a gate-*opener*, and demanding a
preservation form for a source that does not exist forced fabrication.

## Why this is a patch and not a major

The version policy says a debatable bump must be argued rather than defaulted, so:
all three tightenings move behavior *toward* the already-documented contract
rather than changing a public shape. The placeholder set already declared `n/a`;
the enum-plus-length skip contract is unchanged and only *which characters count*
moved; and nobody was ever told that the word `Answer:` earns a floor exemption —
that was an accident. No command, flag, path, skill id, or evidence-line grammar
changed. A false PASS on an irreversible boundary is a defect, and refusing the
input that produced it is the fix, not a contract change.

The honest argument against: a downstream repo can go red on update, and the
remedy is a human editing prose. If that is disruptive for you, the three remedies
above are each a single line.

## Also in this release

- Deletion-only and rename-only staged commits now schedule the same commit-boundary
  gates a modification does (previously zero gates were planned).
- The provenance guard no longer exempts the in-repo plugin tree as `same-tree`,
  and no longer discards a non-empty drift list when the entry script is absent.
- Empty-scope gates (`validate_packaging`, export-safe imports, bootstrap-shim
  consistency, critique-artifact paths) no longer report PASS over a zero-file scan.
- Author-facing shape describers now render enforced floors from the live
  constants instead of restating them.

## Non-claims

- The publish carrier's own distinct-channel and installed-readback verification
  are known-unproven at this version (reproduced defects D4/D6/D8 in the
  evidence-surface bug hunt): the HTTP probe confirms on any 200 with a non-empty
  body without checking content, and the installed readback records `observed` on
  exit code alone without comparing the version read back. These claims were
  equally unearned in 2.11.2; this release does not improve them.
- 20 of the 30 reproduced evidence-surface defects remain open, including the
  release-claim cluster.
