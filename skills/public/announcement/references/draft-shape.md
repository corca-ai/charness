# Draft Shape

Announcements should be short, human-facing, and ordered by value.

Good announcement bullets answer:

- who benefits
- what changed on a real human surface
- what new confidence, capability, or recovery path now exists

Prefer:

- concise section headers from the adapter
- concrete verbs
- one useful sentence per bullet

Avoid:

- commit-message paraphrases with no human consequence
- internal cleanup unless it materially changes reliability, rollout safety, or
  operator understanding

## Audience Tone Enforcement

Audience tags are not just labels; they steer wording. When a bullet is tagged
with an end-user audience (`user`, `사용자`, etc.), the draft must reframe the
content into user-visible verbs and effects, not implementation paraphrase.
Internal jargon, file paths, environment variables, validator/phase names, and
commit-message vocabulary belong in operator/developer-tagged bullets at most,
and even there they should be tied to a human-visible outcome.

### user / 사용자

- good: "메시지를 수정해서 명령을 다시 실행할 수 있습니다."
- bad (commit paraphrase): "Slack edit-trigger fix routes through `worker-ceal-events-command` path."
- good: "긴 답변이 채널에 안 들어가던 문제가 풀렸습니다."
- bad (commit paraphrase): "msg_too_long branch falls back to chunked `chat.postMessage` path."

### operator

- good: "재시작 후 같은 명령을 한 번만 다시 실행하면 됩니다."
- bad (commit paraphrase): "seed_state heal-on-reconcile cycle now no-ops on idempotent restarts."

### developer

- good: "구독자 수 제한 관련 회귀가 사라졌습니다 (관련 phase counts 안정)."
- bad (commit paraphrase): "JSONL telemetry phase counts → workflow frame conversion finalized."

If a bullet is hard to phrase for a user-tagged audience, that is a signal that
it does not actually belong on the user-facing track. Move it to an
operator/developer-tagged bullet, or drop it.

## Release-Note Digest Density

Release-note style digests default to 2-4 actionable items, not a verbatim
commit list. Each item should answer four questions concisely:

- what changed on a real human surface
- who cares (which audience uses or operates this)
- one concrete usage or operator example so the change is recognizable
- source links (commit, PR, issue, or relevant doc) for traceability

When the source set is large or source-dense (many commits, many PRs, a
wide release window), favor a compact top-level message plus a detail
thread/reply rather than padding the top-level digest. For Slack
delivery in this shape, disable URL unfurls so the source links do not
explode the surface area; the format-rules conversion path
(`references/delivery-seams.md`) names the unfurl-disable knob.

## Public Body Shape

`public_body_shape` decides whether adapter sections are rendered taxonomy or
only coverage hints:

- `chat_update`: group the public body by reader-visible outcomes. Headings
  should sound like what a person can now do, avoid, or trust, not like the
  adapter taxonomy. Use prior successful announcements as style exemplars
  when available: section rhythm, opener, audience split, and specificity.
- `release_notes`: adapter sections may appear as public headings, but each
  bullet still needs human consequence and source traceability.

For chat updates, keep proof vocabulary, host/provider internals, file paths,
eval field names, and adapter taxonomy in maintainer-facing outputs unless
they directly change user behavior. The public body should not expose terms
like `provider_roundtrip`, `host_decision`, or backend command syntax when the
actual user experience is natural-language chat.

## Dual-Output Drafts

Some announcements have two genuine audiences in the same delivery (a
short user-facing top-level message plus a longer maintainer-facing thread
reply, or a release-notes file plus an internal comment).

When the adapter declares an `outputs` list, treat each output as one
independent draft body. Audience tags route bullets to outputs:

- a bullet tagged with any audience listed under an output's `audience_tags`
  belongs to that output
- a bullet that matches no output is dropped from delivery, not silently
  attached to the first output
- the delivery seam reads each output's `delivery_role` to decide how to post
  it (`parent`, `thread_reply`, or `single`)

When the adapter has no `outputs` list (or it is empty), produce one single
draft body and use `delivery_role: single` semantics. This keeps the default
behavior unchanged for repos that do not need dual-output drafts.
