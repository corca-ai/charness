# Brief Shape

Use the aligned source-of-truth docs as input, not as an excuse to dump repo
paths into the audience-facing body.

## External or Mixed Audiences

- self-contained by default
- explain internal stage names inline or replace them
- avoid `docs/...`, `src/...`, decision ids, or commit hashes unless the reader
  can act on them
- if the source brief is ephemeral, treat repo pointers as invalid by default

## Internal Audiences

- pointers are acceptable when the reader is likely to open the repo
- keep the durable truth in the source docs; use the brief to compress, not to
  fork a second reality

## Relationship to `announcement`

If the docs already align and the user mainly needs delivery wording or backend
posting, hand off to `announcement`.
