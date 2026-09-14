"""Stable constants and input errors shared by the task-run owners."""

from __future__ import annotations

import re

PASS = "pass"
FAIL = "fail"
SCHEMA_VERSION = 1
TASK_MODEL = "gpt-5.6-luna"
TASK_EFFORTS = ("medium", "xhigh", "max")
TASK_EXECUTORS = ("codex", "muse")
TASK_EXECUTOR_DEFAULT = "codex"
# Muse (Meta) lanes run the `muse` CLI's default model; the runner pins only
# the reasoning effort. `high` is the muse default and the curator-approved
# lane preset alongside the shared medium/xhigh/max set.
TASK_MUSE_EFFORTS = ("medium", "high", "xhigh", "max")
TASK_MUSE_MODEL = "default"
_GIT_DISCOVERY_ENV = ("GIT_DIR", "GIT_COMMON_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE")
_BRANCH_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]*$")
_TASK_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,95}$")


class TaskRunError(ValueError):
    """A task-run preflight input is not safe or resolvable."""
