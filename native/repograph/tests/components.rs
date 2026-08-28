use std::collections::BTreeMap;
use std::fs;
use std::path::PathBuf;
use std::process::Command;

use serde_json::Value;

const FIXTURE_ROOT: &str = concat!(env!("CARGO_MANIFEST_DIR"), "/fixtures/components");

struct FileList(PathBuf);

impl Drop for FileList {
    fn drop(&mut self) {
        let _ = fs::remove_file(&self.0);
    }
}

fn file_list(name: &str) -> FileList {
    let paths = [
        "runtime_bootstrap.py",
        "scripts/boundary_violation.py",
        "scripts/cross_a.py",
        "scripts/explain_dependent.py",
        "scripts/explain_middle.py",
        "scripts/explain_target.py",
        "scripts/rootless_a.py",
        "scripts/rootless_b.py",
        "skills/shared/scripts/cross_b.py",
        "tests/test_island.py",
        "tests/test_island_helper.py",
    ];
    let path = std::env::temp_dir().join(format!(
        "repograph-746-components-{name}-{}.nul",
        std::process::id()
    ));
    let bytes = paths
        .into_iter()
        .flat_map(|path| path.as_bytes().iter().copied().chain(std::iter::once(0)))
        .collect::<Vec<_>>();
    fs::write(&path, bytes).unwrap();
    FileList(path)
}

fn run(command: &str, list: &FileList, path: Option<&str>) -> (i32, Value) {
    let mut args = vec![
        command,
        "--repo-root",
        FIXTURE_ROOT,
        "--file-list",
        list.0.to_str().unwrap(),
    ];
    if let Some(path) = path {
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

fn expected() -> Value {
    serde_json::from_str(include_str!(
        "../fixtures/components/expected/components.json"
    ))
    .unwrap()
}

fn component_members(report: &Value, predicate: impl Fn(&Value) -> bool) -> Vec<Vec<String>> {
    report["components"]
        .as_array()
        .unwrap()
        .iter()
        .filter(|component| predicate(component))
        .map(|component| {
            component["members"]
                .as_array()
                .unwrap()
                .iter()
                .map(|member| member.as_str().unwrap().to_string())
                .collect()
        })
        .collect()
}

fn members_value(value: &Value) -> Vec<Vec<String>> {
    value
        .as_array()
        .unwrap()
        .iter()
        .map(|members| {
            members
                .as_array()
                .unwrap()
                .iter()
                .map(|member| member.as_str().unwrap().to_string())
                .collect()
        })
        .collect()
}

#[test]
fn components_pins_cycles_rootless_components_and_test_islands() {
    let list = file_list("sets");
    let (status, report) = run("components", &list, None);
    assert_eq!(status, 0);
    let expected = expected();

    assert_eq!(
        component_members(&report, |component| component["size"] == 2),
        members_value(&expected["cyclic_component_members"])
    );
    let by_id = report["components"]
        .as_array()
        .unwrap()
        .iter()
        .map(|component| (component["id"].as_str().unwrap(), component))
        .collect::<BTreeMap<_, _>>();
    let expected_rootless = members_value(&expected["rootless_component_members"])
        .iter()
        .map(|members| {
            let first = members[0].as_str();
            let id = format!("component:{first}");
            by_id[id.as_str()]["members"].clone()
        })
        .collect::<Vec<_>>();
    let actual_rootless = report["rootless_components"]
        .as_array()
        .unwrap()
        .iter()
        .map(|id| by_id[id.as_str().unwrap()]["members"].clone())
        .collect::<Vec<_>>();
    assert_eq!(actual_rootless, expected_rootless);
    assert_eq!(
        report["rootless_component_count"],
        expected["rootless_component_members"]
            .as_array()
            .unwrap()
            .len()
    );

    let expected_test_only = members_value(&expected["validator_test_only_component_members"])
        .iter()
        .map(|members| {
            let first = members[0].as_str();
            let id = format!("component:{first}");
            by_id[id.as_str()]["members"].clone()
        })
        .collect::<Vec<_>>();
    let actual_test_only = report["validator_test_only_islands"]
        .as_array()
        .unwrap()
        .iter()
        .map(|id| by_id[id.as_str().unwrap()]["members"].clone())
        .collect::<Vec<_>>();
    assert_eq!(actual_test_only, expected_test_only);
    assert_eq!(report["test_only_island_count"], 1);
}

#[test]
fn components_and_export_safe_agree_on_boundary_violation_set() {
    let list = file_list("boundary");
    let (components_status, components_report) = run("components", &list, None);
    let (export_status, export_report) = run("export-safe", &list, None);
    assert_eq!(components_status, 0);
    assert_eq!(export_status, 1);

    let component_set = components_report["import_boundary_violations"]
        .as_array()
        .unwrap()
        .iter()
        .map(|violation| {
            (
                violation["path"].clone(),
                violation["line"].clone(),
                violation["kind"].clone(),
                violation["source"].clone(),
            )
        })
        .collect::<Vec<_>>();
    let export_set = export_report["violations"]
        .as_array()
        .unwrap()
        .iter()
        .map(|violation| {
            (
                violation["path"].clone(),
                violation["line"].clone(),
                violation["kind"].clone(),
                violation["source"].clone(),
            )
        })
        .collect::<Vec<_>>();
    assert_eq!(component_set, export_set);
    assert_eq!(component_set.len(), 1);
}

#[test]
fn explain_pins_typed_shortest_path_dependents_and_nearest_ancestors() {
    let list = file_list("explain");
    let (status, report) = run("explain", &list, Some("scripts/explain_target.py"));
    assert_eq!(status, 0);
    let expected = expected();
    assert_eq!(report["path"], expected["explain_path"]["path"]);
    assert_eq!(report["paths_bounded"], false);
    assert_eq!(report["root_paths"].as_array().unwrap().len(), 1);
    assert_eq!(
        report["root_paths"][0]["root"]["id"],
        expected["explain_path"]["root"]
    );
    assert_eq!(
        report["root_paths"][0]["edges"]
            .as_array()
            .unwrap()
            .iter()
            .map(|edge| {
                serde_json::json!({
                    "kind": edge["kind"],
                    "source": edge["source"],
                    "target": edge["target"],
                })
            })
            .collect::<Vec<_>>(),
        expected["explain_path"]["edges"]
            .as_array()
            .unwrap()
            .to_vec()
    );
    let dependents = report["dependents"]
        .as_array()
        .unwrap()
        .iter()
        .map(|edge| edge["source"].as_str().unwrap().to_string())
        .collect::<Vec<_>>();
    let expected_dependents = expected["explain_path"]["dependents"]
        .as_array()
        .unwrap()
        .iter()
        .map(|path| path.as_str().unwrap().to_string())
        .collect::<Vec<_>>();
    assert_eq!(dependents, expected_dependents);
    assert!(report["nearest_classified_ancestors"]
        .as_array()
        .unwrap()
        .is_empty());

    let (rootless_status, rootless) = run("explain", &list, Some("scripts/rootless_a.py"));
    assert_eq!(rootless_status, 0);
    assert!(rootless["root_paths"].as_array().unwrap().is_empty());
    assert_eq!(
        rootless["nearest_classified_ancestors"][0]["path"],
        "scripts/rootless_b.py"
    );
    assert_eq!(rootless["nearest_classified_ancestors"][0]["distance"], 1);
}
