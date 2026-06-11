gather: support YouTube sources and harden adapter YAML rendering

Closes #352.
Closes #353.

Issue closeout carrier: direct-commit.

Classification #352: feature.
Issue #352: Support YouTube sources in gather skill.

JTBD: an operator who gives gather a YouTube URL wants a durable source record
that preserves the video identity and states whether the content is
transcript-backed, metadata-only, blocked, or unavailable, so downstream
summary workflows do not imply stronger source proof than the gather artifact
actually contains.

Boundary: this is unauthenticated, local-first YouTube acquisition through the
public gather path. It does not use private browser profiles, authenticated
YouTube sessions, hosted fetch escalation, or claim that every YouTube URL can
produce a transcript in the current runtime.

Resolution brief: add a YouTube-specific web-fetch route that prefers captions
when `yt-dlp` can provide them, degrades to metadata-only or blocked records
when captions are unavailable, and writes the selected attempt's source
identity into the durable gather artifact.

Implementation: added `skills/support/web-fetch/scripts/youtube_source.py`,
wired `acquire_public_url.py` to select it for YouTube hosts, treated
`metadata-only` as success-like acquisition trace status, and updated
`gather_public_url.py` so partial/degraded/blocked YouTube acquisitions write
durable records with source details instead of disappearing as generic
no-write failures. Plugin exports are synced.

Prevention: `tests/test_youtube_source.py` covers transcript-backed seeded
caption extraction, metadata-only acquisition, blocked bot-verification
acquisition, missing-`yt-dlp` unavailable acquisition, and selected-attempt
identity. The live local artifact
`charness-artifacts/gather/2026-06-11-youtube-hak1koqwm18-unavailable-details.md`
proves the unauthenticated blocked/missing-tool path without claiming
transcript evidence.

Classification #353: bug.
Issue #353: adapter_lib YAML renderer hygiene for newlines, unsupported
constructs, and falsy explicit fields.

JTBD: an operator who relies on adapter YAML wants the repo renderer to
round-trip the supported subset without corrupting newlines, silently
normalizing unsupported YAML constructs, or dropping explicit falsy fields
that carry adapter intent.

Root Cause: `scripts/adapter_lib.py` used a narrow YAML subset parser/renderer
without enough scalar escaping, unsupported-construct refusal, or block-scalar
handling, while `quality_bootstrap_lib.py` rendered known fields from truthy
values rather than from explicit preserved status.

Debug Artifact: charness-artifacts/debug/latest.md.

Siblings: decision - scan the adapter parser, quality bootstrap renderer,
checked-in adapter examples, public-skill dogfood, workflow-style block-scalar
fixtures, and plugin exports rather than patching only the failing scalar case;
proof - `tests/quality_gates/test_adapter_lib_yaml.py`,
`tests/quality_gates/test_quality_bootstrap.py`, `validate_adapters`, broad
non-release pytest, and plugin packaging validators cover the sibling seams
folded into this fix.

Prevention: newline and carriage-return scalars are escaped on render and
decoded on parse, limited `|`/`>` block scalars are preserved, YAML
anchors/tags/unsupported block modifiers are refused loudly, the quality
adapter glob that looked like an alias is quoted, and quality bootstrap now
renders explicit falsy fields when status says they were preserved.

Tests: focused YouTube/web-fetch tests passed 65 tests; focused post-critique
tests passed 40 tests; final changed-surface validators passed, including
packaging, markdown, secret scan, skill policy, adapters, critique/debug,
integration, support/tool dry-runs, ruff, Python length gate with advisory
warn-band notes only, attention visibility, gitignore scan hygiene, and broad
pytest with 2771 passed, 4 skipped, 26 deselected.

Critique #352 #353: charness-artifacts/critique/2026-06-11-youtube-gather-and-adapter-renderer-closeout-critique.md
Retro: charness-artifacts/retro/2026-06-11-youtube-gather-adapter-closeout.md
Disposition review: charness-artifacts/critique/2026-06-11-youtube-gather-adapter-disposition-review.md
