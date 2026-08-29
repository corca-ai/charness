# Quality Review
Date: 2026-08-30

Title: One class, nine instances — the declaration-intersection sweep

## Scope

Target boundary: the reviewed-input declaration path. After `#759`, the operator
asked why the sibling pattern surfaced only by accident and directed a sweep. The
class: **two individually-correct rules whose intersection makes a legitimate
input undeclarable, or two components answering "what is the reviewed input"
differently.**

Ambient repo findings: three defects of the same class that I introduced while
repairing it, each caught by a channel other than my own review.

## Surface Contract Review

- semantic coverage: observed — five lenses, each verified against a git fixture.
- surface: what enters the identity, and whether narrative and binding agree.
- owner: `reviewed_input_identity.py` and `reviewed_input_verification.py`.
- projections: refusal codes, reviewed_paths/reviewed_content, rendered sections.
- state scope: throwaway `/tmp` fixtures; the charness tree read-only.
- transitions: seven repairs, one module split, one deliberate non-repair.
- proof boundary: every finding reproduced by running the code, not reading it.
- unexamined axes: the retro packet path, non-critique `surfaces_lib` consumers.

## Current Gates

Ten agents, five lenses, adversarial verification. **8 confirmed, 0 refuted.**
Zero refutations is itself a caution, so two were re-reproduced by hand.

| # | instance | severity | disposition |
| --- | --- | --- | --- |
| 1 | deletions in a committed range (`#759`) | high | fixed earlier |
| 2 | `a...b` split naively → `rev-parse .feature` traceback | high | fixed |
| 3 | `core.quotepath` — narrative C-quoted, binding raw | high | fixed |
| 4 | merge commit — identity 0 paths, section 2 | high | fixed |
| 5 | staged-add-then-delete bound nothing | high | fixed |
| 6 | submodule bump undeclarable in EITHER substrate | high | fixed |
| 7 | `--all` never reached the zero-path refusal | high | fixed |
| 8 | pointer retarget did not stale a verdict | high | fixed |
| 9 | exec bit absent from ref per-path hash | medium | NOT fixed |
| 10 | committed packet in range vs exactness | medium | policy |

### The four root causes

Nine instances collapse into four:

- **No single owner for "enumerate changed paths."** `_auto_paths` and
  `surfaces_lib` ran different git invocations: `-z` (#3), `-m` (#4), staged arm
  (#5). Aligning the flags closed three at once.
- **Range syntax parsed twice, incompatibly.** `_auto_paths` handed the string to
  git; `_patch_components` did `split("..", 1)` — two functions in ONE module
  disagreeing about their own input (#2).
- **Boundary enforcement conditional on substrate.** `_review_paths` skips
  `_checked_path` under `changed_ref`, so one `CLAUDE.md` is `captured` in ref
  mode and refused in working-tree mode (#6, #9).
- **A correct disable taking an unrelated rule with it.** `--all` turns currency
  off for a real reason — historical bindings are stale by design — but "covers
  zero paths" is not a currency question (#7).

### Why this surfaced only now

I repaired `#759` as a SYMPTOM — "deletions in committed-ref mode" — instead of
characterizing the class. Naming the class first makes the opening move obvious:
diff the git invocations of every path-enumerating function, which is exactly
what found #3, #4 and #5. The repo's own Sibling Search discipline exists for
this; I skipped it.

### Three instances I created while repairing the class

Recorded as evidence about method:

1. **Excluded EVERY symlink from the sweep.** `CLAUDE.md` is a tracked
   compatibility symlink needing the operator's approval to retarget, and
   `auto_excluded_paths` is never digested — so a retarget could not stale a
   verdict. *Caught by the reviewer.*
2. **Asserted a blanket symlink refusal** committed-ref mode does not perform.
   *Caught by the reviewer, proved against a real commit.*
3. **Aliased a callable at import time**, making the owner non-authoritative
   under monkeypatch. *Caught by an existing test.*

None was caught by my own review — the honest answer to "why only now". This is a
class I do not reliably self-detect, which is why the two reviewer `block`
verdicts were the load-bearing signal here rather than friction.

### The deliberate non-repair

**#9, exec bit.** In ref mode the per-path `content_sha256` does not move on a
chmod-only commit; `identity_sha256` does, via the patch hash, so detection is
not bypassed. Folding mode into the per-path hash would change EVERY ref-mode
identity ever captured and read as `stale` corpus-wide — a false alarm across the
whole record to fix a field another field already covers.

## Runtime Signals

- runtime source: timing capture is missing; no structured metrics collected.
  Wall-clock only: ten agents in ~407s; each gate run ~117s.
- runtime hot spots: none introduced.
- coverage gate: no changed-line or mutation verdict is claimed.
- evaluator depth: five verified lenses, two hand re-reproductions, two
  fresh-eye rounds.

## Healthy

The reviewer blocked twice and was right both times, on work I had already
convinced myself was done.

## Weak

Zero refutations across ten agents is weak evidence of verifier skepticism, not
strong evidence of finder precision. Two were re-checked by hand; six rest on the
agents' own fixtures.

The `latest.md` predicate is still a basename proxy, not an adapter-resolved
pointer path. Binding the payload rather than excluding it makes a
misclassification benign, but the proxy remains.

## Missing

No gate asserts the two path enumerators agree. They were aligned by hand, and
nothing stops them drifting again — which is how three of these started.

## Deferred

- A shared owner for path enumeration, with a test that both callers agree.
- Instance #10: a committed critique packet inside a reviewed range. An exact
  declaration exists (explicit manifest, range binding kept), so it is a policy
  call rather than a defect.

## Advisory

- `python3 scripts/check_code_lengths.py --repo-root .` forced the module split.
  The boundary is production vs verification, and it is load-bearing: the shipped
  reviewer runtime loads these files BY PATH, so production must stay a leaf.

## Delegated Review

- status: executed — two `code-critique` rounds against `67555154e` and
  `ac6e74a04`; both returned `block`, all five findings reproduced and repaired.

## Commands Run

Five-lens sweep with adversarial verification; hand re-reproduction of the
triple-dot and `core.quotepath` instances; fixture probes for merge,
staged-delete, submodule, pointer retarget; `./scripts/run-quality.sh --full`.

## Recommended Next Quality Moves

- active land the seven repairs and the split; the gate is green and all five
  reviewer findings are answered.
- passive because it needs its own evidence: build the enumerator-agreement gate
  before another enumeration site is added.

## History

- [2026-07-14 quality review](history/2026-07-14-open-issue-resolution-proof.md)
