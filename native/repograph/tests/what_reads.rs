use std::collections::BTreeSet;
use std::fs;
use std::path::PathBuf;
use std::process::{Command, Output};

use serde_json::Value;

const FIXTURE_ROOT: &str = concat!(env!("CARGO_MANIFEST_DIR"), "/fixtures/what_reads");
const FIXTURE_FILES: &[&str] = &[
    ".githooks/pre-commit",
    ".agents/topology.json",
    "README.md",
    "config.json",
    "config.yaml",
    "data/nested/item.fixture.json",
    "plugins/charness/mirror.md",
    "runtime_bootstrap.py",
    "scripts/globs.py",
    "scripts/importer.py",
    "scripts/quiet.py",
    "scripts/quiet.rs",
    "scripts/reader.py",
    "scripts/reader.sh",
    "scripts/target.py",
];

struct FileList(PathBuf);

impl Drop for FileList {
    fn drop(&mut self) {
        let _ = fs::remove_file(&self.0);
    }
}

fn file_list(name: &str) -> FileList {
    let path = std::env::temp_dir().join(format!(
        "repograph-748-what-reads-{name}-{}.nul",
        std::process::id()
    ));
    let bytes = FIXTURE_FILES
        .iter()
        .flat_map(|path| path.as_bytes().iter().copied().chain(std::iter::once(0)))
        .collect::<Vec<_>>();
    fs::write(&path, bytes).unwrap();
    FileList(path)
}

fn run_query(list: &FileList, path: &str, detail: bool, include_mirrors: bool) -> Output {
    let mut args = vec![
        "what-reads",
        "--repo-root",
        FIXTURE_ROOT,
        "--file-list",
        list.0.to_str().unwrap(),
        "--path",
        path,
    ];
    if detail {
        args.push("--detail");
    }
    if include_mirrors {
        args.push("--include-mirrors");
    }
    Command::new(env!("CARGO_BIN_EXE_repograph"))
        .args(args)
        .output()
        .unwrap()
}

fn parse_report(output: &Output) -> Value {
    serde_json::from_slice(&output.stdout).unwrap()
}

#[test]
fn path_evidence_and_graph_projection_are_typed() {
    let list = file_list("evidence");
    let output = run_query(&list, "scripts/target.py", true, false);
    assert_eq!(output.status.code(), Some(0));
    let report = parse_report(&output);
    assert_eq!(report["schema"], "repograph.what_reads.v1");
    assert_eq!(report["target_kind"], "path");
    assert_eq!(report["listing"], "file-list");

    let files = report["references"]
        .as_array()
        .unwrap()
        .iter()
        .map(|entry| entry["file"].as_str().unwrap().to_string())
        .collect::<BTreeSet<_>>();
    for path in [
        ".githooks/pre-commit",
        "README.md",
        "config.json",
        "config.yaml",
        "scripts/reader.py",
        "scripts/reader.sh",
    ] {
        assert!(files.contains(path), "missing evidence from {path}");
    }
    let kinds = report["reference_kinds"].as_object().unwrap();
    assert!(kinds.contains_key("literal-path"));
    assert!(kinds.contains_key("glob-consumption"));
    assert!(kinds.contains_key("basename-reference"));
    assert!(kinds.contains_key("command-carrier"));

    let carrier = report["references"]
        .as_array()
        .unwrap()
        .iter()
        .find(|entry| entry["file"] == ".githooks/pre-commit")
        .unwrap();
    assert_eq!(carrier["hits"][0]["kind"], "command-carrier");
    assert_eq!(carrier["hits"][0]["line"], 2);
    assert!(carrier["hits"][0]["carrier_id"]
        .as_str()
        .unwrap()
        .starts_with("command-carrier:"));

    let dependents = report["graph"]["dependents"]
        .as_array()
        .unwrap()
        .iter()
        .map(|edge| edge["source"].as_str().unwrap())
        .collect::<BTreeSet<_>>();
    assert!(dependents.contains("scripts/importer.py"));
    assert!(report["graph"]["root_paths"]
        .as_array()
        .unwrap()
        .iter()
        .any(|path| path["root"]["id"] == "runtime:runtime_bootstrap.py"));
}

#[test]
fn path_glob_and_mirror_contracts_are_pinned() {
    let list = file_list("globs");
    let output = run_query(&list, "data/nested/item.fixture.json", true, false);
    assert_eq!(output.status.code(), Some(0));
    let report = parse_report(&output);
    let hits = report["references"]
        .as_array()
        .unwrap()
        .iter()
        .flat_map(|entry| entry["hits"].as_array().unwrap())
        .collect::<Vec<_>>();
    assert!(hits.iter().any(|hit| {
        hit["kind"] == "glob-consumption" && hit["glob"] == "data/nested/*.fixture.json"
    }));
    assert!(hits
        .iter()
        .any(|hit| hit["kind"] == "basename-glob" && hit["glob"] == "*.fixture.json"));
    assert!(!hits.iter().any(|hit| hit["glob"] == "data/*fixture.json"));
    assert!(!hits.iter().any(|hit| hit["glob"] == "*.json"));

    let excluded = parse_report(&run_query(&list, "scripts/target.py", true, false));
    assert!(!excluded["files_with_references"]
        .as_array()
        .unwrap()
        .iter()
        .any(|path| path == "plugins/charness/mirror.md"));
    let included = parse_report(&run_query(&list, "scripts/target.py", true, true));
    assert!(included["files_with_references"]
        .as_array()
        .unwrap()
        .iter()
        .any(|path| path == "plugins/charness/mirror.md"));
    assert!(included["references"]
        .as_array()
        .unwrap()
        .iter()
        .any(|entry| entry["surface"] == "mirror"));
}

#[test]
fn zero_hits_keep_the_caveat_and_retired_modes_are_usage_errors() {
    let list = file_list("zero");
    let output = run_query(&list, "scripts/quiet.rs", false, false);
    assert_eq!(output.status.code(), Some(0));
    let report = parse_report(&output);
    assert_eq!(report["reference_count"], 0);
    assert_eq!(report["zero_result_caveat"].as_str().unwrap(), "No reference was found in the scanned surfaces. That is not 'nothing reads this': read `unscanned_surfaces` before proposing a removal.");
    assert!(report["unscanned_surfaces"]
        .as_array()
        .unwrap()
        .iter()
        .any(|surface| surface.as_str().unwrap().contains("plugins/**")));
    assert!(report["unscanned_surfaces"]
        .as_array()
        .unwrap()
        .iter()
        .any(|surface| surface.as_str().unwrap().contains("prose is not a program")));

    for retired_flag in ["--symbol", "--config-key"] {
        let output = Command::new(env!("CARGO_BIN_EXE_repograph"))
            .args([
                "what-reads",
                "--repo-root",
                FIXTURE_ROOT,
                "--file-list",
                list.0.to_str().unwrap(),
                retired_flag,
                "VALUE",
            ])
            .output()
            .unwrap();
        assert_eq!(
            output.status.code(),
            Some(2),
            "accepted retired {retired_flag}"
        );
    }
}
