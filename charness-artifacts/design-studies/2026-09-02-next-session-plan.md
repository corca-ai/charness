# Next-session plan: consumer-facing defects first, then the surfaces that let them sit

> Written at the close of the 2026-08-29 session, with the operator.
> Supersedes `2026-09-01-next-session-plan.md`, whose Step 1, Step 3, and every
> deferred handoff it inherited are now closed.

## Read this FIRST, and read the files, not this summary

This plan cites inputs. **Open them before planning.** The single largest waste of
the last session was re-deriving measurements, decisions, and a fully-diagnosed
follow-up that a prior retro already held, because the plan named its inputs in
prose and prose citation is not a mechanism. If you find yourself measuring
something, grep the retro corpus for it first.

Required opens, in this order:

1. `charness-artifacts/retro/purpose-and-the-unread-input.md` — the last session's
   retro. Its `Waste`, `Sibling Search`, and `Next Improvements` are this plan's
   backing.
2. `charness-artifacts/retro/2026-08-29-detector-blind-class.md` — the retro
   BEFORE that. Read it too: last session skipped it and paid for it.
3. `docs/design-north-star.md` — specifically the `Purpose` section, which is new.
   Every item below is ranked by it.
4. `charness-artifacts/retro/recent-lessons.md` — but know its limit: it sources
   24 of 419 corpus files and did NOT pick up the retro written minutes before
   this plan. Do not treat it as the corpus.

The ranking rule, from the north star's Purpose: **charness exists to reduce
rework in the repositories that CONSUME it.** A defect a consumer hits outranks a
defect this checkout hits, however green this checkout measures.

## Step 1 — The consumer-facing open issues

These are ranked above everything else because a consumer meets them. Check each
against code before believing its text; two of last session's severity readings
changed on contact.

- **#755 — reviewer capability non-claim digest invalidates delivery.** Filed
  from Ceal against 8.0.0: every reviewer returned substantive bounded-review
  JSON and delivery was rejected anyway, because model-authored
  `capability_non_claims` provenance had to match a launch envelope exactly. This
  is the consumer-facing shape of the class the last session spent itself on — a
  mechanism refusing on a question the worker was never able to answer. Highest
  rank: it blocks a paying path end-to-end, three times, on a canonical mode with
  no customization.
- **#750 — retro adapter cannot opt out of the recent-lessons projection.**
  `resolve_adapter.py:62` fills the default unconditionally, so a consumer repo
  cannot decline a surface it does not want. Small, and consumer-facing.
- **#731 — bounded-review friction; partial worker progress is not first-class.**
  Related to #755 in surface and in feel. Read them together before designing
  either.

## Step 2 — Read the inventory this session produced, then disposition it

`skills/public/quality/scripts/inventory_empty_scope_honesty.py --summary` reports
per detector what it says when it establishes nothing. Today: 129 detectors, 42
refuse, 48 are honest in prose only, 2 carry a machine-readable marker, 13 assert
success over a scope they never established, 16 could not be probed.

**The deliverable of Step 2 is a disposition of those 13**, not a new gate. For
each: is this the sanctioned discovered-empty pass, or the defect? The repo already
forbids this exact shape on one gate (`check_code_lengths`'s named arm) and
permits it on that same gate's discovered arm, so the answer is per-detector
judgment, not a sweep.

An inventory nobody reads is the cost the Purpose clause names. If Step 2 does not
happen, delete the inventory rather than keep it.

## Step 3 — The prose-honesty gate, per the operator's design

`check_regenerable_facts` is configured for `docs/**`, exempts nothing relevant,
runs clean, and misses. Its detector is *digit + space + an enumerated noun*.
Measured against five real phrasings from `docs/design-north-star.md`: one hit,
four misses — spelled-out numerals, unit suffixes (`17.6K lines`), hyphenated
compounds (`5.8K-test suite`), and nouns outside the list all pass.

The operator's design, to be built rather than re-litigated:

> The detector is heuristic. Accept false negatives. Surface it as a **pre-commit
> ADVISORY** on changes to `AGENTS.md`, `README.md`, and `docs/**/*.md`, and let
> an agent judge the flagged text against the warning's own stated rule, rather
> than widening the regex.

Do not widen the noun list. That is the enumeration this repo's own P3 rejects,
inside the gate that enforces prose honesty, on the page where P3 is written.

## Step 4 — Two carry-forward surfaces that failed while being used

Both found while persisting the last retro. Both are small and both cost real
work when they fire.

- **The retro scaffold and the persist helper disagree about the path.** The
  scaffold checks a DATED artifact path; the helper writes an UNDATED one. The
  scaffold reported the target empty, the helper overwrote a tracked retro from
  another session, and only a `git status` read caught it. One subject key, two
  paths.
- **`recent-lessons.md` did not pick up a retro persisted minutes earlier** — not
  in a slot, not even in `Sources` (419 corpus files, 24 sourced). This is the one
  surface routed to a session start. Whether the selection policy is wrong or the
  harvest is, a same-day retro whose subject is "the last session's output went
  unread" not reaching the digest is the failure mode stated twice over.

## Step 5 — The release, if the above leaves room

8.0.0 remains prepared and unpushed; the hole the last plan named before it
(`_publish_and_finalize`) is closed — the closeout tail is now covered through the
path a release actually takes. 100+ commits are unpushed. This is deliberately
LAST: none of it is consumer-facing until it ships, and shipping it on top of
#755 would ship a known blocked review path.

## Deliberately not in this session

- **#748 / #749 / #744, the Rust migration.** The advantageous conversions are
  done; four Python owners deleted. The three that remain are Python for recorded
  reasons — consumer contract, measured-slower, and an acceptance bullet that
  requires Python. Do not reopen without a NEW measurement.
- **#753.** Untouched last session and not consumer-facing.
- **Arming anything built last session.** The Rust changed-line floor and the
  empty-scope inventory both ship unarmed on purpose. Arming is its own decision
  with its own evidence; the ratio-cap entry in the corpus is what happens
  otherwise.

## Working shape

- Consumer-facing repairs go to Codex lanes; the parent owns design, integration,
  and final verification.
- **Build `--scope` from a real search, not `ls <dir> | grep`.** Two of three
  lanes last session returned `invalid` because a needed test file lived in a
  subdirectory the scope never listed.
- **Run the FULL standing lane, including `--include-release-only`, before
  calling a production-surface change done.** It caught three violations last
  session that focused runs did not: a cross-module private import, a polyglot
  constant needing a boundary marker, and a skill-ownership overlap.
- Any proposal containing "faster / smaller / cheaper" carries its measurement in
  the same message.
- Before optimising a mechanism, ask what it is FOR. That question has been the
  operator's intervention in each of the last two sessions.
- `plugins/` is untracked. The mirror is regenerated by `charness init`/`update`
  and by the release version bump — NOT by pre-push. Regenerate derived surfaces
  after the last source edit:
  `python3 scripts/sync_root_plugin_manifests.py --repo-root .` and
  `./charness catalog refresh --repo-root .`.
