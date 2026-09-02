use std::collections::HashSet;
use std::path::{Path, PathBuf};

use serde::Serialize;

use crate::inventory::{FileInventory, InventoryError};
use crate::selection::matching_files;

pub const SCAN_PATTERNS: &[&str] = &[
    "*.py",
    "scripts/*.py",
    "tools/*.py",
    "skills/*/*/scripts/*.py",
    "skills/*/scripts/*.py",
    "skills/*/*/references/*.py",
    "skills/*/references/*.py",
    "support/*/scripts/*.py",
    "shared/scripts/*.py",
];

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct ProbeShape {
    pub shape: String,
    pub command: String,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct ProbeTarget {
    pub module: String,
    pub shapes: Vec<ProbeShape>,
    pub path: String,
}

#[derive(Debug, Serialize)]
pub struct StandaloneReport {
    pub schema: &'static str,
    pub claim: &'static str,
    pub listing: String,
    pub scope: String,
    pub checked: usize,
    pub discovered: usize,
    pub targets: Vec<ProbeTarget>,
    pub unmatched_changed: Vec<String>,
    pub scope_note: String,
    pub unestablished: Vec<StandaloneUnestablished>,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct StandaloneUnestablished {
    pub status: String,
    pub detail: String,
}

pub fn analyze(
    repo_root: &Path,
    inventory: &FileInventory,
    changed: Option<&[String]>,
) -> StandaloneReport {
    let discovered = matching_files(repo_root, inventory, SCAN_PATTERNS)
        .into_iter()
        .filter(|path| {
            Path::new(path.as_str())
                .file_name()
                .is_some_and(|name| name != "__init__.py")
        })
        .collect::<Vec<_>>();
    let (selected, unmatched_changed, scope) = match changed {
        None => (discovered.clone(), Vec::new(), "full".to_string()),
        Some(changed) => {
            let mut seen = HashSet::new();
            let mut selected = Vec::new();
            let mut unmatched = Vec::new();
            let discovered_by_resolved = discovered
                .iter()
                .filter_map(|path| {
                    std::fs::canonicalize(path.on_disk(repo_root))
                        .ok()
                        .map(|resolved| (resolved, *path))
                })
                .collect::<std::collections::HashMap<_, _>>();
            for original in changed {
                let candidate = if Path::new(original).is_absolute() {
                    PathBuf::from(original)
                } else {
                    repo_root.join(original)
                };
                let resolved = std::fs::canonicalize(&candidate).ok();
                let dedupe_key = resolved.clone().unwrap_or_else(|| candidate.clone());
                if !seen.insert(dedupe_key) {
                    continue;
                }
                if let Some(path) =
                    resolved.and_then(|resolved| discovered_by_resolved.get(&resolved).copied())
                {
                    selected.push(path);
                } else {
                    unmatched.push(original.clone());
                }
            }
            unmatched.sort();
            (selected, unmatched, "partial".to_string())
        }
    };
    let targets = selected
        .iter()
        .map(|path| probe_target(repo_root, path.as_str()))
        .collect::<Vec<_>>();
    let checked = targets.len();
    let scope_note = if scope == "full" {
        format!("checked all {checked} discovered module(s)")
    } else if checked == 0 {
        "PARTIAL: NOTHING WAS CHECKED: no --changed path matched a discovered module".to_string()
    } else {
        format!(
            "PARTIAL: checked {checked} of {} discovered module(s); the rest are UNCHECKED, not proven clean",
            discovered.len()
        )
    };
    StandaloneReport {
        schema: "repograph.standalone_targets.v1",
        claim: "static-selection-only",
        listing: inventory.source().as_str().to_string(),
        scope,
        checked,
        discovered: discovered.len(),
        targets,
        unmatched_changed,
        scope_note,
        unestablished: Vec::new(),
    }
}

fn probe_target(repo_root: &Path, path: &str) -> ProbeTarget {
    let relative = Path::new(path);
    let module = relative
        .file_stem()
        .and_then(|stem| stem.to_str())
        .unwrap_or_default()
        .to_string();
    let mut shapes = Vec::new();
    let is_top_level_scripts = relative
        .parent()
        .is_some_and(|parent| parent == Path::new("scripts"));
    if is_top_level_scripts {
        shapes.push(ProbeShape {
            shape: "package".to_string(),
            command: format!("import scripts.{module}"),
        });
    }
    let parent = repo_root.join(relative.parent().unwrap_or_else(|| Path::new(".")));
    shapes.push(ProbeShape {
        shape: "direct".to_string(),
        command: format!(
            "import sys; sys.path.insert(0, {}); import {module}",
            python_repr(&parent.to_string_lossy())
        ),
    });
    ProbeTarget {
        module,
        shapes,
        path: path.to_string(),
    }
}

fn python_repr(value: &str) -> String {
    if !value.contains('\'') {
        return format!("'{value}'");
    }
    format!("\"{}\"", value.replace('\\', "\\\\").replace('"', "\\\""))
}

pub fn run<I>(args: I) -> i32
where
    I: IntoIterator<Item = String>,
{
    let mut args = args.into_iter().peekable();
    let mut repo_root = match std::env::current_dir() {
        Ok(path) => path,
        Err(error) => {
            eprintln!("usage error: could not determine current directory: {error}");
            return 2;
        }
    };
    let mut file_list = None;
    let mut changed = None;
    let mut help = false;
    while let Some(argument) = args.next() {
        match argument.as_str() {
            "--repo-root" => match required_value(&mut args, "--repo-root") {
                Ok(value) => repo_root = PathBuf::from(value),
                Err(error) => return cli_error(&error),
            },
            "--file-list" => match required_value(&mut args, "--file-list") {
                Ok(value) => file_list = Some(PathBuf::from(value)),
                Err(error) => return cli_error(&error),
            },
            "--changed" => {
                let mut values: Vec<String> = changed.take().unwrap_or_default();
                loop {
                    let take_value = args.peek().is_some_and(|value| !value.starts_with('-'));
                    if !take_value {
                        break;
                    }
                    values.push(args.next().expect("peeked argument must exist"));
                }
                changed = Some(values);
            }
            "--help" | "-h" => help = true,
            argument if argument.starts_with('-') => {
                return cli_error(&format!("unknown option {argument:?}"))
            }
            argument => return cli_error(&format!("unexpected positional argument {argument:?}")),
        }
    }
    if help {
        println!("{}", usage());
        return 0;
    }
    let repo_root = std::fs::canonicalize(&repo_root).unwrap_or(repo_root);
    let inventory = match crate::inventory::acquire(&repo_root, file_list.as_deref()) {
        Ok(inventory) => inventory,
        Err(error) => {
            emit_unestablished(&repo_root, &error);
            return 3;
        }
    };
    let report = analyze(&repo_root, &inventory, changed.as_deref());
    match serde_json::to_string(&report) {
        Ok(json) => {
            println!("{json}");
            0
        }
        Err(error) => {
            eprintln!("internal error: could not write JSON output: {error}");
            70
        }
    }
}

fn emit_unestablished(repo_root: &Path, error: &InventoryError) {
    let report = StandaloneReport {
        schema: "repograph.standalone_targets.v1",
        claim: "static-selection-only",
        listing: "unestablished".to_string(),
        scope: "unestablished".to_string(),
        checked: 0,
        discovered: 0,
        targets: Vec::new(),
        unmatched_changed: Vec::new(),
        scope_note: "file inventory was not established".to_string(),
        unestablished: vec![StandaloneUnestablished {
            status: "inventory".to_string(),
            detail: error.to_string(),
        }],
    };
    if let Ok(json) = serde_json::to_string(&report) {
        println!("{json}");
    }
    eprintln!("{repo_root:?}: {error}");
}

fn required_value<I>(args: &mut I, flag: &str) -> Result<String, String>
where
    I: Iterator<Item = String>,
{
    match args.next() {
        Some(value) if !value.starts_with('-') => Ok(value),
        Some(value) => Err(format!("{flag} requires a value, got {value:?}")),
        None => Err(format!("{flag} requires a value")),
    }
}

fn cli_error(message: &str) -> i32 {
    eprintln!("usage error: {message}\n{}", usage());
    2
}

fn usage() -> &'static str {
    "repograph standalone-targets [--repo-root PATH] [--file-list PATH] [--changed [PATH ...]]"
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::inventory::FileInventory;

    #[test]
    fn changed_selection_keeps_first_occurrence_order_and_excludes_init() {
        let inventory = FileInventory::from_file_list_bytes(
            b"scripts/second.py\0scripts/first.py\0scripts/__init__.py\0",
        )
        .unwrap();
        let root = Path::new(env!("CARGO_MANIFEST_DIR")).join("fixtures");
        let changed = vec![
            "scripts/second.py".to_string(),
            "scripts/first.py".to_string(),
            "scripts/second.py".to_string(),
        ];
        let report = analyze(&root, &inventory, Some(&changed));
        assert_eq!(
            report
                .targets
                .iter()
                .map(|target| target.path.as_str())
                .collect::<Vec<_>>(),
            ["scripts/second.py", "scripts/first.py"]
        );
    }

    #[test]
    fn explicit_empty_changed_scope_is_successful_and_named() {
        let inventory = FileInventory::from_file_list_bytes(b"root.py\0").unwrap();
        let root = Path::new(env!("CARGO_MANIFEST_DIR")).join("fixtures");
        let report = analyze(&root, &inventory, Some(&[]));
        assert_eq!(report.checked, 0);
        assert!(report.scope_note.contains("NOTHING WAS CHECKED"));
    }
}
