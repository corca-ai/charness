# Gather Notion Runtime Contract

This support package exports a published Notion page to local markdown.

## Inputs

- published Notion URL or bare page id
- output markdown path

## Runtime

- `python3`
- no extra credential for the published-page path

## Behavior

1. Accept a published Notion URL or page id.
2. Fetch page blocks through the published-page export path.
3. Convert blocks into markdown.
4. Write the artifact to the requested local path.

## Limitations

- the page must already be published to the web
- private API access is out of scope for this support package
- sub-pages, images, and database views may lose fidelity
