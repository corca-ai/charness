# Premortem — Slice B: Issues #130 and #131 (Doc/Spec Rename Lens)

Date: 2026-05-09
Decisions under review:

- **#130** — `premortem` `references/angle-selection.md` adds a new
  `first-reader` angle covering plain-language reading path,
  legacy-coupled negative phrasing, product-story-before-taxonomy, and
  title-slug coherence sub-lenses. New trigger paragraph fires the angle
  when the decision changes durable docs, spec indexes, public skill prose,
  README-like surfaces, or source-of-truth narrative, and references the
  deterministic checker for the title-slug lens.
- **#131** — new `scripts/check_title_slug_drift.py` deterministic checker
  that flags Markdown files whose H1 title content words have zero
  intersection with the filename slug content words. Skips structural single-
  word H1s like `Problem`/`Decision`/`Spec` and structural slugs like
  `SKILL`/`README`/`AGENTS`/`CONFIG`/`CLAUDE`/`INDEX`/`MAIN`. Default roots:
  `docs/specs/` and `charness-artifacts/spec/`; `--include-skill-prose`
  expands coverage; `--strict` exits 1 when drift is detected.
- The script is surfaced as a `quality` `AUTO_CANDIDATE` example
  recommendation in `proposal-flow.md` and as deterministic evidence under
  the `first-reader` angle in `angle-selection.md`.

## Success Criteria

- `find_drift` flags the cautilus-style rename failure mode (title `How The
  Views Relate` vs slug `projection-contract.spec.md`) without flagging
  aligned files (`names-and-keys.spec.md`/`Names And Keys`).
- Default scope on the real repo reports zero drift (25 spec files clean).
- `--include-skill-prose` reports zero drift on the real `skills/` tree
  thanks to the structural-slug skip-list.
- `angle-selection.md` triggers the `first-reader` angle on the five named
  surfaces and references the script as deterministic evidence.

## Out of Scope

- CI / pre-push wiring of `--strict`. Helper ships as advisory + quality
  recommendation; locking the heuristic into a hard gate before dogfooding
  on a real rename event would freeze its current edge cases as failures.
- Speculative `STRUCTURAL_H1` additions like `Status`/`Changelog`/`Notes`/
  `Goals`/`Non-Goals`. The zero-intersection guard already passes when a
  slug shares the heading word; speculative entries are gold-plating.
- H1+H2 mismatch and duplicated concept-home page detection — covered by
  the prose lens, not by the deterministic checker.
- Wiring the checker into `docs/`-wide and `AGENTS.md`-style coverage —
  current default scope is the right initial blast radius.

## Angles + Counterweight

Bounded angle subagent + counterweight delegated to the parent task agent
under the repo `Subagent Delegation` clause. Triage:

- **Act Before Ship**: none.
- **Bundle Anyway**: structural-slug skip-list (`SKILL`/`README`/`CONFIG`/
  `AGENTS`/`CLAUDE`/`INDEX`/`MAIN`) so `--include-skill-prose` is honest;
  bundled in this slice, drops 25 false positives to zero on the real
  skill tree.
- **Over-Worry**: angle overlap with `customer-of-this-capability` and
  `future maintainer` (the four sub-lenses are concrete enough that
  reviewers will not collapse them); structural-H1 list shortness (zero-
  intersection guard already passes when slug shares the heading word);
  heuristic crudeness vs broader cautilus problem set (explicit non-goal).
- **Valid but Defer**: CI/pre-push wiring of `--strict`; speculative
  structural-H1 entries; broader `docs/`-wide coverage. Recorded for a
  future slice after dogfooding on a real rename event.

## Recurrence Prevention

- 10 deterministic tests cover detection (cautilus-style drift), false-
  positive avoidance (aligned title/slug, structural H1, structural slug,
  no-H1 files), CLI behavior (`--strict` exit 1, default advisory exit 0),
  and citation chain (angle-selection lists the lens, references the
  script; proposal-flow lists the script as a recommendation example).
- Premortem prose lens covers the structural drift cases (legacy-coupled
  negative phrasing, product-story-before-taxonomy) the deterministic
  checker cannot mechanize.
