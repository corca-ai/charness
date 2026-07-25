# Gather: The New Rules of Context Engineering for Claude 5 Generation Models

- **Source**: https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models (Anthropic / claude.com blog)
- **Knowledge Capability**: Vendor guidance on how to size and structure system prompts, CLAUDE.md, skills, and tool interfaces for Claude 5 generation models. Used when auditing charness prompt/skill/contract surfaces for over-instruction.
- **Canonical Asset**: `charness-artifacts/gather/2026-07-25-claude5-context-engineering-rules.md`
- **Freshness**: fetched 2026-07-25
- **Access Mode**: public (degraded)
- **Route / Selected Attempt**: `gather_public_url.py` direct-public-fetch classified `login-wall` (`final_confidence: none`, no proof captured). Selected attempt: host `WebFetch` capability, which returned a model-condensed rendering of the article, not raw source HTML.

## Requested Facts (as captured)

Headline claim: Anthropic removed >80% of Claude Code's system prompt for advanced models (Opus 5, Fable 5) with no measurable coding-eval regression.

Named shifts:

1. **Rules -> judgment.** Replace explicit prohibitions with a standard the model can apply (the article's own example: instead of "never write multi-paragraph docstrings", say to match the surrounding code's comment density, naming, and idiom).
2. **Examples -> interface design.** Rather than shipping tool usage examples, make parameters expressive and enumerations clear so the interface itself steers behavior.
3. **Upfront information -> progressive disclosure.** Move detail into selectively loaded skills and deferred-loading tools instead of a comprehensive system prompt; load context at the moment it is needed.
4. **Repetition -> clarity.** Remove duplicated instructions across system prompt and tool descriptions; put each piece of guidance in the single most relevant place.
5. **Manual memory -> auto-memory.** Claude saves relevant memories automatically rather than requiring manual CLAUDE.md edits.
6. **Simple specs -> rich references.** Point at real code, test suites, HTML artifacts, and detailed rubrics instead of prose markdown descriptions.

Context-assembly guidance by surface:

- System prompt: product-specific guidance, rarely user-modified.
- CLAUDE.md: keep lightweight; repo-specific gotchas, progressive disclosure.
- Skills: encode team-specific opinions and practice; avoid over-constraining.
- References: prefer code-based specs and artifacts over descriptions.

Practical recommendation: use `claude doctor` (`/doctor` in Claude Code) to audit and rightsize skills, CLAUDE.md, and system prompts.

## Captured vs Human Confirmation

- Captured: all of the above, via `WebFetch` extraction.
- Not human-confirmed: none of this was verified against raw page HTML in this session.

## Open Gaps

- Raw-HTML primary capture failed (`login-wall` classification on direct fetch); the record is a model-condensed rendering, so exact wording beyond the quoted comment-density line is paraphrase, not verbatim source.
- No quantitative detail behind the ">80% removal, no measurable loss" claim was captured (which evals, which models, what deltas).
- `gather_public_url.py` classified this claude.com article page as `login-wall` on the direct route and stopped without trying `impersonated-public-fetch` / reader / render fallbacks. Possible classifier false positive worth checking against `support/web-fetch`.
