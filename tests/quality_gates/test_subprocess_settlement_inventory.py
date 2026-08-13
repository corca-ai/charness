from __future__ import annotations

import ast
import importlib.util
import json
from pathlib import Path
from types import ModuleType

from tests.script_main import load_script_module, run_loaded_script_main

from .support import ROOT

SCRIPT = ROOT / "skills" / "public" / "quality" / "scripts" / "inventory_standing_test_economics.py"
SURFACE_LIB = ROOT / "skills" / "public" / "quality" / "scripts" / "surface_marker_lib.py"


def _load_surface_marker_lib() -> ModuleType:
    spec = importlib.util.spec_from_file_location("surface_marker_lib_for_settlement_test", SURFACE_LIB)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _run_inventory_cli(*args: str):
    return run_loaded_script_main(
        "inventory_standing_test_economics.py",
        load_script_module("inventory_standing_test_economics_for_settlement_test", SCRIPT),
        *args,
    )


def test_subprocess_settlement_seams_are_conservative_and_callsite_attributed(tmp_path: Path) -> None:
    lib = _load_surface_marker_lib()
    repo = tmp_path / "repo"
    repo.mkdir()
    tests = repo / "tests"
    tests.mkdir()
    fixture = tests / "test_settlement.py"
    fixture.write_text(
        "import subprocess\n\n"
        "def test_bounded():\n"
        "    subprocess.run(['probe'], timeout=5, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)\n\n"
        "def test_unbounded_capture():\n"
        "    subprocess.run(['probe'], capture_output=True)\n\n"
        "def test_mixed_output():\n"
        "    subprocess.run(['probe'], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)\n\n"
        "def test_unknown_lifecycle():\n"
        "    subprocess.Popen(['observe'])\n\n"
        "def test_dynamic_timeout():\n"
        "    subprocess.run(['probe'], timeout=maybe_timeout)\n",
        encoding="utf-8",
    )

    assert lib.subprocess_settlement_seams(repo, [fixture]) == [
        {"path": "tests/test_settlement.py", "line": 4, "call": "subprocess.run", "deadline": "present", "lifecycle": "finite", "process_tree_termination": "unknown", "output_bounding": "bounded"},
        {"path": "tests/test_settlement.py", "line": 7, "call": "subprocess.run", "deadline": "absent", "lifecycle": "unknown", "process_tree_termination": "unknown", "output_bounding": "unbounded"},
        {"path": "tests/test_settlement.py", "line": 10, "call": "subprocess.run", "deadline": "absent", "lifecycle": "unknown", "process_tree_termination": "unknown", "output_bounding": "unbounded"},
        {"path": "tests/test_settlement.py", "line": 13, "call": "subprocess.Popen", "deadline": "absent", "lifecycle": "unknown", "process_tree_termination": "unknown", "output_bounding": "unknown"},
        {"path": "tests/test_settlement.py", "line": 16, "call": "subprocess.run", "deadline": "unknown", "lifecycle": "unknown", "process_tree_termination": "unknown", "output_bounding": "unknown"},
    ]

    js_fixture = tests / "test_settlement.js"
    js_fixture.write_text(
        "execSync('probe', { timeout: 1000, stdio: 'ignore' });\n"
        "execSync('observe', { timeout: maybeUndefined });\n",
        encoding="utf-8",
    )
    assert lib.subprocess_settlement_seams(repo, [js_fixture]) == [
        {"path": "tests/test_settlement.js", "line": 1, "call": "execSync", "deadline": "present", "lifecycle": "finite", "process_tree_termination": "unknown", "output_bounding": "bounded"},
        {"path": "tests/test_settlement.js", "line": 2, "call": "execSync", "deadline": "unknown", "lifecycle": "unknown", "process_tree_termination": "unknown", "output_bounding": "unknown"},
    ]


def _js_states(lib, repo: Path, source: str) -> list[tuple[str, int, str, str]]:
    path = repo / "tests" / "probe.js"
    path.write_text(source, encoding="utf-8")
    return [
        (seam["call"], seam["line"], seam["deadline"], seam["lifecycle"])
        for seam in lib.subprocess_settlement_seams(repo, [path])
    ]


def test_a_js_deadline_expression_is_never_read_as_a_literal(tmp_path: Path) -> None:
    """The claim "only literal numeric deadlines yield finite" was FALSE on the JS path.

    The value pattern was ``[^,}\\s]+``, which stops at the first space, so it captured a
    PREFIX: `30 * 1000` yielded `30`, matched the numeric test, and reported a finite
    deadline for an expression the scanner cannot evaluate. Only the unspaced non-numeric
    form the round-2 fixture happened to cover ever reached `unknown`.
    """
    lib = _load_surface_marker_lib()
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)

    for source in (
        "execSync('probe', { timeout: 30 * 1000 });\n",
        "execSync('probe', { timeout: 5 + delay });\n",
        "execSync('probe', { timeout: MINUTES * 60 });\n",
        "execSync('probe', { timeout: opts.timeoutMs });\n",
    ):
        assert _js_states(lib, repo, source) == [("execSync", 1, "unknown", "unknown")], source


def test_a_js_zero_timeout_is_no_deadline_not_a_finite_one(tmp_path: Path) -> None:
    """`child_process` applies its timeout only when the value is greater than zero, so
    `timeout: 0` is the documented spelling of "no deadline". The predecessor classified
    it `present`/`finite` -- the inverse of the truth, on a settlement-risk surface whose
    whole purpose is to say which calls can hang."""
    lib = _load_surface_marker_lib()
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)

    assert _js_states(lib, repo, "execSync('probe', { timeout: 0 });\n") == [
        ("execSync", 1, "absent", "unknown")
    ]
    assert _js_states(lib, repo, "execSync('probe', { timeout: 0.0 });\n") == [
        ("execSync", 1, "absent", "unknown")
    ]
    # A positive literal still reads finite; the repair narrows, it does not disarm.
    assert _js_states(lib, repo, "execSync('probe', { timeout: 0.5 });\n") == [
        ("execSync", 1, "present", "finite")
    ]
    for absent_literal in ("undefined", "null"):
        assert _js_states(lib, repo, f"execSync('probe', {{ timeout: {absent_literal} }});\n") == [
            ("execSync", 1, "absent", "unknown")
        ], absent_literal


def test_a_js_deadline_is_not_borrowed_across_sibling_calls_on_one_line(tmp_path: Path) -> None:
    """The predecessor searched the whole LINE for `timeout:`, so an undeadlined call
    inherited its neighbour's deadline and was reported finite."""
    lib = _load_surface_marker_lib()
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)

    # Seams are sorted by (path, line, call), so same-line calls come back in NAME order
    # regardless of which one the source wrote first -- both directions are asserted so a
    # repair that only binds the leftmost call cannot pass.
    assert _js_states(lib, repo, "execSync('a'); spawnSync('b', { timeout: 100 });\n") == [
        ("execSync", 1, "absent", "unknown"),
        ("spawnSync", 1, "present", "finite"),
    ]
    assert _js_states(lib, repo, "spawnSync('b', { timeout: 100 }); execSync('a');\n") == [
        ("execSync", 1, "absent", "unknown"),
        ("spawnSync", 1, "present", "finite"),
    ]


def test_a_js_deadline_is_not_borrowed_from_a_nested_call(tmp_path: Path) -> None:
    """The nested call declares the timeout; the outer one declares none. Attributing it
    outward is the same borrowing defect, one nesting level down."""
    lib = _load_surface_marker_lib()
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)

    assert _js_states(lib, repo, "spawn(cmd, opts, wrap(execSync('x', { timeout: 5 })));\n") == [
        ("execSync", 1, "present", "finite"),
        ("spawn", 1, "absent", "unknown"),
    ]


def test_a_js_call_spanning_lines_keeps_its_own_deadline(tmp_path: Path) -> None:
    """The mirror of borrowing: a line-scoped search reported `absent` for a call whose
    options object simply wrapped onto the next line."""
    lib = _load_surface_marker_lib()
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)

    assert _js_states(
        lib, repo, "spawnSync(cmd, [\n  'arg',\n], {\n  timeout: 5000,\n  stdio: 'ignore',\n});\n"
    ) == [("spawnSync", 1, "present", "finite")]


def test_js_option_reads_survive_strings_comments_and_quoted_keys(tmp_path: Path) -> None:
    lib = _load_surface_marker_lib()
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)

    # A brace or `timeout:` inside a string or comment must not be read as syntax.
    assert _js_states(lib, repo, "execSync('echo { timeout: 5 }');\n") == [
        ("execSync", 1, "absent", "unknown")
    ]
    assert _js_states(lib, repo, "execSync('probe', { /* timeout: 5 */ cwd: dir });\n") == [
        ("execSync", 1, "absent", "unknown")
    ]
    assert _js_states(lib, repo, "execSync('probe', { 'timeout': 100 });\n") == [
        ("execSync", 1, "present", "finite")
    ]


def test_an_unbalanced_js_call_is_unknown_rather_than_deadline_free(tmp_path: Path) -> None:
    """A region the scanner cannot read is not an empty argument list. Reading it as one
    would publish `absent` about a call whose text was never parsed."""
    lib = _load_surface_marker_lib()
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)

    assert _js_states(lib, repo, "execSync('probe', { timeout: 5000\n") == [
        ("execSync", 1, "unknown", "unknown")
    ]


def test_js_output_bounding_is_call_scoped_too(tmp_path: Path) -> None:
    """`stdio` was line-scoped by the same search, so it borrowed identically."""
    lib = _load_surface_marker_lib()
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    path = repo / "tests" / "probe.js"
    path.write_text("execSync('a'); spawnSync('b', { stdio: 'ignore' });\n", encoding="utf-8")

    assert [seam["output_bounding"] for seam in lib.subprocess_settlement_seams(repo, [path])] == [
        "unknown",
        "bounded",
    ]

    path.write_text("execSync('a', { stdio: 'pipe' });\n", encoding="utf-8")
    assert [seam["output_bounding"] for seam in lib.subprocess_settlement_seams(repo, [path])] == [
        "unbounded"
    ]


def test_standing_test_economics_hides_settlement_callsite_list_in_summary(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    tests = repo / "tests"
    tests.mkdir()
    (tests / "test_settlement.py").write_text(
        "import subprocess\nsubprocess.run(['probe'], timeout=5, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)\n",
        encoding="utf-8",
    )

    summary = _run_inventory_cli("--repo-root", str(repo), "--summary", "--json")
    detail = _run_inventory_cli("--repo-root", str(repo), "--detail", "--json")
    assert summary.returncode == 0, summary.stderr
    assert detail.returncode == 0, detail.stderr
    summary_payload = json.loads(summary.stdout)
    detail_payload = json.loads(detail.stdout)
    assert summary_payload["subprocess_settlement"] == {
        "seam_count": 1,
        "deadline_counts": {"present": 1, "absent": 0, "unknown": 0},
        "lifecycle_counts": {"finite": 1, "until_interrupted": 0, "unknown": 0},
        "process_tree_termination_counts": {"owned": 0, "not_owned": 0, "unknown": 1},
        "output_bounding_counts": {"bounded": 1, "unbounded": 0, "unknown": 0},
    }
    assert "seams" not in summary_payload["subprocess_settlement"]
    assert detail_payload["subprocess_settlement"]["seams"][0]["path"] == "tests/test_settlement.py"


def test_subprocess_settlement_marks_unknown_syntax_and_unreadable_inputs_conservatively(
    tmp_path: Path, monkeypatch
) -> None:
    lib = _load_surface_marker_lib()
    repo = tmp_path / "repo"
    repo.mkdir()
    tests = repo / "tests"
    tests.mkdir()
    malformed = tests / "broken.py"
    malformed.write_text("def broken(:\n", encoding="utf-8")
    system = tests / "system.py"
    system.write_text("import os\nos.system('probe')\n", encoding="utf-8")
    js = tests / "stream.js"
    js.write_text("execSync('probe', { stdio: 'pipe' });\n", encoding="utf-8")

    assert lib._literal_truth(ast.parse("value").body[0].value) is None
    assert lib._literal_deadline_state(ast.parse("timeout=dynamic").body[0].value) == "unknown"
    assert lib._call_parts(ast.parse("42").body[0].value) == []
    assert lib.subprocess_settlement_seams(repo, [malformed, system, js]) == [
        {"path": "tests/stream.js", "line": 1, "call": "execSync", "deadline": "absent", "lifecycle": "unknown", "process_tree_termination": "unknown", "output_bounding": "unbounded"},
    ]

    unreadable = tests / "unreadable.py"
    unreadable.write_text("import subprocess\n", encoding="utf-8")
    original_read_text = Path.read_text

    def fail_only_target(path: Path, *args, **kwargs):
        if path == unreadable:
            raise UnicodeDecodeError("utf-8", b"x", 0, 1, "forced")
        return original_read_text(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", fail_only_target)
    assert lib.subprocess_settlement_seams(repo, [unreadable]) == []


def test_a_call_name_in_a_comment_or_string_is_not_a_call_site(tmp_path: Path) -> None:
    """Round 1 of this repair built a "skip what is not code" walker and then did not use
    it for the one decision that MINTS a seam: the call regex ran over raw source, so a
    commented-out call was reported with a confident `present`/`finite` deadline computed
    from text that never executes. Commented-out subprocess calls are ordinary in test
    files, so this moved the reported counts in both directions."""
    lib = _load_surface_marker_lib()
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)

    assert _js_states(lib, repo, "// legacy: execSync(cmd, { timeout: 1000 })\n") == []
    assert _js_states(lib, repo, "/* execSync(cmd, { timeout: 1000 }) */\n") == []
    assert _js_states(lib, repo, "const doc = \"execSync(cmd, { timeout: 1000 })\";\n") == []
    assert _js_states(lib, repo, "// TODO: spawn(cmd)\n") == []
    # A real call on the same line as a comment mentioning one is still found once.
    assert _js_states(lib, repo, "spawnSync(a); // execSync(b, { timeout: 5 })\n") == [
        ("spawnSync", 1, "absent", "unknown")
    ]


def test_a_regex_literal_cannot_make_the_walker_read_past_the_call(tmp_path: Path) -> None:
    """`/\\//` is four characters whose middle two are `//`. The comment rule swallowed the
    rest of the line, and the region then ran on into unrelated statements and still
    BALANCED -- so the unbalanced guard never fired and a confident verdict was published
    about text the walker never parsed. A balanced mis-parse is worse than an unbalanced
    one, because only the unbalanced case degrades to `unknown`."""
    lib = _load_surface_marker_lib()
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)

    # The call declares no timeout; a later statement does. It must not be borrowed.
    borrowed = (
        "it('y', () => {\n"
        "  execSync(cmd, [/\\//]);\n"
        "  const opts = { timeout: 1000 };\n"
        "  spawnSync(x, opts);\n"
        "});\n"
    )
    assert _js_states(lib, repo, borrowed) == [
        ("execSync", 2, "absent", "unknown"),
        ("spawnSync", 4, "absent", "unknown"),
    ]

    # The mirror: the call's own timeout must not be swallowed by the regex.
    swallowed = "execSync(cmd.split(/\\//)[0], { timeout: 1000 });\n"
    assert _js_states(lib, repo, swallowed) == [("execSync", 1, "present", "finite")]

    # A character class holds a literal `/` that does not close the literal.
    assert _js_states(lib, repo, "execSync(cmd.replace(/[/]/g, '-'), { timeout: 20 });\n") == [
        ("execSync", 1, "present", "finite")
    ]
    # Division is not a regex: the operand before `/` ends a value.
    assert _js_states(lib, repo, "execSync(cmd, { timeout: total / parts });\n") == [
        ("execSync", 1, "unknown", "unknown")
    ]


def test_an_option_nested_one_container_deep_is_not_the_calls_own(tmp_path: Path) -> None:
    """Round 1 closed one nesting mechanism and not the other. A nested CALL raises the
    parenthesis depth and was excluded; a nested OBJECT or ARRAY was not, so
    `{env: e, child: {timeout: 1000}}` read as a 1000 ms deadline on a call that declares
    none. Same borrowing defect, one container type over."""
    lib = _load_surface_marker_lib()
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)

    assert _js_states(lib, repo, "spawnSync(cmd, args, { env: e, child: { timeout: 1000 } });\n") == [
        ("spawnSync", 1, "absent", "unknown")
    ]
    assert _js_states(lib, repo, "spawnSync(cmd, { steps: [{ timeout: 500 }] });\n") == [
        ("spawnSync", 1, "absent", "unknown")
    ]
    # The direct property still reads, including alongside a nested object.
    assert _js_states(lib, repo, "spawnSync(cmd, { env: { X: 1 }, timeout: 700 });\n") == [
        ("spawnSync", 1, "present", "finite")
    ]

    path = repo / "tests" / "probe.js"
    path.write_text("spawnSync(cmd, { hooks: { stdio: 'ignore' } });\n", encoding="utf-8")
    assert [seam["output_bounding"] for seam in lib.subprocess_settlement_seams(repo, [path])] == [
        "unknown"
    ]


def test_jsx_test_files_are_scanned_like_every_other_js_family_extension(tmp_path: Path) -> None:
    """`test_discovery_lib` discovers `*.test.jsx`, and the scanned-suffix set omitted it,
    so such a file counted as a nested-CLI file and contributed zero seams -- a silent
    undercount with nothing reconciling the two lists."""
    lib = _load_surface_marker_lib()
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    path = repo / "tests" / "run.test.jsx"
    path.write_text("execSync(cmd, { timeout: 2000 });\n", encoding="utf-8")

    assert lib.nested_cli_files(repo, [path]) == ["tests/run.test.jsx"]
    assert [seam["deadline"] for seam in lib.subprocess_settlement_seams(repo, [path])] == ["present"]


def test_a_jsx_self_closing_tag_does_not_open_a_phantom_regex(tmp_path: Path) -> None:
    """Round 2's finding, and it is the class round 1 closed, reopened by round 1's own
    regex fold. `}` was in the value-position set, so the `/` of `<App route={r} />` read
    as a regex opener; the scan ran past the tag and terminated on a `/` inside a later
    string, after which the walk was INSIDE a string literal -- minting a seam from text
    that never executes, and dropping the real call that followed."""
    lib = _load_surface_marker_lib()
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    path = repo / "tests" / "probe.jsx"

    path.write_text(
        "render(<App route={r} />, mount('#a/execSync(cmd, { timeout: 1000 })'));\n",
        encoding="utf-8",
    )
    assert lib.subprocess_settlement_seams(repo, [path]) == []

    path.write_text(
        "test('x', () => {\n"
        "  render(<App route={r} />, mount('#app/root'));\n"
        "  execSync('probe', { timeout: 1000 });\n"
        "});\n",
        encoding="utf-8",
    )
    assert [(s["call"], s["line"], s["deadline"]) for s in lib.subprocess_settlement_seams(repo, [path])] == [
        ("execSync", 3, "present")
    ]


def test_a_regex_after_a_keyword_is_recognized_as_a_regex(tmp_path: Path) -> None:
    """A character set cannot see keywords, so `return /'/.test(s)` read the `/` as
    division and scanned the regex body as code -- and the `'` in that body opened a
    phantom string that ran to the next quote in the file, fabricating a seam from its
    contents."""
    lib = _load_surface_marker_lib()
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)

    assert _js_states(
        lib, repo,
        "const hasQuote = (s) => { return /'/.test(s); };\n"
        "const doc = 'execSync(cmd, { timeout: 1000 })';\n",
    ) == []
    # Division after an ordinary identifier is still division, not a regex.
    assert _js_states(lib, repo, "execSync(cmd, { timeout: total / parts });\n") == [
        ("execSync", 1, "unknown", "unknown")
    ]


def test_a_stray_quote_cannot_desync_the_walk_past_its_own_line(tmp_path: Path) -> None:
    """The amplifier. `_js_skip_regex` bails on a newline; `_js_skip_quoted` did not, so a
    stray `'` ran to the next quote ANYWHERE in the file and turned one corrupted line
    into a file-wide desync. A raw newline cannot appear in a '' or "" string, so the same
    bail applies -- and bounds every mis-parse to one line. Template literals are
    genuinely multi-line and keep scanning."""
    lib = _load_surface_marker_lib()
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)

    # An unterminated quote on line 1 must not swallow the real call on line 3.
    assert _js_states(
        lib, repo,
        "const broken = 'oops;\n"
        "const other = 1;\n"
        "execSync('probe', { timeout: 250 });\n",
    ) == [("execSync", 3, "present", "finite")]

    # A multi-line template literal still spans lines, so a call inside one stays hidden.
    assert _js_states(
        lib, repo,
        "const script = `line one\nexecSync('x', { timeout: 5 })\nline three`;\n"
        "spawnSync('real', { timeout: 90 });\n",
    ) == [("spawnSync", 4, "present", "finite")]
