# Issue #509 Causal Review

Date: 2026-08-06
Issue: https://github.com/corca-ai/charness/issues/509
Classification: bug

## Live Issue Read

- GitHub adapter: `gh`
- State: `OPEN`
- `comments_read: true`; comment count: 0
- Title: `gather auto-derived URL slugs are rejected by the dated-record writer`
- Live read: `python3 skills/public/issue/scripts/issue_tool.py read --repo corca-ai/charness --number 509`
- Frozen source URL: `https://wiki.g15e.com/pages/AOP%20and%20CSS.md`

## JTBD

As a gather operator, normal public-URL `--execute` with no slug workaround
should yield a valid durable dated record.

## Causal Review

Fresh-eye satisfaction: parent-delegated. The unnamed bounded reviewer read the
current source and plugin mirror read-only; rail-1 boundary verification for
window `issue-509-causal-v1` returned `verdict: clean` with `drift: []`.

### Classification confirmation

Bug. The default producer emits a value that its required final writer rejects;
the live issue is OPEN and the direct local falsifier reproduced the reported
derived slug and `WriteError`.

### Root cause

`gather_public_url._slug_from_url` builds `safe` from the URL identity while
preserving ASCII case and percent-encoded path spelling
(`skills/public/gather/scripts/gather_public_url.py:43-51`), then passes that
value when `--slug` is omitted (`:183-197`). The final writer validates every
slug against a lowercase-only contract
(`skills/public/gather/scripts/gather_writer_lib.py:20-24`,
`skills/public/gather/scripts/write_record.py:102-109`). The checked-in plugin
producer is identical at
`plugins/charness/skills/gather/scripts/gather_public_url.py:43-51`.

Falsifiable claim: a successful acquisition whose implicit URL identity contains
uppercase ASCII can fail before record creation unless the operator supplies an
explicit slug. Cheapest disconfirmer: derive the slug for the issue URL and run
the writer validator. Result: confirmed locally — it produced
`wiki-g15e-com-pages-AOP-20and-20CSS-md-e0a17463` and the writer rejected it.

This consumes the disconfirmer-first substrate
(`skills/public/debug/references/disconfirmer-first.md`) and the
five-whys/structural-cause substrate
(`skills/public/debug/references/five-whys-causal-chain.md`). Do not re-derive
the RCA body in causal review.

### Invariant proof

Invariant: when `gather_public_url` produces an implicit slug,
`write_record` must accept it and create the dated record before the gather
workflow can report success.

- Producer proof: omission of `--slug` selects `_slug_from_url` at
  `skills/public/gather/scripts/gather_public_url.py:183-197`; source/plugin
  producer parity is confirmed by `cmp -s`.
- Final-consumer proof: `write_record` validates the slug before computing the
  record path or writing at `skills/public/gather/scripts/write_record.py:102-134`.
- Non-claims: no disposable full `--execute` provider/readback was run; this
  causal slice proves local producer-to-validator behavior, not a live URL
  provider roundtrip.

This consumes `skills/public/debug/references/invariant-first-review.md`. Do not
re-derive the invariant-first review body in causal review.

### Detection gap

Existing default-slug coverage exercises lowercase paths and successful writes,
while other success tests supply `--slug` explicitly
(`tests/test_web_fetch_support.py:298-313` and `:539-581`). The missing
detection surface is an omitted-slug, uppercase/percent-encoded URL reaching
the writer and reading the resulting record back. The smallest detector is one
regression case that leaves `--slug` omitted, uses the issue-shaped URL, and
asserts both writer acceptance and dated-record readback.

This consumes `skills/public/debug/references/detection-gap.md`. Do not
re-derive the detection-gap walk in causal review.

### Sibling search

Mental model: an automatic identifier is treated as valid merely because its
producer applies a “safe character” transform, without proving the final
consumer's stricter contract.

- Same layer — `plugins/charness/skills/gather/scripts/gather_public_url.py:43-51`:
  same producer and same emitted value; decision: `same bug, fix now`; proof:
  `local payload proof` plus source/plugin parity.
- Abstraction up — the producer-to-writer boundary above is the structural
  pattern; `skills/public/gather/scripts/write_record.py:109-118` is the final
  filename construction under the deliberate dated-record contract; decision:
  `intentional plain-text or non-rendering boundary`; proof: `static scan only`.
- Specialization down — the issue-shaped uppercase and percent-encoded path is
  the specific failing axis within `_slug_from_url`; decision: `same bug, fix
  now`; proof: `local payload proof`.
- Mental-model sibling — no additional automatic identifier crossing a strict
  writer contract was found in the bounded gather source/plugin scan; decision:
  `same class, diagnostic-only for this slice`; proof: `static scan only`.

This consumes `skills/public/debug/references/sibling-search.md`. Do not
re-derive the sibling-search walk in causal review.

### Bundle vs Defer recommendation

- Bundle now: source/plugin parity and an omitted-slug regression with
  uppercase/percent-encoded URL axes, digest retention, writer acceptance, and
  disposable dated-record readback.
- Defer: no separate sibling issue; no provider, installed-host, or live URL
  claim can be bundled into local proof.

Fresh-Eye Satisfaction: parent-delegated.
