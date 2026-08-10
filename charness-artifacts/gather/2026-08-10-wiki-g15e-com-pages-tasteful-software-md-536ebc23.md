# Gathered Public URL

- Source: https://wiki.g15e.com/pages/Tasteful%20software.md
- Access Mode: support/web-fetch public route
- Content Persistence: `extracted`
- Route: `direct-then-fallback`
- Route Family: `public`
- Route Access Modes: grant, public, degraded
- Disposition: `success`
- Final Status: `success`
- Final Confidence: `weak`
- Source Identity: `not-applicable`

## Selected Attempt

- Stage: `direct-public-fetch`
- Tool: `direct`
- Status: `success`
- Confidence: `weak`

## Acquisition Trace

- `direct-public-fetch` via `direct`: success / weak
- `content-negotiated-markdown` via `direct`: skipped / none (prior-stage-sufficient)
- `impersonated-public-fetch` via `curl_cffi`: skipped / none (prior-stage-sufficient)
- `defuddle-reader-extraction` via `defuddle`: skipped / none (prior-stage-sufficient)
- `patchright-render-recon` via `patchright`: skipped / none (prior-stage-sufficient)
- `patchright-network-recon` via `patchright`: skipped / none (prior-stage-sufficient)
- `agent-browser-render-recon` via `agent-browser`: skipped / none (prior-stage-sufficient)
- `agent-browser-network-recon` via `agent-browser`: skipped / none (prior-stage-sufficient)
- `archive-or-cache` via `direct`: skipped / none (prior-stage-sufficient)
- `clean-stop` via `direct`: skipped / none (prior-stage-sufficient)

## Open Gaps

- None recorded.

## Extracted Content

- Source Stage: `direct-public-fetch`
- Format: `text`
- Chars: `3874`
- Original Chars: `3874`
- Truncated: `False`

```text
# Tasteful software > 누구나 무엇이나 만들 수 있는 시대일수록 취향이 더욱 중요해진다고 생각한다. 각자 자기만의 취향을 담아 소프트웨어를 만들면 세상에 지금보다 나은 소프트웨어들이 많아질거라고 믿는다. 누구나 무엇이나 만들 수 있는 시대일수록 취향이 더욱 중요해진다고 생각한다. 각자 자기만의 취향을 담아 소프트웨어를 만들면 세상에 지금보다 나은 소프트웨어들이 많아질거라고 믿는다. ## 취향이란 '취향'은 워낙 두루뭉술한 단어니까 뜻을 좀 좁혀놓고 시작하면 좋겠다. - **타고난 재능 아님**: 난 취향이라는 게 그냥 타고난 심미안이나 절대음감 같은 게 아니라(왜냐하면 인간이 타고난 재능 차이는 생각보다 크지 않으므로) 꾸준히 갈고 닦으며 벼려낸 무언가일거라고 믿는다. [개리 클레인](https://wiki.g15e.com/pages/Gary%20Klein.txt) 등이 말하는 전문적 직관skilled intuition이라는 개념이랑도 어느 정도 겹치는 것 같다. - **무인도에서 득도하는 거 아님**: 취향을 갈고 닦는다는 건 산에서 10년 도를 닦는다거나 하는 게 아니라, 기존 연구들을 부지런히 읽고 시행착오를 겪어보면서 각자의 마음 속에서 하나의 정합적인 틀로 담아내려고 노력하는 방식에 가까울거라고 믿는다. - **완성된 거 아님**: 물론 완벽하게 정합적인 지식의 총체란 불가능하니 이 시도는 성공할 수 없고 언제나 진행형일 것이다([동사로서의 완벽](https://wiki.g15e.com/pages/Perfect%20as%20a%20verb.txt)). 게다가 이 틀이 변하는 세상 안에서도 계속 유용하려면 꾸준히 뭘 비워내야만 하겠다(unlearning). 타고난 재능이 없어도 되고 깊은 깨달음의 경험을 하지 않아도 되고 완성되지 않아도 되는거라면, 나에게도 취향이 있다고 말할 수 있다. 물론 그게 좋은 취향인지 아닌지는 모르겠지만. 이런 취향을 가져야 수많은 가능성 중에서 무엇을 선택할지 잘 결정할 수 있을거라고 믿는다. 이 말은, 수많은 가능성 중 대부분을 버린다는 뜻이기도 하다. 각자 자기만의 취향을 담아 소프트웨어를 만들면 세상에 지금보다 나은 소프트웨어들이 많아질거라고 믿는다. ## 내 취향 내가 세운 [디자인의 정의](https://wiki.g15e.com/pages/Definition%20of%20design.txt)를 만족하면 좋다: > 모든 시스템에는 더 이상 제거할 수 없는 [내재된 복잡성이 존재](https://wiki.g15e.com/pages/Law%20of%20conservation%20of%20complexity.txt)한다. 이 복잡성을 시스템에 관여하는 여러 요소(네트워크를 이룬 컴퓨터들과 네트워크를 이룬 인간들)의 제한된 부품들(메모리, CPU, 기억, 인지, 주의, 몸, 환경, 각 엔티티 간 정보전달채널의 지연, 대역폭, 정확성 등)에 가장 효율적으로 분배하고, 각 요소들을 [서로 이롭게 연결](https://wiki.g15e.com/pages/Beneficially%20relating%20elements.txt)하는 일이 디자인이다. 이 때 디자이너는 각 요소의 물리적 속성보다는 요소가 전체 시스템 내에서 [실제로 수행하는 기능 또는 역할이 무엇인지를 기준으로 생각](https://wiki.g15e.com/pages/Distributed%20functional%20decomposition.txt)해야 한다. [#ref](https://wiki.g15e.com/pages/Definition%20of%20design.txt#definition) 적을수록 좋다: - 할 수 있는 일의 양(capabilities)이 동일하다면 기능(features)이 적을수록 좋다. (참고: [기능보다는 가능성](https://wiki.g15e.com/pages/Capabilities%20over%20features.txt)) - 기능이 동일하다면 코드의 양이 적을수록 좋다. - 코드의 양이 동일하다면 오픈 소스의 비중이 높을수록 좋다. - 코드의 양이 동일하다면 절차적 코드보다 선언적 코드가 좋다. 강렬한 느낌 혹은 깊은 호기심: - 기존 방식을 크게 바꾸고 싶다는 강렬한 느낌 혹은 깊은 호기심. 예: "[그것은 나무가 아니다](https://wiki.g15e.com/pages/It%20is%20not%20a%20tree.txt)." - 세상에 있어야할 무언가가 아직 없다는 (혹은 세상에 없어야할 무언가가 아직 있다는) 강렬한 느낌 혹은 깊은 호기심. [각별히 뛰어난 사용성](https://wiki.g15e.com/pages/Exceptional%20usability.txt): - 배우기 쉬움과 사용하기 쉬움 모두를 달성할 방법을 깊게 고민한다. 타협하지 않기 위해 노력한다. - 타협을 할 수 밖에 없는 상황이라면 사용하기 쉬움을 선택한다. - [왜곡된 사용자 중심 디자인](https://wiki.g15e.com/pages/Distorted%20user-centered%20design.txt)을 하지 않는다. 결에 맞는 디자인: - 소프트웨어는 진공에 존재하지 않는다. 소프트웨어가 놓인 맥락에 따라 여러 방향의 자연스러운 "결"이 생긴다. 비즈니스적인 결, 기술적인 결, 디자인적인 결 등. 예를 들어 웹이라는 맥락에 놓인 소프트웨어는 와 이라는 결을 거스르지 않아야 한다. (참고: [시맨틱 HTML은 거의 은총알이다](https://wiki.g15e.com/pages/Semantic%20HTML%20is%20a%20silver%20bullet,%20mostly.txt)) - 결을 잘 맞추면 모든 게 쉽고 가벼워지는 반면 결을 거스르면 모든 게 어렵고 무거워진다. 잘 설계된 제약: - 뭘 안해야 하는지 구체적으로 알아야 나머지 가능성의 공간을 자유롭게 탐색할 수 있다. 잘 설계된 제약이 없으면 오히려 탐색에 제약이 생긴다. - 구조역학이 충분히 발달하고 제약이 극도로 정교해져야 비로소 다양한 현대적 건축물들이 탄생할 수 있게 된다. ## 내 취향에 영향을 준 소프트웨어/강연/글 (관사 빼고 알파벳순) - [The extended mind](https://wiki.g15e.com/pages/The%20extended%20mind%20(book.txt)) - [FIT](https://wiki.g15e.com/pages/Framework%20for%20integrated%20test.txt) - [The Humane Environment](https://wiki.g15e.com/pages/The%20Humane%20Environment.txt) - [Inventing on principle](https://wiki.g15e.com/pages/Inventing%20on%20principle.txt) - [Original Wiki](https://wiki.g15e.com/pages/Original%20Wiki.txt) - [Representational State Transfer](https://wiki.g15e.com/pages/Representational%20State%20Transfer.txt) ## 취향과 카피캣 취향이 부족하면 좋은 카피캣 조차도 만들 수 없다. 좋은 제품을 따라하려고 할 때 좋은 제품의 어떤 요소를 베껴야 하는지 감별할 능력이 부족하기 때문. 혹은 "개선"을 한다는 생각으로 개악을 하거나. 예를 들어 맥을 카피한 윈도의 경우, 시작 메뉴+테스크바+시스템 트레이가 10년 가까이 [피츠의 법칙](https://wiki.g15e.com/pages/Fitts%20law.txt)을 활용하지도 못하면서 괜히 가장자리를 낭비하고 있었다. ( 가 나오면서 드디어 해결됐던 걸로 기억한다.) ## 고려해볼 개념들 아직 잘 정리도지는 않았지만 더 곱씹어볼 개념들 - [UI density](https://wiki.g15e.com/pages/UI%20density.txt)
```

## Trace JSON

```json
{
  "source_url": "https://wiki.g15e.com/pages/Tasteful%20software.md",
  "route": {
    "input_url": "https://wiki.g15e.com/pages/Tasteful%20software.md",
    "normalized_host": "wiki.g15e.com",
    "route_id": "direct-then-fallback",
    "route_family": "public",
    "summary": "Try direct public fetch first, then reader, metadata-only, and archive fallback in order.",
    "required_tools": [
      "curl"
    ],
    "access_modes": [
      "grant",
      "public",
      "degraded"
    ],
    "fallback_order": [
      "direct-public-fetch",
      "content-negotiated-markdown",
      "domain-specific-route",
      "impersonated-public-fetch",
      "defuddle-reader-extraction",
      "patchright-render-recon",
      "patchright-network-recon",
      "agent-browser-render-recon",
      "agent-browser-network-recon",
      "reader-or-metadata-fallback",
      "archive-or-cache",
      "clean-stop"
    ],
    "acquisition_plan": [
      {
        "stage_id": "direct-public-fetch",
        "tool_id": null,
        "when": "Start here for public URLs unless a stronger domain route is known.",
        "proof": "classify-fetch-response"
      },
      {
        "stage_id": "content-negotiated-markdown",
        "tool_id": null,
        "when": "After a direct login wall or Markdown-looking URL, try the same public URL with an explicit Markdown Accept header.",
        "proof": "classify-fetch-response plus representation and route trace"
      },
      {
        "stage_id": "impersonated-public-fetch",
        "tool_id": "curl_cffi",
        "when": "Retry public HTML with browser-like TLS/HTTP impersonation before paying browser-render cost.",
        "proof": "classify-fetch-response plus impersonation profile"
      },
      {
        "stage_id": "defuddle-reader-extraction",
        "tool_id": "defuddle",
        "when": "Use for article-like public pages when direct HTML is weak, cluttered, or partial.",
        "proof": "clean markdown plus source URL and classifier confidence"
      },
      {
        "stage_id": "patchright-render-recon",
        "tool_id": "patchright",
        "when": "Use a headless Patchright Chromium render when fetch/reader paths are blocked, JS-rendered, or unclear.",
        "proof": "headless rendered body text and access mode"
      },
      {
        "stage_id": "patchright-network-recon",
        "tool_id": "patchright",
        "when": "For collection intent, record public-looking /api/, /graphql, or .json requests seen by headless Patchright.",
        "proof": "network request candidates; no clicks, form submits, or login bypass"
      },
      {
        "stage_id": "agent-browser-render-recon",
        "tool_id": "agent-browser",
        "when": "Use for JS-rendered pages, empty SPA shells, repeated challenge signals, or weak cleaner output.",
        "proof": "rendered body text/html and access mode"
      },
      {
        "stage_id": "agent-browser-network-recon",
        "tool_id": "agent-browser",
        "when": "Use for list/collection intent to record public-looking /api/, /graphql, or .json request candidates.",
        "proof": "network request candidates; no clicks, form submits, or login bypass"
      },
      {
        "stage_id": "archive-or-cache",
        "tool_id": null,
        "when": "Use only when a stale or cached source still honestly answers the request.",
        "proof": "archive/cache source identity and freshness caveat"
      },
      {
        "stage_id": "clean-stop",
        "tool_id": null,
        "when": "Stop when access, auth, challenge, or confidence gaps remain.",
        "proof": "recorded failure mode and missing capability"
      }
    ],
    "notes": [
      "Do not skip the direct path when the page may still be readable as plain HTML."
    ]
  },
  "disposition": "success",
  "attempts": [
    {
      "stage_id": "direct-public-fetch",
      "tool_id": null,
      "status": "success",
      "confidence": "weak",
      "elapsed_s": 0.476,
      "output_chars": 3929,
      "classification": {
        "status": "success",
        "confidence": "weak",
        "text_length": 3874,
        "matched_signals": [],
        "signals": [
          "long-text"
        ],
        "proof": [],
        "proof_errors": [],
        "fallback_candidates": [],
        "recommended_next_step": "Use the content as a source and preserve the retrieval method."
      }
    },
    {
      "stage_id": "content-negotiated-markdown",
      "tool_id": null,
      "status": "skipped",
      "confidence": "none",
      "elapsed_s": 0.0,
      "output_chars": 0,
      "details": {
        "reason": "prior-stage-sufficient"
      }
    },
    {
      "stage_id": "impersonated-public-fetch",
      "tool_id": "curl_cffi",
      "status": "skipped",
      "confidence": "none",
      "elapsed_s": 0.0,
      "output_chars": 0,
      "details": {
        "reason": "prior-stage-sufficient"
      }
    },
    {
      "stage_id": "defuddle-reader-extraction",
      "tool_id": "defuddle",
      "status": "skipped",
      "confidence": "none",
      "elapsed_s": 0.0,
      "output_chars": 0,
      "details": {
        "reason": "prior-stage-sufficient"
      }
    },
    {
      "stage_id": "patchright-render-recon",
      "tool_id": "patchright",
      "status": "skipped",
      "confidence": "none",
      "elapsed_s": 0.0,
      "output_chars": 0,
      "details": {
        "reason": "prior-stage-sufficient"
      }
    },
    {
      "stage_id": "patchright-network-recon",
      "tool_id": "patchright",
      "status": "skipped",
      "confidence": "none",
      "elapsed_s": 0.0,
      "output_chars": 0,
      "details": {
        "reason": "prior-stage-sufficient"
      }
    },
    {
      "stage_id": "agent-browser-render-recon",
      "tool_id": "agent-browser",
      "status": "skipped",
      "confidence": "none",
      "elapsed_s": 0.0,
      "output_chars": 0,
      "details": {
        "reason": "prior-stage-sufficient"
      }
    },
    {
      "stage_id": "agent-browser-network-recon",
      "tool_id": "agent-browser",
      "status": "skipped",
      "confidence": "none",
      "elapsed_s": 0.0,
      "output_chars": 0,
      "details": {
        "reason": "prior-stage-sufficient"
      }
    },
    {
      "stage_id": "archive-or-cache",
      "tool_id": null,
      "status": "skipped",
      "confidence": "none",
      "elapsed_s": 0.0,
      "output_chars": 0,
      "details": {
        "reason": "prior-stage-sufficient"
      }
    },
    {
      "stage_id": "clean-stop",
      "tool_id": null,
      "status": "skipped",
      "confidence": "none",
      "elapsed_s": 0.0,
      "output_chars": 0,
      "details": {
        "reason": "prior-stage-sufficient"
      }
    }
  ],
  "selected_attempt": {
    "stage_id": "direct-public-fetch",
    "tool_id": null,
    "status": "success",
    "confidence": "weak",
    "elapsed_s": 0.476,
    "output_chars": 3929,
    "classification": {
      "status": "success",
      "confidence": "weak",
      "text_length": 3874,
      "matched_signals": [],
      "signals": [
        "long-text"
      ],
      "proof": [],
      "proof_errors": [],
      "fallback_candidates": [],
      "recommended_next_step": "Use the content as a source and preserve the retrieval method."
    }
  },
  "final_status": "success",
  "final_confidence": "weak"
}
```
