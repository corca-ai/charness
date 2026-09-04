# Initial Routing Table

Domain-family tactics and fallback stage order live in the route mechanisms,
not in this page:

- `scripts/route_public_fetch_routes.py` — per-domain route identities
- `scripts/route_stage_catalog.py` — stage ladder / fallback order

Resolve a URL through the typed helper:

```bash
python3 "$SKILL_DIR/scripts/route_public_fetch.py" --url "https://www.reddit.com/r/python/"
```

## Scope Rule

This table is intentionally incomplete.

Add a route only when:

- the domain appears repeatedly enough to justify a checked-in tactic
- the tactic is stable enough to explain honestly
- `charness` is willing to maintain the route or name the real external owner
