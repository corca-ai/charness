# Justification — setup greenfield Slice 9c capture (#410 / #413 rider)

- source-kind: operator-log

Operator authorization (2026-07-09, session): "알아서 전체 진행" — proceed with
the entire remaining #410 queue, which names the setup/greenfield fresh-sandbox
capture as a queue item (deferred by #410 as not-in-repo-capturable; the
capture harness gained --run-cwd for exactly this scenario).

This capture observes a real /charness:setup greenfield run on a brand-new
empty sandbox repo (git init only), graded against
evals/cautilus/setup-claim-fidelity/greenfield.spec.json (current RCF floor)
to decide the census-MOVE flip from observed behavior, never assumption.
