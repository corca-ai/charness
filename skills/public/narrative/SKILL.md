---
name: narrative
description: "Use when a repo's source-of-truth docs and current product or project story need to be aligned together. Tighten the durable narrative first, then derive one audience-neutral brief skeleton when a compressed handoff artifact would help."
---

# Narrative

Use this when the repo already has a product, project, or operating story, but
that story needs to be created, realigned, or compressed into one portable
brief skeleton without leaving the durable docs behind.

`narrative` is one public concept:

- map the current source-of-truth surface
- surface contradictions, stale assumptions, and missing decisions
- rewrite the durable docs so the current story is honest in one place
- derive one audience-neutral brief skeleton from that aligned story when
  useful

Borrow Barbara Minto-style structure when compressing a repo story: lead with
the governing idea, group supporting points cleanly, and order the document so
the reader can recover the argument without reverse-engineering it.

If the idea is still under-shaped, use `ideation` first. If the docs are
already aligned and the user mainly wants audience adaptation or delivery-ready
wording, use
`announcement`.
If the repo has little or no durable truth surface yet, use `init-repo` to
bootstrap that surface before treating the task as narrative alignment.
If the target is a high-leverage truth surface and the repo-specific narrative
contract is still missing, shape or scaffold the adapter before rewriting in
earnest instead of letting fallback inference silently stand in for repo truth.

## Bootstrap

Resolve the adapter first.

```bash
python3 "$SKILL_DIR/scripts/resolve_adapter.py" --repo-root .
```

Default durable artifact:

- [`charness-artifacts/narrative/latest.md`](../../../charness-artifacts/narrative/latest.md)

What you get after one run:

- one aligned truth-surface artifact anchored to the repo's durable docs
- one audience-neutral brief skeleton that later delivery work can adapt

What this does not do:

- audience-specific adaptation or delivery transport; that belongs to `announcement`

If the repo would benefit from an explicit truth surface, scaffold an adapter:

```bash
python3 "$SKILL_DIR/scripts/init_adapter.py" --repo-root .
```

When rendered Markdown proof matters for README, landing pages, or durable
spec prose, surface the supported runtime recommendation before pretending raw
source review is enough:

```bash
python3 "$SKILL_DIR/scripts/list_tool_recommendations.py" --repo-root .
```

Then inspect current state:

```bash
sed -n '1,220p' charness-artifacts/narrative/latest.md 2>/dev/null || true
python3 "$SKILL_DIR/scripts/map_sources.py" --repo-root .
git status --short
```

## Workflow

1. Restate the narrative goal.
   - bootstrap a new durable story surface
   - realign stale source-of-truth docs
   - realign docs and also produce an audience-neutral brief skeleton
   - state the primary reader context before rewriting a first-touch surface;
     if the user wants delivery-local adaptation, keep that for `announcement`
2. Map the current truth surface.
   - read the source documents before inventing a fresh summary
   - check whether local context may be stale relative to git remote state
   - if freshness is ambiguous and the repo cannot be trusted as-is, surface
     that risk before editing
   - if the adapter is missing and the target is README, landing copy, operator
     docs, or another first-touch truth surface, stop to shape the truth
     surface and primary reader contract before rewriting in earnest
   - if the source map is effectively empty or only placeholder-level, stop and
     recommend `init-repo` rather than pretending there is already a narrative
     surface to align
3. Inventory intent before rewriting a high-leverage first-touch surface.
   - recover explicit intent from source docs, repo-local adapter guidance, and
     user-confirmed direction from the current thread
   - classify high-signal prior blocks as preserved, moved, compressed, or
     intentionally deleted
   - treat preserved meaning as the contract; headings and section order are
     flexible
4. Run the landing rewrite loop when the target is a high-leverage first-touch
   surface.
   - use `references/landing-rewrite-loop.md` for comparables, tension log,
     decision log, compression metric, opening-language filter, quick-start
     actor check, claim audit, self-premortem, and carry-forward review
   - if the work is really a cross-repo issue or proposal packet, use
     `references/cross-repo-issue-shaping.md` so `why` and `what` stay ahead
     of `how`
   - when rendered preview matters, surface the repo-owned install/verify path
     for `glow` before accepting degraded raw-Markdown review
   - resolve research/source-truth tensions before editing
   - keep a claim-to-acceptance/spec matrix before calling the rewrite done
5. Tighten the durable story first.
   - rewrite contradictions instead of layering parallel narratives
   - propagate user-confirmed direction changes into source-of-truth docs, not
     only into the brief
   - keep README, roadmap, handoff, operator docs, and adjacent maintainer docs
     consistent enough that the next session does not inherit drift
   - when the repo has multiple first-class use cases or the adapter declares
     `scenario_surfaces`, add short scenario blocks for the main use-case
     paths; use the relevant subset of `references/scenario-blocks.md` instead
     of forcing every slot
   - prefer checked-in fixtures, schemas, or example files over abstract prose
     when the block needs a concrete input example
   - if the docs coin product-local jargon, define it inline at first use
     instead of sending the reader to a later glossary
   - challenge internal terms that help maintainers more than readers, and
     define unavoidable product-local jargon at first use
   - when the repo identity depends on a few high-leverage concepts, prefer a
     compact concept table or concept list before a flat feature inventory
   - if the adapter carries quick-start execution guidance, respect who should
     actually act instead of assuming inline human CLI steps
   - when the repo is aligning around a non-trivial design decision, keep one
     short rejected-alternative or `Deliberately Not Doing` block in the
     durable docs instead of leaving that memory in chat or handoff only
6. Derive the brief second.
   - keep it audience-neutral by default
   - prefer one self-contained compression layer that `announcement` can later
     adapt for a concrete audience, language, tone, or channel
   - when the repo adapter declares `brief_template`, use that ordered skeleton
     instead of inventing a new brief shape in session
7. Show the aligned edits, claim audit, compression metric, and brief draft
   before any delivery action.
   - include a short carry-forward note for user-stated intents that were
     preserved, challenged, or left unresolved
8. Hand off to `announcement` only when the user explicitly wants human-facing
   adaptation or backend delivery after the narrative itself is aligned.

## Output Shape

The result should usually include:

- `Source Map`
- `Narrative Drift`
- `Updated Truth`
- `Brief`
- `Claim Audit`
- `Compression`
- `Carry-Forward`
- `Open Questions`
- `Next Step`

## Guardrails

- Do not use `narrative` as a substitute for `ideation` when the concept is
  still vague or upstream decisions are genuinely unresolved.
- Do not leave user-confirmed direction changes only in an ephemeral brief.
- Do not treat a stale handoff as the sole truth surface when git freshness
  suggests the repo may have moved.
- Do not collapse durable truth docs and audience-specific briefs into one file
  when their lifecycles differ.
- Do not mistake a cleaner outline for success when preserved intent was lost.
- Do not strip away the short "why not this other path" note when that note is
  what keeps the next reader from reopening the same design debate.
- Do not let audience, language, tone, or channel adaptation pull `narrative`
  into `announcement` territory.
- Do not let repo-local adapter hints harden into a global README template for
  every repo.
- Keep the brief portable enough that later audience adaptation does not require
  re-aligning the durable truth from scratch.
- If delivery backend execution is the only remaining task, prefer
  `announcement` rather than growing `narrative` into a transport skill.

## References

- `references/adapter-contract.md`
- `references/source-map.md`
- `references/brief-shape.md`
- `references/scenario-blocks.md`
- `references/landing-rewrite-loop.md`
- `references/cross-repo-issue-shaping.md`
- `scripts/map_sources.py`
