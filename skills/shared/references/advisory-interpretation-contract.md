# Advisory Interpretation Contract

An **inference-layer** output — a heuristic, proxy, ranking, or trend, anything
whose number is a *sensor reading* rather than a verified fact — must not be
repeated to a reader as if it were a verdict. As deterministic heuristics improve
they get easier to defer to, and the agent's own intelligence quietly drops out
of the loop. This contract keeps the judgment in.

It generalizes two existing rules from passive prohibition into an active
requirement:

- `quality/references/automation-promotion.md`: "do not repeat an automated
  finding without repository-level interpretation."
- `shared/references/agent-assessment-invariant.md`: present the agent's own
  judgment before handing a decision off.

## Scope: inference layer only

This contract attaches ONLY to inference-layer outputs:

- clone/duplication percentages, ergonomics heuristics, test-economics trends,
  recommendation rankings, length/pressure smells, proxy scores.

It must NOT attach to **verifiable deterministic facts** — green gates, exact
counts, AST results, pass/fail validators. Inducing distrust in a verified fact
reintroduces the manual-ritual waste validators exist to remove, contradicting
"validator over prose ritual." If the output is a checkable fact, this contract
does not apply.

## The self-declaration (positive form)

An inference-layer output declares four things — about what it measures, not a
disclaimer about itself:

1. **measures** — the literal thing it counts or scores.
2. **proxy for** — the real concern the number stands in for.
3. **blind spots** — what the measure cannot see, where proxy and reality
   diverge (the most load-bearing field).
4. **interpretation question** — the one question the number cannot answer, that
   only repository judgment can.

This is NOT a blanket "distrust me" banner repeated on every output (which
habituates the reader into ignoring it and adds noise). It is a per-measure,
positive statement of blind spots and the open question.

## The consumer requirement

A skill that repeats an inference-layer output to a reader (e.g. `quality`
folding the `nose` advisory into a posture artifact) must **answer the declared
interpretation question first**, in its own words, against this repository —
before acting on, ranking, or escalating the number. Repeating the bare number
without answering is the exact failure this contract blocks.

The existing fresh-eye subagent review remains the real independent-intelligence
backstop; this contract feeds it an honest, pre-interpreted signal instead of a
raw proxy.

## Pilot

The `nose` clone advisory (`quality/scripts/inventory_nose_clones.py`) carries an
`interpretation` self-declaration: it measures lexical clone families, proxies
for refactorable duplication debt, is blind to intentional per-package
boilerplate (which inflates the line total), and cannot answer "which families
are intentional vs extractable?" — which the `quality` consumer answers per
repo before treating the total as debt. Rollout to the other inference-layer
surfaces is tracked as a separate issue.
