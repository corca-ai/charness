# Cache script fixture

This dependency-free seed has an existing script interface:

```text
python3 scripts/refresh_cache.py SOURCE
python3 scripts/check_cache.py
```

`SOURCE` is a JSON file. The refresh script parses it and writes the parsed
value to `.state/cache.json`; the check script reads that cache and reports its
status. These are the existing behaviors the later CLI must preserve.

Run the baseline with:

```text
python3 -m unittest discover -s tests -v
```
