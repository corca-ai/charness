## Resolution — split the export self-sufficiency umbrella

JTBD: ensure the exported plugin carries the bootstrap dependency contract
needed by the installer and expose the remaining export-only gaps honestly.

Boundary: this issue owns the bootstrap contract and documented-entrypoint
availability arm. Consumer-facing instruction paths, unrooted shell gates, and
unshipped repo-root data readers belong to successor #735.

Resolution brief: close the repaired contract arm and split the residual instead
of retaining an umbrella that implies the whole export is self-sufficient.

## Implementation and prevention

Implementation: the export now ships `packaging/bootstrap-python.json` and
`packaging/bootstrap-requirements.txt` beside `scripts/bootstrap_runtime.py`,
and the documented-entrypoint detector refuses an unguarded hard dependency.

Prevention: keep the checked-in export as the availability oracle, test against
hand-built consumer fixtures, and route instruction/shell/data-reader gaps to
the explicitly named successor owner #735.

## Behavior #634

Behavior #634: local-only-by-contract — the real checked-in export and
hand-built consumer fixtures pass the export self-sufficiency target (`45
passed`); this confirms the dependency-contract arm, not the successor residue.

## Resolution critique

The remaining inventory is real but independently owned. Closing the umbrella
without #735 would erase live cwd-relative instructions, shell gates, and data
readers; keeping the fixed dependency arm open would instead conflate separate
owners. The split preserves both facts.

## Explicit non-claims

This resolution does not claim every bare import is fixed, installed-host or
consumer adoption, scheduler behavior, hosted enforcement, remote CI, push,
release, tag, or fresh-eye review. Forced handoff and micro-slice rituals were
omitted by operator direction.

Successor: #735 — Exported consumer paths remain self-insufficient after
dependency contract fix.
Implementation carrier: the already-landed export dependency-contract changes;
the issue body was updated through the #724 Goal Run provider and read back as
`body_verified: true` before this close operation.
Manual fallback reason: operator-directed-manual-close.

Critique: blocked operator-directed implementation path omits forced fresh-eye
review; the bounded contract evidence and explicit successor split are the
intended closeout scope.

AI-provenance: authored by an agent session.
