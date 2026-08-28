"""Stable constants and input errors shared by the task-run owners."""

from __future__ import annotations

import re

PASS = "pass"
FAIL = "fail"
SCHEMA_VERSION = 1
TASK_MODEL = "gpt-5.6-luna"
TASK_EFFORTS = ("medium", "xhigh", "max")
_GIT_DISCOVERY_ENV = ("GIT_DIR", "GIT_COMMON_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE")
_BRANCH_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]*$")
_TASK_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,95}$")


class TaskRunError(ValueError):
    """A task-run preflight input is not safe or resolvable."""
