from __future__ import annotations

DEFAULT_DRAFT_ACTIVE_FRAME_LINES = (
    "- Current slice: before activation.",
    "- Current slice intent: before activation. The reviewable-intent unit in progress",
    "  and the commits it spans; critique and broad proof do not re-fire within one",
    "  unchanged intent — update it when the intent changes, not per commit",
    "  (meaningful-slice-cadence).",
    "- Next action: activate with `/goal @{goal_rel}`.",
    "- Verification cadence: cheap deterministic checks at commit boundaries;",
    "  higher-cost or fresh-eye proof at slice boundaries; final broad/live proof at",
    "  closeout.",
    "- Gate cadence: pre-lock slices use `run_slice_closeout.py --skip-broad-pytest`;",
    "  final/bundle proof records the verification lock and uses `--verification-lock`.",
    "- Slice review packet: before fresh-eye slice critique, provide intent, changed",
    "  files and owning/generated surfaces, expected invariants, tests/proof,",
    "  non-claims, out-of-scope lines, and reviewer questions.",
    "- History boundary: keep this frame current; move completed detail to",
    "  `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.",
)


def render_draft_active_frame(lines: list[str] | tuple[str, ...], *, goal_rel_path: str) -> str:
    return "\n".join(line.replace("{goal_rel}", goal_rel_path) for line in lines)


def render_goal_template(
    template: str,
    *,
    title: str,
    date: str,
    status: str,
    goal_rel_path: str,
    goal_body: str,
    frame_lines: list[str],
) -> str:
    return template.format(
        title=title,
        date=date,
        status=status,
        goal_rel=goal_rel_path,
        active_frame=render_draft_active_frame(frame_lines, goal_rel_path=goal_rel_path),
        goal_body=goal_body.strip() or "_State the desired outcome before activation._",
    )
