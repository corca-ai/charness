"""A minimal canonical-key catalog used by the consumer fixture."""

from __future__ import annotations


class Catalog:
    """Resolve values by their canonical keys."""

    def __init__(self, mapping):
        self._mapping = dict(mapping)

    def resolve(self, key):
        return self._mapping[key]
