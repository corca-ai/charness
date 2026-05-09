# Source Priority

Gather from the highest-value source first.

## Preferred Order

1. named local file or local repo artifact
2. direct upstream source named by the user
3. known official source URL (project docs, official site, vendor API
   reference, GitHub repo) when the canonical source is identifiable from
   the request
4. primary documentation found through search
5. secondary explanations or commentary

## Official URL Before WebSearch

When the request names a project, library, vendor, or product whose
canonical source is identifiable (e.g., the project's docs site, official
GitHub repo, or vendor reference), fetch that URL directly before a broad
`WebSearch`. WebSearch is for cases where the canonical source is not
known up front. Skipping straight to search dilutes provenance and can
return derivative summaries even when the official page is one hop away.

## Reason

The point of `gather` is durable knowledge with traceable provenance. Every hop
away from the primary source weakens that.
