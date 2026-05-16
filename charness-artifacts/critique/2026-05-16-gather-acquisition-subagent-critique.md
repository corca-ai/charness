# Gather Acquisition Subagent Critique

- Date: 2026-05-16
- Target: code critique for `c894b60..HEAD`
- Fresh-Eye Satisfaction: parent-delegated
- Packet Consumed: `charness-artifacts/critique/2026-05-16-014421-packet.md`
- Packet Caveat: the prepared packet saw a clean working tree and reported no changed paths; reviewers used `c894b60..HEAD` as source of truth.

## Change

The reviewed change adds a web-fetch acquisition stack for public URL gather:
direct fetch classification, optional `defuddle` reader extraction,
read-only `agent-browser` render/network reconnaissance, proof/confidence
classification, route acquisition plans, integration manifest, plugin export,
and tests.

## Angles

- Michael Jackson / problem framing: checked whether the change solves gather acquisition rather than only trace diagnostics.
- Gerald Weinberg / diagnostic: checked whether fallback logic addresses the actual weak-fetch failure modes.
- Atul Gawande / operational checklist: checked runtime safety, trace completeness, missing-tool behavior, and operator-facing signals.
- Counterweight: separated blockers from speculative follow-up.

## Counterweight Triage

### Act Before Ship

1. Non-HTTP URL schemes are accepted.
   - Evidence basis: strong.
   - Risk: `urllib.request.urlopen()` can read `file://` and report success for a supposed public URL acquisition.
   - Next move: reject non-`http`/`https` before routing, fetching, or browser stages; add a regression test.

2. Invalid `--expect-regex` can become strong proof.
   - Evidence basis: strong.
   - Risk: regex parse errors are recorded under proof, then any proof promotes the response to strong success.
   - Next move: classify invalid regex as input/config error or invalid proof, never successful proof; add a regression test.

3. Missing fallback binaries disappear from the trace.
   - Evidence basis: strong.
   - Risk: planned `defuddle` or `agent-browser` fallback stages are skipped by `shutil.which()` checks without skipped-stage records.
   - Next move: emit explicit skipped attempts with reasons such as `missing-tool`, `browser-mode-off`, or `route-not-applicable`.

4. Domain-specific route plans are advertised but not executed or marked skipped.
   - Evidence basis: strong.
   - Risk: routes add `domain-specific-route` for Reddit, HN, Stack Exchange, GitHub, media, and Naver, but acquisition only runs direct plus generic fallbacks.
   - Next move: implement those stages or mark them `not-implemented` / `skipped` so operator output does not imply the full route ladder ran.

5. Browser network reconnaissance can satisfy acquisition without content acquisition.
   - Evidence basis: strong.
   - Risk: a nonempty network request list can be `success`/`weak` and satisfy overall success without fetching and classifying candidate content.
   - Next move: make network recon diagnostic-only unless a candidate URL is fetched and classified; exclude recon-only attempts from success selection.

6. Positive proof overrides blocker signals.
   - Evidence basis: strong.
   - Risk: CAPTCHA, login, or error pages containing expected text can become strong success because proof is checked before blocker signals.
   - Next move: detect blocker signals before success, or return blocked/contested with proof recorded but not trusted.

7. Public `gather` does not yet route arbitrary public URLs through `web-fetch`.
   - Evidence basis: strong.
   - Risk: the support seam is not reachable from the public workflow it claims to support.
   - Next move: update gather's public URL path to invoke `acquire_public_url.py` and preserve route/trace in the durable asset.

### Bundle Anyway

1. Final status/confidence can describe the last auxiliary attempt rather than the selected success.
   - Evidence basis: strong.
   - Next move: add `selected_attempt` fields or compute final status/confidence from the selected successful attempt while keeping network recon as auxiliary metadata.

2. Selector proof is documented but not implemented.
   - Evidence basis: strong.
   - Next move: remove selector wording from shipped docs or add explicit `--expect-selector` support with tests.

### Valid But Defer

1. Weak direct success stops before `defuddle`.
   - Evidence basis: contested.
   - Rationale: true in code and tests, but forcing reader extraction for every long page is a latency/policy decision and needs a separate acceptance rule.

2. `acquire_public_url.py` returns trace metadata, not acquired content.
   - Evidence basis: moderate.
   - Rationale: real limitation, but raw content persistence needs an artifact/content-size/copyright design rather than a rushed patch.

3. No-site-name/generic-helper lint from the insane-search review is still absent.
   - Evidence basis: moderate.
   - Rationale: the gathered review framed this as follow-up, not current acceptance.

### Over-Worry

1. `defuddle parse <url> --markdown` command shape should not block.
   - Evidence basis: weak.
   - Rationale: current repo tests exercise the intended invocation and reviewers found no concrete contrary evidence in this range.

## Next Move

Do not treat `b05bb68` as shippable yet. The minimum repair slice should fix
the seven Act Before Ship items first, then include the selected-attempt and
selector-doc cleanup while touching the same support surface.
