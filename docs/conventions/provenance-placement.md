# Provenance-Placement Policy

Standing/contract docs state the **timeless rule**. Provenance — *why* a rule
exists, *when* it was added, *which* incident drove it — lives in the **record
layer**, not the rule body. This doc owns where provenance goes; the portable
check `check_standing_doc_provenance.py` (a `quality` capability) enforces it so
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

Dates age and issue numbers couple a standing rule to mutable tracker state
(issues close, renumber). A reader opening a contract should learn the current
rule, not wade through incident history.

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

The policy does **not** blanket-strip refs. Two doc classes:

- **Standing-rule docs** — their job is to state timeless rules/contracts (the
  docs linked from `AGENTS.md`/`CLAUDE.md` as the rule layer, e.g.
  [operating-contract.md](./operating-contract.md),
  [implementation-discipline.md](./implementation-discipline.md),
  [authoring-preflight.md](./authoring-preflight.md),
  [prescribed-skill-closeout-contract.md](../prescribed-skill-closeout-contract.md)).
  Here, dates / multiple issue refs in rule prose are the smell to fix.
- **Tracking docs** — their content *is* a ledger; the refs are load-bearing
  (e.g. [support-tool-followup.md](../support-tool-followup.md),
  [deferred-decisions.md](../deferred-decisions.md),
  [product-success-metrics.md](../product-success-metrics.md),
  [artifact-policy.md](../artifact-policy.md)). These are **allowlisted**.
- **Record-layer artifacts** — `retro/*`, `debug/*`, `*/latest.md`,
  `charness-artifacts/*`. These *are* the provenance home and are never scanned.

## Enforcement

The portable check is config-driven through the **quality adapter**
(`<repo-root>/.agents/quality-adapter.yaml`), block `standing_doc_provenance`:

- `standing_docs`: explicit globs of the rule docs to scan;
- `tracking_allowlist`: globs excluded even when a `standing_docs` glob matches
  them;
- `inline_allow_marker`: a per-line escape hatch (default
  `provenance-allow`) for a genuinely load-bearing line that must keep a date or
  second ref — visible, not silent.

Empty `standing_docs` makes the check inert (stack-neutral default), so a
consuming repo opts in by listing its own rule docs. Run it with:

```bash
python3 skills/public/quality/scripts/check_standing_doc_provenance.py --repo-root .
```

It generalizes the skill-package anchor gate
(`skill_text_quality_lib.py`: `ISSUE_ANCHOR_RE`, `DATED_INCIDENT_RE`) to standing
docs; see [the quality reference](../../skills/public/quality/references/standing-doc-provenance.md).
