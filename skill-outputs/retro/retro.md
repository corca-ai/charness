# Retro Review

Mode: session

Context:
- The repo added a checked-in pre-push hook, but a later push showed that this
  clone had never activated it.
- The user correctly pointed out that the hook did not appear to run.

Waste:
- I treated "checked-in hook exists" as too close to "this clone enforces it".
- I verified the repo structure, but not the clone-local `core.hooksPath`
  state until the user challenged the assumption.

Critical Decisions:
- Move maintainer hook activation into a deterministic quality gate instead of
  relying on operator memory.
- Strengthen `retro` itself so valid user-caught misses trigger a short session
  retro and persistence is always stated explicitly.

Expert Counterfactuals:
- Kent Beck would have asked for the smallest failing check first: "What proves
  this clone will actually run the hook on push?" before treating the setup as
  complete.
- Charity Majors would have optimized for runtime truth over structural truth:
  "show me the actual execution path" instead of assuming the checked-in file
  meant the operational path was live.

Next Improvements:
- workflow: verify clone-local activation whenever repo-owned git hooks are
  introduced, not just the presence of checked-in hook files
- capability: keep `scripts/validate-maintainer-setup.py` in the canonical
  quality runner so this class of miss fails closed
- memory: require `retro` to report `Persisted` explicitly so users do not have
  to ask whether retrospective findings were written anywhere

Persisted: yes: skill-outputs/retro/retro.md
