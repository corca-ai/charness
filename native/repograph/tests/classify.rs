use std::collections::BTreeMap;
use std::fs;
use std::path::PathBuf;
use std::process::Command;

use serde_json::Value;

const FIXTURE_ROOT: &str = concat!(env!("CARGO_MANIFEST_DIR"), "/fixtures/classify");

struct FileList(PathBuf);

impl Drop for FileList {
    fn drop(&mut self) {
        let _ = fs::remove_file(&self.0);
    }
}

fn file_list(name: &str, extra: &[&str]) -> FileList {
    let mut paths = vec![
        ".agents/surfaces.json",
        ".agents/topology.json",
        "README.md",
        "scripts/x.go",
        "scripts/x_test.go",
        "scripts/testdata/sample.txt",
    ];
    paths.extend(extra);
    let path =
        std::env::temp_dir().join(format!("repograph-746-{name}-{}.nul", std::process::id()));
    let bytes = paths
        .into_iter()
        .flat_map(|path| path.as_bytes().iter().copied().chain(std::iter::once(0)))
        .collect::<Vec<_>>();
    fs::write(&path, bytes).unwrap();
    FileList(path)
}

fn command(command: &str, list: &FileList, paths: &[&str]) -> (i32, Value) {
    let mut args = vec![
        command,
        "--repo-root",
        FIXTURE_ROOT,
        "--file-list",
        list.0.to_str().unwrap(),
        "--surfaces",
        ".agents/surfaces.json",
    ];
    for path in paths {
        args.extend(["--path", path]);
    }
    let output = Command::new(env!("CARGO_BIN_EXE_repograph"))
        .args(args)
        .output()
        .unwrap();
    let status = output.status.code().unwrap();
    let report = serde_json::from_slice(&output.stdout).unwrap();
    (status, report)
}

fn surface_ids(path: &Value) -> Vec<String> {
    path["surfaces"]
        .as_array()
        .unwrap()
        .iter()
        .map(|surface| surface["surface_id"].as_str().unwrap().to_string())
        .collect()
}

#[test]
fn classify_pins_the_743_exclusion_and_go_shape_contract() {
    let list = file_list("scenario", &[]);
    let (status, report) = command(
        "classify",
        &list,
        &[
            "scripts/x.go",
            "scripts/x_test.go",
            "scripts/testdata/sample.txt",
            "README.md",
            "unknown.data",
        ],
    );
    assert_eq!(status, 3);

    let paths = report["paths"].as_array().unwrap();
    let by_path = paths
        .iter()
        .map(|path| (path["path"].as_str().unwrap(), path))
        .collect::<BTreeMap<_, _>>();
    let expected: Value =
        serde_json::from_str(include_str!("../fixtures/classify/expected/classify.json")).unwrap();
    for (expected_key, expected_role) in [
        ("production", "production"),
        ("test", "test"),
        ("doc", "doc"),
    ] {
        let mut actual = paths
            .iter()
            .filter(|path| path["role"] == expected_role)
            .map(|path| path["path"].as_str().unwrap().to_string())
            .collect::<Vec<_>>();
        actual.sort();
        assert_eq!(
            actual,
            expected[expected_key]
                .as_array()
                .unwrap()
                .iter()
                .map(|path| path.as_str().unwrap().to_string())
                .collect::<Vec<_>>()
        );
    }
    let actual_unestablished = paths
        .iter()
        .filter(|path| path["role"].as_str().unwrap().starts_with("unestablished"))
        .map(|path| path["path"].as_str().unwrap().to_string())
        .collect::<Vec<_>>();
    assert_eq!(
        actual_unestablished,
        expected["unestablished"]
            .as_array()
            .unwrap()
            .iter()
            .map(|path| path.as_str().unwrap().to_string())
            .collect::<Vec<_>>()
    );
    assert_eq!(by_path["scripts/x.go"]["role"], "production");
    assert_eq!(by_path["scripts/x.go"]["presence"], "present");
    assert_eq!(by_path["scripts/x.go"]["package"], "scripts");
    assert_eq!(
        surface_ids(by_path["scripts/x.go"]),
        expected["go_runtime_surfaces"]
            .as_array()
            .unwrap()
            .iter()
            .map(|surface| surface.as_str().unwrap().to_string())
            .collect::<Vec<_>>()
    );
    assert_eq!(by_path["scripts/x.go"]["surfaces"][0]["production"], true);

    assert_eq!(by_path["scripts/x_test.go"]["role"], "test");
    assert_eq!(
        surface_ids(by_path["scripts/x_test.go"]),
        expected["test_surfaces"]
            .as_array()
            .unwrap()
            .iter()
            .map(|surface| surface.as_str().unwrap().to_string())
            .collect::<Vec<_>>()
    );
    assert_eq!(
        by_path["scripts/x_test.go"]["surfaces"][0]["production"],
        false
    );
    assert_eq!(by_path["scripts/testdata/sample.txt"]["role"], "test");

    assert_eq!(by_path["README.md"]["role"], "doc");
    assert_eq!(
        surface_ids(by_path["README.md"]),
        expected["doc_surfaces"]
            .as_array()
            .unwrap()
            .iter()
            .map(|surface| surface.as_str().unwrap().to_string())
            .collect::<Vec<_>>()
    );
    assert_eq!(by_path["README.md"]["surfaces"][0]["production"], false);

    assert_eq!(by_path["unknown.data"]["role"], "unestablished-absent");
    assert_eq!(by_path["unknown.data"]["presence"], "absent-from-snapshot");
    assert!(by_path["unknown.data"]["package"].is_null());
    assert!(by_path["unknown.data"]["surfaces"]
        .as_array()
        .unwrap()
        .is_empty());
    assert_eq!(report["role_census"]["unestablished"], 1);
    assert_eq!(report["unestablished_by_top_level"]["<root>"], 1);
}

#[test]
fn classify_surface_membership_matches_match_surfaces_v1() {
    let list = file_list("equality", &[]);
    let (classify_status, classify_report) = command(
        "classify",
        &list,
        &["scripts/x.go", "scripts/x_test.go", "README.md"],
    );
    assert_eq!(classify_status, 0);

    let output = Command::new(env!("CARGO_BIN_EXE_repograph"))
        .args([
            "match-surfaces",
            "--repo-root",
            FIXTURE_ROOT,
            "--surfaces",
            ".agents/surfaces.json",
            "--path",
            "scripts/x.go",
            "--path",
            "scripts/x_test.go",
            "--path",
            "README.md",
        ])
        .output()
        .unwrap();
    assert_eq!(output.status.code(), Some(0));
    let match_report: Value = serde_json::from_slice(&output.stdout).unwrap();

    let mut expected = BTreeMap::new();
    for surface in match_report["matched_surfaces"].as_array().unwrap() {
        let id = surface["surface_id"].as_str().unwrap();
        for key in ["matched_source_paths", "matched_derived_paths"] {
            for path in surface[key].as_array().unwrap() {
                expected
                    .entry(path.as_str().unwrap().to_string())
                    .or_insert_with(Vec::new)
                    .push(id.to_string());
            }
        }
    }
    for path in classify_report["paths"].as_array().unwrap() {
        let name = path["path"].as_str().unwrap();
        assert_eq!(surface_ids(path), expected[name]);
    }
}

#[test]
fn changed_reports_affected_surfaces_packages_roots_and_reasons() {
    let list = file_list("changed", &[]);
    let (status, report) = command(
        "changed",
        &list,
        &["scripts/x.go", "scripts/x_test.go", "README.md"],
    );
    assert_eq!(status, 0);
    assert_eq!(
        report["affected_surfaces"],
        serde_json::json!(["go-runtime", "host-trigger"])
    );
    assert_eq!(report["affected_packages"], serde_json::json!(["scripts"]));
    assert_eq!(report["affected_roots"][0]["id"], "test:scripts/x_test.go");
    assert!(report["paths"]
        .as_array()
        .unwrap()
        .iter()
        .all(|path| !path["explanations"].as_array().unwrap().is_empty()));
}

#[test]
fn deletion_and_rename_inventories_preserve_absent_pattern_classification() {
    let deleted_list = file_list("deleted", &[]);
    let renamed_list = file_list("renamed", &["scripts/new.go"]);
    let (deleted_status, deleted) = command("classify", &deleted_list, &["scripts/removed.go"]);
    let (renamed_status, renamed) = command("classify", &renamed_list, &["scripts/old.go"]);
    assert_eq!(deleted_status, 0);
    assert_eq!(renamed_status, 0);

    let expected_deleted: Value =
        serde_json::from_str(include_str!("../fixtures/classify/expected/deletion.json")).unwrap();
    let expected_renamed: Value =
        serde_json::from_str(include_str!("../fixtures/classify/expected/rename.json")).unwrap();
    assert_absent_projection(&deleted["paths"][0], &expected_deleted);
    assert_absent_projection(&renamed["paths"][0], &expected_renamed);
    assert_eq!(
        deleted["paths"][0]["surfaces"],
        renamed["paths"][0]["surfaces"]
    );
}

fn assert_absent_projection(actual: &Value, expected: &Value) {
    assert_eq!(actual["path"], expected["path"]);
    assert_eq!(actual["presence"], expected["presence"]);
    assert_eq!(actual["role"], expected["role"]);
    assert_eq!(actual["package"], expected["package"]);
    let actual_surfaces = actual["surfaces"]
        .as_array()
        .unwrap()
        .iter()
        .map(|surface| surface["surface_id"].clone())
        .collect::<Vec<_>>();
    assert_eq!(
        actual_surfaces,
        expected["surface_ids"].as_array().unwrap().to_vec()
    );
    assert!(actual["surfaces"]
        .as_array()
        .unwrap()
        .iter()
        .all(|surface| surface["production"].is_null()));
}
