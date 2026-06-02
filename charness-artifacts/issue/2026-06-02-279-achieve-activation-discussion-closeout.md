# Issue Closeout: #279 Achieve Activation Discussion Closeout

JTBD: make `achieve` Before-phase closeout honest when activation discussion
items exist, so a user does not discover unresolved decisions only inside the
goal artifact after readiness is reported.

Classification: bug.

Root cause: the `achieve` contract encoded the deterministic floor
(`Discuss before activation:` summary exists) but not the human collaboration
obligation (discussion items are resolved or explicitly asked about before
readiness/activation is offered). The helper and prose used readiness language
that made `discussion_summary_present` look like discussion completion.

Debug artifact:
`charness-artifacts/debug/2026-06-02-279-achieve-activation-discussion-closeout.md`

Siblings: helper JSON output, `charness goal check` wrapper output,
Before-phase closeout guidance, lifecycle reference guidance, and dogfood
scenario review. Decision: bundle helper warning, prose guidance, CLI wrapper
test, and dogfood evidence because they are one interface contract; no live Ceal
replay is claimed. Proof: focused helper/prose/CLI tests and slice closeout
rehearsal pass.

Prevention: keep "discussion surfaced" separate from "discussion resolved" in
helper output, public skill guidance, and CLI wrapper tests, so future operators
cannot treat a present summary as permission to skip transcript discussion.

Critique: charness-artifacts/critique/2026-06-02-279-achieve-activation-discussion-closeout.md

Close #279.

Evidence:

- Goal artifact:
  `charness-artifacts/goals/2026-06-02-279-achieve-activation-discussion-closeout.md`
- Carrier artifact:
  `charness-artifacts/issue/2026-06-02-279-achieve-activation-discussion-closeout.md`
- Debug artifact:
  `charness-artifacts/debug/2026-06-02-279-achieve-activation-discussion-closeout.md`
- Resolution critique:
  `charness-artifacts/critique/2026-06-02-279-achieve-activation-discussion-closeout.md`
- Implementation commit:
  `a0f00520 Warn on unresolved achieve activation discussion`
