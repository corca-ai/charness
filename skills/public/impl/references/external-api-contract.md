# External API Contract Traps

Mocked unit tests prove that the orchestration around an external API call is
wired, not that the request shape and response parsing match the provider's
real contract. Use this reference as a checklist when the slice touches a
third-party API and `verification-ladder.md` asks for an executed round-trip.

## Why Mocks Stay Green Through Real Bugs

Mock fixtures usually start as a copy of a sibling endpoint or a hand-written
sample. They drift from the live contract on:

- list-shaped parameters that are not strongly typed by the SDK wrapper
- timestamp encoding mismatches between similar endpoints
- required parameters the SDK silently omits or only sends on certain calls
- response field renames between endpoints that look interchangeable
- pagination shape moves between similar endpoints

A mocked unit test exercises only the values the test author chose. The
provider rejects or quietly relabels those values at runtime, and the bug
ships.

## Recurring Trap Shapes

### Request

- list params: array vs comma-separated string (Slack `content_types`,
  `channel_types`, GitHub `labels`, Notion `filter` arrays)
- timestamps: ISO-8601 vs Unix seconds vs Unix milliseconds; some providers
  require seconds for `after`/`before` and milliseconds elsewhere on the same
  endpoint family
- limits and caps: documented endpoint cap differs from the SDK's generic
  default (Slack search endpoints often cap at 20, not the SDK's 200)
- silently required parameters: bot calls that need an `action_token`,
  workspace calls that need an explicit `team_id`, Drive calls that need
  `supportsAllDrives`, Sheets calls that need `valueInputOption`
- auth scope mismatches: the bot token has the scope but the user token does
  not, or vice versa, and the failure surfaces only at runtime

### Response

- field rename between sibling endpoints: `text` vs `content`, `ts` vs
  `message_ts`, `user` vs `author_user_id`, `channel.id` vs `channel_id`
- nested vs flat ID shape: `{ "channel": { "id": ... } }` vs `"channel_id"`
- pagination keys: `response_metadata.next_cursor` vs `nextPageToken` vs
  `_links.next.href` vs an `offset`/`limit` echo
- empty-result shapes: `null` vs `[]` vs missing key entirely
- error envelope shape: HTTP 200 with `{ "ok": false, "error": "..." }` vs
  HTTP 4xx with a body, depending on endpoint

## Smallest Honest Probe

Before closeout, run at least one executed call against the real provider:

- send the exact request the production code would send for the touched path
- log or print the raw response body once and compare it to the parser's
  expectations field by field
- exercise both the success branch and the most likely error branch (auth
  scope, rate limit, or missing-resource) when feasible

If credentials are not available in the current host, do not fall back to
"mocked tests pass". Mark the seam unverified at the contract level so the
next operator knows the request and response shape have not been proven against
the live provider.

## When To Add A Repo-Owned Fixture

If the same provider seam is exercised by multiple slices, capture one real
response body as a checked-in fixture so future mocked tests start from a
real-shape sample instead of drifting again. Keep the fixture small and
field-named so the rename traps above stay visible to a reader.
