"""Default backend command templates for issue closeout."""

from __future__ import annotations

GH_COMMENT_DEFAULT = ["issue", "comment", "--repo", "{repo}", "{number}", "--body-file", "{body_file}"]
GH_CLOSE_DEFAULT = ["issue", "close", "--repo", "{repo}", "{number}", "--reason", "{reason}"]
GH_VIEW_DEFAULT = ["issue", "view", "--repo", "{repo}", "{number}", "--json", "{json_fields}"]
GH_VIEW_TARGET_DEFAULT = [
    "issue", "view", "--repo", "{repo}", "{number}", "--json", "number,state,url,body"
]

COMMENT_PLACEHOLDERS: frozenset[str] = frozenset({"repo", "number", "body_file", "reason"})
CLOSE_PLACEHOLDERS: frozenset[str] = frozenset({"repo", "number", "reason"})
VIEW_PLACEHOLDERS: frozenset[str] = frozenset({"repo", "number", "json_fields"})
