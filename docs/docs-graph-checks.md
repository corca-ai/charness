# Docs Graph Checks: check_doc_links vs awiki

> Status: current
> Source of truth: this page and its linked executable surfaces
> Last verified: 2026-09-02

Two tools look at the same markdown and answer different questions. This page
says which, so neither is promoted, trusted, or retired on a guess about what the
other already covers.

Every row below was MEASURED against awiki 0.5.0 and this repo's own
[check_doc_links.py](../scripts/check_doc_links.py), not read off either tool's
description. The reproductions are at the bottom; run them rather than trusting
this table.

## The one-sentence split

[`check_doc_links.py`](../scripts/check_doc_links.py) asks **"does this reference resolve?"**, per link, and
refuses the ones that do not. `awiki lint` asks **"is this page reachable?"**,
per graph, and cannot see a broken link at all.

Neither is a superset of the other, which is why the docs-graph question stayed
unanswered for as long as it did: the green gate was answering a different
question, honestly, and nobody was asking this one.

## Command-level matrix

| Question | [`check_doc_links.py`](../scripts/check_doc_links.py) | `awiki lint -root docs -recursive` |
| --- | --- | --- |
| Does a markdown link resolve to a real file? | **YES — hard fail.** `broken relative link` | **NO.** Reports `ok` with a link to a page that does not exist. Surfaced only by the separate `awiki wanted`, and framed as a page you might want to create rather than as an error. |
| Is the link form right (`./` prefix, no absolute paths)? | **YES — hard fail.** | No opinion. |
| Is a repo path backticked instead of linked? | **YES — hard fail**, with a reason tag (`pathy`, `prefix`, `unique-basename`, `unmarked-tree`, `portable-absolute`). | No opinion. |
| Does a documented command name a script that exists? | **YES — hard fail**, in fences and inline spans alike. | No opinion. A hypothetical `scripts/<name>.py` is outside its model because it only treats Markdown pages inside its root as wiki pages. |
| Is a page reachable from the rest of the docs? | **NO.** It validates each link where it is written; reachability is never computed. | **YES — hard fail.** `orphans=N`, and names each page. |
| Is a cluster of pages cut off from the main component? | **NO.** | **YES — hard fail.** `islands=N`, plus `largest_component_ratio`. |
| Is a page an empty stub? | No opinion. | **Metric only.** `content_coverage` drops; lint still reports `ok`. |
| Does a link line carry local context? | No opinion. | **Hard fail** on `link_only_lines`, evaluated per PHYSICAL line — so hard-wrapped prose trips it. |
| What is covered? | [the repo readme](../README.md), `AGENTS.md`, `docs/**`, `presets/**`, `profiles/**`, and the portable skill packages. | `docs/**` only, as passed via `-root`. |

## What this means for the gate

The repo gates on NAMED METRICS against declared bars, and never on awiki's exit
code. Three points, all measured:

1. **Nothing else answers the connectivity question.** Before the docs index hub
   existed, seven pages were unreachable while [`check_doc_links.py`](../scripts/check_doc_links.py) was green —
   correctly green, because every link in the repo resolved. That is the exact
   shape of a gate reporting a verdict it never observed, and it is why awiki is
   worth a lane of its own rather than being folded into the existing one.
   `orphans` and `islands` are barred at zero.
2. **`link_only_lines` is gated too, at a RATCHET above zero.** This reverses a
   decision this page used to record and no longer contains — that the rule was
   "worth pursuing" but that adopting it "is not what this gate is for" — and the
   test that pinned it, `test_link_only_lines_alone_do_not_fail_the_gate`, whose
   retraction is written out by name in
   [test_docs_graph_gate.py](../tests/test_docs_graph_gate.py). What changed is the instrument, not the
   measurement: adopting the rule then meant adopting awiki's exit code, which
   bundles every rule it has and cannot be selected down. A named metric judged
   against a bar takes the count without the exit code, and can sit above zero
   where the rule over-reports. The bar is a required value that may only ever
   decrease; since S6 it lives in the ratchet record below, which
   [check_docs_graph.py](../scripts/check_docs_graph.py) reads.
3. **The residual under that bar is the wrapping population, and the sweep
   decision still stands.** Recount rather than trusting a number here —
   `awiki lint -root docs -recursive` prints it and it moves with every docs
   edit. Measured 2026-08-09, roughly three-fifths of the findings were this
   repo's own 80-column prose wrapping putting a link alone on a physical line.
   Re-measured 2026-08-15 — by reading each flagged source line, which is a
   different question from the count and is not corroborated by it — the
   wrapping share was nearer two-thirds. The list entries whose link line
   carried no descriptor were rewritten to carry one. The wrapped-prose
   remainder was NOT: a reflow sweep across the whole docs tree is still not the
   way, and the bar is sized to that remainder rather than to zero.

The gate must therefore SAY what it did not judge — link resolution, page
accuracy, and whether a counted link-only line is a bare link or wrapped prose —
and it must report NOT-RUN with a named reason when the binary is absent. An
unobserved orphan count is not zero.

## The `link_only_lines` ratchet record

The bar may only ever decrease. That sentence lived only in prose, which made the
cheapest repair for a red lane "edit one three-digit literal" — the exact
zero-work move the release contract's Fixed Decision names. This table is the
second surface.

**This record is now the bar's only home (S6, 2026-08-15).**
[check_docs_graph.py](../scripts/check_docs_graph.py) READS the last row below
rather than carrying its own literal, through `ratchet_rows`; when no record is
present it falls to `DEFAULT_LINK_ONLY_LINES_BAR`, which is `0`. That matters
because the gate is exported to consuming repos and this page is not: before the
change, installing charness handed a repo a threshold measured on charness's own
80-column docs tree, with neither this record nor the test that ratchets it, and
nothing said so. Absence now falls to the STRICT side —
a repo with no record refuses every context-free link line rather than inheriting
a foreign allowance.

**"May only ever decrease" is enforced by the GATE, not only by the test.**
`ratchet_rows` refuses the whole record when its bars are not non-increasing, so
the rule travels with the exported artifact. That is what makes this change a net
strengthening for a consuming repo rather than a weakening: without it, sourcing
the bar from a consumer-controlled file while leaving monotonicity to a
non-exported test would let a consumer append an increasing row and go green with
nothing red anywhere in what they installed. A round-1 reviewer found exactly
that gap in the first version of this change.
[test_docs_graph_gate.py](../tests/test_docs_graph_gate.py) then asserts against
the rows the gate itself parses — the founding row's date and value are
unchanged, the gate's resolved bar equals the LAST row, an increasing record is
refused, and no bar constant is bound in the exported module besides the `0`
default.

It is a speed bump, not a proof. Stated precisely, because the first version of
this paragraph over-claimed and a round-2 reviewer measured the gap: an author
can still raise the bar by appending a row here and editing the test that refuses
it. Since S6 they must also get past the gate's own monotonicity refusal, so a
raise now means editing the gate as well — the same three-surface cost as before
the bar moved into this record, and for a consuming repo it is two surfaces where
it used to be a regenerated literal. `--link-only-lines-bar` remains a per-run
probe that bypasses all of it and leaves no history; that is deliberate, and it
is why calibration means recording a row rather than passing the flag. What the
founding-row anchor buys is that the record must be APPENDED to rather than
rewritten, so a raise cannot be a quiet in-place edit of the only row present.

### How this repo's founding bar was measured

Moved here from a comment in the exported gate (S6): a number measured on one
docs tree has no meaning in a file every consuming repo installs.

Measured 2026-08-15. ONE observer: `awiki lint -root docs -recursive` reported
`link_only_lines=255` — the field the bar is compared against, not the bundled
finding total, which is a different number whenever another rule fires. An
earlier draft of this description called that two channels agreeing, counting the
gate's own parse of the same stdout as a second one. It is the same observer read
twice, which is what P4 in the [design north star](./design-north-star.md)
refuses, and it was caught in review rather than by anything executable.

The split came from reading each flagged source line, which awiki's summary does
not report and cannot corroborate:

- 88 were list entries whose link line carried no descriptor — 83 bare, and 5
  more whose descriptor had wrapped onto the following line, which reads fine to a
  human and still leaves a physical line that is only a link. Every one was
  repaired.
- 167 were links that landed alone on a physical line inside ordinary wrapped
  prose, and they are what the bar allows.

Both populations are scoped to what awiki flagged, which is measured by
construction. That a list entry whose only link is an external URL falls outside
both is INFERRED from awiki modelling markdown pages inside its root, and is not
separately reproduced: reading what was flagged cannot establish what would not
be.

| date | bar | why it moved |
| --- | --- | --- |
| 2026-08-15 | 167 | First bar. Every list entry whose link line carried no descriptor was repaired; the remainder is the hard-wrapped-prose population this rule over-reports on, and the bar is sized to it. |

## Reproductions

Run these from anywhere; they build their own throwaway wiki under `/tmp`.

The brackets are built from `$LB`/`$RB` on purpose. This repo's own link gate
validates markdown links INSIDE fenced blocks too — deliberately, so a
documented example cannot outlive the file it names — and these fixtures link to
files that must NOT exist. Writing the brackets literally here would make this
page fail the very gate it is describing.

```bash
LB='['; RB=']'
mkdir -p /tmp/p/docs && cd /tmp/p
printf "# A\n\nSee ${LB}B${RB}(./b.md) and a ${LB}missing page${RB}(./nope.md) here.\n" > docs/a.md
printf "# B\n\nBack to ${LB}A${RB}(./a.md) for context.\n" > docs/b.md

# 1. A broken link does NOT fail lint. It is only visible via `wanted`.
awiki lint -root docs -recursive     # ok connected_graph
awiki wanted -root docs -recursive   # reports the missing page as WANTED, not broken

# 2. An empty stub lowers a metric but still passes.
printf '# Stub\n' > docs/stub.md
printf "\nA ${LB}stub${RB}(./stub.md) link from A.\n" >> docs/a.md
awiki lint -root docs -recursive     # ok, content_coverage=0.6667

# 3. A disconnected pair DOES fail.
printf "# I1\n\nSee ${LB}I2${RB}(./i2.md) for more.\n" > docs/i1.md
printf "# I2\n\nBack to ${LB}I1${RB}(./i1.md) again.\n" > docs/i2.md
awiki lint -root docs -recursive     # lint_failed islands=1 ratio=0.6000
```

## Not claimed

- These are black-box observations of awiki 0.5.0. Its source was not read, and a
  version bump can change any row — the summary line it prints is not a declared
  stable interface, which
  [the integration manifest](../integrations/tools/awiki.json) already records.
- "No opinion" means the tool does not answer that question, not that the
  question does not matter.
- Reachability is not accuracy. A fully connected docs graph says nothing about
  whether any page is correct or current.
