# Catalog fixture

This dependency-free seed exposes a deliberately small public API:

```python
from src.catalog import Catalog

catalog = Catalog({"books": ["novel"]})
catalog.resolve("books")
```

`Catalog(mapping)` performs canonical-key lookup. An unknown key raises the
normal `KeyError`. The seed does not contain alias support or a generated
specification; those belong to the later journey contexts.

Run the baseline with:

```text
python3 -m unittest discover -s tests -v
```
