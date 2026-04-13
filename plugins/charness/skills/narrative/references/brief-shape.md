# Brief Shape

Use the aligned source-of-truth docs as input, not as an excuse to dump repo
paths into a new audience-local body.

## Core Rule

The brief that `narrative` derives should be audience-neutral by default.

- self-contained enough that `announcement` can adapt it later without
  rediscovering the story
- compressed enough that it does not fork a second durable truth surface
- shaped by the repo adapter's `brief_template` when one exists

## What To Avoid

- do not bake in one concrete audience, language, or channel
- do not dump repo paths, decision ids, or stage labels unless they are part of
  the durable story and still readable without local context
- do not use the brief to replace source-of-truth docs

## Relationship to `announcement`

`announcement` is the right next layer when the aligned story or neutral brief
must be tailored for:

- one concrete audience
- one language or tone
- one delivery target or backend
