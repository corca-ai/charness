"""Observer-only correct control; not producer scaffolding."""


class Catalog:
    def __init__(self, mapping, aliases=None):
        self.mapping = dict(mapping)
        pairs = list(aliases or [])
        targets = {}
        for name, target in pairs:
            if name in self.mapping or name in targets:
                raise ValueError(name)
            targets[name] = target
        self.keys = {name: name for name in self.mapping}
        for name, target in pairs:
            seen = {name}
            while target not in self.mapping:
                if target in seen or target not in targets:
                    raise ValueError(name)
                seen.add(target)
                target = targets[target]
            self.keys[name] = target

    def canonical_key(self, name):
        return self.keys[name]

    def resolve(self, name):
        return self.mapping[self.canonical_key(name)]
