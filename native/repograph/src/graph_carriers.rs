//! Static command-carrier extraction for the topology graph.
//!
//! This is intentionally a bounded shell tokenizer, not a shell evaluator.  A
//! command whose program position cannot be resolved without evaluating shell
//! is retained as a typed opacity record.  In particular, this module never
//! turns a path-looking argument into an invocation merely because it happens
//! to contain a familiar executable name.

use std::collections::HashSet;
use std::path::{Path, PathBuf};

use serde::Serialize;
use serde_json::Value;

use crate::graph::{display_repo_root, DEFAULT_EXCLUDE_PREFIXES};
use crate::graph_model::{
    CarrierPathReference, CarrierSourceKind, CarrierTier, CommandCarrierNode, Edge, EdgeKind, Node,
    QualityLabel, Root, RootKind, RuntimeProbeNode, UnresolvedCarrier, ValidationCommandNode,
};
use crate::inventory::FileInventory;

#[path = "quality_gate_shell.rs"]
mod quality_gate_shell;
#[path = "quality_gate_yaml.rs"]
mod quality_gate_yaml;

use quality_gate_shell::{
    function_open_name, literal_quality_label, logical_lines, queue_call, split_first_token,
};
use quality_gate_yaml::{parse_quality_gate_list, shell_quote};

const QUALITY_QUEUE_FUNCTIONS: &[&str] = &[
    "queue_selected",
    "queue_timed",
    "queue_agent_browser_runtime_gate",
];
const QUALITY_GATE_LIST_PATH: &str = ".agents/quality-gates.yaml";
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct CarrierReport {
    pub nodes: Vec<Node>,
    pub edges: Vec<Edge>,
    pub roots: Vec<Root>,
    pub unresolved_carriers: Vec<UnresolvedCarrier>,
    pub carrier_path_references: Vec<CarrierPathReference>,
    pub quality_labels: Vec<QualityLabel>,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
struct CarrierCommandReport {
    schema: &'static str,
    repo_root: String,
    listing: String,
    excludes: Vec<String>,
    nodes: Vec<Node>,
    edges: Vec<Edge>,
    roots: Vec<Root>,
    unresolved_carriers: Vec<UnresolvedCarrier>,
    carrier_path_references: Vec<CarrierPathReference>,
    quality_labels: Vec<QualityLabel>,
}

/// Scan all carrier surfaces represented by one already-established inventory.
pub fn scan(repo_root: &Path, inventory: &FileInventory, excludes: &[String]) -> CarrierReport {
    let selected = inventory
        .paths()
        .iter()
        .map(|path| path.as_str().to_string())
        .filter(|path| !excludes.iter().any(|prefix| path.starts_with(prefix)))
        .collect::<HashSet<_>>();
    let mut scanner = Scanner {
        repo_root,
        selected: &selected,
        nodes: Vec::new(),
        edges: Vec::new(),
        roots: Vec::new(),
        unresolved_carriers: Vec::new(),
        carrier_path_references: Vec::new(),
        quality_labels: Vec::new(),
        quality_gate_list_scanned: false,
    };

    let mut paths = selected.iter().cloned().collect::<Vec<_>>();
    paths.sort();
    for path in paths {
        if path.starts_with(".githooks/") {
            scanner.scan_hook(&path);
        } else if path.starts_with(".github/workflows/") && path.ends_with(".yml") {
            scanner.scan_workflow(&path);
        } else if path == "package.json" {
            scanner.scan_package_json(&path);
        } else if is_structured_plan(&path) {
            scanner.scan_structured_plan(&path);
        } else if path == ".agents/surfaces.json" {
            scanner.scan_surfaces(&path);
        } else if path.starts_with("integrations/tools/") && path.ends_with(".json") {
            scanner.scan_integration(&path);
        } else if path == QUALITY_GATE_LIST_PATH {
            scanner.scan_quality_gate_list(&path);
        } else if path == "scripts/run-quality.sh" {
            scanner.scan_quality_runner(&path);
        } else if path == ".agents/quality-adapter.yaml" {
            scanner.record_yaml_gap(&path);
        }
    }

    scanner.finish()
}

/// Run the additive carrier diagnostic command.  The graph command is the
/// normal consumer; this arm exists so the extraction can be inspected without
/// asking a reader to filter the full topology document.
pub fn run<I>(args: I) -> i32
where
    I: IntoIterator<Item = String>,
{
    let options = match parse_options(args.into_iter()) {
        Ok(options) => options,
        Err(message) => {
            eprintln!("usage error: {message}\n{}", usage());
            return 2;
        }
    };
    if options.help {
        println!("{}", usage());
        return 0;
    }
    let repo_root_argument = options.repo_root.clone();
    let repo_root =
        std::fs::canonicalize(&options.repo_root).unwrap_or_else(|_| options.repo_root.clone());
    let inventory = match crate::inventory::acquire(&repo_root, options.file_list.as_deref()) {
        Ok(inventory) => inventory,
        Err(error) => {
            eprintln!("{error}");
            return 3;
        }
    };
    let report = scan(&repo_root, &inventory, &options.excludes);
    let output = CarrierCommandReport {
        schema: "repograph.carriers.v1",
        repo_root: display_repo_root(&repo_root_argument),
        listing: inventory.source().as_str().to_string(),
        excludes: options.excludes,
        nodes: report.nodes,
        edges: report.edges,
        roots: report.roots,
        unresolved_carriers: report.unresolved_carriers,
        carrier_path_references: report.carrier_path_references,
        quality_labels: report.quality_labels,
    };
    match serde_json::to_string(&output) {
        Ok(json) => {
            println!("{json}");
            if output.unresolved_carriers.is_empty() {
                0
            } else {
                3
            }
        }
        Err(error) => {
            eprintln!("internal error: could not write JSON output: {error}");
            70
        }
    }
}

struct CarrierOptions {
    repo_root: PathBuf,
    file_list: Option<PathBuf>,
    excludes: Vec<String>,
    help: bool,
}

fn parse_options<I>(args: I) -> Result<CarrierOptions, String>
where
    I: Iterator<Item = String>,
{
    let mut repo_root = std::env::current_dir()
        .map_err(|error| format!("could not determine current directory: {error}"))?;
    let mut file_list = None;
    let mut excludes = Vec::new();
    let mut help = false;
    let mut args = args.peekable();
    while let Some(argument) = args.next() {
        match argument.as_str() {
            "--repo-root" => repo_root = PathBuf::from(required_value(&mut args, "--repo-root")?),
            "--file-list" => {
                file_list = Some(PathBuf::from(required_value(&mut args, "--file-list")?))
            }
            "--exclude-prefix" => excludes.push(required_value(&mut args, "--exclude-prefix")?),
            "--help" | "-h" => help = true,
            argument if argument.starts_with('-') => {
                return Err(format!("unknown option {argument:?}"));
            }
            argument => return Err(format!("unexpected positional argument {argument:?}")),
        }
    }
    if excludes.is_empty() {
        excludes = DEFAULT_EXCLUDE_PREFIXES
            .iter()
            .map(|prefix| (*prefix).to_string())
            .collect();
    }
    Ok(CarrierOptions {
        repo_root,
        file_list,
        excludes,
        help,
    })
}

fn required_value<I>(args: &mut std::iter::Peekable<I>, flag: &str) -> Result<String, String>
where
    I: Iterator<Item = String>,
{
    match args.next() {
        Some(value) if !value.starts_with('-') => Ok(value),
        Some(value) => Err(format!("{flag} requires a value, got {value:?}")),
        None => Err(format!("{flag} requires a value")),
    }
}

fn usage() -> &'static str {
    "repograph carriers [--repo-root PATH] [--file-list PATH] [--exclude-prefix PREFIX]..."
}

struct Scanner<'a> {
    repo_root: &'a Path,
    selected: &'a HashSet<String>,
    nodes: Vec<Node>,
    edges: Vec<Edge>,
    roots: Vec<Root>,
    unresolved_carriers: Vec<UnresolvedCarrier>,
    carrier_path_references: Vec<CarrierPathReference>,
    quality_labels: Vec<QualityLabel>,
    quality_gate_list_scanned: bool,
}

impl<'a> Scanner<'a> {
    fn finish(mut self) -> CarrierReport {
        self.nodes.sort_by(|left, right| {
            left.class_name()
                .cmp(right.class_name())
                .then(left.id().cmp(right.id()))
        });
        self.edges.sort_by(|left, right| {
            edge_kind_name(left.kind)
                .cmp(edge_kind_name(right.kind))
                .then(left.source.cmp(&right.source))
                .then(left.target.cmp(&right.target))
                .then(left.line.cmp(&right.line))
        });
        self.roots.sort_by(|left, right| {
            root_kind_name(left.kind)
                .cmp(root_kind_name(right.kind))
                .then(left.id.cmp(&right.id))
                .then(left.target.cmp(&right.target))
        });
        self.roots.dedup();
        self.unresolved_carriers.sort_by(|left, right| {
            left.carrier_id
                .cmp(&right.carrier_id)
                .then(left.line.cmp(&right.line))
                .then(left.reason.cmp(&right.reason))
        });
        self.carrier_path_references.sort_by(|left, right| {
            left.carrier_id
                .cmp(&right.carrier_id)
                .then(left.path.cmp(&right.path))
                .then(left.line.cmp(&right.line))
        });
        CarrierReport {
            nodes: self.nodes,
            edges: self.edges,
            roots: self.roots,
            unresolved_carriers: self.unresolved_carriers,
            carrier_path_references: self.carrier_path_references,
            quality_labels: self.quality_labels,
        }
    }

    fn scan_hook(&mut self, path: &str) {
        let Some(text) = self.read(path, CarrierTier::Tokenizable, "hook source") else {
            return;
        };
        for (line, raw) in logical_lines(&text) {
            let trimmed = raw.trim();
            if trimmed.is_empty()
                || trimmed.starts_with('#')
                || trimmed.starts_with("#!")
                || is_shell_structure(trimmed)
            {
                if is_shell_structure(trimmed) && looks_command_shaped(trimmed) {
                    self.add_unresolved(
                        path,
                        CarrierSourceKind::GitHook,
                        CarrierTier::Opaque,
                        format!("line:{line}"),
                        Some(line),
                        raw,
                        "shell control flow is not evaluated",
                    );
                }
                continue;
            }
            if shell_line_is_candidate(trimmed) {
                self.add_command(
                    path,
                    CarrierSourceKind::GitHook,
                    CarrierTier::Tokenizable,
                    format!("line:{line}"),
                    Some(line),
                    raw.clone(),
                    raw,
                    None,
                    true,
                );
            }
        }
    }

    fn scan_workflow(&mut self, path: &str) {
        let Some(text) = self.read(path, CarrierTier::Opaque, "workflow source") else {
            return;
        };
        let lines = text.lines().collect::<Vec<_>>();
        let mut index = 0;
        while index < lines.len() {
            let raw = lines[index];
            let trimmed = raw.trim_start();
            if trimmed.starts_with('#') || !trimmed.starts_with("run:") {
                index += 1;
                continue;
            }
            let line = index + 1;
            let value = trimmed["run:".len()..].trim_start();
            let name = format!("run:{line}");
            if value == "|" || value == ">" {
                let indent = raw.len() - raw.trim_start().len();
                let mut body = Vec::new();
                index += 1;
                while index < lines.len() {
                    let candidate = lines[index];
                    let candidate_indent = candidate.len() - candidate.trim_start().len();
                    if !candidate.trim().is_empty() && candidate_indent <= indent {
                        break;
                    }
                    body.push(candidate.trim());
                    index += 1;
                }
                let raw_text = body.join("\n");
                self.add_unresolved(
                    path,
                    CarrierSourceKind::CiWorkflow,
                    CarrierTier::Opaque,
                    name,
                    Some(line),
                    raw_text,
                    "multi-line workflow run is opaque",
                );
                continue;
            }
            if value.contains("${{") || value.contains("}}") {
                self.add_unresolved(
                    path,
                    CarrierSourceKind::CiWorkflow,
                    CarrierTier::Opaque,
                    name,
                    Some(line),
                    value.to_string(),
                    "workflow expression is unresolved",
                );
            } else {
                self.add_command(
                    path,
                    CarrierSourceKind::CiWorkflow,
                    CarrierTier::Tokenizable,
                    name,
                    Some(line),
                    value.to_string(),
                    value.to_string(),
                    None,
                    true,
                );
            }
            index += 1;
        }
    }

    fn scan_package_json(&mut self, path: &str) {
        let Some(text) = self.read(path, CarrierTier::Tokenizable, "package manifest") else {
            return;
        };
        let raw: Value = match serde_json::from_str(&text) {
            Ok(raw) => raw,
            Err(error) => {
                self.add_unresolved(
                    path,
                    CarrierSourceKind::PackageScript,
                    CarrierTier::Tokenizable,
                    "document".to_string(),
                    None,
                    text,
                    format!("package.json is invalid JSON: {error}"),
                );
                return;
            }
        };
        let Some(scripts) = raw.get("scripts").and_then(Value::as_object) else {
            return;
        };
        for (name, value) in scripts {
            let Some(command) = value.as_str() else {
                self.add_unresolved(
                    path,
                    CarrierSourceKind::PackageScript,
                    CarrierTier::Tokenizable,
                    format!("script:{name}"),
                    None,
                    value.to_string(),
                    "package script is not a string",
                );
                continue;
            };
            self.add_command(
                path,
                CarrierSourceKind::PackageScript,
                CarrierTier::Tokenizable,
                format!("script:{name}"),
                None,
                command.to_string(),
                command.to_string(),
                None,
                false,
            );
        }
    }

    fn scan_structured_plan(&mut self, path: &str) {
        let Some(text) = self.read(path, CarrierTier::StructuredUnparsed, "structured plan") else {
            return;
        };
        self.add_unresolved(
            path,
            CarrierSourceKind::StructuredPlan,
            CarrierTier::StructuredUnparsed,
            "document".to_string(),
            None,
            text,
            "structured command plan is unparsed in v1",
        );
    }

    fn scan_surfaces(&mut self, path: &str) {
        let Some(text) = self.read(path, CarrierTier::Tokenizable, "surface manifest") else {
            return;
        };
        let raw: Value = match serde_json::from_str(&text) {
            Ok(raw) => raw,
            Err(error) => {
                self.add_unresolved(
                    path,
                    CarrierSourceKind::SurfaceCommand,
                    CarrierTier::Tokenizable,
                    "document".to_string(),
                    None,
                    text,
                    format!("surfaces manifest is invalid JSON: {error}"),
                );
                return;
            }
        };
        let Some(surfaces) = raw.get("surfaces").and_then(Value::as_array) else {
            return;
        };
        for (surface_index, surface) in surfaces.iter().enumerate() {
            let Some(surface) = surface.as_object() else {
                continue;
            };
            for field in ["sync_commands", "verify_commands"] {
                let Some(commands) = surface.get(field).and_then(Value::as_array) else {
                    continue;
                };
                for (command_index, command) in commands.iter().enumerate() {
                    let name = format!("surface:{surface_index}:{field}:{command_index}");
                    let Some(command) = command.as_str() else {
                        self.add_unresolved(
                            path,
                            CarrierSourceKind::SurfaceCommand,
                            CarrierTier::Tokenizable,
                            name,
                            None,
                            command.to_string(),
                            "surface command is not a string",
                        );
                        continue;
                    };
                    self.add_command(
                        path,
                        CarrierSourceKind::SurfaceCommand,
                        CarrierTier::Tokenizable,
                        name,
                        None,
                        command.to_string(),
                        command.to_string(),
                        None,
                        true,
                    );
                }
            }
        }
    }

    fn scan_integration(&mut self, path: &str) {
        let Some(text) = self.read(path, CarrierTier::Tokenizable, "integration manifest") else {
            return;
        };
        let raw: Value = match serde_json::from_str(&text) {
            Ok(raw) => raw,
            Err(error) => {
                self.add_unresolved(
                    path,
                    CarrierSourceKind::IntegrationCheck,
                    CarrierTier::Tokenizable,
                    "document".to_string(),
                    None,
                    text,
                    format!("integration manifest is invalid JSON: {error}"),
                );
                return;
            }
        };
        let Some(checks) = raw.get("checks").and_then(Value::as_object) else {
            return;
        };
        for (check_name, check) in checks {
            let Some(commands) = check.get("commands").and_then(Value::as_array) else {
                continue;
            };
            for (command_index, command) in commands.iter().enumerate() {
                let name = format!("check:{check_name}:{command_index}");
                let probe_id = format!("runtime-probe:{path}:{check_name}:{command_index}");
                self.nodes.push(Node::RuntimeProbe(RuntimeProbeNode {
                    id: probe_id,
                    path: path.to_string(),
                }));
                let Some(command) = command.as_str() else {
                    self.add_unresolved(
                        path,
                        CarrierSourceKind::IntegrationCheck,
                        CarrierTier::Tokenizable,
                        name,
                        None,
                        command.to_string(),
                        "integration check is not a string",
                    );
                    continue;
                };
                self.add_command(
                    path,
                    CarrierSourceKind::IntegrationCheck,
                    CarrierTier::Tokenizable,
                    name,
                    None,
                    command.to_string(),
                    command.to_string(),
                    None,
                    true,
                );
            }
        }
    }

    fn scan_quality_gate_list(&mut self, path: &str) {
        if self.quality_gate_list_scanned {
            return;
        }
        self.quality_gate_list_scanned = true;
        let Some(text) = self.read(path, CarrierTier::StructuredUnparsed, "quality gate list")
        else {
            return;
        };
        let gates = match parse_quality_gate_list(&text) {
            Ok(gates) => gates,
            Err(reason) => {
                self.add_unresolved(
                    path,
                    CarrierSourceKind::QualityGate,
                    CarrierTier::StructuredUnparsed,
                    "gate-list".to_string(),
                    None,
                    text,
                    format!("quality gate list is not readable: {reason}"),
                );
                return;
            }
        };
        for gate in gates {
            if !self
                .quality_labels
                .iter()
                .any(|entry| entry.label == gate.label)
            {
                self.quality_labels.push(QualityLabel {
                    label: gate.label.clone(),
                    source: "quality-gates.yaml:gate-row".to_string(),
                    line: Some(gate.line),
                });
            }
            let command = gate
                .command
                .iter()
                .map(|argument| shell_quote(argument))
                .collect::<Vec<_>>()
                .join(" ");
            let name = format!("gate:{}:line:{}", gate.label, gate.line);
            self.add_command(
                path,
                CarrierSourceKind::QualityGate,
                CarrierTier::Tokenizable,
                name,
                Some(gate.line),
                gate.raw,
                command,
                Some(gate.label),
                true,
            );
        }
        quality_gate_shell::add_quality_aggregate_labels(&mut self.quality_labels);
    }

    fn scan_quality_runner(&mut self, path: &str) {
        if self.repo_root.join(QUALITY_GATE_LIST_PATH).is_file() {
            self.scan_quality_gate_list(QUALITY_GATE_LIST_PATH);
            return;
        }
        let Some(text) = self.read(path, CarrierTier::Opaque, "quality runner") else {
            return;
        };
        let mut current_function = None;
        for (line, raw) in logical_lines(&text) {
            if let Some(name) = function_open_name(&raw) {
                current_function = Some(name);
                continue;
            }
            if raw.starts_with('}') {
                current_function = None;
                continue;
            }
            let Some((function, rest)) = queue_call(&raw, QUALITY_QUEUE_FUNCTIONS) else {
                continue;
            };
            let function = function.to_string();
            if current_function
                .as_deref()
                .is_some_and(|name| QUALITY_QUEUE_FUNCTIONS.contains(&name))
            {
                continue;
            }
            let Some((label_token, command)) = split_first_token(rest) else {
                self.add_unresolved(
                    path,
                    CarrierSourceKind::QualityGate,
                    CarrierTier::Tokenizable,
                    format!("{function}:line:{line}"),
                    Some(line),
                    raw,
                    "quality queue call has no label",
                );
                continue;
            };
            let Some(label) = literal_quality_label(label_token) else {
                self.add_unresolved(
                    path,
                    CarrierSourceKind::QualityGate,
                    CarrierTier::Tokenizable,
                    format!("{function}:line:{line}"),
                    Some(line),
                    raw,
                    "quality queue label is not a literal runtime label",
                );
                continue;
            };
            if !self.quality_labels.iter().any(|entry| entry.label == label) {
                self.quality_labels.push(QualityLabel {
                    label: label.clone(),
                    source: "run-quality.sh:queue-call-site".to_string(),
                    line: Some(line),
                });
            }
            let name = format!("gate:{label}:line:{line}");
            let command = command.to_string();
            self.add_command(
                path,
                CarrierSourceKind::QualityGate,
                CarrierTier::Tokenizable,
                name,
                Some(line),
                raw,
                command.clone(),
                Some(label),
                true,
            );
        }
        quality_gate_shell::add_quality_aggregate_labels(&mut self.quality_labels);
    }

    fn record_yaml_gap(&mut self, path: &str) {
        let Some(text) = self.read(path, CarrierTier::Opaque, "quality adapter") else {
            return;
        };
        self.add_unresolved(
            path,
            CarrierSourceKind::QualityGate,
            CarrierTier::Opaque,
            "startup_probes".to_string(),
            None,
            text,
            "unresolved (yaml): startup_probes labels are identity-only in v1",
        );
    }

    fn read(&mut self, path: &str, tier: CarrierTier, reason: &str) -> Option<String> {
        match std::fs::read_to_string(self.repo_root.join(path)) {
            Ok(text) => Some(text),
            Err(error) => {
                self.add_unresolved(
                    path,
                    source_kind_for_path(path),
                    tier,
                    "read".to_string(),
                    None,
                    String::new(),
                    format!("{reason} is unreadable: {error}"),
                );
                None
            }
        }
    }

    #[allow(clippy::too_many_arguments)]
    fn add_command(
        &mut self,
        path: &str,
        source_kind: CarrierSourceKind,
        tier: CarrierTier,
        name: String,
        line: Option<usize>,
        raw: String,
        command: String,
        label: Option<String>,
        validation: bool,
    ) {
        let carrier_id = format!("command-carrier:{path}:{name}");
        self.nodes.push(Node::CommandCarrier(CommandCarrierNode {
            id: carrier_id.clone(),
            path: path.to_string(),
            source_kind,
            tier,
            name,
            line,
            raw: raw.clone(),
        }));
        let source = if validation {
            let id = format!("validation-command:{carrier_id}");
            self.nodes
                .push(Node::ValidationCommand(ValidationCommandNode {
                    id: id.clone(),
                    carrier_id: carrier_id.clone(),
                    label,
                    command: command.clone(),
                }));
            self.roots.push(Root {
                kind: RootKind::Validation,
                id: id.clone(),
                target: id.clone(),
            });
            id
        } else {
            carrier_id.clone()
        };
        match parse_command(&command, self.selected) {
            ParsedCommand::Resolved { target, references } => {
                if let Some(target) = target {
                    self.edges.push(Edge {
                        kind: EdgeKind::Invokes,
                        source: source.clone(),
                        target,
                        rule_id: Some("program-position".to_string()),
                        module: None,
                        line,
                    });
                }
                for path in references {
                    self.carrier_path_references.push(CarrierPathReference {
                        kind: "carrier-path-reference",
                        carrier_id: carrier_id.clone(),
                        path,
                        raw: command.clone(),
                        line,
                    });
                }
            }
            ParsedCommand::Opaque(reason) => {
                self.add_unresolved_with_id(carrier_id, tier, line, raw, reason)
            }
            ParsedCommand::Noop => {}
        }
    }

    #[allow(clippy::too_many_arguments)]
    fn add_unresolved(
        &mut self,
        path: &str,
        source_kind: CarrierSourceKind,
        tier: CarrierTier,
        name: String,
        line: Option<usize>,
        raw: String,
        reason: impl Into<String>,
    ) {
        let carrier_id = format!("command-carrier:{path}:{name}");
        self.nodes.push(Node::CommandCarrier(CommandCarrierNode {
            id: carrier_id.clone(),
            path: path.to_string(),
            source_kind,
            tier,
            name,
            line,
            raw: raw.clone(),
        }));
        self.add_unresolved_with_id(carrier_id, tier, line, raw, reason);
    }

    fn add_unresolved_with_id(
        &mut self,
        carrier_id: String,
        tier: CarrierTier,
        line: Option<usize>,
        raw: String,
        reason: impl Into<String>,
    ) {
        self.unresolved_carriers.push(UnresolvedCarrier {
            kind: "unresolved-carrier",
            carrier_id,
            tier,
            reason: reason.into(),
            raw,
            line,
        });
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
enum ParsedCommand {
    Resolved {
        target: Option<String>,
        references: Vec<String>,
    },
    Opaque(String),
    Noop,
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct ShellToken {
    value: String,
    dynamic: bool,
}

fn parse_command(command: &str, selected: &HashSet<String>) -> ParsedCommand {
    let tokens = match tokenize(command) {
        Ok((tokens, has_control)) => {
            if has_control {
                return ParsedCommand::Opaque(
                    "multi-statement or shell control flow is unresolved".to_string(),
                );
            }
            tokens
        }
        Err(reason) => return ParsedCommand::Opaque(reason),
    };
    if tokens.is_empty() {
        return ParsedCommand::Noop;
    }
    let mut program_index = 0;
    while program_index < tokens.len() && is_assignment(&tokens[program_index].value) {
        program_index += 1;
    }
    if program_index == tokens.len() {
        return ParsedCommand::Noop;
    }
    if tokens[program_index].value == "env" {
        program_index += 1;
        while program_index < tokens.len() {
            let value = &tokens[program_index].value;
            if is_assignment(value) {
                program_index += 1;
            } else if value == "-u" || value == "--unset" || value == "-C" || value == "--chdir" {
                program_index += 2;
            } else if value.starts_with('-') {
                program_index += 1;
            } else {
                break;
            }
        }
    }
    if program_index >= tokens.len() {
        return ParsedCommand::Opaque("env command has no resolved program".to_string());
    }
    if tokens[program_index].dynamic {
        return ParsedCommand::Opaque("program position is computed".to_string());
    }
    let program = tokens[program_index].value.as_str();
    if program == "echo" || program == "printf" {
        if tokens[program_index + 1..]
            .iter()
            .any(|token| looks_command_shaped(&token.value))
        {
            return ParsedCommand::Opaque(
                "command-shaped text is an echo/printf argument".to_string(),
            );
        }
        return ParsedCommand::Noop;
    }

    let mut target_index = program_index;
    if is_interpreter(program) {
        target_index += 1;
        while target_index < tokens.len() {
            let flag = tokens[target_index].value.as_str();
            if flag == "-c" || flag == "--command" {
                return ParsedCommand::Opaque("command payload is nested under -c".to_string());
            }
            if flag == "-m" || flag == "--module" {
                return ParsedCommand::Resolved {
                    target: None,
                    references: path_references(&tokens, target_index + 2, None, selected),
                };
            }
            if flag == "--" {
                target_index += 1;
                break;
            }
            if flag.starts_with('-') {
                target_index += 1;
                if interpreter_flag_takes_value(program, flag) {
                    target_index += 1;
                }
                continue;
            }
            break;
        }
        if target_index >= tokens.len() {
            return ParsedCommand::Noop;
        }
        if tokens[target_index].dynamic {
            return ParsedCommand::Opaque("interpreter target is computed".to_string());
        }
    }
    let target = snapshot_path(&tokens[target_index].value, selected);
    let references = path_references(&tokens, target_index + 1, target.as_deref(), selected);
    ParsedCommand::Resolved { target, references }
}

fn path_references(
    tokens: &[ShellToken],
    start: usize,
    target: Option<&str>,
    selected: &HashSet<String>,
) -> Vec<String> {
    tokens
        .iter()
        .enumerate()
        .skip(start)
        .filter_map(|(_, token)| {
            if token.dynamic {
                return None;
            }
            let candidate = token
                .value
                .split_once('=')
                .map_or(token.value.as_str(), |(_, value)| value);
            let path = snapshot_path(candidate, selected)?;
            (target != Some(path.as_str())).then_some(path)
        })
        .collect()
}

fn tokenize(command: &str) -> Result<(Vec<ShellToken>, bool), String> {
    let mut tokens = Vec::new();
    let mut current = String::new();
    let mut dynamic = false;
    let mut quote = None;
    let mut has_control = false;
    let mut escaped = false;
    for character in command.chars() {
        if escaped {
            current.push(character);
            escaped = false;
            continue;
        }
        if let Some(active_quote) = quote {
            if character == active_quote {
                quote = None;
            } else {
                if active_quote == '"' && character == '$' {
                    dynamic = true;
                }
                current.push(character);
            }
            continue;
        }
        match character {
            '\'' | '"' => quote = Some(character),
            '\\' => escaped = true,
            '$' => {
                dynamic = true;
                current.push(character);
            }
            ';' | '|' | '&' => {
                has_control = true;
                if !current.is_empty() {
                    tokens.push(ShellToken {
                        value: current,
                        dynamic,
                    });
                    current = String::new();
                    dynamic = false;
                }
            }
            character if character.is_whitespace() => {
                if !current.is_empty() {
                    tokens.push(ShellToken {
                        value: current,
                        dynamic,
                    });
                    current = String::new();
                    dynamic = false;
                }
            }
            character => current.push(character),
        }
    }
    if escaped {
        return Err("shell command ends with an escape".to_string());
    }
    if quote.is_some() {
        return Err("shell command has an unterminated quote".to_string());
    }
    if !current.is_empty() {
        tokens.push(ShellToken {
            value: current,
            dynamic,
        });
    }
    Ok((tokens, has_control))
}

fn is_assignment(value: &str) -> bool {
    let Some((name, _)) = value.split_once('=') else {
        return false;
    };
    !name.is_empty()
        && name.chars().enumerate().all(|(index, character)| {
            character == '_'
                || character.is_ascii_alphanumeric() && index > 0
                || character.is_ascii_alphabetic() && index == 0
        })
}

fn snapshot_path(value: &str, selected: &HashSet<String>) -> Option<String> {
    if value == "." || value == ".." || value.starts_with('/') || value.contains('$') {
        return None;
    }
    let normalized = value.strip_prefix("./").unwrap_or(value);
    if normalized.is_empty() || normalized.split('/').any(|part| part == "..") {
        return None;
    }
    selected
        .contains(normalized)
        .then_some(normalized.to_string())
}

fn is_interpreter(program: &str) -> bool {
    matches!(
        program,
        "python"
            | "python3"
            | "python3.10"
            | "python3.11"
            | "python3.12"
            | "bash"
            | "sh"
            | "zsh"
            | "node"
            | "ruby"
            | "perl"
    )
}

fn interpreter_flag_takes_value(program: &str, flag: &str) -> bool {
    match program {
        "python" | "python3" | "python3.10" | "python3.11" | "python3.12" => {
            matches!(flag, "-W" | "-X" | "-Q" | "--check-hash-based-pycs")
        }
        "bash" | "sh" | "zsh" => matches!(flag, "-o" | "--option"),
        _ => false,
    }
}

fn source_kind_for_path(path: &str) -> CarrierSourceKind {
    if path.starts_with(".githooks/") {
        CarrierSourceKind::GitHook
    } else if path.starts_with(".github/workflows/") {
        CarrierSourceKind::CiWorkflow
    } else if path == "package.json" {
        CarrierSourceKind::PackageScript
    } else if path == ".agents/surfaces.json" {
        CarrierSourceKind::SurfaceCommand
    } else if path.starts_with("integrations/tools/") {
        CarrierSourceKind::IntegrationCheck
    } else if is_structured_plan(path) {
        CarrierSourceKind::StructuredPlan
    } else {
        CarrierSourceKind::QualityGate
    }
}

fn is_structured_plan(path: &str) -> bool {
    path.starts_with(".agents/")
        && path.ends_with(".json")
        && (path.contains("command_plan") || path.contains("command-plan"))
}

fn is_shell_structure(line: &str) -> bool {
    [
        "if ", "for ", "while ", "case ", "then", "else", "elif ", "do", "done", "fi", "{",
    ]
    .iter()
    .any(|prefix| line == *prefix || line.starts_with(prefix))
}

fn shell_line_is_candidate(line: &str) -> bool {
    let first = line
        .split_whitespace()
        .find(|word| !is_assignment(word))
        .unwrap_or("");
    first.starts_with("./")
        || first.starts_with("python")
        || matches!(
            first,
            "env"
                | "bash"
                | "sh"
                | "zsh"
                | "node"
                | "ruby"
                | "perl"
                | "echo"
                | "printf"
                | "npm"
                | "cargo"
                | "git"
                | "ruff"
                | "pytest"
                | "charness"
                | "command"
        )
        || looks_command_shaped(line)
}

fn looks_command_shaped(text: &str) -> bool {
    let words = text
        .split(|character: char| {
            character.is_whitespace() || matches!(character, '"' | '\'' | '(' | ')' | ';' | '|')
        })
        .filter(|word| !word.is_empty());
    words.clone().any(|word| {
        word.starts_with("./")
            || word.starts_with("python")
            || matches!(word, "bash" | "sh" | "zsh" | "node" | "ruby" | "perl")
    })
}

fn edge_kind_name(kind: EdgeKind) -> &'static str {
    match kind {
        EdgeKind::Imports => "imports",
        EdgeKind::Invokes => "invokes",
        EdgeKind::Packages => "packages",
        EdgeKind::Mirrors => "mirrors",
        EdgeKind::Documents => "documents",
        EdgeKind::Tests => "tests",
    }
}

fn root_kind_name(kind: RootKind) -> &'static str {
    match kind {
        RootKind::ProductRuntime => "product-runtime",
        RootKind::Validation => "validation",
        RootKind::Tests => "tests",
        RootKind::Generated => "generated",
        RootKind::HostDiscovered => "host-discovered",
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::inventory::FileInventory;
    use serde_json::json;

    fn selected(values: &[&str]) -> HashSet<String> {
        values.iter().map(|value| (*value).to_string()).collect()
    }

    #[test]
    fn only_the_program_position_produces_an_invocation() {
        let paths = selected(&["scripts/check.py", "scripts/other.py"]);
        assert_eq!(
            parse_command(
                "env MODE=full python3 -B scripts/check.py --path scripts/other.py",
                &paths
            ),
            ParsedCommand::Resolved {
                target: Some("scripts/check.py".to_string()),
                references: vec!["scripts/other.py".to_string()],
            }
        );
        assert_eq!(
            parse_command("python3 -m pkg.mod", &paths),
            ParsedCommand::Resolved {
                target: None,
                references: Vec::new(),
            }
        );
        assert_eq!(
            parse_command("bash scripts/check.py", &paths),
            ParsedCommand::Resolved {
                target: Some("scripts/check.py".to_string()),
                references: Vec::new(),
            }
        );
    }

    #[test]
    fn named_negative_carriers_have_no_invocation() {
        let paths = selected(&["scripts/x.py"]);
        assert!(matches!(
            parse_command("echo \"advice: run python3 scripts/x.py\"", &paths),
            ParsedCommand::Opaque(_)
        ));
        assert!(matches!(
            parse_command("python3 \"$VAR\" --repo-root .", &paths),
            ParsedCommand::Opaque(_)
        ));
    }

    #[test]
    fn quality_source_reader_matches_its_literal_contract() {
        let inventory = FileInventory::from_file_list_bytes(
            b"scripts/run-quality.sh\0scripts/check.py\0.agents/quality-adapter.yaml\0",
        )
        .unwrap();
        let report = scan(
            Path::new(env!("CARGO_MANIFEST_DIR"))
                .join("fixtures/carriers")
                .as_path(),
            &inventory,
            &["never/".to_string()],
        );
        let labels = report
            .quality_labels
            .iter()
            .map(|label| label.label.as_str())
            .collect::<Vec<_>>();
        assert!(labels.contains(&"fixture-label"));
        assert!(report
            .unresolved_carriers
            .iter()
            .any(|entry| entry.reason.contains("unresolved (yaml)")));
    }

    #[test]
    fn carrier_fixture_matches_exact_expected_sets() {
        let inventory = FileInventory::from_file_list_bytes(
            b".githooks/pre-commit\0.github/workflows/quality.yml\0.agents/command_plan_preflight.json\0.agents/surfaces.json\0.agents/quality-adapter.yaml\0package.json\0integrations/tools/fixture.json\0scripts/run-quality.sh\0scripts/ci_validator.py\0scripts/ci_shell_validator.sh\0scripts/echo_advice.py\0scripts/first_validator.py\0scripts/hook_shell_validator.sh\0scripts/hook_validator.py\0scripts/integration_health.py\0scripts/package_shell_validator.sh\0scripts/package_validator.py\0scripts/payload_validator.py\0scripts/quality_shell_validator.sh\0scripts/quality_validator.py\0scripts/second_validator.py\0scripts/shared_input.py\0scripts/surface_sync.py\0scripts/surface_verify.py\0scripts/surface_verify.sh\0",
        )
        .unwrap();
        let report = scan(
            &Path::new(env!("CARGO_MANIFEST_DIR")).join("fixtures/carriers"),
            &inventory,
            &["never/".to_string()],
        );
        let actual = json!({
            "invokes": report.edges.iter().filter(|edge| edge.kind == EdgeKind::Invokes).map(|edge| json!({
                "source": edge.source,
                "target": edge.target,
                "line": edge.line,
            })).collect::<Vec<_>>(),
            "carrier_path_references": report.carrier_path_references.iter().map(|reference| json!({
                "kind": reference.kind,
                "carrier_id": reference.carrier_id,
                "path": reference.path,
                "line": reference.line,
            })).collect::<Vec<_>>(),
            "unresolved_carriers": report.unresolved_carriers.iter().map(|entry| json!({
                "kind": entry.kind,
                "carrier_id": entry.carrier_id,
                "tier": match entry.tier {
                    CarrierTier::StructuredUnparsed => "structured-unparsed",
                    CarrierTier::Tokenizable => "tokenizable",
                    CarrierTier::Opaque => "opaque",
                },
                "reason": entry.reason,
                "line": entry.line,
            })).collect::<Vec<_>>(),
            "quality_labels": report.quality_labels.iter().map(|label| label.label.clone()).collect::<Vec<_>>(),
        });
        let expected: Value =
            serde_json::from_str(include_str!("../fixtures/carriers/expected/carriers.json"))
                .unwrap();
        assert_eq!(actual, expected);
    }

    #[test]
    fn rust_bash_labels_match_captured_python_reader_with_yaml_gap() {
        let repo_root = Path::new(env!("CARGO_MANIFEST_DIR")).join("../..");
        let inventory = crate::inventory::acquire(&repo_root, None).unwrap();
        let report = scan(
            &repo_root,
            &inventory,
            &[
                "plugins/".to_string(),
                "native/repograph/fixtures/".to_string(),
            ],
        );
        let expected = include_str!("../fixtures/carriers/expected/quality_label_universe.yaml");
        let python_labels = yaml_list(expected, "labels:", 0);
        let yaml_labels = yaml_list(expected, "  standing_startup_probes:", 2);
        let expected_bash = python_labels
            .into_iter()
            .filter(|label| !yaml_labels.contains(label))
            .collect::<Vec<_>>();
        let rust_labels = report
            .quality_labels
            .iter()
            .map(|label| label.label.clone())
            .collect::<Vec<_>>();
        assert_eq!(rust_labels, expected_bash);
        assert!(report
            .unresolved_carriers
            .iter()
            .any(|entry| entry.reason.contains("unresolved (yaml)")));
    }

    fn yaml_list(document: &str, heading: &str, indent: usize) -> Vec<String> {
        let mut values = Vec::new();
        let mut active = false;
        for line in document.lines() {
            if line == heading {
                active = true;
                continue;
            }
            if active {
                if line.starts_with(' ')
                    && line.trim_end().ends_with(':')
                    && !line.starts_with(&" ".repeat(indent + 2))
                {
                    break;
                }
                let prefix = format!("{}- ", " ".repeat(indent));
                if let Some(value) = line.strip_prefix(&prefix) {
                    values.push(value.to_string());
                }
            }
        }
        values
    }
}
