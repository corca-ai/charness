# YouTube Browser UI Transcript Live Proof
Date: 2026-06-11

## Scope

Live proof for the `youtube-browser-transcript-ui` fallback shipped in the
`gather`/`web-fetch` route for YouTube URLs.

## Command

```bash
python3 skills/support/web-fetch/scripts/acquire_public_url.py --repo-root . --url https://youtu.be/haK1KoQWm18 --browser-mode auto --timeout 40 --intent collect --include-selected-content --selected-content-max-chars 1000
```

## Result

- exit code: `0`
- disposition: `success`
- source identity: `youtube-transcript-browser-ui`
- selected stage: `youtube-browser-transcript-ui`
- selected tool: `agent-browser`
- selected status: `success`
- selected confidence: `strong`
- video id: `haK1KoQWm18`
- transcript segment count: `239`
- selector opened: `ytd-video-description-transcript-section-renderer`
- selected content format: `markdown`
- selected content original chars: `31341`

## Fallback Evidence

- `direct-public-fetch` returned `captcha` with matched signals `captcha` and
  `robot`.
- `domain-specific-route` returned `missing-tool:yt-dlp` on this machine.
- `archive-or-cache` and `clean-stop` were skipped with
  `prior-stage-sufficient` after the browser UI transcript stage succeeded.

## Notes

The proof demonstrates that the fixed route can obtain transcript content from
the YouTube transcript UI through `agent-browser` when direct public fetch and
`yt-dlp` do not produce transcript content on the authoring machine. This is a
live-source proof, not a guarantee that every YouTube URL exposes an available
transcript UI.
