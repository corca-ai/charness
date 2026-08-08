# Docs Graph Checks: check_doc_links vs awiki

Two tools look at the same markdown and answer different questions. This page
says which, so neither is promoted, trusted, or retired on a guess about what the
other already covers.

Every row below was MEASURED against awiki 0.5.0 and this repo's own
[check_doc_links.py](../scripts/check_doc_links.py), not read off either tool's
description. The reproductions are at the bottom; run them rather than trusting
this table.

## The one-sentence split

`check_doc_links.py` asks **"does this reference resolve?"**, per link, and
refuses the ones that do not. `awiki lint` asks **"is this page reachable?"**,
per graph, and cannot see a broken link at all.

Neither is a superset of the other, which is why the docs-graph question stayed
unanswered for as long as it did: the green gate was answering a different
question, honestly, and nobody was asking this one.

## Command-level matrix

| Question | `check_doc_links.py` | `awiki lint -root docs -recursive` |
| --- | --- | --- |
| Does a markdown link resolve to a real file? | **YES — hard fail.** `broken relative link` | **NO.** Reports `ok` with a link to a page that does not exist. Surfaced only by the separate `awiki wanted`, and framed as a page you might want to create rather than as an error. |
| Is the link form right (`./` prefix, no absolute paths)? | **YES — hard fail.** | No opinion. |
| Is a repo path backticked instead of linked? | **YES — hard fail**, with a reason tag (`pathy`, `prefix`, `unique-basename`, `unmarked-tree`, `portable-absolute`). | No opinion. |
| Does a documented command name a script that exists? | **YES — hard fail**, in fences and inline spans alike. | No opinion. Treats `../scripts/tool.py` as a wanted wiki page even when the file exists, because it only models markdown pages inside its root. |
| Is a page reachable from the rest of the docs? | **NO.** It validates each link where it is written; reachability is never computed. | **YES — hard fail.** `orphans=N`, and names each page. |
| Is a cluster of pages cut off from the main component? | **NO.** | **YES — hard fail.** `islands=N`, plus `largest_component_ratio`. |
| Is a page an empty stub? | No opinion. | **Metric only.** `content_coverage` drops; lint still reports `ok`. |
| Does a link line carry local context? | No opinion. | **Hard fail** on `link_only_lines`, evaluated per PHYSICAL line. |
| What is covered? | [the repo readme](../README.md), `AGENTS.md`, `docs/**`, `presets/**`, `profiles/**`, and the portable skill packages. | `docs/**` only, as passed via `-root`. |

## What this means for the gate

The repo gates on awiki's **connectivity** answer — `orphans` and `islands` — and
not on its exit code. Two reasons, both measured:

1. **The exit code is dominated by a rule we are not adopting yet.** It also
   fails on `link_only_lines`, of which this repo has 229. 139 of those are its
   own 80-column prose wrapping putting a link alone on a physical line, not
   context-free links. The rule is worth pursuing; a reflow sweep across 28 files
   is not the way, and it is not what this gate is for.
2. **Nothing else answers the connectivity question.** Before the docs index hub
   existed, seven pages were unreachable while `check_doc_links.py` was green —
   correctly green, because every link in the repo resolved. That is the exact
   shape of a gate reporting a verdict it never observed, and it is why awiki is
   worth a lane of its own rather than being folded into the existing one.

The gate must therefore SAY that it does not judge link-only style or link
resolution, and it must report NOT-RUN with a named reason when the binary is
absent. An unobserved orphan count is not zero.

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
