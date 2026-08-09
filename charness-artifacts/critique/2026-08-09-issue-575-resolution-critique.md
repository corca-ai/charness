# Issue #575 resolution critique

Date: 2026-08-09
Classification: bug
Fresh-eye satisfaction: parent-delegated
Verdict: CLOSABLE after the round-1 blocker was repaired.

## What #575 asked for

`regenerable_facts_lib.py` carried a comment asserting that dated-record
directories are "out of scope by nature", while `DEFAULT_SURFACES` right below it
included `docs/**/*.md` and swept every dated record under `docs/`. The gate was
registered in the consumer-facing catalog, armed by default, exit 1 on findings.
Measured with the shipped copy against five real consuming repos: 4 of 5 failed,
up to 52 findings, most of them historical records doing exactly what they should.
The job-to-be-done: decide whether the comment or the code is right, and stop
failing consumers for writing the numbers their records exist to carry.

## Delegated review — round 1: NOT-CLOSABLE

A bounded read-only fresh-eye subagent confirmed:

- The comment/code contradiction is gone: `regenerable_facts_lib.py:45-56` no
  longer claims a docs exclusion it does not have, and `DEFAULT_SURFACES` contains
  no docs glob.
- The repair is **FIXED, not merely HONEST**. The reviewer tested the strong
  refusal ("you turned exit 1 into exit 0 and printed a paragraph") and it fails on
  the facts: the canonical defaults are still scanned and still hard-fail
  (`test_findings_map_to_exit_one`), and the `NOT CONFIGURED FOR DOCS` branch is
  reachable **only when findings are empty**, so the non-verdict can never mask a
  verdict. What #575 complained about was a false negative-verdict; that verdict is
  now refused rather than rendered wrongly.
- The gate can still fire for a configured consumer, and that path is documented in
  `adapter-contract.md:546-583`, `adapter.example.yaml:160-186`, and
  `catalog.yaml:144-150`.
- charness itself did not go inert: `.agents/quality-adapter.yaml:743-783` declares
  `surfaces`, so this repo renders a real verdict, pinned by two tests that would
  fail on a vacuous green.
- Mirror parity and test adequacy both clean; defaults are regression-pinned
  (`docs/**/*.md` is asserted NOT to be a default).

Refused the close on one blocker:

- **BLOCKER** `skills/public/setup/references/default-surfaces.md:261-268` (and its
  mirror) still described PRE-repair behavior — it listed "the docs tree" among the
  default surfaces and told consumers "the defaults will match them and **fail
  you**". Both are now impossible. Worse, it steered the consumer's remedy toward
  narrowing `surfaces`, which `adapter-contract.md:566-571` documents as dropping
  `AGENTS.md`, `CLAUDE.md`, `README.md`, and skill prose out of scope — de-arming
  the one part of the gate that still renders a verdict for them. This is the same
  defect class #575 filed (a shipped assertion about a scope the code does not
  have), relocated one file over.

## Repair made in response

`default-surfaces.md` (and mirror) now states the current behavior: `docs/` is not
a default surface; an unconfigured docs tree is reported `NOT CONFIGURED FOR DOCS`
at exit 0, a typed no-verdict and never a clean claim; keeping retros or audits
under `docs/` does not fail the build; opting docs into the verdict means declaring
`regenerable_facts.surfaces` plus reasoned `exemptions`. The "narrow `surfaces`
until the noise stops" reflex is now explicitly named as wrong, with the reason.

Round 2 re-read the rewritten prose against the code claim-by-claim and found it
accurate, with one residual: a "Two things to check" heading over four bullets,
now corrected. Round-2 repairs are recorded as accepted-unreviewed per the
two-round cap.

## Behavioral verdict (channel distinct from CLOSED state and carrier body)

The shipped gate was re-run at HEAD against the same five external consuming repos
the issue measured — `../stdy.blog`, `../cmanki`, `../ceal`, `../ceal-cli`,
`../journal.stdy.blog`:

| repo | before (issue) | after |
| --- | --- | --- |
| `journal.stdy.blog` | exit 0, 0 findings | exit 0, `NOT CONFIGURED FOR DOCS` (3 checked / 6 unclassified) |
| `stdy.blog` | exit 1, 4 findings | exit 0, 3 checked / 18 unclassified |
| `cmanki` | exit 1, 11 findings | exit 0, 7 checked / 36 unclassified |
| `ceal-cli` | exit 1, 30 findings | exit 0, 3 checked / 40 unclassified |
| `ceal` | exit 1, 52 findings | exit 0, 3 checked / 253 unclassified |

Five external repositories are a channel distinct from the carrier body and from
`CLOSED` state. The observer is the same session that made the repair, not an
independent one; the reviewer judged evidence-channel distinctness satisfied and
observer-distinctness explicitly not claimed.

## Non-claims

- No checked-in artifact records the five-repo run beyond this critique; the
  numbers above are this record.
- No test covers the case where `declared=True` but the declared scope is narrower
  than the docs tree (a bare verdict with no scoping non-claim). That is a
  deliberate "the repo chose its scope" design, warned about in
  `adapter-contract.md:566-571`, and belongs to a different issue's class.
- Consumers keeping records under `docs/` are now **unjudged**, not proven clean.

AI-provenance: this critique and the repairs it records were authored by an agent
session; the bounded review rounds ran as separate read-only subagent contexts.

## Reviewer Tier Evidence

- Requested tier: `bounded-reviewer` (the repo's typed read-only subagent).
- Requested spawn fields: `subagent_type: bounded-reviewer`, prompt, synchronous
  return; deliberately no host addressing/team `name`, per the repo's spawn-shape rule.
- Host exposure state: host-defaulted
- Application state: n/a — no per-subagent model or effort override was requested, so
  the host had no such control to apply or report.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated

## Boundary Ownership

- Producer: the regenerable-facts gate and its default scope.
- Consumer: a consuming repo wiring the gate from the shipped catalog, guided by the
  `setup` default-surfaces reference.
- Owning surface: the gate owns what it judges; the wiring reference owns what it tells
  a consumer to expect, and it had drifted from the gate.
- Verdict: owned-correctly
