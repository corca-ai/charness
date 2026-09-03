# Docs Graph Checks: check_doc_links vs awiki

> Status: current
> Source of truth: this page and its linked executable surfaces
> Last verified: 2026-09-02

Two tools look at the same markdown and answer different questions. This page
says which, so neither is promoted, trusted, or retired on a guess about what the
other already covers.

Every row below was MEASURED against awiki 0.5.0 and this repo's own
[check_doc_links.py](../scripts/gates/check_doc_links.py), not read off either tool's
description. The reproductions are at the bottom; run them rather than trusting
this table.

## The one-sentence split

[`check_doc_links.py`](../scripts/gates/check_doc_links.py) asks **"does this reference resolve?"**, per link, and
refuses the ones that do not. `awiki lint` asks **"is this page reachable?"**,
per graph, and cannot see a broken link at all.

Neither is a superset of the other.

## Command-level matrix

| Question | [`check_doc_links.py`](../scripts/gates/check_doc_links.py) | `awiki lint -root docs -recursive` |
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

1. **Nothing else answers the connectivity question.** `orphans` and `islands`
   are barred at zero; [`check_doc_links.py`](../scripts/gates/check_doc_links.py)
   stays green on an unreachable page, because every link in it resolves.
2. **`link_only_lines` is gated too, at a ratchet above zero.** The gate judges
   a named metric against a bar, not awiki's exit code, which bundles every rule
   and cannot be selected down; the bar is the last row of the ratchet record
   below, which [check_docs_graph.py](../scripts/gates/check_docs_graph.py)
   reads. The console line renders awiki's findings exit as
   `OBSERVED [docs-graph-awiki]`, never `FAIL`, because the verdict is the
   gate's; a timeout or unknown exit code keeps the guard's `FAIL` line beside
   the gate's NOT-RUN verdict.
3. **The residual under that bar is hard-wrapped prose.**
   `awiki lint -root docs -recursive` prints the current count and it moves with
   every docs edit; recount rather than trust a number here. A reflow sweep
   across the docs tree is not the remedy, so the bar is sized to that remainder
   rather than to zero.

The gate must therefore SAY what it did not judge — link resolution, page
accuracy, and whether a counted link-only line is a bare link or wrapped prose —
and it must report NOT-RUN with a named reason when the binary is absent. An
unobserved orphan count is not zero.

## The `link_only_lines` ratchet record

The bar may only ever decrease.
[check_docs_graph.py](../scripts/gates/check_docs_graph.py) reads the last row of
the table under this heading through `ratchet_rows`; an absent, unreadable, or
rising record falls to `DEFAULT_LINK_ONLY_LINES_BAR` (`0`), so a consuming repo
without its own record refuses every context-free link line rather than
inheriting this one.
[test_docs_graph_gate.py](../tests/test_docs_graph_gate.py) asserts against the
rows the gate parses. Raising the bar therefore means appending a row here,
editing that test, and getting past the gate's own refusal.
`--link-only-lines-bar` is a per-run probe that bypasses the record and leaves no
history; calibration means recording a row, not passing the flag.

| date | bar | why it moved |
| --- | --- | --- |
| 2026-08-15 | 167 | First bar. Every list entry whose link line carried no descriptor was repaired; the remainder is the hard-wrapped-prose population this rule over-reports on, and the bar is sized to it. [How it was measured](../charness-artifacts/quality/2026-09-03-docs-graph-founding-bar.md). |

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
