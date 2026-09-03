# How this repo's founding `link_only_lines` bar was measured — moved verbatim from `docs/docs-graph-checks.md` on 2026-09-03.

Moved here from a comment in the exported gate (S6): a number measured on one
docs tree has no meaning in a file every consuming repo installs.

Measured 2026-08-15. ONE observer: `awiki lint -root docs -recursive` reported
`link_only_lines=255` — the field the bar is compared against, not the bundled
finding total, which is a different number whenever another rule fires. An
earlier draft of this description called that two channels agreeing, counting the
gate's own parse of the same stdout as a second one. It is the same observer read
twice, which is what P4 in the [design north star](../../docs/design-north-star.md)
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
