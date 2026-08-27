from __future__ import annotations

DEFAULT_DRAFT_ACTIVE_FRAME_LINES = (
    "- Current slice: real draft/backlog awaiting activation.",
    "- Current slice intent: real draft/backlog awaiting activation; reshape before",
    "  activating if the acceptance boundary has changed. Once active, this names",
    "  the reviewable-intent unit in progress and the commits it spans.",
    "- Next action: activate with `/goal @{goal_rel}` after confirming the draft is",
    "  still intended.",
    "- History boundary: keep this frame current; move completed detail to",
    "  `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.",
)


def render_draft_active_frame(
    lines: list[str] | tuple[str, ...],
    *,
    goal_rel_path: str,
    execution_efficiency_context_path: str | None = None,
) -> str:
    rendered = [line.replace("{goal_rel}", goal_rel_path) for line in lines]
    if execution_efficiency_context_path:
        rendered.append(
            "- Execution-efficiency context: read "
            f"`{execution_efficiency_context_path}` before shaping and at resumed-goal pickup."
        )
    return "\n".join(rendered)


def render_goal_template(
    template: str,
    *,
    title: str,
    date: str,
    status: str,
    goal_rel_path: str,
    goal_body: str,
    frame_lines: list[str],
    execution_efficiency_context_path: str | None = None,
) -> str:
    return template.format(
        title=title,
        date=date,
        status=status,
        goal_rel=goal_rel_path,
        active_frame=render_draft_active_frame(
            frame_lines,
            goal_rel_path=goal_rel_path,
            execution_efficiency_context_path=execution_efficiency_context_path,
        ),
        goal_body=goal_body.strip() or "_State the desired outcome before activation._",
    )
