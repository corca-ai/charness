use std::collections::{BTreeMap, BTreeSet, HashMap, HashSet};
use std::path::{Path, PathBuf};

use serde_json::Value;

use crate::graph_analyzer::ingest as ingest_analyzer_results;
use crate::graph_carriers::scan as scan_carriers;
use crate::graph_imports::{extract_import_references, resolve_imports};
use crate::graph_mirrors::{derive_mirrors, MirrorDerivation, MirrorManifest};
use crate::graph_model::{
    AdapterNode, AdapterStatus, ConditionKind, Edge, EdgeKind, FileNode, GraphReport,
    MirrorPairNode, Node, PackageKind, PackageNode, Role, Root, RootKind, SkillNode, SkillStatus,
    TestNode, TopologyConfig, TopologyDocument, Unestablished,
};
use crate::graph_roles::{classify_role, skill_frontmatter_name};
use crate::inventory::{FileInventory, InventoryError};
use crate::parser::parse_module_file;

pub const DEFAULT_EXCLUDE_PREFIXES: &[&str] = &["plugins/", "native/repograph/fixtures/"];

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct GraphOptions {
    pub repo_root: PathBuf,
    pub file_list: Option<PathBuf>,
    pub excludes: Vec<String>,
    pub analyzer_results: Vec<PathBuf>,
    pub help: bool,
}

pub fn build(
    repo_root: &Path,
    inventory: &FileInventory,
    excludes: &[String],
    analyzer_results: &[PathBuf],
) -> GraphReport {
    let snapshot_paths = inventory
        .paths()
        .iter()
        .map(|path| path.as_str().to_string())
        .collect::<HashSet<_>>();
    let selected_paths = dedupe_sorted(
        inventory
            .paths()
            .iter()
            .map(|path| path.as_str().to_string())
            .filter(|path| !excludes.iter().any(|prefix| path.starts_with(prefix)))
            .collect(),
    );

    let mut unestablished = Vec::new();
    let config = match load_topology_config(repo_root, &snapshot_paths) {
        Ok(config) => config,
        Err(condition) => {
            unestablished.push(condition);
            TopologyConfig::default()
        }
    };
    let (manifest, manifest_condition) = load_mirror_manifest(repo_root, &snapshot_paths);
    if let Some(condition) = manifest_condition {
        unestablished.push(condition);
    }

    let package_members = package_members(&selected_paths);
    let mirror_derivation = derive_mirrors(&selected_paths, &snapshot_paths, &manifest);
    unestablished.extend(mirror_derivation.unestablished.clone());
    let generated_paths = mirror_derivation
        .destinations
        .iter()
        .cloned()
        .collect::<HashSet<_>>();

    let mut nodes = package_nodes(&package_members);
    let mut edges = Vec::new();
    let mut roots = Vec::new();
    let mut roles = HashMap::new();
    let mut role_census = BTreeMap::new();
    for role in [
        Role::Production,
        Role::Test,
        Role::Generated,
        Role::Doc,
        Role::Unestablished,
    ] {
        role_census.insert(role.as_str().to_string(), 0);
    }

    for path in &selected_paths {
        let packages = packages_for_path(&package_members, path);
        let resolution = classify_role(
            path,
            !packages.is_empty(),
            generated_paths.contains(path),
            &config,
        );
        *role_census
            .get_mut(resolution.role.as_str())
            .expect("all Role variants are initialized") += 1;
        roles.insert(path.clone(), resolution.role);
        if let Some(condition) = resolution.condition {
            unestablished.push(condition);
        }
        nodes.push(Node::File(FileNode {
            id: path.clone(),
            path: path.clone(),
            role: resolution.role,
            packages: packages.clone(),
        }));
        for package in packages {
            edges.push(Edge {
                kind: EdgeKind::Packages,
                source: path.clone(),
                target: package,
                rule_id: None,
                module: None,
                line: None,
            });
        }
        if resolution.role == Role::Test {
            nodes.push(Node::Test(TestNode {
                id: format!("test:{path}"),
                file: path.clone(),
            }));
            roots.push(Root {
                kind: RootKind::Tests,
                id: format!("test:{path}"),
                target: path.clone(),
            });
        }
        if path.ends_with(".py") {
            collect_python_imports(
                repo_root,
                path,
                &snapshot_paths,
                &mut edges,
                &mut unestablished,
            );
        }
        if path.ends_with(".md") {
            collect_document_edges(path, repo_root, &snapshot_paths, &mut edges);
        }
    }

    for (path, role) in &roles {
        if *role == Role::Test {
            let test_edges = edges
                .iter()
                .filter(|edge| {
                    edge.source == *path
                        && matches!(edge.kind, EdgeKind::Imports | EdgeKind::Invokes)
                })
                .cloned()
                .collect::<Vec<_>>();
            for edge in test_edges {
                edges.push(Edge {
                    kind: EdgeKind::Tests,
                    source: edge.source.clone(),
                    target: edge.target.clone(),
                    rule_id: edge.rule_id.clone(),
                    module: edge.module.clone(),
                    line: edge.line,
                });
            }
        }
    }

    let (skill_nodes, skill_edges, skill_roots, skill_conditions) =
        discover_skill_nodes(repo_root, &selected_paths, &snapshot_paths, &manifest);
    nodes.extend(skill_nodes);
    edges.extend(skill_edges);
    roots.extend(skill_roots);
    unestablished.extend(skill_conditions);
    add_adapter_nodes(&selected_paths, &mut nodes, &mut unestablished);
    add_mirror_nodes(
        &mirror_derivation,
        &snapshot_paths,
        &mut nodes,
        &mut edges,
        &mut roots,
    );
    add_static_roots(&selected_paths, &roles, &mirror_derivation, &mut roots);
    let carrier_report = scan_carriers(repo_root, inventory, excludes);
    nodes.extend(carrier_report.nodes);
    edges.extend(carrier_report.edges);
    roots.extend(carrier_report.roots);
    let analyzer_ingestion =
        ingest_analyzer_results(repo_root, &selected_paths, &nodes, &edges, analyzer_results);
    nodes.extend(analyzer_ingestion.nodes);
    edges.extend(analyzer_ingestion.edges);
    unestablished.extend(analyzer_ingestion.unestablished);

    nodes.sort_by(|left, right| {
        left.class_name()
            .cmp(right.class_name())
            .then(left.id().cmp(right.id()))
    });
    edges.sort_by_key(edge_sort_key);
    roots.sort_by(|left, right| {
        root_kind_name(left.kind)
            .cmp(root_kind_name(right.kind))
            .then(left.id.cmp(&right.id))
            .then(left.target.cmp(&right.target))
    });
    roots.dedup();
    unestablished.sort_by(|left, right| {
        condition_kind_name(left.kind)
            .cmp(condition_kind_name(right.kind))
            .then(left.subject.cmp(&right.subject))
            .then(left.detail.cmp(&right.detail))
    });

    GraphReport {
        schema: "repograph.graph.v1",
        repo_root: display_repo_root(repo_root),
        listing: inventory.source().as_str().to_string(),
        excludes: excludes.to_vec(),
        nodes,
        edges,
        roots,
        mirror_destination_count: mirror_derivation.destinations.len(),
        mirror_destinations: mirror_derivation.destinations,
        analyzer_inputs: analyzer_ingestion.analyzer_inputs,
        role_census,
        unresolved_carriers: carrier_report.unresolved_carriers,
        carrier_path_references: carrier_report.carrier_path_references,
        quality_labels: carrier_report.quality_labels,
        unestablished,
    }
}

pub fn run<I>(args: I) -> i32
where
    I: IntoIterator<Item = String>,
{
    let options = match parse_options(args.into_iter()) {
        Ok(options) => options,
        Err(message) => return cli_error(&message),
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
            emit_inventory_error(&repo_root_argument, &options, error);
            return 3;
        }
    };
    let report = build(
        &repo_root,
        &inventory,
        &options.excludes,
        &options.analyzer_results,
    );
    let has_unestablished =
        !report.unestablished.is_empty() || !report.unresolved_carriers.is_empty();
    match serde_json::to_string(&report) {
        Ok(json) => {
            println!("{json}");
            if has_unestablished {
                3
            } else {
                0
            }
        }
        Err(error) => {
            eprintln!("internal error: could not write JSON output: {error}");
            70
        }
    }
}

fn parse_options<I>(args: I) -> Result<GraphOptions, String>
where
    I: Iterator<Item = String>,
{
    let mut repo_root = std::env::current_dir()
        .map_err(|error| format!("could not determine current directory: {error}"))?;
    let mut file_list = None;
    let mut excludes = Vec::new();
    let mut analyzer_results = Vec::new();
    let mut help = false;
    let mut args = args.peekable();
    while let Some(argument) = args.next() {
        match argument.as_str() {
            "--repo-root" => repo_root = PathBuf::from(required_value(&mut args, "--repo-root")?),
            "--file-list" => {
                file_list = Some(PathBuf::from(required_value(&mut args, "--file-list")?))
            }
            "--exclude-prefix" => excludes.push(required_value(&mut args, "--exclude-prefix")?),
            "--analyzer-result" => {
                analyzer_results.push(PathBuf::from(required_value(
                    &mut args,
                    "--analyzer-result",
                )?));
            }
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
    Ok(GraphOptions {
        repo_root,
        file_list,
        excludes,
        analyzer_results,
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

fn cli_error(message: &str) -> i32 {
    eprintln!("usage error: {message}\n{}", usage());
    2
}

fn usage() -> &'static str {
    "repograph graph [--repo-root PATH] [--file-list PATH] [--exclude-prefix PREFIX]... [--analyzer-result FILE]..."
}

fn emit_inventory_error(repo_root: &Path, options: &GraphOptions, error: InventoryError) {
    let report = GraphReport {
        schema: "repograph.graph.v1",
        repo_root: display_repo_root(repo_root),
        listing: "unestablished".to_string(),
        excludes: options.excludes.clone(),
        nodes: Vec::new(),
        edges: Vec::new(),
        roots: Vec::new(),
        mirror_destinations: Vec::new(),
        mirror_destination_count: 0,
        analyzer_inputs: Vec::new(),
        role_census: ["production", "test", "generated", "doc", "unestablished"]
            .into_iter()
            .map(|role| (role.to_string(), 0))
            .collect(),
        unresolved_carriers: Vec::new(),
        carrier_path_references: Vec::new(),
        quality_labels: Vec::new(),
        unestablished: vec![Unestablished {
            kind: ConditionKind::Inventory,
            subject: "<inventory>".to_string(),
            detail: error.to_string(),
            rules: Vec::new(),
        }],
    };
    if let Ok(json) = serde_json::to_string(&report) {
        println!("{json}");
    }
}

fn load_topology_config(
    repo_root: &Path,
    snapshot_paths: &HashSet<String>,
) -> Result<TopologyConfig, Unestablished> {
    let path = ".agents/topology.json";
    if !snapshot_paths.contains(path) {
        return Ok(TopologyConfig::default());
    }
    let on_disk = repo_root.join(path);
    let contents = std::fs::read_to_string(&on_disk).map_err(|error| Unestablished {
        kind: ConditionKind::TopologyConfig,
        subject: path.to_string(),
        detail: format!("could not read topology config: {error}"),
        rules: Vec::new(),
    })?;
    if let Ok(document) = serde_json::from_str::<TopologyDocument>(&contents) {
        return Ok(document.topology);
    }
    serde_json::from_str::<TopologyConfig>(&contents).map_err(|error| Unestablished {
        kind: ConditionKind::TopologyConfig,
        subject: path.to_string(),
        detail: format!("invalid topology config: {error}"),
        rules: Vec::new(),
    })
}

fn load_mirror_manifest(
    repo_root: &Path,
    snapshot_paths: &HashSet<String>,
) -> (MirrorManifest, Option<Unestablished>) {
    let manifest_path = "packaging/charness.json";
    let mut manifest = MirrorManifest::default();
    if !snapshot_paths.contains(manifest_path) {
        return (manifest, None);
    }
    let contents = match std::fs::read_to_string(repo_root.join(manifest_path)) {
        Ok(contents) => contents,
        Err(error) => {
            return (
                manifest,
                Some(Unestablished {
                    kind: ConditionKind::UnmodeledMirrorRule,
                    subject: manifest_path.to_string(),
                    detail: format!("could not read packaging manifest: {error}"),
                    rules: Vec::new(),
                }),
            );
        }
    };
    let raw: Value = match serde_json::from_str(&contents) {
        Ok(raw) => raw,
        Err(error) => {
            return (
                manifest,
                Some(Unestablished {
                    kind: ConditionKind::UnmodeledMirrorRule,
                    subject: manifest_path.to_string(),
                    detail: format!("invalid packaging manifest: {error}"),
                    rules: Vec::new(),
                }),
            );
        }
    };
    let source = raw.get("source").and_then(Value::as_object);
    if let Some(source) = source {
        set_string(source, "public_skills_dir", &mut manifest.public_skills_dir);
        set_string(
            source,
            "support_skills_dir",
            &mut manifest.support_skills_dir,
        );
        set_string(source, "profiles_dir", &mut manifest.profiles_dir);
        set_string(source, "presets_dir", &mut manifest.presets_dir);
        set_string(source, "integrations_dir", &mut manifest.integrations_dir);
    }
    if let Some(path) = raw
        .get("codex")
        .and_then(|value| value.get("repo_marketplace"))
        .and_then(|value| value.get("default_source_path"))
        .and_then(Value::as_str)
    {
        manifest.plugin_root = path.trim_start_matches("./").to_string();
        manifest.claude_plugin_manifest =
            format!("{}/.claude-plugin/plugin.json", manifest.plugin_root);
        manifest.codex_plugin_manifest =
            format!("{}/.codex-plugin/plugin.json", manifest.plugin_root);
    }
    if let Some(path) = raw
        .get("claude")
        .and_then(|value| value.get("marketplace"))
        .and_then(|value| value.get("path"))
        .and_then(Value::as_str)
    {
        manifest.claude_marketplace_manifest = path.to_string();
    }
    if let Some(path) = raw
        .get("codex")
        .and_then(|value| value.get("repo_marketplace"))
        .and_then(|value| value.get("path"))
        .and_then(Value::as_str)
    {
        manifest.codex_marketplace_manifest = path.to_string();
    }
    for path in snapshot_paths {
        if !path.starts_with("integrations/tools/") || !path.ends_with(".json") {
            continue;
        }
        let Ok(contents) = std::fs::read_to_string(repo_root.join(path)) else {
            continue;
        };
        let Ok(raw) = serde_json::from_str::<Value>(&contents) else {
            continue;
        };
        let Some(tool_id) = raw.get("tool_id").and_then(Value::as_str) else {
            continue;
        };
        let Some(support) = raw.get("support_skill_source").and_then(Value::as_object) else {
            continue;
        };
        let support_id =
            if support.get("source_type").and_then(Value::as_str) == Some("local_wrapper") {
                support
                    .get("wrapper_skill_id")
                    .and_then(Value::as_str)
                    .unwrap_or(tool_id)
            } else {
                tool_id
            };
        manifest
            .upstream_consumed_support_ids
            .insert(support_id.to_string());
    }
    (manifest, None)
}

fn set_string(source: &serde_json::Map<String, Value>, name: &str, target: &mut String) {
    if let Some(value) = source.get(name).and_then(Value::as_str) {
        *target = value.to_string();
    }
}

fn package_members(paths: &[String]) -> BTreeMap<String, Vec<String>> {
    let mut members = BTreeMap::<String, Vec<String>>::new();
    for path in paths {
        for (package, _) in package_ids_for_path(path) {
            members.entry(package).or_default().push(path.clone());
        }
    }
    for paths in members.values_mut() {
        paths.sort();
        paths.dedup();
    }
    members
}

fn package_nodes(members: &BTreeMap<String, Vec<String>>) -> Vec<Node> {
    members
        .iter()
        .map(|(id, paths)| {
            let (path, kind) =
                package_ids_for_path(paths.first().map(String::as_str).unwrap_or(id))
                    .into_iter()
                    .find(|(candidate, _)| candidate == id)
                    .unwrap_or_else(|| (id.clone(), PackageKind::Scripts));
            Node::Package(PackageNode {
                id: id.clone(),
                package_kind: kind,
                path,
                members: paths.clone(),
            })
        })
        .collect()
}

fn packages_for_path(members: &BTreeMap<String, Vec<String>>, path: &str) -> Vec<String> {
    members
        .iter()
        .filter(|(_, paths)| paths.iter().any(|member| member == path))
        .map(|(package, _)| package.clone())
        .collect()
}

fn package_ids_for_path(path: &str) -> Vec<(String, PackageKind)> {
    let mut packages = Vec::new();
    if let Some(rest) = path.strip_prefix("skills/public/") {
        if let Some(skill) = skill_directory_component(rest) {
            packages.push((format!("skills/public/{skill}"), PackageKind::Skill));
        }
    } else if let Some(rest) = path.strip_prefix("skills/support/") {
        if let Some(skill) = skill_directory_component(rest) {
            packages.push((format!("skills/support/{skill}"), PackageKind::Skill));
        }
    }
    if path == "skills/shared" || path.starts_with("skills/shared/") {
        packages.push(("skills/shared".to_string(), PackageKind::SharedLibrary));
    }
    if path == "scripts" || path.starts_with("scripts/") {
        packages.push(("scripts".to_string(), PackageKind::Scripts));
    }
    if path == "tools" || path.starts_with("tools/") {
        packages.push(("tools".to_string(), PackageKind::Scripts));
    }
    if path == "tests" || path.starts_with("tests/") {
        packages.push(("tests".to_string(), PackageKind::Tests));
    }
    if path == "plugins/charness" || path.starts_with("plugins/charness/") {
        packages.push(("plugins/charness".to_string(), PackageKind::PluginExport));
    }
    if path == "native/repograph" || path.starts_with("native/repograph/") {
        packages.push(("native/repograph".to_string(), PackageKind::NativeCrate));
    }
    if [
        "charness",
        "init.sh",
        "runtime_bootstrap.py",
        "yaml_output.py",
        "skill_runtime_bootstrap.py",
    ]
    .contains(&path)
    {
        packages.push(("charness".to_string(), PackageKind::Cli));
    }
    packages
}

fn skill_directory_component(rest: &str) -> Option<&str> {
    let mut components = rest.split('/');
    let skill = components.next().filter(|value| !value.is_empty())?;
    if skill.starts_with('.') || components.next().is_none() {
        return None;
    }
    Some(skill)
}

fn collect_python_imports(
    repo_root: &Path,
    path: &str,
    snapshot_paths: &HashSet<String>,
    edges: &mut Vec<Edge>,
    unestablished: &mut Vec<Unestablished>,
) {
    let source = match std::fs::read_to_string(repo_root.join(path)) {
        Ok(source) => source,
        Err(error) => {
            unestablished.push(Unestablished {
                kind: ConditionKind::ParseFailure,
                subject: path.to_string(),
                detail: format!("unreadable Python source: {error}"),
                rules: Vec::new(),
            });
            return;
        }
    };
    let module = match parse_module_file(repo_root, path) {
        Ok(module) => module,
        Err(result) => {
            unestablished.push(Unestablished {
                kind: ConditionKind::ParseFailure,
                subject: path.to_string(),
                detail: result.detail,
                rules: Vec::new(),
            });
            return;
        }
    };
    let (references, inserted_paths) = extract_import_references(&module, &source);
    for resolved in resolve_imports(
        repo_root,
        path,
        &references,
        &inserted_paths,
        snapshot_paths,
    ) {
        edges.push(Edge {
            kind: EdgeKind::Imports,
            source: path.to_string(),
            target: resolved.target,
            rule_id: None,
            module: Some(resolved.reference.module),
            line: Some(resolved.reference.line),
        });
    }
}

fn collect_document_edges(
    path: &str,
    repo_root: &Path,
    snapshot_paths: &HashSet<String>,
    edges: &mut Vec<Edge>,
) {
    let Ok(contents) = std::fs::read_to_string(repo_root.join(path)) else {
        return;
    };
    let parent = Path::new(path).parent().unwrap_or_else(|| Path::new(""));
    let mut remainder = contents.as_str();
    while let Some(index) = remainder.find("](") {
        remainder = &remainder[index + 2..];
        let Some(end) = remainder.find(')') else {
            break;
        };
        let mut target = remainder[..end].trim();
        if let Some(stripped) = target
            .strip_prefix('<')
            .and_then(|value| value.strip_suffix('>'))
        {
            target = stripped;
        }
        target = target.split(['#', '?']).next().unwrap_or(target);
        if !target.is_empty()
            && !target.starts_with('/')
            && !target.contains("://")
            && !target.starts_with("mailto:")
        {
            let candidate = normalize_relative_path(parent, target);
            if snapshot_paths.contains(&candidate) {
                edges.push(Edge {
                    kind: EdgeKind::Documents,
                    source: path.to_string(),
                    target: candidate,
                    rule_id: None,
                    module: None,
                    line: None,
                });
            }
        }
        remainder = &remainder[end + 1..];
    }
}

fn normalize_relative_path(parent: &Path, target: &str) -> String {
    let mut components = parent
        .join(target)
        .components()
        .filter_map(|component| match component {
            std::path::Component::Normal(value) => value.to_str().map(str::to_string),
            std::path::Component::ParentDir => Some("..".to_string()),
            _ => None,
        })
        .collect::<Vec<_>>();
    while components.iter().any(|component| component == "..") {
        let Some(index) = components.iter().position(|component| component == "..") else {
            break;
        };
        if index == 0 {
            components.remove(index);
        } else {
            components.drain(index - 1..=index);
        }
    }
    components.join("/")
}

fn discover_skill_nodes(
    repo_root: &Path,
    selected_paths: &[String],
    snapshot_paths: &HashSet<String>,
    manifest: &MirrorManifest,
) -> (Vec<Node>, Vec<Edge>, Vec<Root>, Vec<Unestablished>) {
    let mut nodes = Vec::new();
    let mut edges = Vec::new();
    let mut roots = Vec::new();
    let mut unestablished = Vec::new();
    let mut directories = BTreeSet::new();
    for path in selected_paths {
        for prefix in ["skills/public/", "skills/support/"] {
            if let Some(rest) = path.strip_prefix(prefix) {
                if let Some(skill) = skill_directory_component(rest) {
                    directories.insert(format!("{prefix}{skill}"));
                }
            }
        }
    }
    for directory in directories {
        if directory == "skills/support/generated" {
            continue;
        }
        if directory.starts_with("skills/support/") {
            let skill_id = directory.trim_start_matches("skills/support/");
            if manifest.upstream_consumed_support_ids.contains(skill_id) {
                continue;
            }
        }
        let skill_file = format!("{directory}/SKILL.md");
        let name = snapshot_paths
            .contains(&skill_file)
            .then(|| std::fs::read_to_string(repo_root.join(&skill_file)).ok())
            .flatten()
            .and_then(|contents| skill_frontmatter_name(&contents));
        let modeled = name.is_some();
        let id = name
            .clone()
            .unwrap_or_else(|| format!("malformed-skill:{directory}"));
        nodes.push(Node::Skill(SkillNode {
            id: id.clone(),
            directory: directory.clone(),
            frontmatter_name: name,
            status: if modeled {
                SkillStatus::Modeled
            } else {
                SkillStatus::MalformedSkill
            },
        }));
        let package_id = directory.clone();
        if selected_paths
            .iter()
            .any(|path| path.starts_with(&(directory.clone() + "/")))
        {
            edges.push(Edge {
                kind: EdgeKind::Packages,
                source: id.clone(),
                target: package_id,
                rule_id: None,
                module: None,
                line: None,
            });
        }
        roots.push(Root {
            kind: RootKind::HostDiscovered,
            id: format!("skill:{id}"),
            target: id,
        });
        if !modeled {
            unestablished.push(Unestablished {
                kind: ConditionKind::MalformedSkill,
                subject: directory,
                detail: "skill candidate has no valid frontmatter name: line".to_string(),
                rules: vec!["frontmatter-subset".to_string()],
            });
        }
    }
    (nodes, edges, roots, unestablished)
}

const ADAPTER_TABLE: &[(&str, &str)] = &[
    (".agents/achieve-adapter.yaml", "achieve"),
    (".agents/critique-adapter.yaml", "critique"),
    (".agents/create-skill-adapter.yaml", "create-skill"),
    (".agents/hitl-adapter.yaml", "hitl"),
    (".agents/impl-adapter.yaml", "impl"),
    (".agents/issue-adapter.yaml", "issue"),
    (".agents/markdown-preview.yaml", "markdown-preview"),
    (".agents/narrative-adapter.yaml", "narrative"),
    (".agents/quality-adapter.yaml", "quality"),
    (".agents/release-adapter.yaml", "release"),
    (".agents/retro-adapter.yaml", "retro"),
    (".agents/setup-adapter.yaml", "setup"),
    (".agents/worktree-adapter.yaml", "integrations/worktree"),
];

fn add_adapter_nodes(
    selected_paths: &[String],
    nodes: &mut Vec<Node>,
    unestablished: &mut Vec<Unestablished>,
) {
    for path in selected_paths {
        let Some(rest) = path.strip_prefix(".agents/") else {
            continue;
        };
        if rest.contains('/') {
            continue;
        }
        let owner = ADAPTER_TABLE
            .iter()
            .find(|(candidate, _)| *candidate == path)
            .map(|(_, owner)| (*owner).to_string());
        let modeled = owner.is_some();
        nodes.push(Node::Adapter(AdapterNode {
            id: path.clone(),
            declaration_path: path.clone(),
            owner,
            status: if modeled {
                AdapterStatus::Modeled
            } else {
                AdapterStatus::UnmodeledDeclaration
            },
        }));
        if !modeled {
            unestablished.push(Unestablished {
                kind: ConditionKind::UnmodeledDeclaration,
                subject: path.clone(),
                detail: "`.agents/*` declaration is not in the explicit adapter table".to_string(),
                rules: vec!["explicit-adapter-table".to_string()],
            });
        }
    }
}

fn add_mirror_nodes(
    derivation: &MirrorDerivation,
    snapshot_paths: &HashSet<String>,
    nodes: &mut Vec<Node>,
    edges: &mut Vec<Edge>,
    roots: &mut Vec<Root>,
) {
    for pair in &derivation.pairs {
        let source_id = pair.source.as_deref().unwrap_or("<manifest>");
        let id = format!("{}:{source_id}:{}", pair.rule_id, pair.destination);
        nodes.push(Node::MirrorPair(MirrorPairNode {
            id,
            rule_id: pair.rule_id.clone(),
            source: pair.source.clone(),
            destination: pair.destination.clone(),
            transform: pair.transform,
            content_transformed: pair.content_transformed,
            destination_in_snapshot: snapshot_paths.contains(&pair.destination),
        }));
        if let Some(source) = &pair.source {
            edges.push(Edge {
                kind: EdgeKind::Mirrors,
                source: source.clone(),
                target: pair.destination.clone(),
                rule_id: Some(pair.rule_id.clone()),
                module: None,
                line: None,
            });
        }
        roots.push(Root {
            kind: RootKind::Generated,
            id: format!("generated:{}", pair.destination),
            target: pair.destination.clone(),
        });
    }
}

fn add_static_roots(
    selected_paths: &[String],
    roles: &HashMap<String, Role>,
    derivation: &MirrorDerivation,
    roots: &mut Vec<Root>,
) {
    for path in selected_paths {
        if [
            "charness",
            "init.sh",
            "runtime_bootstrap.py",
            "yaml_output.py",
            "skill_runtime_bootstrap.py",
        ]
        .contains(&path.as_str())
        {
            roots.push(Root {
                kind: RootKind::ProductRuntime,
                id: format!("runtime:{path}"),
                target: path.clone(),
            });
        }
        if path == "scripts/run-quality.sh"
            || path == ".githooks/pre-commit"
            || path.starts_with(".github/workflows/")
            || path == ".agents/surfaces.json"
        {
            roots.push(Root {
                kind: RootKind::Validation,
                id: format!("validation:{path}"),
                target: path.clone(),
            });
        }
        if path.starts_with(".claude/agents/") {
            roots.push(Root {
                kind: RootKind::HostDiscovered,
                id: format!("host:{path}"),
                target: path.clone(),
            });
        }
        if path == ".claude-plugin/marketplace.json" || path == ".agents/plugins/marketplace.json" {
            roots.push(Root {
                kind: RootKind::HostDiscovered,
                id: format!("marketplace:{path}"),
                target: path.clone(),
            });
        }
        let _ = roles.get(path);
    }
    let _ = derivation;
}

fn dedupe_sorted(mut paths: Vec<String>) -> Vec<String> {
    paths.sort();
    paths.dedup();
    paths
}

pub(crate) fn display_repo_root(repo_root: &Path) -> String {
    if repo_root.is_absolute() {
        ".".to_string()
    } else {
        repo_root.to_string_lossy().replace('\\', "/")
    }
}

fn edge_sort_key(edge: &Edge) -> (String, String, String, String, usize) {
    (
        edge_kind_name(edge.kind).to_string(),
        edge.source.clone(),
        edge.target.clone(),
        edge.module.clone().unwrap_or_default(),
        edge.line.unwrap_or(0),
    )
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

fn condition_kind_name(kind: ConditionKind) -> &'static str {
    match kind {
        ConditionKind::AnalyzerNotParsed => "analyzer-not-parsed",
        ConditionKind::AnalyzerParseFailure => "analyzer-parse-failure",
        ConditionKind::AnalyzerVersionMismatch => "analyzer-version-mismatch",
        ConditionKind::AnalyzerIncomplete => "analyzer-incomplete",
        ConditionKind::AnalyzerZeroModules => "analyzer-zero-modules",
        ConditionKind::ScopeViolation => "scope-violation",
        ConditionKind::AnalyzerExcluded => "analyzer-excluded",
        ConditionKind::Inventory => "inventory",
        ConditionKind::MalformedSkill => "malformed-skill",
        ConditionKind::ParseFailure => "parse-failure",
        ConditionKind::RoleConflict => "role-conflict",
        ConditionKind::RoleUnestablished => "role-unestablished",
        ConditionKind::ScopeConflict => "scope-conflict",
        ConditionKind::TopologyConfig => "topology-config",
        ConditionKind::UnmodeledDeclaration => "unmodeled-declaration",
        ConditionKind::UnmodeledMirrorRule => "unmodeled-mirror-rule",
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::inventory::FileInventory;

    fn fixture_root() -> PathBuf {
        Path::new(env!("CARGO_MANIFEST_DIR")).join("fixtures")
    }

    #[test]
    fn duplicate_inventory_paths_are_deduped_and_ordered() {
        let inventory = FileInventory::from_file_list_bytes(
            b"scripts/second.py\0scripts/first.py\0scripts/second.py\0",
        )
        .unwrap();
        let report = build(&fixture_root(), &inventory, &["never/".to_string()], &[]);
        let paths = report
            .nodes
            .iter()
            .filter_map(|node| match node {
                Node::File(file) => Some(file.path.clone()),
                _ => None,
            })
            .collect::<Vec<_>>();
        assert_eq!(paths, ["scripts/first.py", "scripts/second.py"]);
    }

    #[test]
    fn malformed_skill_and_adapter_fallback_are_typed() {
        let inventory = FileInventory::from_file_list_bytes(
            b"skills/public/handoff/SKILL.md\0.agents/unlisted.json\0",
        )
        .unwrap();
        let report = build(&fixture_root(), &inventory, &["never/".to_string()], &[]);
        assert!(report.nodes.iter().any(|node| {
            matches!(node, Node::Skill(skill) if skill.status == SkillStatus::MalformedSkill)
        }));
        assert!(report
            .unestablished
            .iter()
            .any(|entry| entry.kind == ConditionKind::UnmodeledDeclaration));
    }

    #[test]
    fn graph_serialization_is_byte_stable_for_same_file_list() {
        let inventory = FileInventory::from_file_list_bytes(
            b"pkg/cycle_b.py\0pkg/cycle_a.py\0pkg/cycle_a.py\0",
        )
        .unwrap();
        let first = serde_json::to_vec(&build(
            &fixture_root(),
            &inventory,
            &["never/".to_string()],
            &[],
        ))
        .unwrap();
        let second = serde_json::to_vec(&build(
            &fixture_root(),
            &inventory,
            &["never/".to_string()],
            &[],
        ))
        .unwrap();
        assert_eq!(first, second);
    }

    #[test]
    fn analyzer_input_parse_failure_is_typed() {
        let inventory = FileInventory::from_file_list_bytes(b"scripts/helper.py\0").unwrap();
        let report = build(
            &fixture_root(),
            &inventory,
            &["never/".to_string()],
            &[PathBuf::from("missing-analyzer.json")],
        );
        assert_eq!(report.analyzer_inputs[0].scope, "unestablished");
        assert!(report
            .unestablished
            .iter()
            .any(|entry| entry.kind == ConditionKind::AnalyzerParseFailure));
    }

    #[test]
    fn complete_analyzer_result_is_merged_into_graph() {
        let inventory =
            FileInventory::from_file_list_bytes(b"pkg/cycle_a.py\0pkg/cycle_b.py\0").unwrap();
        let result_path =
            Path::new(env!("CARGO_MANIFEST_DIR")).join("fixtures/analyzers/complete.json");
        let report = build(
            &fixture_root(),
            &inventory,
            &["never/".to_string()],
            &[result_path],
        );
        assert_eq!(report.analyzer_inputs.len(), 1);
        assert_eq!(
            report.analyzer_inputs[0].identity,
            "rev-dep@0.4.0:commit:fixture-commit-746"
        );
        assert!(report.nodes.iter().any(|node| {
            matches!(
                node,
                Node::ExternalModule(module)
                    if module.id == "external-module:rev-dep:runtime-library"
            )
        }));
        assert_eq!(
            report
                .edges
                .iter()
                .filter(|edge| edge.rule_id.as_deref() == Some("analyzer:rev-dep@0.4.0"))
                .count(),
            2
        );
    }
}
