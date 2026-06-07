# Standing-Doc Provenance Check

A portable `quality` capability that enforces the **provenance-placement
policy**: standing/contract-rule docs state the timeless rule and keep
provenance terse, so a reader opening a contract learns the current rule instead
of wading through incident history. This reference is the portable description
of the policy the skill ships; charness states the same policy in its
authoring-repo-internal `docs/conventions/provenance-placement.md`.

## Why It Exists

Good provenance culture drifts when issue numbers and ISO dates land in rule
prose. Dates age; issue numbers couple a standing rule to mutable tracker state.
The originating issue / RCA belongs in the record layer (`retro/*`, the RCA
ledger, `debug/*`) with at most one link from the standing doc. This generalizes
the skill-package anchor gate (`skill_text_quality_lib.py`: `ISSUE_ANCHOR_RE`,
`DATED_INCIDENT_RE`) — which already bans issue-anchors / dated-incidents in
skill *package* prose — to standing *docs*, with a standing-vs-tracking
allowlist. It reuses those regexes rather than re-deriving them.

## The Rule It Enforces

A scanned line of a configured standing doc is flagged when it carries:

- an ISO date `20\d{2}-\d{2}-\d{2}` (`standing_doc_date`), OR
- two or more issue refs (`standing_doc_multiple_issue_refs`), OR
- a dated-incident phrase (`standing_doc_dated_incident`).

A single load-bearing trailing `(#NNN)` with no date does **not** flag — that is
the supported way to keep provenance that points the reader at the mechanism the
rule enforces. Fenced code blocks and lines carrying the inline-allow marker are
skipped.

## Configuration

The check is config-driven through the quality adapter
(`.agents/quality-adapter.yaml`), block `standing_doc_provenance`:

- `standing_docs` — globs of the standing-rule docs to scan. **Empty → inert**
  (stack-neutral default; a consuming repo opts in by listing its rule docs).
- `tracking_allowlist` — globs excluded even when a `standing_docs` glob matches
  them. Tracking ledgers (follow-up / deferred-decisions / metrics) go here.
- `inline_allow_marker` — per-line escape-hatch substring (default
  `provenance-allow`).

## Running It

```bash
python3 skills/public/quality/scripts/check_standing_doc_provenance.py --repo-root . --json
```

Exit 0 when clean or inert (opted out); exit 1 on a flagged line or an invalid
adapter (it fails closed — errors surface in the JSON and on stderr). The JSON
shape is
`{ok, adapter_errors, adapter_path, scanned, findings, inert}`; each finding is
`{path, line, heuristics, excerpt}`.

## Standing vs Tracking

| Class | Examples | Provenance in rule prose? |
| --- | --- | --- |
| Standing-rule (scan) | `operating-contract.md`, `implementation-discipline.md`, `authoring-preflight.md`, `prescribed-skill-closeout-contract.md` | dates / multiple refs = the smell |
| Tracking (allowlist) | `support-tool-followup.md`, `deferred-decisions.md`, `product-success-metrics.md`, `artifact-policy.md` | refs are load-bearing → allowed |
| Record layer (never scanned) | `retro/*`, `debug/*`, `*/latest.md`, `charness-artifacts/*` | this *is* the provenance home |

## See Also

- `docs/conventions/provenance-placement.md` — charness's authoring-repo-internal
  statement of this policy (this reference is the portable copy that ships).
- `skill_text_quality_lib.py` — the reused anchor/dated-incident regexes.
- `adapter-contract.md` — the full `standing_doc_provenance` field list.
