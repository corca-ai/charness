use std::collections::{BTreeMap, BTreeSet, HashSet, VecDeque};
use std::path::{Path, PathBuf};

use serde::Serialize;

use crate::graph;
use crate::graph_model::{
    ConditionKind, Edge, GraphReport, Node, Role, Root, RootKind, Unestablished,
};
use crate::inventory::{FileInventory, InventoryError};
use crate::surfaces::{self, SurfaceError, SurfaceManifest};

pub const DEFAULT_SURFACES_PATH: &str = ".agents/surfaces.json";

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct QueryOptions {
    pub repo_root: PathBuf,
    pub file_list: Option<PathBuf>,
    pub surfaces: PathBuf,
    pub paths: Vec<String>,
    pub excludes: Vec<String>,
    pub analyzer_results: Vec<PathBuf>,
    pub help: bool,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize)]
#[serde(rename_all = "kebab-case")]
pub enum Presence {
    Present,
    AbsentFromSnapshot,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct SurfaceMembership {
    pub surface_id: String,
    pub matched_source: bool,
    pub matched_derived: bool,
    pub production: Option<bool>,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct ClassifiedPath {
    pub path: String,
    pub role: String,
    pub presence: Presence,
    pub package: Option<String>,
    pub surfaces: Vec<SurfaceMembership>,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct ClassifyReport {
    pub schema: &'static str,
    pub repo_root: String,
    pub listing: String,
    pub excludes: Vec<String>,
    pub paths: Vec<ClassifiedPath>,
    pub role_census: BTreeMap<String, usize>,
    pub unestablished_by_top_level: BTreeMap<String, usize>,
    pub unestablished: Vec<Unestablished>,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct ChangedRoot {
    pub kind: RootKind,
    pub id: String,
    pub target: String,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct ChangedPath {
    #[serde(flatten)]
    pub classification: ClassifiedPath,
    pub affected_roots: Vec<ChangedRoot>,
    pub explanations: Vec<String>,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct ChangedReport {
    pub schema: &'static str,
    pub repo_root: String,
    pub listing: String,
    pub excludes: Vec<String>,
    pub paths: Vec<ChangedPath>,
    pub affected_surfaces: Vec<String>,
    pub affected_packages: Vec<String>,
    pub affected_roots: Vec<ChangedRoot>,
    pub unestablished: Vec<Unestablished>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct QueryError(pub String);

impl std::fmt::Display for QueryError {
    fn fmt(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        formatter.write_str(&self.0)
    }
}

impl std::error::Error for QueryError {}

pub fn classify(
    repo_root: &Path,
    inventory: &FileInventory,
    options: &QueryOptions,
) -> Result<ClassifyReport, QueryError> {
    let manifest = load_surface_manifest(repo_root, &options.surfaces)?;
    let paths = requested_paths(inventory, &options.paths, &options.excludes)?;
    let snapshot_paths = inventory
        .paths()
        .iter()
        .map(|path| path.as_str().to_string())
        .collect::<HashSet<_>>();
    let graph = build_query_graph(repo_root, inventory, &paths, &options.excludes, options);
    let mut unestablished = analyzer_conditions(&graph);
    let mut classified = Vec::with_capacity(paths.len());
    let mut role_census = role_census();
    let mut unestablished_by_top_level = BTreeMap::new();

    for path in paths {
        let presence = if snapshot_paths.contains(&path) {
            Presence::Present
        } else {
            Presence::AbsentFromSnapshot
        };
        let (role, package, condition) = path_classification(&graph, &path, presence);
        *role_census
            .get_mut(role.as_census_role())
            .expect("all query roles are initialized") += 1;
        if let Some(condition) = condition {
            *unestablished_by_top_level
                .entry(top_level(&path))
                .or_insert(0) += 1;
            unestablished.push(condition);
        }
        classified.push(ClassifiedPath {
            path: path.clone(),
            role: role.as_output_role().to_string(),
            presence,
            package,
            surfaces: surface_memberships(&manifest, &path, presence, role),
        });
    }

    Ok(ClassifyReport {
        schema: "repograph.classify.v1",
        repo_root: display_repo_root(repo_root),
        listing: inventory.source().as_str().to_string(),
        excludes: options.excludes.clone(),
        paths: classified,
        role_census,
        unestablished_by_top_level,
        unestablished: dedupe_conditions(unestablished),
    })
}

pub fn changed(
    repo_root: &Path,
    inventory: &FileInventory,
    options: &QueryOptions,
) -> Result<ChangedReport, QueryError> {
    let classified = classify(repo_root, inventory, options)?;
    let graph = build_query_graph(
        repo_root,
        inventory,
        &classified
            .paths
            .iter()
            .map(|path| path.path.clone())
            .collect::<Vec<_>>(),
        &options.excludes,
        options,
    );
    let mut affected_surfaces = BTreeSet::new();
    let mut affected_packages = BTreeSet::new();
    let mut affected_roots = Vec::new();
    let mut paths = Vec::with_capacity(classified.paths.len());

    let ClassifyReport {
        repo_root,
        listing,
        excludes,
        paths: classified_paths,
        unestablished,
        ..
    } = classified;
    for path in classified_paths {
        for surface in &path.surfaces {
            affected_surfaces.insert(surface.surface_id.clone());
        }
        if let Some(package) = &path.package {
            affected_packages.insert(package.clone());
        }
        let roots = roots_reaching(&graph, &path.path);
        affected_roots.extend(roots.iter().cloned());
        let explanations = explanations(&path, &roots);
        paths.push(ChangedPath {
            classification: path,
            affected_roots: roots,
            explanations,
        });
    }
    affected_roots
        .sort_by(|left, right| left.id.cmp(&right.id).then(left.target.cmp(&right.target)));
    affected_roots.dedup();

    Ok(ChangedReport {
        schema: "repograph.changed.v1",
        repo_root,
        listing,
        excludes,
        paths,
        affected_surfaces: affected_surfaces.into_iter().collect(),
        affected_packages: affected_packages.into_iter().collect(),
        affected_roots,
        unestablished,
    })
}

fn load_surface_manifest(
    repo_root: &Path,
    surfaces_path: &Path,
) -> Result<SurfaceManifest, QueryError> {
    surfaces::load_surfaces(repo_root, surfaces_path).map_err(|error| QueryError(error.to_string()))
}

fn requested_paths(
    inventory: &FileInventory,
    requested: &[String],
    excludes: &[String],
) -> Result<Vec<String>, QueryError> {
    if requested.is_empty() {
        let mut paths = inventory
            .paths()
            .iter()
            .map(|path| path.as_str().to_string())
            .filter(|path| !excludes.iter().any(|prefix| path.starts_with(prefix)))
            .map(|path| surfaces::normalize_repo_path(&path))
            .collect::<Result<Vec<_>, _>>()
            .map_err(|error| QueryError(error.to_string()))?;
        paths.sort();
        paths.dedup();
        return Ok(paths);
    }
    let mut paths = requested
        .iter()
        .map(|path| surfaces::normalize_repo_path(path))
        .collect::<Result<Vec<_>, SurfaceError>>()
        .map_err(|error| QueryError(error.to_string()))?;
    let mut seen = HashSet::new();
    paths.retain(|path| seen.insert(path.clone()));
    Ok(paths)
}

fn build_query_graph(
    repo_root: &Path,
    inventory: &FileInventory,
    query_paths: &[String],
    excludes: &[String],
    options: &QueryOptions,
) -> GraphReport {
    let mut paths = inventory
        .paths()
        .iter()
        .map(|path| path.as_str().to_string())
        .filter(|path| !excludes.iter().any(|prefix| path.starts_with(prefix)))
        .collect::<BTreeSet<_>>();
    paths.extend(query_paths.iter().cloned());
    let bytes = paths
        .into_iter()
        .flat_map(|path| path.into_bytes().into_iter().chain(std::iter::once(0)))
        .collect::<Vec<_>>();
    let augmented = FileInventory::from_file_list_bytes(&bytes)
        .expect("query paths are normalized and inventory paths are already validated");
    graph::build(repo_root, &augmented, &[], &options.analyzer_results)
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum QueryRole {
    Production,
    Test,
    Generated,
    Doc,
    Unestablished,
    UnestablishedAbsent,
}

impl QueryRole {
    fn as_output_role(self) -> &'static str {
        match self {
            Self::Production => "production",
            Self::Test => "test",
            Self::Generated => "generated",
            Self::Doc => "doc",
            Self::Unestablished => "unestablished",
            Self::UnestablishedAbsent => "unestablished-absent",
        }
    }

    fn as_census_role(self) -> &'static str {
        match self {
            Self::UnestablishedAbsent | Self::Unestablished => "unestablished",
            _ => self.as_output_role(),
        }
    }
}

fn path_classification(
    report: &GraphReport,
    path: &str,
    presence: Presence,
) -> (QueryRole, Option<String>, Option<Unestablished>) {
    let file = report.nodes.iter().find_map(|node| match node {
        Node::File(file) if file.path == path => Some(file),
        _ => None,
    });
    let Some(file) = file else {
        return (
            if presence == Presence::AbsentFromSnapshot {
                QueryRole::UnestablishedAbsent
            } else {
                QueryRole::Unestablished
            },
            None,
            Some(Unestablished {
                kind: ConditionKind::RoleUnestablished,
                subject: path.to_string(),
                detail: "query path was not classified by the topology resolver".to_string(),
                rules: Vec::new(),
            }),
        );
    };
    let role = match (file.role, presence) {
        (Role::Production, _) => QueryRole::Production,
        (Role::Test, _) => QueryRole::Test,
        (Role::Generated, _) => QueryRole::Generated,
        (Role::Doc, _) => QueryRole::Doc,
        (Role::Unestablished, Presence::AbsentFromSnapshot) => QueryRole::UnestablishedAbsent,
        (Role::Unestablished, Presence::Present) => QueryRole::Unestablished,
    };
    let condition = report
        .unestablished
        .iter()
        .find(|condition| {
            condition.subject == path
                && matches!(
                    condition.kind,
                    ConditionKind::RoleConflict | ConditionKind::RoleUnestablished
                )
        })
        .cloned();
    (
        role,
        file.packages.first().cloned(),
        condition.or_else(|| {
            (role == QueryRole::Unestablished || role == QueryRole::UnestablishedAbsent).then(
                || Unestablished {
                    kind: ConditionKind::RoleUnestablished,
                    subject: path.to_string(),
                    detail: "topology role is unestablished".to_string(),
                    rules: Vec::new(),
                },
            )
        }),
    )
}

fn surface_memberships(
    manifest: &SurfaceManifest,
    path: &str,
    presence: Presence,
    role: QueryRole,
) -> Vec<SurfaceMembership> {
    manifest
        .surfaces
        .iter()
        .filter_map(|surface| {
            let matched_source = surfaces::path_matches_patterns(path, &surface.source_paths);
            let matched_derived = surfaces::path_matches_patterns(path, &surface.derived_paths);
            (matched_source || matched_derived).then(|| SurfaceMembership {
                surface_id: surface.surface_id.clone(),
                matched_source,
                matched_derived,
                production: if presence == Presence::Present && role != QueryRole::Unestablished {
                    match role {
                        QueryRole::Production => Some(true),
                        QueryRole::Test | QueryRole::Generated | QueryRole::Doc => Some(false),
                        QueryRole::Unestablished | QueryRole::UnestablishedAbsent => None,
                    }
                } else {
                    None
                },
            })
        })
        .collect()
}

fn roots_reaching(report: &GraphReport, path: &str) -> Vec<ChangedRoot> {
    report
        .roots
        .iter()
        .filter(|root| root_reaches_path(root, path, &report.edges))
        .map(|root| ChangedRoot {
            kind: root.kind,
            id: root.id.clone(),
            target: root.target.clone(),
        })
        .collect()
}

fn root_reaches_path(root: &Root, path: &str, edges: &[Edge]) -> bool {
    if root.target == path {
        return true;
    }
    let mut queue = VecDeque::from([root.target.clone()]);
    let mut visited = HashSet::new();
    while let Some(source) = queue.pop_front() {
        if !visited.insert(source.clone()) {
            continue;
        }
        for edge in edges.iter().filter(|edge| edge.source == source) {
            if edge.target == path {
                return true;
            }
            queue.push_back(edge.target.clone());
        }
    }
    false
}

fn explanations(path: &ClassifiedPath, roots: &[ChangedRoot]) -> Vec<String> {
    let mut result = Vec::new();
    for surface in &path.surfaces {
        let match_kind = match (surface.matched_source, surface.matched_derived) {
            (true, true) => "source and derived patterns",
            (true, false) => "source pattern",
            (false, true) => "derived pattern",
            (false, false) => "surface pattern",
        };
        let role_detail = match surface.production {
            Some(true) => "role is production",
            Some(false) => "role is not production",
            None => "production membership is unestablished for this snapshot",
        };
        result.push(format!(
            "surface `{}` matched {match_kind}; {role_detail}",
            surface.surface_id
        ));
    }
    if let Some(package) = &path.package {
        result.push(format!("package `{package}` owns this path"));
    }
    for root in roots {
        result.push(format!("root `{}` reaches this path", root.id));
    }
    if result.is_empty() {
        result.push(format!(
            "no declared surface, package, or root reached `{}`",
            path.path
        ));
    }
    result
}

fn analyzer_conditions(report: &GraphReport) -> Vec<Unestablished> {
    report
        .unestablished
        .iter()
        .filter(|condition| {
            matches!(
                condition.kind,
                ConditionKind::AnalyzerNotParsed
                    | ConditionKind::AnalyzerParseFailure
                    | ConditionKind::AnalyzerVersionMismatch
                    | ConditionKind::AnalyzerIncomplete
                    | ConditionKind::AnalyzerZeroModules
                    | ConditionKind::ScopeViolation
                    | ConditionKind::AnalyzerExcluded
            )
        })
        .cloned()
        .collect()
}

fn dedupe_conditions(mut conditions: Vec<Unestablished>) -> Vec<Unestablished> {
    conditions.sort_by(|left, right| {
        left.subject
            .cmp(&right.subject)
            .then(left.detail.cmp(&right.detail))
    });
    conditions.dedup();
    conditions
}

fn role_census() -> BTreeMap<String, usize> {
    ["production", "test", "generated", "doc", "unestablished"]
        .into_iter()
        .map(|role| (role.to_string(), 0))
        .collect()
}

fn top_level(path: &str) -> String {
    path.split_once('/').map_or_else(
        || "<root>".to_string(),
        |(directory, _)| directory.to_string(),
    )
}

fn display_repo_root(repo_root: &Path) -> String {
    if repo_root.is_absolute() {
        ".".to_string()
    } else {
        repo_root.to_string_lossy().replace('\\', "/")
    }
}

pub fn run_classify<I>(args: I) -> i32
where
    I: IntoIterator<Item = String>,
{
    run_query(args, false)
}

pub fn run_changed<I>(args: I) -> i32
where
    I: IntoIterator<Item = String>,
{
    run_query(args, true)
}

fn run_query<I>(args: I, changed_command: bool) -> i32
where
    I: IntoIterator<Item = String>,
{
    let options = match parse_options(args.into_iter()) {
        Ok(options) => options,
        Err(message) => return cli_error(&message, changed_command),
    };
    if options.help {
        println!("{}", usage(changed_command));
        return 0;
    }
    let repo_root_argument = options.repo_root.clone();
    let repo_root = std::fs::canonicalize(&options.repo_root).unwrap_or(options.repo_root.clone());
    let inventory = match crate::inventory::acquire(&repo_root, options.file_list.as_deref()) {
        Ok(inventory) => inventory,
        Err(error) => {
            emit_inventory_error(&repo_root_argument, &options, error, changed_command);
            return 3;
        }
    };
    let result = if changed_command {
        changed(&repo_root, &inventory, &options).map(|report| {
            (
                report.unestablished.is_empty(),
                serde_json::to_string(&report),
            )
        })
    } else {
        classify(&repo_root, &inventory, &options).map(|report| {
            (
                report.unestablished.is_empty(),
                serde_json::to_string(&report),
            )
        })
    };
    match result {
        Ok((established, Ok(json))) => {
            println!("{json}");
            if established {
                0
            } else {
                3
            }
        }
        Ok((_, Err(error))) => {
            eprintln!("internal error: could not write JSON output: {error}");
            70
        }
        Err(error) => {
            eprintln!("{error}");
            3
        }
    }
}

fn parse_options<I>(args: I) -> Result<QueryOptions, String>
where
    I: Iterator<Item = String>,
{
    let mut repo_root = std::env::current_dir()
        .map_err(|error| format!("could not determine current directory: {error}"))?;
    let mut file_list = None;
    let mut surfaces = PathBuf::from(DEFAULT_SURFACES_PATH);
    let mut paths = Vec::new();
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
            "--surfaces" => surfaces = PathBuf::from(required_value(&mut args, "--surfaces")?),
            "--path" => paths.push(required_value(&mut args, "--path")?),
            "--exclude-prefix" => excludes.push(required_value(&mut args, "--exclude-prefix")?),
            "--analyzer-result" => analyzer_results.push(PathBuf::from(required_value(
                &mut args,
                "--analyzer-result",
            )?)),
            "--help" | "-h" => help = true,
            argument if argument.starts_with('-') => {
                return Err(format!("unknown option {argument:?}"));
            }
            argument => return Err(format!("unexpected positional argument {argument:?}")),
        }
    }
    if excludes.is_empty() {
        excludes = graph::DEFAULT_EXCLUDE_PREFIXES
            .iter()
            .map(|prefix| (*prefix).to_string())
            .collect();
    }
    Ok(QueryOptions {
        repo_root,
        file_list,
        surfaces,
        paths,
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

fn cli_error(message: &str, changed_command: bool) -> i32 {
    eprintln!("usage error: {message}\n{}", usage(changed_command));
    2
}

fn usage(changed_command: bool) -> String {
    let command = if changed_command {
        "changed"
    } else {
        "classify"
    };
    format!(
        "repograph {command} [--repo-root PATH] [--file-list PATH] [--surfaces PATH] [--path PATH]... [--exclude-prefix PREFIX]... [--analyzer-result FILE]..."
    )
}

fn emit_inventory_error(
    repo_root: &Path,
    options: &QueryOptions,
    error: InventoryError,
    changed_command: bool,
) {
    let condition = Unestablished {
        kind: ConditionKind::Inventory,
        subject: "<inventory>".to_string(),
        detail: error.to_string(),
        rules: Vec::new(),
    };
    if changed_command {
        let report = ChangedReport {
            schema: "repograph.changed.v1",
            repo_root: display_repo_root(repo_root),
            listing: "unestablished".to_string(),
            excludes: options.excludes.clone(),
            paths: Vec::new(),
            affected_surfaces: Vec::new(),
            affected_packages: Vec::new(),
            affected_roots: Vec::new(),
            unestablished: vec![condition],
        };
        if let Ok(json) = serde_json::to_string(&report) {
            println!("{json}");
        }
    } else {
        let report = ClassifyReport {
            schema: "repograph.classify.v1",
            repo_root: display_repo_root(repo_root),
            listing: "unestablished".to_string(),
            excludes: options.excludes.clone(),
            paths: Vec::new(),
            role_census: role_census(),
            unestablished_by_top_level: BTreeMap::new(),
            unestablished: vec![condition],
        };
        if let Ok(json) = serde_json::to_string(&report) {
            println!("{json}");
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn absent_unknown_path_keeps_an_unestablished_role_and_typed_membership() {
        let fixture_root = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("fixtures/classify");
        let inventory = FileInventory::from_file_list_bytes(
            b".agents/surfaces.json\0.agents/topology.json\0scripts/x.go\0",
        )
        .unwrap();
        let options = QueryOptions {
            repo_root: fixture_root.clone(),
            file_list: None,
            surfaces: fixture_root.join(".agents/surfaces.json"),
            paths: vec!["unknown.data".to_string()],
            excludes: graph::DEFAULT_EXCLUDE_PREFIXES
                .iter()
                .map(|prefix| (*prefix).to_string())
                .collect(),
            analyzer_results: Vec::new(),
            help: false,
        };
        let report = classify(&fixture_root, &inventory, &options).unwrap();
        assert_eq!(report.paths[0].role, "unestablished-absent");
        assert_eq!(report.paths[0].presence, Presence::AbsentFromSnapshot);
        assert!(report.paths[0].package.is_none());
        assert!(report.paths[0].surfaces.is_empty());
        assert_eq!(report.unestablished_by_top_level["<root>"], 1);
    }

    #[test]
    fn root_reachability_handles_cycles_without_looping() {
        let report = GraphReport {
            schema: "repograph.graph.v1",
            repo_root: ".".to_string(),
            listing: "file-list".to_string(),
            excludes: Vec::new(),
            nodes: Vec::new(),
            unresolved_carriers: Vec::new(),
            carrier_path_references: Vec::new(),
            quality_labels: Vec::new(),
            edges: vec![
                Edge {
                    kind: crate::graph_model::EdgeKind::Imports,
                    source: "a".to_string(),
                    target: "b".to_string(),
                    rule_id: None,
                    module: None,
                    line: None,
                },
                Edge {
                    kind: crate::graph_model::EdgeKind::Imports,
                    source: "b".to_string(),
                    target: "a".to_string(),
                    rule_id: None,
                    module: None,
                    line: None,
                },
            ],
            roots: vec![Root {
                kind: RootKind::ProductRuntime,
                id: "root".to_string(),
                target: "a".to_string(),
            }],
            mirror_destinations: Vec::new(),
            mirror_destination_count: 0,
            analyzer_inputs: Vec::new(),
            role_census: role_census(),
            unestablished: Vec::new(),
        };
        assert_eq!(roots_reaching(&report, "b")[0].id, "root");
    }
}
