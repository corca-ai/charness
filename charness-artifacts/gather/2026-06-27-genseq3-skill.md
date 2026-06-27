# Gathered Public URL

- Source: https://raw.githubusercontent.com/cjunekim/claude-config/refs/heads/main/skills/genseq3/SKILL.md
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
- Chars: `21548`
- Original Chars: `21548`
- Truncated: `False`

```text
--- name: genseq3 description: EXPLICIT-INVOCATION ONLY — the abstract-recipe variant of genseq2's structural-shape routing. It classifies a task into the best and next-best of seven sequence shapes (Pilot-and-Scale, Vertical-Slice-Growth, Organic-Expansion, Align-then-Prototype, Open-then-Deepen, Envision-then-Provision, Anchor-then-Enclose) and fuses the two matching abstract step-recipes, falling back to the living-process principles when no shape fits. Use this skill ONLY when the user types "/genseq3" or asks for "genseq3" by name. Do NOT auto-trigger on planning, sequencing, ordering, or "what order should I do X" tasks — the genseq skill handles those. If the user has not named genseq3 explicitly, do not invoke it. --- # Christopher Alexander — source material for genseq > **Copyright note.** The numbered principles and quoted passages in this file are reproduced from > Christopher Alexander, *The Nature of Order*, Books 2–3 (© Christopher Alexander / Center for > Environmental Structure), quoted for commentary and education and **not** covered by this > repository's MIT License. These are, verbatim, the living-process principles this skill is built on — the method itself, not background reading. Absorb the stance they describe, then use it to form concrete sequences. The principles are organically related — one coherent stance, not a checklist to apply literally one by one. From Christopher Alexander, *The Nature of Order* (Books 2–3). ## Ten Essential Features of a living process (Book 2) 1. A living process is a step-by-step adaptive process, which goes forward in small increments, with opportunity for feedback and correction at every increment (discussed in Chapter 8). 2. It is always the whole which governs in a living process. Whatever greater whole is latent is always the main focus of attention and the driving force which controls the shaping of the parts (discussed in Chapter 9). 3. The entire living process will be governed and guided and moved forward by the formation of living centers in such a way that the centers help each other (discussed in Chapter 10). 4. The steps of a living process always take place in a certain vitally important sequence, and the coherence of its results will be dependent to a large extent on the accuracy of this sequence which controls unfolding (discussed in Chapter 11). 5. Parts which are created during the process of differentiation must become locally unique; otherwise, the process is not a living process. This means that all repetition is based on the uniqueness of the locally shaped parts, each adapted, by the process, to its situation within the whole (discussed in Chapter 12). 6. The formation of centers (along with the sequence of their unfolding) is guided by generic patterns which play the role of genes (discussed in Chapter 13). 7. Every living process is, throughout its length and breadth, congruent with feeling and governed by feeling (discussed in Chapter 14). 8. In the case of buildings, the formation of the structure is guided geometrically by the emergence of an aperiodic grid which brings coherent geometric order to built form (discussed in Chapter 15). 9. The entire living process is oriented by a form language that provides concrete methods of implementing adapted structure through simple combinatory rules (discussed in Chapter 16). 10. The entire living process is oriented by the simplicity transformation, and is pruned steadily, so that it moves towards formation of a beautiful simplicity (discussed in Chapter 17). ## The Fundamental Process (Book 3) 1. At each step, the process begins with a perception of the whole. At every step (whether it is conceiving, designing, making, maintaining, or repairing) we start by looking at and thinking about the whole of that part of the world where we are working. We look at this whole, absorb it, try to feel its deep structure. 2. Within the whole, we consider the latent centers which might be worked on next. These latent centers are dimly, partially visible, large, medium, and small. 3. We choose that one of these latent centers which, if established or strengthened next, will do the most to give the whole an increase of life. We work to intensify that living center, intensifying it in a way which, we judge, does the most good to the whole. 4. At the same time that we try to enhance the living quality of this chosen center, we also try to make it intensify the life of some larger center that it belongs to. 5. Simultaneously, we also make or strengthen at least one center of the same size as the center we are working on, and make it positive, next to the center we are currently concentrating on. 6. Simultaneously, we also start to see, and make, and strengthen smaller centers within the one we are working on -- increasing their life, too. 7. Once the whole has been modified by this operation, we start again. All living processes, in my definition, are combinations and sequences of this fundamental process. ## A worked example of the Fundamental Process: laying out an office From Book 3, Chapter 12 ("The Uniqueness of People's Individual Worlds"), §10 — the Office Layout Process. Alexander's own step-by-step sequence for laying out a workplace: a concrete instance of the Fundamental Process — perceive the whole (how you actually work), find which center matters most, place it first, and let each further center help the ones already there. ### How your office works **What you really do when you work.** "Above all, you must get clear about your actual work habits, that means the way you really work." "One way to get clear about what you do is to pay attention to the following list of processes that may play a role in your work. Rank order them according to the relative importance they have in your own work by writing a number after each one." — Use of desk · Files, filing and storage · Computer use · Conference · Clients · Discussion · Concentration · Using library · Telephoning · Access to records · Overview of projects · Other machines (FAX, xerox etc) · Connection with your staff · Drawing and layout. **Dream about your ideal working conditions.** "Now start going through the short list of key processes, one by one, in the order you have ranked them. Start with the first one. Ask yourself which place or occasion you can remember where this particular kind of activity was working best." "Dream as much as you want and identify the most idyllic and best circumstance you can remember and that you wish was happening in your daily life every day." **Define the essence of the dream condition for each process.** "Now, if you have a vision of the dream condition for each process, write down the key essential elements which made it happen. This is hard to do. To do it, you must construct the essential elements in the form of a center." ### The layout process "You are now in a position to start visualizing the way your office really needs to be. To help this visualization, set up the cardboard model so that it is like your own office." "Now use the model to do the following steps one at a time." *Position of the major centers* 1. **Identify the natural centers of the room.** "Use the small red markers to identify the natural centers in the room which is to be your office." 2. **Window place.** "Mark the spot near the window which is most likely to develop as a window place. Put a white sticker there." 3. **Entrance transition.** "Mark the zone inside the door which needs to be a transition area, so that your room feels protected emotionally from the open doorway. Put a black sticker there." 4. **Locate the main center of your work.** "Now decide in which of the naturally occurring centers you will put the process you have defined as C1, the main center of your work. Use the red spot to mark this main center." 5. **Locate the secondary centers of your work.** "Decide in which of the naturally occurring centers you will put the processes you have defined as C2, C3, C4, the secondary centers of your work. Use the green stickers to mark these secondary centers." 6. **Overlap.** "Note, in what you have just done, and in what you are going to do next, it is essential to remember that different centers may overlap each other." *Layout of the major centers* 7. **Discussion and conference.** "If your main activity is meeting or conferences, to make your room suitable... it may be very helpful to make the main center a conference table." 8. **Your main work surface.** "Choose the main center in the room where you are actually going to work... Fix the main work surface of your work place." 9. **Secondary horizontal surfaces.** "Along with your desk or main work surface, you may need secondary work surfaces. These can be at right angles to the main one." 10. **Sparkling daylight.** "Place wall lights along one or two walls in positions which help to define the area you have designated as the main center of the room... Place reflectors below the wall lights, or above them." …and so on. ## Check information before starting The sequence is only as good as your read of the whole. If necessary information is missing — who the stakeholders are, what the task is for, what counts as good, important constraints, the medium — ask the user before sequencing. Those are prelaid centers. We should start from this configuration and do structure-preserving transformation. Use the request_user_input tool for Codex, and the AskUserQuestion tool for Claude Code, when it fits — or simply ask in natural language in the prose. A short pause to ask is cheaper than a sequence built on guessed requirements. Answers we get from those questions should reveal the most important latent centers even before we lay down the first center in the step 1. You can make assumptions about the pre-laid centers if they seem trivial. However, if misrecognizing any one center would destroy the wholeness or be hard to undo, you MUST ask about it and check it. Before step 1, separate what the prompt has already placed from what still has to be created. A stated arrangement, limit, prior commitment, available material, existing partial artifact, named person, implied audience, access point, or coordination constraint is not scenery; it is a center with ordering force. If later steps depend on outside agreement, availability, acceptance, understanding, use, or changed behavior, put the smallest consequential alignment or trial before detailed construction. The step must expose a real prerequisite, commitment, or reaction that can change the next structural choice. ## Executing the sequence (optional) This skill produces a *plan*, not the finished thing — and a sequence is only as good as its execution. If you build it and let the artifact sit broken between steps, a defect can hide and compound, which is the very cost the ordering was meant to avoid. The **saligo** skill is the matching execution discipline: keep the thing runnable at every step, so each sequence step becomes a small working → broken → working excursion with the break caught immediately. This is for how you *work* the sequence. ## Structural shape routing You must first classify the requested sequence, before writing any step, by the shape of its desired unfolding, not by topic. Use the classification to choose the arc of the sequence; do not copy any domain wording from these labels. You have to choose the best classification, and then the next best classification. Fuse the two when coming up with the final sequence. The two should complement each other with synergy so that it increases the life of the whole. - Pilot-and-Scale: the finished whole must work for many units, cases, people, or runs. Start with one concrete case, make it observable, then expand through small comparable batches. - Vertical-Slice-Growth: one artifact or system must grow in place. Start with the smallest working slice in the final medium, then add one dependent capability at a time. - Organic-Expansion: one expression, argument, or composition grows outward from a seed. Start with the smallest phrase, claim, scene, or unit that carries the whole, then elaborate the part whose growth most helps the whole. - Align-then-Prototype: success depends on an outside decision, buy-in, acceptance, or shared direction. Align with the load-bearing person or group before making detailed artifacts. - Open-then-Locally-Grow: multiple participants move together through a live, forward-only process that cannot be redone. Picture the end-state first, open from the lowest-friction shared start, deepen engagement in small escalating low-risk rounds, and close by making the changed shared state explicit. - Envision-then-Provision: the goal is a bounded experience or undertaking, not a built artifact. Picture the desired experience, translate it into conditions, secure scarce commitments, then arrange flexible details. - Anchor-then-Enclose: several distinct centers must coexist within one bounded field and reinforce one another — no population to scale to, no single seed grown outward, and the extent of the field is itself part of the problem. Name the centers, set the field loosely to fit them, anchor the dominant center first, position each further center to strengthen those already placed, and enclose it last within a bounding frame that supplements the centers rather than predefining them. - Generic: if no other shape fits, use the living-process principles above (of Book 2 and Book 3) directly. Begin your answer with a required route line, before any numbered step: Route: + — . This is not optional — writing the route first is what forces the classification to actually happen and shape the steps, instead of defaulting to a generic plan. Then apply the matched recipes' arcs to the requested whole. Keep the numbered steps themselves focused on the user's requested whole. ## Abstract shape recipes Use these as structural arcs only. Translate them into the local centers already present in the prompt. Do not introduce domain examples from this section. ### Pilot-and-Scale 1. Find the smallest real unit whose response can prove whether the whole is alive. 2. Choose the seed using evidence from prior reactions, constraints, or observed need rather than self-description. 3. Make the seed visible in a form another unit can react to. 4. Add the minimal path by which one unit can actually use, accept, answer, or reject it. 5. Put it before a few real units and preserve what they do. 6. Compare responses, adjust the seed, then expand only to the next small batch. ### Vertical-Slice-Growth 1. Put one visible working fragment in the final medium. 2. Add the defining motion, transformation, or interaction. 3. Add direct control or input over that fragment. 4. Replace placeholders with the smallest real composed unit. 5. Add the first boundary, collision, validation, or persistence rule that the next step depends on. 6. Repeat the working cycle before broadening features, polish, modes, or scale. ### Organic-Expansion 1. Find the smallest seed that already leans toward the whole. 2. Grow it one level and read or inspect the result. 3. Split any compressed move into its distinct parts. 4. Expand the part whose weakness most limits the whole. 5. Reorder and prune before adding a new layer. 6. Stop when the requested whole is present, not when all possible elaborations are exhausted. ### Align-then-Prototype 1. State the purpose and the stakes as the current best read. 2. Take that read to the load-bearing person or group while it is still easy to change. 3. Bring in the smallest reality-check group touched by the decision. 4. Try the idea aloud or in a very small artifact before making the full artifact. 5. Convert what lands into a compact prototype. 6. Trial it with the decision-maker and affected people before scaling depth, polish, or duration. ### Open-then-Locally-Grow 1. Picture the end-state for the whole and for each participant within it. 2. Begin from the lowest-friction shared element already present. 3. Draw a light initial orientation or contribution from each participant. 4. Escalate from small, low-risk exchanges to a shared consolidation of what surfaced. 5. Deepen within small subsets, then return the strongest material to the whole. 6. Close by making the changed shared state explicit. ### Envision-then-Provision 1. Imagine the desired lived state before choosing logistics. 2. Translate the lived state into concrete conditions. 3. Search or design against those conditions. 4. Secure scarce, time-sensitive, or hard-to-reverse commitments. 5. Arrange the flexible interior around the fixed bones. 6. Leave convenience and polish until the core experience is protected. ### Anchor-then-Enclose 1. Name the functions or forces at play as generic centers; do not begin from the container, its outline, or its conventional parts. 2. Rough out the whole's overall scope and rough proportions, sized loosely to fit those centers — not fixed as a boundary before the centers are placed. 3. Establish the orienting condition every placement will be judged against — the governing quality or flow the centers must align to — since each center's value depends on its relation to it. 4. Anchor the single dominant center first, at the strongest position the field affords; every other center is located in relation to it. 5. Add each remaining center in turn, positioning it to strengthen the centers already placed and to balance the whole — never in isolation, and letting centers overlap rather than forcing them apart. 6. Enclose the field last with the bounding frame, shaped to supplement the established centers rather than to predefine them; then move through the whole and prune what weakens it. ## Sequence output discipline When turning the living process into a numbered answer, describe the shortest path by which the requested whole can unfold. Do not describe the finished product roadmap. Start with the smallest live proof, one size smaller than the obvious finished form and one layer closer to the native material. Do not begin with the conventional scaffold, named unit, full container, or standard parts merely because the prompt names them. Choose the smallest inspectable fragment that can prove the central relation through a concrete behavior, exchange, wording, decision, or artifact change. Prove one primitive action on it, using a manual, fixed-input, scripted, hard-coded, or lightweight stand-in when that reveals the core behavior faster than general machinery. Then add only the nearest boundary, rule, or control that the next step will depend on. Add fuller structure, repetition, persistence, aggregation, convenience, production medium, polish, or broad rollout only after the live proof and its primitive dependencies work and only when they are needed for the requested whole. Keep each numbered step to one main transformation plus its checkable result. Each step should add one new center, rule, dependency, or capacity that later steps can lean on. Split any step that both creates a mechanism and consumes it, or that bundles setup, execution, measurement, expansion, persistence, aggregation, interface polish, or error handling before those pieces have been observed separately. Treat familiar templates, outlines, feature sets, and artifact conventions as background constraints, not as the sequence itself. First identify the native substrate the requested whole is literally made from: a word, sentence, exchange, record, comparison, transaction, decision, observable behavior, or other primitive unit that can actually change. If a proposed step names a container, section, screen, role, feature, polish pass, or conventional part before this substrate has produced an inspectable result, it is probably slot filling; revise it so the step consumes the current fragment, changes the native material, and lets that result determine the next structural addition. When the deliverable is only a carrier for a later lived experience, prototype the experience in the least formal native medium that can expose the central relation before polishing the carrier. Use a scale ladder whenever the work involves uncertainty, generated outputs, many cases, many participants, many variants, or a proposed organizational change. First make one concrete case work end to end with fixed inputs and plain observable output. Then repeat it, make reruns comparable, expose failures, preserve raw records, try a small varied set, then a representative slice, and only then move to full scale. Each rung must produce evidence that decides what changes before the next rung. Put durable checkpoints before dependent work: a baseline read of the present whole, an explicit hypothesis or specification when the path is uncertain, raw outputs from the first run, visible failure cases, and a decision point for recalibration. When learning what matters, include unusually successful, unusually failed, or otherwise discrepant cases if they can reveal hidden structure. Aggregate, automate, institutionalize, or polish only after the raw result is inspectable. Stop at the requested whole. Leave advanced controls, secondary modes, cosmetic polish, exports, dashboards, analytics, broad sharing, permanent operations, and convenience features out of the numbered sequence unless the prompt makes them central or they are necessary to verify the whole. A good sequence is compact: enough steps to preserve order, not enough to become a feature backlog.
```

## Trace JSON

```json
{
  "source_url": "https://raw.githubusercontent.com/cjunekim/claude-config/refs/heads/main/skills/genseq3/SKILL.md",
  "route": {
    "input_url": "https://raw.githubusercontent.com/cjunekim/claude-config/refs/heads/main/skills/genseq3/SKILL.md",
    "normalized_host": "raw.githubusercontent.com",
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
      "elapsed_s": 0.191,
      "output_chars": 21680,
      "classification": {
        "status": "success",
        "confidence": "weak",
        "text_length": 21548,
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
    "elapsed_s": 0.191,
    "output_chars": 21680,
    "classification": {
      "status": "success",
      "confidence": "weak",
      "text_length": 21548,
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
