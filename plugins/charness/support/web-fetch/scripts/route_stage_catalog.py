from __future__ import annotations

FALLBACK_ORDER = (
    "direct-public-fetch",
    "domain-specific-route",
    "impersonated-public-fetch",
    "defuddle-reader-extraction",
    "patchright-render-recon",
    "patchright-network-recon",
    "agent-browser-render-recon",
    "agent-browser-network-recon",
    "reader-or-metadata-fallback",
    "archive-or-cache",
    "clean-stop",
)


def stage(stage_id: str, tool_id: str | None, when: str, proof: str) -> dict[str, object]:
    return {"stage_id": stage_id, "tool_id": tool_id, "when": when, "proof": proof}


def direct_stage() -> dict[str, object]:
    return stage(
        "direct-public-fetch",
        None,
        "Start here for public URLs unless a stronger domain route is known.",
        "classify-fetch-response",
    )


def domain_stage(tool_id: str | None) -> dict[str, object]:
    return stage(
        "domain-specific-route",
        tool_id,
        "Use the declared route before generic browser or reader fallbacks.",
        "route-specific structured output",
    )


def youtube_browser_stage() -> dict[str, object]:
    return stage(
        "youtube-browser-transcript-ui",
        "agent-browser",
        "Use the YouTube page UI transcript button when metadata/subtitle extraction is blocked "
        "or transcript captions are not returned.",
        "opened transcript UI plus accessibility snapshot segment extraction",
    )


def reader_fallback_stages() -> list[dict[str, object]]:
    return [
        stage(
            "impersonated-public-fetch",
            "curl_cffi",
            "Retry public HTML with browser-like TLS/HTTP impersonation before paying browser-render cost.",
            "classify-fetch-response plus impersonation profile",
        ),
        stage(
            "defuddle-reader-extraction",
            "defuddle",
            "Use for article-like public pages when direct HTML is weak, cluttered, or partial.",
            "clean markdown plus source URL and classifier confidence",
        ),
        stage(
            "patchright-render-recon",
            "patchright",
            "Use a headless Patchright Chromium render when fetch/reader paths are blocked, JS-rendered, or unclear.",
            "headless rendered body text and access mode",
        ),
        stage(
            "patchright-network-recon",
            "patchright",
            "For collection intent, record public-looking /api/, /graphql, or .json requests seen by headless Patchright.",
            "network request candidates; no clicks, form submits, or login bypass",
        ),
        stage(
            "agent-browser-render-recon",
            "agent-browser",
            "Use for JS-rendered pages, empty SPA shells, repeated challenge signals, or weak cleaner output.",
            "rendered body text/html and access mode",
        ),
        stage(
            "agent-browser-network-recon",
            "agent-browser",
            "Use for list/collection intent to record public-looking /api/, /graphql, or .json request candidates.",
            "network request candidates; no clicks, form submits, or login bypass",
        ),
    ]


def terminal_stages() -> list[dict[str, object]]:
    return [
        stage(
            "archive-or-cache",
            None,
            "Use only when a stale or cached source still honestly answers the request.",
            "archive/cache source identity and freshness caveat",
        ),
        stage(
            "clean-stop",
            None,
            "Stop when access, auth, challenge, or confidence gaps remain.",
            "recorded failure mode and missing capability",
        ),
    ]
