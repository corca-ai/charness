# Unreachable-File Denominator Sweep

Date: 2026-08-04
Class: **shipped prose asserts a file the reader can reach, and the reader
cannot** — the class [#477](https://github.com/corca-ai/charness/issues/477) and
[#478](https://github.com/corca-ai/charness/issues/478) were sub-forms of, filed
as [#479](https://github.com/corca-ai/charness/issues/479).

Every prior pass reported an honest "0 remaining" and was wrong because its
ruler was narrower than the class. This sweep states the ruler beside every
count, so the next reader can tell a real zero from a narrow one.

## The Ruler

- **Corpus:** 510 markdown files — `README.md`, `AGENTS.md`, `docs/**`,
  `presets/**`, `profiles/**`, `skills/**`, `plugins/**`.
- **The blocking gate's corpus for comparison:** `check_doc_links.py`'s
  `DOC_GLOBS` covers the same set **minus `plugins/**`**. 236 of the 510 files
  (46%) are in the shipped mirror and are scanned by no link gate at all —
  taken 2026-08-04 from `check_doc_links.py`'s `DOC_GLOBS`. (Stated as the
  constant name, not a line range: the first draft cited `:24-33` and this
  goal's own import edits shifted it the same day. A line number is a reference
  that rots, which is the class this file is about.)
- **Reader position:** a consumer who has installed `plugins/charness/`, whose
  tree contains the plugin package and nothing above it.

## Counts, With Their Denominators

| Axis | Ruler | Count (2026-08-04) | #479's count (2026-08-02) | Why they differ |
| --- | --- | --- | --- | --- |
| A1 — relative markdown links in `plugins/**/*.md` that do not resolve for a consumer | 236 mirror files; link resolved from the doc, then required to stay inside `plugins/<pkg>/` **and** exist | **12** (11 escape the plugin root, 1 resolves inside it to a nonexistent path) | 11 | the 12th is a *kind-flattening* miss, not an escape: `plugins/charness/shared/references/agent-assessment-invariant.md` links `../../public/hitl/scripts/check_chunk_contract.py`, but the exporter flattens to `skills/hitl/`. An escape-only ruler cannot see it. |
| A2 — prose asserting a file is `authoring-repo-internal` while spelling it with the consumer's `<repo-root>/` prefix | 510 files; **two-line window**, because this prose wraps | **6 source + 6 mirror** | 5 | #479's ruler was line-anchored. 3 of the 6 put `authoring-repo-internal` on one line and `<repo-root>/` on the next, so a single-line grep reported 2 where 6 live. A line-anchored ruler cannot report that it is line-anchored. |
| A3 — `<repo-root>/skills/<kind>/…` in portable skill docs (wrong tree *and* wrong layout — installed is kind-flattened to `<plugin>/skills/<skill>/`) | `skills/**/*.md` only; `docs/**` sites are excluded because `<repo-root>` in an authoring-repo doc denotes this repo, where the path resolves | **4** | 4 | agreement |
| A4 — backticked `scripts/<name>` in a portable skill doc that does not resolve inside its own skill package | `skills/**/*.md`; resolved against `skills/<kind>/<skill>/scripts/` | **30** | 2 | #479 counted only the two it had read. **This axis is judgment-bearing, not a defect count** — see below. |

## A4 Is Not a Defect Count, and That Is the Point

A bare `scripts/run-quality.sh` in a portable skill doc is ambiguous by
construction: it may name *the consuming repo's own* `scripts/`, which is
legitimate and is the whole reason `<repo-root>/` exists. Only a subset of the
30 are defects. Turning A4 into a blocking rule would ship exactly the failure
the previous run had to retract — a gate refusing legitimate references, with
"false positives are structurally impossible" written next to it.

So A4 routes to #479's per-instance disposition table, not to a gate. A1 and A2
are the two axes where the property is decidable without judgment, and they are
the two this goal INTENDS to arm.

## Arming Status, Stated Separately From Intent

A bounded review of the first slice caught this file claiming both were armed
while only one was — the same narrow-claim failure the sweep exists to prevent,
one level up. So the status is its own table, and it says what has SHIPPED:

| Axis | Gate | Live instances |
| --- | --- | --- |
| A1 | **ARMED** — `check_plugin_doc_links.py`, blocking, wired into `run-quality.sh`, the commit-time plan, and `quality-core.yml` | 0 remaining (12 repaired) — see the ruler note below |
| A2 | **ARMED** — `iter_authoring_repo_contradictions` in `check_doc_links.py`, sentence-scoped, blocking | 0 remaining (6 source + 6 mirror repaired) |
| A3 | **ARMED** — `check_plugin_dir_references.py` resolves `<plugin-dir>/` against the generated package and refuses the kind-flattened `skills/public/…` spelling, which IS the A3 defect | 0 remaining (4 repaired via the D50 adoption) |
| A4 | **ARMED** — `unmarked-tree` in `check_doc_links.py`; the rule existed and was switched off inside portable packages | 0 remaining (~70 repaired: 49 + 21 after the `.agents/` prefix bug was fixed) |
| A5 | **NOT RULED** — the same defect in COMMAND carrier | **14 live** (see below) |
| A6 | **NOT RULED** — shipped non-markdown assets | **2 confirmed live** (see below) |
| A7 | **NOT RULED** — `skills/shared/**` is not a portable package | prevention gap; 2 residue sites |

**This table was WRONG until 2026-08-04, in the direction that manufactures a
false zero.** A3 and A4 were armed and their sites repaired, and this table still
said "not gated / 29 live". A future enumerator reading it would have re-repaired
a population that no longer existed while the genuinely unruled axes stayed
unnamed. That is the fourth honest zero in this lineage, and it happened INSIDE
the artifact built to prevent it — one axis over from the A2 instance a claims
review had already caught. Corrected by the delegated resolution critique before
[#479](https://github.com/corca-ai/charness/issues/479) was closed.

## The Three Axes That Still Have No Ruler

Named here rather than left for the next widening to rediscover. Each is
in-class, each is a DENOMINATOR miss, and each has its own issue.

- **A5 — command carrier.** `python3 skills/public/<skill>/scripts/x.py` in a
  shipped doc. Every armed gate is green on it: `unmarked-tree` drops any
  backtick span containing whitespace, and `iter_unresolved_command_targets`
  resolves against the AUTHORING tree, where the path exists. The installed file
  is at `<plugin-dir>/skills/<skill>/scripts/x.py`. **14 live sites**, exemplar
  `skills/public/critique/references/prepare-packet.md:23`. This is the most
  action-bearing spelling: a consumer EXECUTES it.
- **A6 — shipped non-markdown.** The corpus below is 510 MARKDOWN files. Every
  gate globs `*.md`, so shipped `.json`/`.yaml` assets are unenumerated.
  `plugins/charness/integrations/tools/vulture.json:91` and
  `plugins/charness/skills/achieve/adapter.example.yaml:9` both carry it, and the
  second is worse than prose: it is a TEMPLATE a consumer copies into their own
  adapter and runs.
- **A7 — `skills/shared/**` is not a portable package.**
  `PORTABLE_SKILL_KINDS = {"public", "support"}`, so the A4 rule, the
  portable-absolute rule, and `validate_link`'s portable-escape branch are all
  structurally off for 18 shipped files. Small residue today; an open prevention
  gap for the next author.

**A4 moved 30 → 29 for a reason, not by a re-count.** `skills/support/README.md:26`
was in both populations: it named `scripts/sync_support.py` inside a markdown
link that ALSO escaped the plugin root, so it was an A1 instance and an A4
candidate at once. Slice B's A1 repair rewrote it to `<authoring-repo>/`, which
removed it from A4 as a side effect. The remaining 29 all name a script that
exists at `scripts/<name>` in this repo — which is what makes the axis
judgment-bearing rather than decidable, since a consuming repo may have its own.

**The A1 `12` and the A1 `0` were taken with different rulers, and the difference
is stated rather than hidden.** The `12` came from a fence-blind, whole-text
sweep. The `0` is measured by the armed gate, which skips fenced blocks and HTML
comments (a doc TEACHING the broken shape must be able to show it). So the `0`
sits under a ruler that is narrower in one direction and wider in three others:
the gate also catches prose-wrapped links, mismatched `~~~`/``` ``` `` fence
markers, and live text after a mid-line `-->`, all three of which a round-2
bounded review proved the first implementation missed. Checked at the time of
writing: no file in `plugins/**/*.md` has a relative link inside a fence or a
comment, so the two rulers return the same answer on today's tree. That is a fact
about today's tree, not a guarantee that they always agree.

## Non-Claim

These counts are a static, read-only sweep. They report which references cannot
**resolve** for a consumer at the given reader position; they do not prove any
named script would fail at runtime if reached another way, and they do not prove
the class is exhausted. A1 and A2 grew when the ruler widened, which is evidence
about the ruler, not about the tree. The honest claim is that the ruler is now
wider than it was — not that it is wide enough.
