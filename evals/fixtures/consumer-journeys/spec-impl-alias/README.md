# Spec-to-impl alias-resolution consumer packet

This packet is a small, dependency-free consumer repository for the Goal 798
spec-to-impl journey. The `seed/` directory is the unchanged starting repo;
the prompts describe the spec handoff and the implementation handoff.

The seed has only canonical catalog lookup. It intentionally contains no
alias implementation, candidate documentation, or candidate result. The
parent's observer owns acceptance and comparative results.

Run the seed from its root with:

```text
python3 -m unittest discover -s tests -v
```

An isolated task lane may be invoked with `task run --skip-prepare`. The seed
uses only the Python standard library and does not copy Charness skills into
the consumer repository.

Packet contents:

- `seed/` — baseline consumer files and tests.
- `prompts/spec.md` — the installed `spec` handoff.
- `prompts/impl.md` — the installed `impl` handoff.
