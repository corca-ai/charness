"""A minimal canonical-key catalog used by the consumer fixture."""

from __future__ import annotations


class Catalog:
    """Resolve values by their canonical keys."""

    def __init__(self, mapping, aliases=None):
        self._mapping = dict(mapping)
        self._aliases = {}
        seen_aliases = set()

        if aliases is None:
            aliases = ()

        for alias, canonical_key in aliases:
            if alias in self._mapping:
                raise ValueError(f"alias {alias!r} collides with canonical key")
            if alias in seen_aliases:
                raise ValueError(f"duplicate alias {alias!r}")
            seen_aliases.add(alias)
            if canonical_key not in self._mapping:
                raise ValueError(
                    f"alias {alias!r} targets unknown canonical key "
                    f"{canonical_key!r}"
                )
            self._aliases[alias] = canonical_key

    def resolve(self, key):
        if key in self._mapping:
            return self._mapping[key]
        if key in self._aliases:
            return self._mapping[self._aliases[key]]
        return self._mapping[key]
