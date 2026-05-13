# Surface-Driven Adapter Triggers

When a Charness skill gates work on "did the current change touch a repo
seam that matters here", express that gate as **subscription to declared
surface ids** (from [.agents/surfaces.json](../../.agents/surfaces.json)),
not as a per-skill copy of raw path globs. Raw globs remain available for
narrow repo-specific exceptions that do not correspond to any declared
surface.

Today this convention applies to:

- `retro` — `auto_session_trigger_surfaces` in
  [.agents/retro-adapter.yaml](../../.agents/retro-adapter.yaml), consumed by
  [skills/public/retro/scripts/check_auto_trigger.py](../../skills/public/retro/scripts/check_auto_trigger.py)
- `release` — `real_host_required_surfaces` in
  [.agents/release-adapter.yaml](../../.agents/release-adapter.yaml), consumed by
  [skills/public/release/scripts/check_real_host_proof.py](../../skills/public/release/scripts/check_real_host_proof.py)

New trigger consumers (`setup`, future skills) should adopt the same shape
when they need to gate on changed seams.

## Why surface ids, not raw globs

A surface id is a named claim about what the seam is (`release-packaging`,
`integrations-and-control-plane`, `checked-in-plugin-export`, ...) and is
owned by [.agents/surfaces.json](../../.agents/surfaces.json). Multiple
skills can subscribe to the same surface and stay in sync as the path
shape underneath the surface evolves. Raw globs duplicated across adapters
drift independently.

Use raw globs (`auto_session_trigger_path_globs`,
`real_host_required_path_globs`) only when:

- the path is a narrow repo-local exception that does not warrant a
  full-surface declaration; or
- the path is genuinely cross-cutting and naming it as a surface would
  over-claim ownership.

## Fail-loud on unresolved configured ids

A configured trigger id that does not resolve to a declared surface in
[.agents/surfaces.json](../../.agents/surfaces.json) is **a broken adapter
contract**, not a normal non-match. The runtime must distinguish the two:

- *normal non-match*: configured id is declared, but the current changeset
  did not touch any path that maps to that surface → `triggered: false`,
  exit `0`.
- *broken config*: configured id is **not** declared in the manifest (typo,
  stale rename, dropped surface) → `configuration_status: "broken"`,
  `unresolved_trigger_surfaces: [<unresolved ids>]`, JSON on stderr, exit `1`.

This is enforced by `resolve_trigger_surfaces` in
[scripts/surfaces_lib.py](../../scripts/surfaces_lib.py), which returns
`{"declared": [...], "unresolved": [...]}`. Call sites must bail with the
broken-config payload before doing any change-path matching.

Without this fail-loud step, a typo in `auto_session_trigger_surfaces` is
indistinguishable from "the slice didn't touch the surface" — the most
costly silent miss for a gate that exists exactly to flag risk slices.

## Required fixture shape

Every trigger consumer ships at least the following four fixtures, in its
own test file under [tests/quality_gates/](../../tests/quality_gates):

1. **True positive path** — a real path that maps to a configured surface
   id; the consumer triggers with `surface_hits` naming the id.
2. **Unrelated artifact/doc false positive path** — a path that exists in
   the repo and could be conflated with the trigger surface but does not
   actually belong to it; the consumer does **not** trigger.
3. **Clean / no-change false case** — an explicit empty changeset
   (`--paths` with zero values); the consumer does not trigger and reports
   empty `changed_paths`, `surface_hits`, `path_hits`.
4. **Unresolved configured surface id** — adapter configures a typo'd or
   undeclared id against a synthetic manifest containing only the correct
   id; the consumer exits `1` with `configuration_status: "broken"` and
   `unresolved_trigger_surfaces` naming the unresolved entry.

Fixture #3 requires the script to treat `--paths` with zero arguments as
an explicit empty changeset (not as "fall through to git discovery"). The
canonical implementation pattern is:

```python
changed_paths = args.paths if args.paths is not None else collect_changed_paths(repo_root)
```

## Call-site checklist

When you add or change a trigger consumer:

- subscribe to surface ids via the consumer's adapter field; reserve
  raw-glob fields for narrow exceptions
- resolve configured ids via `resolve_trigger_surfaces` in
  [scripts/surfaces_lib.py](../../scripts/surfaces_lib.py) and emit the
  broken-config payload before path matching when `unresolved` is non-empty
- treat `--paths` with zero values as explicit empty changeset
- land all four fixtures from the shape above; do not skip the
  unresolved-id case

## References

- [scripts/surfaces_lib.py](../../scripts/surfaces_lib.py) —
  `resolve_trigger_surfaces` and `match_surfaces`
- [skills/public/retro/scripts/check_auto_trigger.py](../../skills/public/retro/scripts/check_auto_trigger.py)
- [skills/public/release/scripts/check_real_host_proof.py](../../skills/public/release/scripts/check_real_host_proof.py)
- [tests/quality_gates/test_retro_auto_trigger.py](../../tests/quality_gates/test_retro_auto_trigger.py)
- [tests/quality_gates/test_release_real_host.py](../../tests/quality_gates/test_release_real_host.py)
