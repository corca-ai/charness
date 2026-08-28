//! Component and reverse-dependency projections over the typed topology graph.
//!
//! The graph builder remains the only inventory/edge producer.  This module
//! deliberately consumes its report rather than re-extracting imports,
//! invokes, or roots.  `export-safe` remains the verdict owner for boundary
//! findings; components only re-report those findings in its own schema.

use std::collections::{BTreeMap, BTreeSet, HashMap, HashSet, VecDeque};
use std::path::{Path, PathBuf};

use serde::Serialize;

use crate::export_safe::{self, Violation};
use crate::graph;
use crate::graph_model::{
    ConditionKind, Edge, EdgeKind, GraphReport, Node, Role, Root, RootKind, Unestablished,
};
use crate::inventory::{FileInventory, InventoryError};
use crate::surfaces;

pub const MAX_EXPLAIN_PATHS: usize = 3;

/// The reusable typed graph portion of an explanation.
#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct ExplainProjection {
    pub root_paths: Vec<RootPath>,
    pub path_limit: usize,
    pub paths_bounded: bool,
    pub dependents: Vec<Edge>,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct TopologyComponent {
    pub id: String,
    pub members: Vec<String>,
    pub size: usize,
    pub cyclic: bool,
    pub root_ids: Vec<String>,
    pub root_kinds: Vec<RootKind>,
    pub rootless: bool,
    pub validator_test_only: bool,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct ComponentsReport {
    pub schema: &'static str,
    pub repo_root: String,
    pub listing: String,
    pub excludes: Vec<String>,
    pub analyzer_inputs: Vec<crate::graph_model::AnalyzerInput>,
    pub components: Vec<TopologyComponent>,
    pub component_count: usize,
    pub scc_count: usize,
    pub scc_sizes_gt_one: Vec<usize>,
    pub rootless_components: Vec<String>,
    pub rootless_component_count: usize,
    pub validator_test_only_islands: Vec<String>,
    pub validator_test_only_island_count: usize,
    pub test_only_island_count: usize,
    pub import_boundary_violations: Vec<Violation>,
    pub unresolved_carriers: Vec<crate::graph_model::UnresolvedCarrier>,
    pub unestablished: Vec<Unestablished>,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct RootPath {
    pub root: Root,
    pub edges: Vec<Edge>,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct ClassifiedAncestor {
    pub path: String,
    pub role: Role,
    pub distance: usize,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct ExplainReport {
    pub schema: &'static str,
    pub repo_root: String,
    pub listing: String,
    pub excludes: Vec<String>,
    pub analyzer_inputs: Vec<crate::graph_model::AnalyzerInput>,
    pub path: String,
    pub root_paths: Vec<RootPath>,
    pub path_limit: usize,
    pub paths_bounded: bool,
    pub dependents: Vec<Edge>,
    pub nearest_classified_ancestors: Vec<ClassifiedAncestor>,
    pub unresolved_carriers: Vec<crate::graph_model::UnresolvedCarrier>,
    pub unestablished: Vec<Unestablished>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct ComponentsOptions {
    repo_root: PathBuf,
    file_list: Option<PathBuf>,
    excludes: Vec<String>,
    analyzer_results: Vec<PathBuf>,
    help: bool,
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct ExplainOptions {
    repo_root: PathBuf,
    file_list: Option<PathBuf>,
    excludes: Vec<String>,
    analyzer_results: Vec<PathBuf>,
    path: Option<String>,
    help: bool,
}

/// Build the SCC/root projection from an already-built graph report.
pub fn components(
    repo_root: &Path,
    inventory: &FileInventory,
    excludes: &[String],
    analyzer_results: &[PathBuf],
) -> ComponentsReport {
    let graph = graph::build(repo_root, inventory, excludes, analyzer_results);
    let ComponentData {
        components,
        rootless,
        validator_test_only,
    } = component_data(&graph);
    let boundary = export_safe_projection(repo_root, inventory, excludes);
    let mut unestablished = graph.unestablished.clone();
    unestablished.extend(boundary.unestablished);
    let scc_sizes_gt_one = components
        .iter()
        .filter(|component| component.size > 1)
        .map(|component| component.size)
        .collect::<Vec<_>>();
    let component_count = components.len();
    let rootless_component_count = rootless.len();
    let validator_test_only_island_count = validator_test_only.len();
    ComponentsReport {
        schema: "repograph.components.v1",
        repo_root: graph.repo_root,
        listing: graph.listing,
        excludes: graph.excludes,
        analyzer_inputs: graph.analyzer_inputs,
        components,
        component_count,
        scc_count: component_count,
        scc_sizes_gt_one,
        rootless_component_count,
        rootless_components: rootless,
        validator_test_only_island_count,
        test_only_island_count: validator_test_only_island_count,
        validator_test_only_islands: validator_test_only,
        import_boundary_violations: boundary.violations,
        unresolved_carriers: graph.unresolved_carriers,
        unestablished: dedupe_unestablished(unestablished),
    }
}

/// Build the bounded root-path and reverse-dependency projection.
pub fn explain(
    repo_root: &Path,
    inventory: &FileInventory,
    excludes: &[String],
    analyzer_results: &[PathBuf],
    path: &str,
) -> ExplainReport {
    let graph_inventory = augment_inventory(inventory, path);
    let graph = graph::build(repo_root, &graph_inventory, excludes, analyzer_results);
    let projection = explain_projection(&graph, path);
    let nearest = if projection.root_paths.is_empty() {
        nearest_classified_ancestors(&graph, path)
    } else {
        Vec::new()
    };
    let mut unestablished = graph.unestablished.clone();
    if excludes.iter().any(|prefix| path.starts_with(prefix)) {
        unestablished.push(Unestablished {
            kind: ConditionKind::RoleUnestablished,
            subject: path.to_string(),
            detail: "explain path is excluded from the graph snapshot".to_string(),
            rules: vec!["exclude-prefix".to_string()],
        });
    }
    ExplainReport {
        schema: "repograph.explain.v1",
        repo_root: graph.repo_root,
        listing: inventory.source().as_str().to_string(),
        excludes: excludes.to_vec(),
        analyzer_inputs: graph.analyzer_inputs,
        path: path.to_string(),
        root_paths: projection.root_paths,
        path_limit: projection.path_limit,
        paths_bounded: projection.paths_bounded,
        dependents: projection.dependents,
        nearest_classified_ancestors: nearest,
        unresolved_carriers: graph.unresolved_carriers,
        unestablished: dedupe_unestablished(unestablished),
    }
}

/// Project the bounded reverse/root explanation from an already-built graph.
///
/// Commands that need graph context should consume this projection rather than
/// reimplementing traversal or inventing a second root-path ordering.
pub fn explain_projection(report: &GraphReport, path: &str) -> ExplainProjection {
    let root_projection = root_paths(report, path);
    ExplainProjection {
        root_paths: root_projection.paths,
        path_limit: MAX_EXPLAIN_PATHS,
        paths_bounded: root_projection.bounded,
        dependents: reverse_edges(&report.edges, path),
    }
}

struct BoundaryProjection {
    violations: Vec<Violation>,
    unestablished: Vec<Unestablished>,
}

fn export_safe_projection(
    repo_root: &Path,
    inventory: &FileInventory,
    excludes: &[String],
) -> BoundaryProjection {
    let filtered = filtered_inventory(inventory, excludes);
    let (report, _) = export_safe::analyze(repo_root, &filtered);
    let unestablished = report
        .unestablished
        .into_iter()
        .filter(|entry| entry.status != "zero-scope")
        .map(|entry| Unestablished {
            kind: ConditionKind::ParseFailure,
            subject: entry.path,
            detail: entry.detail,
            rules: vec!["export-safe".to_string()],
        })
        .collect();
    BoundaryProjection {
        violations: report.violations,
        unestablished,
    }
}

fn filtered_inventory(inventory: &FileInventory, excludes: &[String]) -> FileInventory {
    let bytes = inventory
        .paths()
        .iter()
        .map(|path| path.as_str())
        .filter(|path| !excludes.iter().any(|prefix| path.starts_with(prefix)))
        .flat_map(|path| path.as_bytes().iter().copied().chain(std::iter::once(0)))
        .collect::<Vec<_>>();
    FileInventory::from_file_list_bytes(&bytes)
        .expect("paths accepted by FileInventory remain valid when filtered")
}

fn augment_inventory(inventory: &FileInventory, path: &str) -> FileInventory {
    if inventory
        .paths()
        .iter()
        .any(|candidate| candidate.as_str() == path)
    {
        return inventory.clone();
    }
    let bytes = inventory
        .paths()
        .iter()
        .map(|candidate| candidate.as_str())
        .chain(std::iter::once(path))
        .flat_map(|candidate| {
            candidate
                .as_bytes()
                .iter()
                .copied()
                .chain(std::iter::once(0))
        })
        .collect::<Vec<_>>();
    FileInventory::from_file_list_bytes(&bytes)
        .expect("normalized explain paths remain valid inventory paths")
}

struct ComponentData {
    components: Vec<TopologyComponent>,
    rootless: Vec<String>,
    validator_test_only: Vec<String>,
}

fn component_data(report: &GraphReport) -> ComponentData {
    let vertices = topology_vertices(report);
    let adjacency = adjacency(&vertices, &report.edges);
    let components = strongly_connected_components(&vertices, &adjacency);
    let component_for = components
        .iter()
        .enumerate()
        .flat_map(|(index, members)| members.iter().map(move |member| (member.clone(), index)))
        .collect::<HashMap<_, _>>();
    let mut root_ids_by_component = BTreeMap::<usize, Vec<String>>::new();
    let mut root_kinds_by_component = BTreeMap::<usize, BTreeSet<RootKindKey>>::new();
    for root in &report.roots {
        let mut queue = VecDeque::from([root.target.clone()]);
        let mut visited = HashSet::new();
        while let Some(source) = queue.pop_front() {
            if !visited.insert(source.clone()) {
                continue;
            }
            if let Some(&component) = component_for.get(&source) {
                root_ids_by_component
                    .entry(component)
                    .or_default()
                    .push(root.id.clone());
                root_kinds_by_component
                    .entry(component)
                    .or_default()
                    .insert(RootKindKey::new(root.kind));
            }
            for edge in adjacency.get(&source).into_iter().flatten() {
                queue.push_back(edge.target.clone());
            }
        }
    }

    let mut projected = components
        .iter()
        .enumerate()
        .map(|(index, members)| {
            let mut root_ids = root_ids_by_component.remove(&index).unwrap_or_default();
            root_ids.sort();
            root_ids.dedup();
            let root_kinds = root_kinds_by_component
                .remove(&index)
                .unwrap_or_default()
                .into_iter()
                .map(RootKindKey::kind)
                .collect::<Vec<_>>();
            let rootless = root_ids.is_empty();
            let validator_test_only = !rootless
                && root_kinds
                    .iter()
                    .all(|kind| matches!(kind, RootKind::Validation | RootKind::Tests));
            TopologyComponent {
                id: format!("component:{}", members[0]),
                members: members.clone(),
                size: members.len(),
                cyclic: members.len() > 1
                    || adjacency
                        .get(&members[0])
                        .is_some_and(|edges| edges.iter().any(|edge| edge.target == members[0])),
                root_ids,
                root_kinds,
                rootless,
                validator_test_only,
            }
        })
        .collect::<Vec<_>>();
    projected.sort_by(|left, right| left.id.cmp(&right.id));

    let rootless = projected
        .iter()
        .filter(|component| component.rootless)
        .map(|component| component.id.clone())
        .collect::<Vec<_>>();
    let validator_test_only = projected
        .iter()
        .filter(|component| component.validator_test_only)
        .map(|component| component.id.clone())
        .collect::<Vec<_>>();
    ComponentData {
        components: projected,
        rootless,
        validator_test_only,
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
struct RootKindKey(u8);

impl RootKindKey {
    fn new(kind: RootKind) -> Self {
        Self(match kind {
            RootKind::ProductRuntime => 0,
            RootKind::Validation => 1,
            RootKind::Tests => 2,
            RootKind::Generated => 3,
            RootKind::HostDiscovered => 4,
        })
    }

    fn kind(self) -> RootKind {
        match self.0 {
            0 => RootKind::ProductRuntime,
            1 => RootKind::Validation,
            2 => RootKind::Tests,
            3 => RootKind::Generated,
            _ => RootKind::HostDiscovered,
        }
    }
}

fn topology_vertices(report: &GraphReport) -> Vec<String> {
    let mut vertices = report
        .nodes
        .iter()
        .filter_map(|node| match node {
            Node::File(file) => Some(file.id.clone()),
            _ => None,
        })
        .collect::<BTreeSet<_>>();
    for edge in topology_edges(&report.edges) {
        vertices.insert(edge.source.clone());
        vertices.insert(edge.target.clone());
    }
    vertices.into_iter().collect()
}

fn topology_edges(edges: &[Edge]) -> Vec<Edge> {
    let mut result = edges
        .iter()
        .filter(|edge| matches!(edge.kind, EdgeKind::Imports | EdgeKind::Invokes))
        .cloned()
        .collect::<Vec<_>>();
    result.sort_by(edge_ordering);
    result.dedup();
    result
}

fn edge_ordering(left: &Edge, right: &Edge) -> std::cmp::Ordering {
    left.source
        .cmp(&right.source)
        .then(left.target.cmp(&right.target))
        .then(edge_kind_order(left.kind).cmp(&edge_kind_order(right.kind)))
        .then(left.module.cmp(&right.module))
        .then(left.line.cmp(&right.line))
        .then(left.rule_id.cmp(&right.rule_id))
}

fn edge_kind_order(kind: EdgeKind) -> u8 {
    match kind {
        EdgeKind::Imports => 0,
        EdgeKind::Invokes => 1,
        EdgeKind::Packages => 2,
        EdgeKind::Mirrors => 3,
        EdgeKind::Documents => 4,
        EdgeKind::Tests => 5,
    }
}

fn adjacency(vertices: &[String], edges: &[Edge]) -> BTreeMap<String, Vec<Edge>> {
    let mut result = vertices
        .iter()
        .cloned()
        .map(|vertex| (vertex, Vec::new()))
        .collect::<BTreeMap<_, _>>();
    for edge in topology_edges(edges) {
        result.entry(edge.source.clone()).or_default().push(edge);
    }
    for edges in result.values_mut() {
        edges.sort_by(edge_ordering);
    }
    result
}

fn strongly_connected_components(
    vertices: &[String],
    adjacency: &BTreeMap<String, Vec<Edge>>,
) -> Vec<Vec<String>> {
    let mut visited = HashSet::new();
    let mut finish_order = Vec::new();
    for vertex in vertices {
        finish_visit(vertex, adjacency, &mut visited, &mut finish_order);
    }

    let mut reverse = BTreeMap::<String, Vec<String>>::new();
    for vertex in vertices {
        reverse.entry(vertex.clone()).or_default();
    }
    for (source, edges) in adjacency {
        for edge in edges {
            reverse
                .entry(edge.target.clone())
                .or_default()
                .push(source.clone());
        }
    }
    for neighbors in reverse.values_mut() {
        neighbors.sort();
        neighbors.dedup();
    }

    visited.clear();
    let mut components = Vec::new();
    while let Some(vertex) = finish_order.pop() {
        if visited.contains(&vertex) {
            continue;
        }
        let mut members = Vec::new();
        reverse_visit(&vertex, &reverse, &mut visited, &mut members);
        members.sort();
        components.push(members);
    }
    components.sort_by(|left, right| left[0].cmp(&right[0]));
    components
}

fn finish_visit(
    vertex: &str,
    adjacency: &BTreeMap<String, Vec<Edge>>,
    visited: &mut HashSet<String>,
    finish_order: &mut Vec<String>,
) {
    if !visited.insert(vertex.to_string()) {
        return;
    }
    if let Some(edges) = adjacency.get(vertex) {
        for edge in edges {
            finish_visit(&edge.target, adjacency, visited, finish_order);
        }
    }
    finish_order.push(vertex.to_string());
}

fn reverse_visit(
    vertex: &str,
    reverse: &BTreeMap<String, Vec<String>>,
    visited: &mut HashSet<String>,
    members: &mut Vec<String>,
) {
    if !visited.insert(vertex.to_string()) {
        return;
    }
    members.push(vertex.to_string());
    if let Some(neighbors) = reverse.get(vertex) {
        for neighbor in neighbors {
            reverse_visit(neighbor, reverse, visited, members);
        }
    }
}

struct RootPathProjection {
    paths: Vec<RootPath>,
    bounded: bool,
}

fn root_paths(report: &GraphReport, target: &str) -> RootPathProjection {
    let edges = topology_edges(&report.edges);
    let vertices = topology_vertices(report);
    let adjacency = adjacency(&vertices, &edges);
    let mut paths = Vec::new();
    let mut roots = report.roots.clone();
    roots.sort_by(|left, right| left.id.cmp(&right.id).then(left.target.cmp(&right.target)));
    for root in roots {
        for path in shortest_paths(&root.target, target, &adjacency, MAX_EXPLAIN_PATHS + 1) {
            paths.push(RootPath {
                root: root.clone(),
                edges: path,
            });
        }
    }
    paths.sort_by(|left, right| {
        left.edges
            .len()
            .cmp(&right.edges.len())
            .then(left.root.id.cmp(&right.root.id))
            .then_with(|| compare_edge_paths(&left.edges, &right.edges))
    });
    let bounded = paths.len() > MAX_EXPLAIN_PATHS;
    paths.truncate(MAX_EXPLAIN_PATHS);
    RootPathProjection { paths, bounded }
}

fn shortest_paths(
    start: &str,
    target: &str,
    adjacency: &BTreeMap<String, Vec<Edge>>,
    limit: usize,
) -> Vec<Vec<Edge>> {
    if start == target {
        return vec![Vec::new()];
    }
    let mut distances = HashMap::<String, usize>::new();
    let mut queue = VecDeque::from([start.to_string()]);
    distances.insert(start.to_string(), 0);
    while let Some(source) = queue.pop_front() {
        let distance = distances[&source];
        for edge in adjacency.get(&source).into_iter().flatten() {
            if !distances.contains_key(&edge.target) {
                distances.insert(edge.target.clone(), distance + 1);
                queue.push_back(edge.target.clone());
            }
        }
    }
    let Some(&target_distance) = distances.get(target) else {
        return Vec::new();
    };
    let mut paths = Vec::new();
    let mut current = Vec::new();
    enumerate_shortest_paths(
        start,
        target,
        target_distance,
        &distances,
        adjacency,
        &mut current,
        &mut paths,
        limit,
    );
    paths
}

#[allow(clippy::too_many_arguments)]
fn enumerate_shortest_paths(
    current: &str,
    target: &str,
    target_distance: usize,
    distances: &HashMap<String, usize>,
    adjacency: &BTreeMap<String, Vec<Edge>>,
    path: &mut Vec<Edge>,
    paths: &mut Vec<Vec<Edge>>,
    limit: usize,
) {
    if paths.len() >= limit {
        return;
    }
    if current == target {
        paths.push(path.clone());
        return;
    }
    let Some(&distance) = distances.get(current) else {
        return;
    };
    if distance >= target_distance {
        return;
    }
    for edge in adjacency.get(current).into_iter().flatten() {
        if distances.get(&edge.target) == Some(&(distance + 1)) {
            path.push(edge.clone());
            enumerate_shortest_paths(
                &edge.target,
                target,
                target_distance,
                distances,
                adjacency,
                path,
                paths,
                limit,
            );
            path.pop();
        }
    }
}

fn compare_edge_paths(left: &[Edge], right: &[Edge]) -> std::cmp::Ordering {
    left.iter()
        .map(edge_sort_key)
        .cmp(right.iter().map(edge_sort_key))
}

fn edge_sort_key(edge: &Edge) -> (String, String, String, String, usize) {
    (
        edge.source.clone(),
        edge.target.clone(),
        format!("{:?}", edge.kind),
        edge.module.clone().unwrap_or_default(),
        edge.line.unwrap_or(0),
    )
}

fn reverse_edges(edges: &[Edge], target: &str) -> Vec<Edge> {
    let mut result = topology_edges(edges)
        .into_iter()
        .filter(|edge| edge.target == target)
        .collect::<Vec<_>>();
    result.sort_by(edge_ordering);
    result
}

fn nearest_classified_ancestors(report: &GraphReport, target: &str) -> Vec<ClassifiedAncestor> {
    let vertices = topology_vertices(report);
    let edges = topology_edges(&report.edges);
    let mut reverse = BTreeMap::<String, Vec<Edge>>::new();
    for vertex in vertices {
        reverse.entry(vertex).or_default();
    }
    for edge in edges {
        reverse.entry(edge.target.clone()).or_default().push(edge);
    }
    for edges in reverse.values_mut() {
        edges.sort_by(edge_ordering);
    }
    let roles = report
        .nodes
        .iter()
        .filter_map(|node| match node {
            Node::File(file) => Some((file.id.clone(), file.role)),
            _ => None,
        })
        .collect::<HashMap<_, _>>();
    let mut queue = VecDeque::from([(target.to_string(), 0usize)]);
    let mut visited = HashSet::new();
    let mut found = Vec::new();
    let mut found_distance = None;
    while let Some((current, distance)) = queue.pop_front() {
        if !visited.insert(current.clone()) {
            continue;
        }
        if found_distance.is_some_and(|known| distance > known) {
            break;
        }
        if distance > 0 {
            if let Some(role) = roles
                .get(&current)
                .copied()
                .filter(|role| *role != Role::Unestablished)
            {
                found_distance.get_or_insert(distance);
                found.push(ClassifiedAncestor {
                    path: current.clone(),
                    role,
                    distance,
                });
                continue;
            }
        }
        for edge in reverse.get(&current).into_iter().flatten() {
            queue.push_back((edge.source.clone(), distance + 1));
        }
    }
    found.sort_by(|left, right| left.path.cmp(&right.path));
    found
}

fn dedupe_unestablished(mut values: Vec<Unestablished>) -> Vec<Unestablished> {
    values.sort_by(|left, right| {
        format!("{:?}", left.kind)
            .cmp(&format!("{:?}", right.kind))
            .then(left.subject.cmp(&right.subject))
            .then(left.detail.cmp(&right.detail))
            .then(left.rules.cmp(&right.rules))
    });
    values.dedup();
    values
}

pub fn run_components<I>(args: I) -> i32
where
    I: IntoIterator<Item = String>,
{
    let options = match parse_components_options(args.into_iter()) {
        Ok(options) => options,
        Err(message) => return cli_error(&message, "components"),
    };
    if options.help {
        println!("{}", components_usage());
        return 0;
    }
    let repo_root_argument = options.repo_root.clone();
    let repo_root = std::fs::canonicalize(&options.repo_root).unwrap_or(options.repo_root.clone());
    let inventory = match crate::inventory::acquire(&repo_root, options.file_list.as_deref()) {
        Ok(inventory) => inventory,
        Err(error) => {
            emit_components_inventory_error(&repo_root_argument, &options, error);
            return 3;
        }
    };
    let report = components(
        &repo_root,
        &inventory,
        &options.excludes,
        &options.analyzer_results,
    );
    let exit = report_exit(&report.unestablished, &report.unresolved_carriers);
    emit_json(&report, exit)
}

pub fn run_explain<I>(args: I) -> i32
where
    I: IntoIterator<Item = String>,
{
    let options = match parse_explain_options(args.into_iter()) {
        Ok(options) => options,
        Err(message) => return cli_error(&message, "explain"),
    };
    if options.help {
        println!("{}", explain_usage());
        return 0;
    }
    let Some(raw_path) = options.path.as_deref() else {
        return cli_error("--path is required", "explain");
    };
    let path = match surfaces::normalize_repo_path(raw_path) {
        Ok(path) => path,
        Err(error) => return emit_explain_usage_error(&error.to_string()),
    };
    let repo_root_argument = options.repo_root.clone();
    let repo_root = std::fs::canonicalize(&options.repo_root).unwrap_or(options.repo_root.clone());
    let inventory = match crate::inventory::acquire(&repo_root, options.file_list.as_deref()) {
        Ok(inventory) => inventory,
        Err(error) => {
            emit_explain_inventory_error(&repo_root_argument, &options, error);
            return 3;
        }
    };
    let report = explain(
        &repo_root,
        &inventory,
        &options.excludes,
        &options.analyzer_results,
        &path,
    );
    let exit = report_exit(&report.unestablished, &report.unresolved_carriers);
    emit_json(&report, exit)
}

fn report_exit(
    unestablished: &[Unestablished],
    unresolved: &[crate::graph_model::UnresolvedCarrier],
) -> i32 {
    if unestablished.is_empty() && unresolved.is_empty() {
        0
    } else {
        3
    }
}

fn emit_json<T: Serialize>(report: &T, exit: i32) -> i32 {
    match serde_json::to_string(report) {
        Ok(json) => {
            println!("{json}");
            exit
        }
        Err(error) => {
            eprintln!("internal error: could not write JSON output: {error}");
            70
        }
    }
}

fn parse_components_options<I>(args: I) -> Result<ComponentsOptions, String>
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
    Ok(ComponentsOptions {
        repo_root,
        file_list,
        excludes,
        analyzer_results,
        help,
    })
}

fn parse_explain_options<I>(args: I) -> Result<ExplainOptions, String>
where
    I: Iterator<Item = String>,
{
    let mut repo_root = std::env::current_dir()
        .map_err(|error| format!("could not determine current directory: {error}"))?;
    let mut file_list = None;
    let mut excludes = Vec::new();
    let mut analyzer_results = Vec::new();
    let mut path = None;
    let mut help = false;
    let mut args = args.peekable();
    while let Some(argument) = args.next() {
        match argument.as_str() {
            "--repo-root" => repo_root = PathBuf::from(required_value(&mut args, "--repo-root")?),
            "--file-list" => {
                file_list = Some(PathBuf::from(required_value(&mut args, "--file-list")?))
            }
            "--exclude-prefix" => excludes.push(required_value(&mut args, "--exclude-prefix")?),
            "--analyzer-result" => analyzer_results.push(PathBuf::from(required_value(
                &mut args,
                "--analyzer-result",
            )?)),
            "--path" => {
                if path.is_some() {
                    return Err("--path may be supplied only once".to_string());
                }
                path = Some(required_value(&mut args, "--path")?);
            }
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
    Ok(ExplainOptions {
        repo_root,
        file_list,
        excludes,
        analyzer_results,
        path,
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

fn cli_error(message: &str, command: &str) -> i32 {
    eprintln!("usage error: {message}\n{}", usage(command));
    2
}

fn emit_explain_usage_error(message: &str) -> i32 {
    eprintln!("usage error: {message}\n{}", explain_usage());
    2
}

fn usage(command: &str) -> String {
    match command {
        "components" => components_usage().to_string(),
        _ => explain_usage().to_string(),
    }
}

fn components_usage() -> &'static str {
    "repograph components [--repo-root PATH] [--file-list PATH] [--exclude-prefix PREFIX]... [--analyzer-result FILE]..."
}

fn explain_usage() -> &'static str {
    "repograph explain --path PATH [--repo-root PATH] [--file-list PATH] [--exclude-prefix PREFIX]... [--analyzer-result FILE]..."
}

fn emit_components_inventory_error(
    repo_root: &Path,
    options: &ComponentsOptions,
    error: InventoryError,
) {
    let report = ComponentsReport {
        schema: "repograph.components.v1",
        repo_root: graph::display_repo_root(repo_root),
        listing: "unestablished".to_string(),
        excludes: options.excludes.clone(),
        analyzer_inputs: Vec::new(),
        components: Vec::new(),
        component_count: 0,
        scc_count: 0,
        scc_sizes_gt_one: Vec::new(),
        rootless_components: Vec::new(),
        rootless_component_count: 0,
        validator_test_only_islands: Vec::new(),
        validator_test_only_island_count: 0,
        test_only_island_count: 0,
        import_boundary_violations: Vec::new(),
        unresolved_carriers: Vec::new(),
        unestablished: vec![inventory_condition(error)],
    };
    let _ = emit_json(&report, 3);
}

fn emit_explain_inventory_error(repo_root: &Path, options: &ExplainOptions, error: InventoryError) {
    let report = ExplainReport {
        schema: "repograph.explain.v1",
        repo_root: graph::display_repo_root(repo_root),
        listing: "unestablished".to_string(),
        excludes: options.excludes.clone(),
        analyzer_inputs: Vec::new(),
        path: options.path.clone().unwrap_or_default(),
        root_paths: Vec::new(),
        path_limit: MAX_EXPLAIN_PATHS,
        paths_bounded: false,
        dependents: Vec::new(),
        nearest_classified_ancestors: Vec::new(),
        unresolved_carriers: Vec::new(),
        unestablished: vec![inventory_condition(error)],
    };
    let _ = emit_json(&report, 3);
}

fn inventory_condition(error: InventoryError) -> Unestablished {
    Unestablished {
        kind: ConditionKind::Inventory,
        subject: "<inventory>".to_string(),
        detail: error.to_string(),
        rules: Vec::new(),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::graph_model::{FileNode, GraphReport};

    fn graph_with_edges(edges: Vec<Edge>, roots: Vec<Root>, files: &[&str]) -> GraphReport {
        GraphReport {
            schema: "repograph.graph.v1",
            repo_root: ".".to_string(),
            listing: "file-list".to_string(),
            excludes: Vec::new(),
            nodes: files
                .iter()
                .map(|path| {
                    Node::File(FileNode {
                        id: (*path).to_string(),
                        path: (*path).to_string(),
                        role: Role::Production,
                        packages: vec!["scripts".to_string()],
                    })
                })
                .collect(),
            edges,
            roots,
            mirror_destinations: Vec::new(),
            mirror_destination_count: 0,
            analyzer_inputs: Vec::new(),
            role_census: BTreeMap::new(),
            unresolved_carriers: Vec::new(),
            carrier_path_references: Vec::new(),
            quality_labels: Vec::new(),
            unestablished: Vec::new(),
        }
    }

    fn edge(source: &str, target: &str, kind: EdgeKind) -> Edge {
        Edge {
            kind,
            source: source.to_string(),
            target: target.to_string(),
            rule_id: Some("fixture".to_string()),
            module: Some("fixture.module".to_string()),
            line: Some(1),
        }
    }

    #[test]
    fn scc_projection_marks_cycles_and_rootless_components() {
        let report = graph_with_edges(
            vec![
                edge("a.py", "b.py", EdgeKind::Imports),
                edge("b.py", "a.py", EdgeKind::Imports),
            ],
            Vec::new(),
            &["a.py", "b.py", "orphan.py"],
        );
        let data = component_data(&report);
        assert_eq!(data.components.len(), 2);
        assert_eq!(data.components[0].members, ["a.py", "b.py"]);
        assert!(data.components[0].cyclic);
        assert_eq!(data.rootless.len(), 2);
    }

    #[test]
    fn shortest_root_paths_keep_typed_edges_and_report_the_bound() {
        let report = graph_with_edges(
            vec![
                edge("root.py", "middle.py", EdgeKind::Imports),
                edge("middle.py", "target.py", EdgeKind::Invokes),
                edge("root.py", "target.py", EdgeKind::Imports),
            ],
            vec![Root {
                kind: RootKind::ProductRuntime,
                id: "runtime:root.py".to_string(),
                target: "root.py".to_string(),
            }],
            &["root.py", "middle.py", "target.py"],
        );
        let projection = root_paths(&report, "target.py");
        assert_eq!(projection.paths.len(), 1);
        assert_eq!(projection.paths[0].edges.len(), 1);
        assert_eq!(projection.paths[0].edges[0].kind, EdgeKind::Imports);
        assert!(!projection.bounded);
    }

    #[test]
    fn shortest_root_paths_set_bounded_when_the_limit_is_exceeded() {
        let mut edges = Vec::new();
        for (index, branch) in ["a.py", "b.py", "c.py", "d.py"].into_iter().enumerate() {
            edges.push(edge("root.py", branch, EdgeKind::Imports));
            edges.push(Edge {
                line: Some(index + 2),
                ..edge(branch, "target.py", EdgeKind::Invokes)
            });
        }
        let report = graph_with_edges(
            edges,
            vec![Root {
                kind: RootKind::ProductRuntime,
                id: "runtime:root.py".to_string(),
                target: "root.py".to_string(),
            }],
            &["root.py", "a.py", "b.py", "c.py", "d.py", "target.py"],
        );
        let projection = root_paths(&report, "target.py");
        assert_eq!(projection.paths.len(), MAX_EXPLAIN_PATHS);
        assert!(projection.bounded);
    }
}
