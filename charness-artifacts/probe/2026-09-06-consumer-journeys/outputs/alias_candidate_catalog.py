"""A minimal canonical-key catalog used by the consumer fixture."""

from __future__ import annotations


class Catalog:
    """Resolve values by their canonical keys."""

    def __init__(self, mapping, *, aliases=None):
        self._mapping = dict(mapping)
        self._aliases = {}

        if aliases is None:
            aliases = []

        for alias, canonical_key in aliases:
            if alias in self._mapping:
                raise ValueError(
                    f"alias {alias!r} collides with canonical key"
                )
            if canonical_key not in self._mapping:
                raise ValueError(
                    f"alias {alias!r} targets unknown canonical key "
                    f"{canonical_key!r}"
                )
            if alias in self._aliases:
                raise ValueError(f"duplicate alias {alias!r}")
            self._aliases[alias] = canonical_key

    def resolve(self, key):
        if key in self._mapping:
            return self._mapping[key]
        return self._mapping[self._aliases[key]]
