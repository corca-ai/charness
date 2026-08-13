feat: complete lesson and contract lifecycle replay

Closes #616
Classification: feature
JTBD: Let maintainers archive or restore durable lessons and apply reviewed
contract graduation or retirement without hand-rewriting history or treating a
score, projection, or retention signal as authorization.
Boundary: Append-only ledger/register events own lifecycle history; materialized
JSON and live H2 docs are separately checked projections. Quality evidence may
create a proposal, while an existing reviewed Markdown decision is required for
application. No live lifecycle or contract-membership transition is performed.
Resolution Brief: charness-artifacts/spec/2026-08-12-lesson-ledger-and-contract-register.md
Implementation: Migrate the lesson ledger to v4 with a 50-active budget and
archive/resurrect events; make preview policy v2 use a real archive slot. Migrate
the contract register to v2 with frozen seed units, evidence-backed proposals,
reviewed graduation/retirement replay, historical citations, and a
non-authorizing retention report. Supply dry-run migrations, explicit operator
commands, synchronized plugin mirrors, and deterministic refusal tests.
Prevention: Durable events replay before projections are trusted; committed
streams and fixed budgets cannot be rewritten, contract applications must match
the live H2 inventory, invalid operator identities refuse without changing bytes,
and proof-surface changes receive two bounded review rounds.
Critique #616: charness-artifacts/critique/2026-08-13-issue-616-applied-lifecycle-resolution.md
Behavior #616: Confirmed through 85 focused ledger, selection, continuity,
register, migration, and real-CLI behaviors plus live read-only checkers showing
16 active lessons and 26 active contract units with no applied transition.
AI-provenance: Agent-authored direct-commit carrier; issue re-read, quality
classification, replay tests, operator receipts, two-round bounded review,
generated-mirror synchronization, and external-state non-claims are recorded in
the bound artifacts.
