# Provenance-Placement Policy

> Status: current
> Source of truth: this page and its linked executable surfaces
> Last verified: 2026-09-04

Standing/contract docs state the **timeless rule**. Provenance — *why* a rule
exists, *when* it was added, *which* incident drove it — lives in the **record
layer**, not the rule body. This doc owns where provenance goes; the portable
check [`check_standing_doc_provenance.py`](../skills/public/quality/scripts/check_standing_doc_provenance.py) (a `quality` capability) enforces it so
consuming repos inherit the hygiene, not just charness.

## The Rule

In a standing/contract doc, a rule line:

- states the timeless rule first;
- carries originating provenance as a **terse trailing `(#NNN)` only when
  load-bearing** — the ref points the reader at the actual mechanism, test, or
  record the issue introduced and they would need it to act on the rule. **At
  most one ref per rule line.**
- otherwise carries **a single link** to the owning record artifact (`retro/*`,
  the RCA ledger, `debug/*`) instead of the provenance itself;
- **never** stacks dates or incident-names in the rule body. That diary noise
  moves to the record layer plus the one link above.

```text
# smell (stacked diary noise in a rule body):
Always sync the mirror before validators (added 2026-05-01 after #257, see also
the 2026-04 regression and #251 / #260).

# good (timeless rule + one load-bearing ref):
Always sync the mirror before validators; the pre-commit gate blocks the
staged-source/unstaged-mirror split (#257).

# good (provenance lives in the record layer, one link):
Always sync the mirror before validators. Background: retro/2026-05-01-mirror-drift.md.
```

## Standing-Rule Docs vs Tracking Docs

The policy does **not** blanket-strip refs. The doc classes, strictest first:

- **Exported reusable guidance** (`skills/public/**`, `skills/support/**`,
  `skills/shared/references/**`, generated
  [cli-reference](./cli-reference.md)) — no issue anchors and no charness
  self-version pins in prose at all; skill packages are held by
  `validate_skill_ergonomics`
  ([portable skill packages](./authoring-preflight.md#portable-skill-packages)),
  the rest by the advisory
  [`check_public_doc_coupling.py`](../tools/check_public_doc_coupling.py).
  External tool versions are not self-version pins.
- **Standing-rule docs** — their job is to state timeless rules/contracts (the
  docs linked from `AGENTS.md`/[`CLAUDE.md`](../CLAUDE.md) as the rule layer, e.g.
  [operating-contract.md](./operating-contract.md),
  [implementation-discipline.md](./implementation-discipline.md),
  [authoring-preflight.md](./authoring-preflight.md),
  [prescribed-skill-closeout-contract.md](./prescribed-skill-closeout-contract.md)).
  Here, dates / multiple issue refs in rule prose are the smell to fix.
- **Tracking docs** — their content *is* a ledger; the refs are load-bearing
  (e.g. [the deferred-decisions archive](../charness-artifacts/spec/2026-09-04-deferred-decisions-archive.md),
  [artifact-policy.md](./artifact-policy.md)). These are **allowlisted**.
- **Record-layer artifacts** — `retro/*`, `debug/*`, `*/latest.md`,
  `charness-artifacts/*`. These *are* the provenance home and are never scanned.

## Enforcement

Config-driven through the quality adapter's `standing_doc_provenance` block
(`standing_docs`, `tracking_allowlist`, `inline_allow_marker`);
[adapter-contract.md](../skills/public/quality/references/adapter-contract.md)
holds the field list. Empty `standing_docs` is inert, so a consuming repo opts
in. Run it with:

```bash
python3 skills/public/quality/scripts/check_standing_doc_provenance.py --repo-root .
```

Portable description:
[standing-doc-provenance.md](../skills/public/quality/references/standing-doc-provenance.md).
