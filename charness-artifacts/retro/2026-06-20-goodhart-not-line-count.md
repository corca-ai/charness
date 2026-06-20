## Mode

session (bounded — single revealed miss)

## Context

After Phase 4 closeout, the operator corrected my framing: I described
"fewer lines / fewer gates" as a north-star *failure signature* in a way that
inverted into "more code = success," and I cited the net diff `+2138 / −83` as
**positive evidence** that the metric was "honored." That is backwards.

## Waste / The Miss

- I conflated two different things: the doctrine's **Goodhart warning** ("do not
  make *fewer gates* the TARGET you optimize — you will delete real guards to hit
  the number") with a false claim that **adding code is itself good**.
- I then used line-count *direction* (`+2138`) as evidence in a closeout
  disposition review. Line count is **orthogonal** to success and must not be
  cited as a virtue in either direction. A goal can add 2138 lines of bloat and
  still be bad; a goal can delete 500 lines and be excellent.
- The operator's principles (the correct lens): **capabilities over features**;
  for equal capability, **less code is better**; for equal code, **more open** and
  **declarative over procedural** is better.

## Critical Decision (re-evaluated through the correct lens)

The actual Phase-4 work mostly holds up — but for reasons I stated wrongly:

- **WS-3b(b-ii)** turned a hardcoded English regex (`apply/restart|deploy`) into
  **adapter-provided data with a default** — i.e. *procedural → declarative /
  data-driven*. That is genuinely the right direction (capabilities-over-features,
  declarative), and I *undersold* it by fixating on the line count instead.
- **WS-1/WS-2** ADD gates (presence floors). They are justified because they close
  real escapes with no guard lost — but "they added lines" is not the
  justification; "they closed an escape and stayed rung-1/minimal" is. I should
  also have actively asked "can these be smaller / more declarative?" rather than
  treating addition as neutral-good.

## Next Improvements

- **memory/judgment:** The success metric for this class of work is
  **escape-closed + no-guard-lost + concept clearer/more-portable/more-declarative**.
  **Never cite line-count direction as evidence** (up OR down). When reporting or
  reviewing, lead with the *capability* delta, not the diff size.
- **workflow:** Apply the operator's ordering as an active lens on every change:
  (1) fewer capabilities-equal features, (2) less code for equal capability,
  (3) more open, (4) declarative over procedural. Ask "could this be smaller or
  more declarative?" of every ADDED floor/gate, not only of deletions.
- The Goodhart point ("don't make fewer-gates a *target*") is real and stays —
  but it is a warning against *optimizing the proxy*, not a license to inflate.

## Sibling Search

n/a — trivial framing/judgment fix; no plausible code-sibling. The durable home is
the lesson above so the inverted-Goodhart framing does not recur.

## Persisted

(set by the persistence helper)
