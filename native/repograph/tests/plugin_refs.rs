use std::fs;
use std::path::PathBuf;
use std::process::Command;

use serde_json::Value;

const CRATE_ROOT: &str = env!("CARGO_MANIFEST_DIR");

struct FileList(PathBuf);

impl Drop for FileList {
    fn drop(&mut self) {
        let _ = fs::remove_file(&self.0);
    }
}

fn file_list(name: &str, paths: &[&str]) -> FileList {
    let path = std::env::temp_dir().join(format!(
        "repograph-plugin-refs-{name}-{}.nul",
        std::process::id()
    ));
    let bytes = paths
        .iter()
        .flat_map(|path| path.as_bytes().iter().copied().chain(std::iter::once(0)))
        .collect::<Vec<_>>();
    fs::write(&path, bytes).unwrap();
    FileList(path)
}

fn run(repo_root: &str, list: &FileList) -> (i32, Value, String) {
    let output = Command::new(env!("CARGO_BIN_EXE_repograph"))
        .current_dir(CRATE_ROOT)
        .args([
            "plugin-refs",
            "--repo-root",
            repo_root,
            "--file-list",
            list.0.to_str().unwrap(),
        ])
        .output()
        .unwrap();
    let status = output.status.code().unwrap();
    let report = serde_json::from_slice(&output.stdout).unwrap();
    (status, report, String::from_utf8(output.stderr).unwrap())
}

#[test]
fn fixture_report_pins_all_reference_classes_and_skipping_rules() {
    let list = file_list(
        "findings",
        &[
            "README.md",
            "AGENTS.md",
            "docs/guide.md",
            "presets/guide.md",
            "profiles/guide.md",
            "skills/public/demo/SKILL.md",
            "plugins/demo/README.md",
            "plugins/demo/skills/demo/SKILL.md",
        ],
    );
    let (status, report, stderr) = run("fixtures/plugin_refs", &list);
    assert_eq!(status, 1, "{stderr}");
    let expected: Value = serde_json::from_str(include_str!(
        "../fixtures/plugin_refs/expected/plugin_refs.json"
    ))
    .unwrap();
    assert_eq!(report, expected);
    assert_eq!(report["references"].as_array().unwrap().len(), 13);
    assert_eq!(report["findings"].as_array().unwrap().len(), 4);
}

#[test]
fn no_package_fixture_is_a_successful_typed_zero_scope() {
    let list = file_list("no-package", &["README.md", "docs/guide.md"]);
    let (status, report, stderr) = run("fixtures/plugin_refs/no_plugins", &list);
    assert_eq!(status, 0, "{stderr}");
    let expected: Value = serde_json::from_str(include_str!(
        "../fixtures/plugin_refs/expected/no_plugins.json"
    ))
    .unwrap();
    assert_eq!(report, expected);
}

#[test]
fn inventory_failure_is_reported_with_exit_three() {
    let output = Command::new(env!("CARGO_BIN_EXE_repograph"))
        .current_dir(CRATE_ROOT)
        .args([
            "plugin-refs",
            "--repo-root",
            "fixtures/plugin_refs",
            "--file-list",
            "/tmp/repograph-plugin-refs-file-does-not-exist",
        ])
        .output()
        .unwrap();
    assert_eq!(output.status.code(), Some(3));
    let report: Value = serde_json::from_slice(&output.stdout).unwrap();
    assert_eq!(report["listing"], "unestablished");
    assert_eq!(report["unestablished"][0]["status"], "inventory");
}
