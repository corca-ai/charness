"""In-process doubles for release resume edge contracts.

These doubles deliberately expose command intent without constructing a repository.  The
edge tests use them for state-machine and refusal matrices; a smaller resilience suite
retains the real Git/process paths for representative end-to-end proof.
"""

from __future__ import annotations

from types import SimpleNamespace


class ClaimsResumeCli:
    def __init__(
        self,
        commands: list[list[str]],
        *,
        notes_preflights: list[dict] | None = None,
        allow_create: bool = False,
        verify_returncode: int = 0,
        version_surface_error: str | None = None,
    ):
        self.commands = commands
        self.notes_preflights = notes_preflights if notes_preflights is not None else []
        self.allow_create = allow_create
        self.verify_returncode = verify_returncode
        self.version_surface_error = version_surface_error
        self.version_surface_checks: list[dict] = []
        self.final_artifact_commits: list[dict] = []
        self.finalized_payloads: list[dict] = []

    def run(self, command, *, cwd, check=True):
        self.commands.append(command)
        return SimpleNamespace(returncode=0, stdout="https://example.test/v1.2.3")

    def run_notes_file_preflight(
        self, repo_root, *, target_tag, notes_file, on_resume=False, previous_version=None
    ):
        self.notes_preflights.append(
            {
                "target_tag": target_tag,
                "notes_file": notes_file,
                "on_resume": on_resume,
                "previous_version": previous_version,
            }
        )

    @staticmethod
    def backend_command(_backend, _operation, fallback):
        return fallback

    @staticmethod
    def release_content_close_keyword_refs(_text):
        return []

    @staticmethod
    def run_fresh_checkout_probes(_root):
        return {"status": "passed"}

    @staticmethod
    def expected_github_release_url(_root, _backend, _tag):
        return "https://example.test/v1.2.3"

    def ensure_release_surface(self, _repo_root, expected_version, *, stage):
        self.version_surface_checks.append({"version": expected_version, "stage": stage})
        if self.version_surface_error:
            raise SystemExit(self.version_surface_error)
        return {
            "status": "passed",
            "stage": stage,
            "checked_version": expected_version,
            "surfaces": ["packaging/charness.json", "plugins/charness/.codex-plugin/plugin.json"],
            "drift": [],
        }

    def verify_release_visible(self, *_args, **_kwargs):
        return SimpleNamespace(
            returncode=self.verify_returncode,
            args=["gh", "release", "view", "v1.2.3"],
            stdout="",
            stderr="release not found",
        )

    def finalize_release_payload(self, _repo_root, payload, **_kwargs):
        self.finalized_payloads.append(dict(payload))

    def commit_final_release_artifact(self, *_args, **kwargs):
        self.final_artifact_commits.append(kwargs)

    @staticmethod
    def fail_after_post_create_verification(_payload, *, verification_result):
        raise SystemExit(
            "release post-create verification failed after external mutation\n"
            f"exit_code: {verification_result.returncode}"
        )

    def create_release(self, *_args, **_kwargs):
        if not self.allow_create:
            raise AssertionError("existing release should not be created again")
        return SimpleNamespace(returncode=0, stdout="https://example.test/v1.2.3")


class ClaimsResumeCommon:
    @staticmethod
    def preflight_close_issue_carrier(*_args, **_kwargs):
        return None

    @staticmethod
    def run_pre_push_quality_gates(*_args, **_kwargs):
        return None

    @staticmethod
    def timed(_payload, _label, action):
        return action()

    @staticmethod
    def run_release_closeout_tail(*_args, **_kwargs):
        return None


class ResumeCli:
    def __init__(
        self,
        *,
        changed: list[str],
        files: dict[str, str],
        push_error: bool = False,
        remote_sha: str = "",
    ):
        self.changed = changed
        self.files = files
        self.push_error = push_error
        self.remote_sha = remote_sha
        self.commands: list[list[str]] = []

    def run(self, command, *, cwd, check=True):
        self.commands.append(command)
        if command[:2] == ["git", "show"]:
            path = command[2].split(":", 1)[1]
            return SimpleNamespace(
                returncode=0 if path in self.files else 1,
                stdout=self.files.get(path, ""),
            )
        if command[:3] == ["git", "diff-tree", "--no-commit-id"]:
            return SimpleNamespace(returncode=0, stdout="\n".join(self.changed))
        if command[:2] == ["git", "push"]:
            if self.push_error:
                raise RuntimeError("connection lost after remote receipt")
            return SimpleNamespace(returncode=0, stdout="")
        if command[:2] == ["git", "ls-remote"]:
            return SimpleNamespace(returncode=0, stdout=f"{self.remote_sha}\trefs/heads/main\n")
        raise AssertionError(f"unexpected command: {command}")

    @staticmethod
    def validate_release_observer_record(_record):
        return None

    @staticmethod
    def validate_release_closeout_commit_message(*_args, **_kwargs):
        return {"ok": True}


class ClassifierCli:
    """Enough Git for ``resumable_state``, and nothing that reaches a repository."""

    MARKER = "charness-release-state:prepared-awaiting-claims-review"

    def __init__(
        self,
        *,
        revs: dict[str, str],
        subject: str,
        messages: dict[str, str],
        tag_local: bool = True,
        close_refs: list[str] | None = None,
        marked: tuple[str, ...] = (),
        parents: dict[str, str] | None = None,
        children: dict[str, str] | None = None,
        evidence_changed: list[str] | None = None,
        evidence_changed_by_commit: dict[str, list[str]] | None = None,
    ):
        self.revs = revs
        self.subject = subject
        self.messages = messages
        self.tag_local = tag_local
        self.close_refs = close_refs or []
        self.marked = marked
        self.parents = parents or {}
        self.children = children or {}
        self.evidence_changed = evidence_changed or ["charness-artifacts/release-review/r.json"]
        self.evidence_changed_by_commit = evidence_changed_by_commit or {}
        self._helpers = SimpleNamespace(
            tag_exists=lambda *_a, **_k: {
                "local": tag_local,
                "remote": True,
                "remote_tag_sha": revs.get("tag", ""),
            },
            release_exists=lambda *_a, **_k: True,
        )

    def run(self, command, *, cwd, check=True):
        args = command[1:]
        if args[:2] == ["log", "-1"]:
            return SimpleNamespace(returncode=0, stdout=self.subject)
        if args[:1] == ["rev-parse"]:
            return SimpleNamespace(returncode=0, stdout=self.revs.get(args[1], ""))
        if args[:3] == ["show", "-s", "--format=%P"]:
            parent = self.parents.get(args[-1])
            return SimpleNamespace(returncode=0 if parent is not None else 1, stdout=parent or "")
        if args[:2] == ["show", "-s"]:
            return SimpleNamespace(returncode=0, stdout=self.messages.get(args[-1], ""))
        if args[:1] == ["show"]:
            commit = args[1].split(":", 1)[0]
            if commit in self.marked:
                return SimpleNamespace(
                    returncode=0,
                    stdout=f"# Release\n<!-- {self.MARKER} -->\n",
                )
            return SimpleNamespace(returncode=0, stdout="# Release\n")
        if args[:1] == ["rev-list"] and "--all" in args:
            return SimpleNamespace(
                returncode=0,
                stdout="".join(f"{child} {parent}\n" for parent, child in self.children.items()),
            )
        if args[:1] == ["rev-list"]:
            return SimpleNamespace(returncode=0, stdout=self.revs.get("tag", ""))
        if args[:2] == ["diff-tree", "--no-commit-id"]:
            changed = self.evidence_changed_by_commit.get(args[-1], self.evidence_changed)
            return SimpleNamespace(returncode=0, stdout="\n".join(changed))
        if args[:1] == ["merge-base"]:
            return SimpleNamespace(returncode=0, stdout="")
        if args[:1] == ["ls-remote"]:
            return SimpleNamespace(returncode=0, stdout="remote-sha\trefs/heads/main\n")
        raise AssertionError(f"unexpected command: {command}")

    def release_content_close_keyword_refs(self, text):
        return list(self.close_refs) if "Close #" in text else []
