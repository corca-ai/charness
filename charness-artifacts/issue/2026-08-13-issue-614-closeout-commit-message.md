fix: bound failed pytest and mutation report retention

Closes #614
Classification: bug
JTBD: Keep recent failed-test evidence inspectable while preventing runner-owned
basetemps and unmanaged mutation diagnostics from growing without an owner.
Boundary: Automatic cleanup owns only marked failed basetemps created by the
standing runner. Mutation report deletion stays an explicit dry-run, digest
confirmation, and unchanged-candidate operator action; managed, nested, fresh,
symlinked, and ambiguous evidence is preserved.
Implementation: Retain the newest three marked failed basetemps with sibling
liveness locks and explicit success-keep markers; add a managed-path mutation
report inventory whose execute path anchors the report root, revalidates each
candidate, and emits a structured receipt. Fresh checkouts receive an empty
inventory and confirmed no-op without directory creation.
Root Cause: The standing runner deliberately escaped pytest's unsafe nested
cleanup but supplied only success cleanup, leaving failures unbounded. Mutation
producers used fixed paths but no surface classified current managed outputs
against old ad-hoc diagnostics, so cleanup could not be decided safely.
Debug Artifact: charness-artifacts/debug/2026-08-13-issue-614-unbounded-local-artifact-retention.md
Siblings: decision: fixed the same-layer failed-basetemp and mutation-report
owners now (proof: 156 related tests and a nine-candidate live dry-run); decision:
preserved explicit-kept, legacy, custom, active, managed, nested, and fresh paths
(proof: 40 repaired-surface tests); decision: defer small hidden roots until
growth reproduces (proof: debug artifact records their current 12 MB and 8.7 MB
scale and the named monitoring anchor).
Prevention: Retention stays adjacent to the producer that can prove lifecycle;
automatic pruning requires a failure marker plus inactive lock, while ambiguous
ignored reports require current managed-path inventory and explicit confirmation.
Critique #614: charness-artifacts/critique/2026-08-13-issue-614-local-artifact-retention-resolution.md
Behavior #614: Confirmed through 156 related pytest behaviors, including 40
repaired-surface lifecycle and CLI tests; a separate live dry-run inventoried
nine candidates totaling 2,051,034,430 bytes and removed nothing.
AI-provenance: Agent-authored direct-commit carrier; causal debug, producer
inventory, parity evidence, bounded fresh-eye reviews, synchronized plugin
mirrors, and explicit non-claims are recorded in the bound artifacts.
