use std::fs;
use std::path::{Path, PathBuf};

use repograph::graph_carriers::scan;
use repograph::graph_model::Node;
use repograph::inventory::FileInventory;

const DECLARED_FIXTURE_ROOT: &str = concat!(
    env!("CARGO_MANIFEST_DIR"),
    "/../../tests/quality_gates/fixtures"
);
const SHELL_FIXTURE_ROOT: &str = concat!(env!("CARGO_MANIFEST_DIR"), "/fixtures/carriers");

fn inventory(paths: &[&str]) -> FileInventory {
    let bytes = paths
        .iter()
        .flat_map(|path| path.as_bytes().iter().copied().chain(std::iter::once(0)))
        .collect::<Vec<_>>();
    FileInventory::from_file_list_bytes(&bytes).unwrap()
}

#[test]
fn declared_gate_rows_supply_labels_and_commands() {
    let report = scan(
        Path::new(DECLARED_FIXTURE_ROOT),
        &inventory(&[".agents/quality-gates.yaml", "scripts/run-quality.sh"]),
        &[],
    );

    assert!(
        report
            .unresolved_carriers
            .iter()
            .all(|entry| !entry.reason.contains("quality gate list is not readable")),
        "{report:?}"
    );
    assert_eq!(report.quality_labels[0].label, "pytest-release");
    assert!(report
        .quality_labels
        .iter()
        .any(|label| label.label == "check-rust"));
    assert!(!report
        .quality_labels
        .iter()
        .any(|label| label.label == "shell-only"));
    let command = report
        .nodes
        .iter()
        .find_map(|node| match node {
            Node::ValidationCommand(command) if command.label.as_deref() == Some("check-rust") => {
                Some(command)
            }
            _ => None,
        })
        .expect("declared check-rust command");
    assert_eq!(command.command, "./scripts/check-rust.sh");
    assert!(report.nodes.iter().any(|node| match node {
        Node::CommandCarrier(carrier) => {
            carrier.path == ".agents/quality-gates.yaml"
                && carrier.name.starts_with("gate:check-rust:")
        }
        _ => false,
    }));
}

#[test]
fn shell_reader_is_the_fallback_without_a_declared_gate_list() {
    let report = scan(
        Path::new(SHELL_FIXTURE_ROOT),
        &inventory(&["scripts/run-quality.sh"]),
        &[],
    );

    assert!(report
        .quality_labels
        .iter()
        .any(|label| label.label == "fixture-label"));
    assert!(report.nodes.iter().any(|node| match node {
        Node::CommandCarrier(carrier) => carrier.path == "scripts/run-quality.sh",
        _ => false,
    }));
}

struct TemporaryRepo(PathBuf);

impl Drop for TemporaryRepo {
    fn drop(&mut self) {
        let _ = fs::remove_dir_all(&self.0);
    }
}

#[test]
fn malformed_declared_gate_list_is_reported_instead_of_falling_back() {
    let root = std::env::temp_dir().join(format!(
        "repograph-769-quality-gates-{}",
        std::process::id()
    ));
    let _ = fs::remove_dir_all(&root);
    fs::create_dir_all(root.join(".agents")).unwrap();
    fs::write(
        root.join(".agents/quality-gates.yaml"),
        "schema: charness/quality-gates/v1\nphases:\n- id: test\n  gates:\n  - label: bad-gate\n    command: [python3]\n",
    )
    .unwrap();
    let _temporary = TemporaryRepo(root.clone());
    let report = scan(
        &root,
        &inventory(&[".agents/quality-gates.yaml", "scripts/run-quality.sh"]),
        &[],
    );

    assert!(report.quality_labels.is_empty());
    assert!(
        report.unresolved_carriers.iter().any(|entry| {
            entry.carrier_id == "command-carrier:.agents/quality-gates.yaml:gate-list"
                && entry.reason.contains("inline command")
        }),
        "{report:?}"
    );
}
