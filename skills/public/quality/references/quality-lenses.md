# Quality Lenses

`quality` uses four lenses.

## Concept

Use a concept-integrity lens:

- stable concepts
- ownership honesty
- source-of-truth clarity
- doc-to-runtime synchronization
- duplicate documentation that creates competing sources of truth
- skill trigger-contract honesty when the repo authors skills

Boundary note:

- `quality` should catch duplicated or drifting concept surfaces when they are
  already visible in docs, gates, or runtime seams
- a deeper question like "should these be two concepts at all?" still belongs
  to concept-integrity analysis, not only duplicate detection
- ask what structural simplification is missing before reaching for a new
  heuristic or threshold
- treat length, duplicate, and pressure findings as prompts to ask what
  structural simplification is missing: deletion, merge, ownership split,
  helper extraction, or interface narrowing

## Behavior

Use a behavior-confidence lens:

- behavior-facing assertions
- failure-path confidence
- low-signal or gameable checks
- duplicate-pressure and missing seam coverage
- helper scripts that actually prove the skill can cold-start and resolve its
  adapter seams
- code-reduction-first: if a confidence gap can be closed either by shrinking
  production branches/interfaces or by adding more tests, prefer the smaller
  production surface first when it preserves behavior
- bounded test-ratio posture: a lower bound to prevent test-surface collapse
  and an upper bound to prevent quality work from defaulting to ever-growing
  test code; count executable spec surface separately when the repo uses it
- focused-gate evidence drift: after helpers or tests move to cleaner seam
  files, verify focused coverage gates, changed-file routers, and smoke maps
  still point at the new evidence
- authority-only belief check: repeated practices, conventional advice, or
  expert-sounding claims should not pass as behavior evidence unless a
  repo-local gate, source pointer, or measured observation supports them
- gate-last posture: when a confidence gap can be closed either by structural
  simplification or a new heuristic, prefer the simpler design first unless a
  standing invariant still needs enforcement afterward

## Security

Borrow from `security-audit` and broader review practice:

- dependency and supply-chain posture
- secret handling
- risky trust boundaries
- CI and setup safety assumptions

## Operability

Check whether the quality bar can actually be maintained:

- local setup honesty
- CI gate realism
- maintenance burden
- runtime drift for standing lint, test, eval, or quality commands
- useful diagnostics or logs that appear early enough for operators and agents
- drift between claimed and runnable commands
- retention and rotation for long-lived logs or machine-readable diagnostics
- refactor pressure from copied helper seams or skill-package drift
- duplicated documentation that should collapse into one maintained surface
- adapter-driven local enforcement as a positive pattern: checked-in hook
  config, repo-owned installer/checker, and repo-owned binary install path when
  the gate depends on extra tools

## Named Expert Defaults

Use named experts only when they sharpen the next quality move.

- W. Edwards Deming: is the repo measuring the system it is trying to improve,
  or only inspecting output after the fact?
- Charity Majors: does the current bar fail early and emit diagnostics that a
  maintainer can actually use under time pressure?
- Kent Beck: are fast lower-layer checks carrying enough change-safety load, or
  are slow broad checks covering for weak local feedback?
- John Ousterhout: is quality complexity hiding design complexity, copied
  helpers, or avoidable interface sprawl?
