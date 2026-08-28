//! Strict external-analyzer result ingestion.
//!
//! A provider can add external-module nodes and imports edges, but it cannot
//! become a second source of truth for Charness-owned topology.

use std::collections::{BTreeSet, HashSet};
use std::path::{Path, PathBuf};

use serde::{Deserialize, Serialize};

use crate::graph_model::{
    AnalyzerInput, ConditionKind, Edge, EdgeKind, ExternalModuleNode, Node, Unestablished,
};
use crate::surfaces;

pub const ANALYZER_RESULT_SCHEMA: &str = "repograph.analyzer_result.v1";

#[derive(Debug, Clone, PartialEq, Eq, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct AnalyzerResult {
    pub schema: String,
    pub analyzer: AnalyzerIdentity,
    pub source: SourceIdentity,
    pub scope: DeclaredScope,
    #[serde(default)]
    pub modules: Vec<AnalyzerModule>,
    #[serde(default)]
    pub imports: Vec<AnalyzerImport>,
    #[serde(default)]
    pub exclusions: Vec<AnalyzerExclusion>,
    #[serde(default)]
    pub parse_conditions: Vec<ParseCondition>,
    pub completeness: Completeness,
}

#[derive(Debug, Clone, PartialEq, Eq, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct AnalyzerIdentity {
    pub name: String,
    pub version: String,
}

#[derive(Debug, Clone, PartialEq, Eq, Deserialize)]
#[serde(untagged)]
pub enum SourceIdentity {
    Commit(CommitSource),
    Digest(DigestSource),
}

#[derive(Debug, Clone, PartialEq, Eq, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct CommitSource {
    pub commit: String,
}

#[derive(Debug, Clone, PartialEq, Eq, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct DigestSource {
    pub digest: String,
}

#[derive(Debug, Clone, PartialEq, Eq, Deserialize)]
#[serde(untagged)]
pub enum DeclaredScope {
    Paths(PathScope),
    Globs(GlobScope),
}

#[derive(Debug, Clone, PartialEq, Eq, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct PathScope {
    pub paths: Vec<String>,
}

#[derive(Debug, Clone, PartialEq, Eq, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct GlobScope {
    pub globs: Vec<String>,
}

#[derive(Debug, Clone, PartialEq, Eq, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct AnalyzerModule {
    pub id: String,
}

#[derive(Debug, Clone, PartialEq, Eq, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct AnalyzerImport {
    pub source: AnalyzerEndpoint,
    pub target: AnalyzerEndpoint,
    #[serde(default)]
    pub module: Option<String>,
    #[serde(default)]
    pub line: Option<usize>,
}

#[derive(Debug, Clone, PartialEq, Eq, Deserialize)]
#[serde(tag = "kind", rename_all = "kebab-case", deny_unknown_fields)]
pub enum AnalyzerEndpoint {
    ExternalModule { id: String },
    File { path: String },
}

#[derive(Debug, Clone, PartialEq, Eq, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct AnalyzerExclusion {
    pub path: String,
    pub reason: String,
}

#[derive(Debug, Clone, PartialEq, Eq, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ParseCondition {
    pub path: String,
    pub kind: ParseConditionKind,
    pub detail: String,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Deserialize)]
#[serde(rename_all = "kebab-case")]
pub enum ParseConditionKind {
    DynamicImport,
    ParseError,
    UnsupportedSyntax,
    Unreadable,
    Excluded,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum Completeness {
    Complete,
    Partial,
    Failed,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct AnalyzerIngestion {
    pub analyzer_inputs: Vec<AnalyzerInput>,
    pub nodes: Vec<Node>,
    pub edges: Vec<Edge>,
    pub unestablished: Vec<Unestablished>,
}

#[derive(Debug, Clone, PartialEq, Eq, Deserialize)]
#[serde(deny_unknown_fields)]
struct RevDepOutput {
    tool: String,
    tool_version: String,
    source: SourceIdentity,
    scope: RevDepScope,
    #[serde(default)]
    modules: Vec<RevDepModule>,
    #[serde(default)]
    excluded: Vec<RevDepExclusion>,
    #[serde(default)]
    conditions: Vec<RevDepCondition>,
    status: Completeness,
}

#[derive(Debug, Clone, PartialEq, Eq, Deserialize)]
#[serde(deny_unknown_fields)]
struct RevDepScope {
    files: Vec<String>,
}

#[derive(Debug, Clone, PartialEq, Eq, Deserialize)]
#[serde(deny_unknown_fields)]
struct RevDepModule {
    name: String,
    #[serde(default)]
    imports: Vec<RevDepImport>,
}

#[derive(Debug, Clone, PartialEq, Eq, Deserialize)]
#[serde(deny_unknown_fields)]
struct RevDepImport {
    file: String,
    specifier: String,
    #[serde(default)]
    line: Option<usize>,
}

#[derive(Debug, Clone, PartialEq, Eq, Deserialize)]
#[serde(deny_unknown_fields)]
struct RevDepExclusion {
    file: String,
    reason: String,
}

#[derive(Debug, Clone, PartialEq, Eq, Deserialize)]
#[serde(deny_unknown_fields)]
struct RevDepCondition {
    file: String,
    status: ParseConditionKind,
    message: String,
}

/// Convert the documented rev-dep fixture shape into the provider contract.
///
/// This is an adapter for captured output, not a rev-dep runner.  In
/// particular, it performs no process launch, network access, or filesystem
/// discovery beyond deserializing the supplied document.
pub fn adapt_rev_dep(input: &str) -> Result<AnalyzerResult, String> {
    let output = serde_json::from_str::<RevDepOutput>(input)
        .map_err(|error| format!("invalid rev-dep output: {error}"))?;
    if output.tool != "rev-dep" {
        return Err(format!("unsupported analyzer output tool {}", output.tool));
    }
    let modules = output
        .modules
        .iter()
        .map(|module| AnalyzerModule {
            id: module.name.clone(),
        })
        .collect::<Vec<_>>();
    let imports = output
        .modules
        .iter()
        .flat_map(|module| {
            module.imports.iter().map(|import| AnalyzerImport {
                source: AnalyzerEndpoint::File {
                    path: import.file.clone(),
                },
                target: AnalyzerEndpoint::ExternalModule {
                    id: module.name.clone(),
                },
                module: Some(import.specifier.clone()),
                line: import.line,
            })
        })
        .collect();
    Ok(AnalyzerResult {
        schema: ANALYZER_RESULT_SCHEMA.to_string(),
        analyzer: AnalyzerIdentity {
            name: output.tool,
            version: output.tool_version,
        },
        source: output.source,
        scope: DeclaredScope::Paths(PathScope {
            paths: output.scope.files,
        }),
        modules,
        imports,
        exclusions: output
            .excluded
            .into_iter()
            .map(|exclusion| AnalyzerExclusion {
                path: exclusion.file,
                reason: exclusion.reason,
            })
            .collect(),
        parse_conditions: output
            .conditions
            .into_iter()
            .map(|condition| ParseCondition {
                path: condition.file,
                kind: condition.status,
                detail: condition.message,
            })
            .collect(),
        completeness: output.status,
    })
}

#[derive(Debug, Clone, PartialEq, Eq)]
enum ScopeMatcher {
    Paths(Vec<String>),
    Globs(Vec<String>),
}

impl AnalyzerResult {
    fn validate(&self) -> Result<ScopeMatcher, String> {
        if self.analyzer.name.trim().is_empty() {
            return Err("analyzer name must be non-empty".to_string());
        }
        if self.analyzer.version.trim().is_empty() {
            return Err("analyzer version must be non-empty".to_string());
        }
        match &self.source {
            SourceIdentity::Commit(source) if source.commit.trim().is_empty() => {
                return Err("source commit must be non-empty".to_string());
            }
            SourceIdentity::Digest(source) if source.digest.trim().is_empty() => {
                return Err("source digest must be non-empty".to_string());
            }
            _ => {}
        }

        let matcher = match &self.scope {
            DeclaredScope::Paths(scope) => {
                ScopeMatcher::Paths(normalize_scope_values(&scope.paths, "scope paths")?)
            }
            DeclaredScope::Globs(scope) => {
                ScopeMatcher::Globs(normalize_scope_values(&scope.globs, "scope globs")?)
            }
        };
        if matcher.values().is_empty() {
            return Err("declared scope must contain at least one value".to_string());
        }

        let mut module_ids = HashSet::new();
        for module in &self.modules {
            if module.id.trim().is_empty() {
                return Err("module id must be non-empty".to_string());
            }
            if !module_ids.insert(module.id.as_str()) {
                return Err(format!("duplicate module id {}", module.id));
            }
        }
        for import in &self.imports {
            validate_endpoint(&import.source)?;
            validate_endpoint(&import.target)?;
            if import.module.as_deref().is_some_and(str::is_empty) {
                return Err("import module must be non-empty when present".to_string());
            }
            if import.line == Some(0) {
                return Err("import line must be one-based when present".to_string());
            }
        }
        for exclusion in &self.exclusions {
            if exclusion.reason.trim().is_empty() {
                return Err("exclusion reason must be non-empty".to_string());
            }
            normalize_repo_path(&exclusion.path)
                .map_err(|error| format!("invalid exclusion path: {error}"))?;
        }
        for parse_condition in &self.parse_conditions {
            if parse_condition.detail.trim().is_empty() {
                return Err("parse condition detail must be non-empty".to_string());
            }
            normalize_repo_path(&parse_condition.path)
                .map_err(|error| format!("invalid parse-condition path: {error}"))?;
        }
        Ok(matcher)
    }

    fn source_label(&self) -> String {
        match &self.source {
            SourceIdentity::Commit(source) => format!("commit:{}", source.commit),
            SourceIdentity::Digest(source) => format!("digest:{}", source.digest),
        }
    }
}

impl ScopeMatcher {
    fn values(&self) -> &[String] {
        match self {
            Self::Paths(values) | Self::Globs(values) => values,
        }
    }

    fn contains(&self, path: &str) -> bool {
        match self {
            Self::Paths(paths) => paths.iter().any(|candidate| candidate == path),
            Self::Globs(globs) => surfaces::path_matches_patterns(path, globs),
        }
    }

    fn describe(&self) -> String {
        let prefix = match self {
            Self::Paths(_) => "paths",
            Self::Globs(_) => "globs",
        };
        format!("{prefix}:{}", self.values().join(","))
    }

    fn declared_paths(&self) -> impl Iterator<Item = &String> {
        match self {
            Self::Paths(paths) => paths.iter(),
            Self::Globs(_) => [].iter(),
        }
    }
}

/// Ingest ordered provider files into a graph projection.
pub fn ingest(
    repo_root: &Path,
    selected_paths: &[String],
    existing_nodes: &[Node],
    existing_edges: &[Edge],
    result_paths: &[PathBuf],
) -> AnalyzerIngestion {
    let mut result = AnalyzerIngestion {
        analyzer_inputs: Vec::new(),
        nodes: Vec::new(),
        edges: Vec::new(),
        unestablished: Vec::new(),
    };
    let mut scopes: Vec<(String, ScopeMatcher)> = Vec::new();

    for result_path in result_paths {
        let display = display_input_path(repo_root, result_path);
        let bytes = match std::fs::read(result_path) {
            Ok(bytes) => bytes,
            Err(error) => {
                result.analyzer_inputs.push(AnalyzerInput {
                    path: display.clone(),
                    identity: format!("{display}:unreadable"),
                    scope: "unestablished".to_string(),
                });
                result.unestablished.push(condition(
                    ConditionKind::AnalyzerParseFailure,
                    display,
                    format!("could not read analyzer result: {error}"),
                    vec!["analyzer-result-input"],
                ));
                continue;
            }
        };
        let byte_identity = format!("{display}:bytes-{}", bytes.len());
        let document = match serde_json::from_slice::<AnalyzerResult>(&bytes) {
            Ok(document) => document,
            Err(error) => {
                result.analyzer_inputs.push(AnalyzerInput {
                    path: display.clone(),
                    identity: byte_identity,
                    scope: "unestablished".to_string(),
                });
                result.unestablished.push(condition(
                    ConditionKind::AnalyzerParseFailure,
                    display,
                    format!("invalid analyzer result: {error}"),
                    vec!["analyzer-result-schema"],
                ));
                continue;
            }
        };
        let matcher = match document.validate() {
            Ok(matcher) => matcher,
            Err(error) => {
                result.analyzer_inputs.push(AnalyzerInput {
                    path: display.clone(),
                    identity: byte_identity,
                    scope: "unestablished".to_string(),
                });
                result.unestablished.push(condition(
                    ConditionKind::AnalyzerParseFailure,
                    display,
                    format!("invalid analyzer result: {error}"),
                    vec!["analyzer-result-values"],
                ));
                continue;
            }
        };
        let input_scope = matcher.describe();
        result.analyzer_inputs.push(AnalyzerInput {
            path: display.clone(),
            identity: format!(
                "{}@{}:{}",
                document.analyzer.name,
                document.analyzer.version,
                document.source_label()
            ),
            scope: input_scope,
        });

        for (previous_display, previous_scope) in &scopes {
            let overlap = overlapping_paths(previous_scope, &matcher, selected_paths);
            if !overlap.is_empty() {
                result.unestablished.push(condition(
                    ConditionKind::ScopeConflict,
                    format!("scope:{previous_display}|{display}"),
                    format!("declared analyzer scopes overlap on {}", overlap.join(", ")),
                    vec!["non-overlapping-analyzer-scopes"],
                ));
            }
        }
        scopes.push((display.clone(), matcher.clone()));

        if document.schema != ANALYZER_RESULT_SCHEMA {
            add_scope_conditions(
                &mut result.unestablished,
                &matcher,
                selected_paths,
                ConditionKind::AnalyzerVersionMismatch,
                format!(
                    "incompatible analyzer result schema {}; expected {ANALYZER_RESULT_SCHEMA}",
                    document.schema
                ),
                vec!["analyzer-result-schema-version"],
            );
            continue;
        }

        ingest_document(
            &mut result,
            &document,
            &display,
            &matcher,
            selected_paths,
            existing_nodes,
            existing_edges,
        );
    }

    result
}

fn ingest_document(
    result: &mut AnalyzerIngestion,
    document: &AnalyzerResult,
    display: &str,
    scope: &ScopeMatcher,
    selected_paths: &[String],
    existing_nodes: &[Node],
    existing_edges: &[Edge],
) {
    if matches!(
        document.completeness,
        Completeness::Partial | Completeness::Failed
    ) {
        add_scope_conditions(
            &mut result.unestablished,
            scope,
            selected_paths,
            ConditionKind::AnalyzerIncomplete,
            format!(
                "analyzer reported {} completeness over the declared scope",
                completeness_label(document.completeness)
            ),
            vec!["analyzer-completeness"],
        );
    }
    if document.modules.is_empty() {
        add_scope_conditions(
            &mut result.unestablished,
            scope,
            selected_paths,
            ConditionKind::AnalyzerZeroModules,
            "analyzer result declared zero external modules".to_string(),
            vec!["analyzer-module-count"],
        );
    }

    for exclusion in &document.exclusions {
        let path = normalize_repo_path(&exclusion.path).unwrap_or_else(|_| exclusion.path.clone());
        if !scope.contains(&path) {
            result.unestablished.push(condition(
                ConditionKind::ScopeViolation,
                format!("{display}:exclusion:{path}"),
                format!("exclusion path {path} falls outside the declared scope"),
                vec!["declared-scope"],
            ));
        } else {
            result.unestablished.push(condition(
                ConditionKind::AnalyzerExcluded,
                path,
                format!("analyzer excluded this path: {}", exclusion.reason),
                vec!["analyzer-exclusion"],
            ));
        }
    }
    for parse_condition in &document.parse_conditions {
        result.unestablished.push(condition(
            ConditionKind::AnalyzerParseFailure,
            parse_condition.path.clone(),
            format!(
                "analyzer parse condition {}: {}",
                parse_condition_kind_label(parse_condition.kind),
                parse_condition.detail
            ),
            vec!["analyzer-parse-condition"],
        ));
    }

    if document.completeness == Completeness::Failed {
        return;
    }

    let declared_modules = document
        .modules
        .iter()
        .map(|module| module.id.as_str())
        .collect::<HashSet<_>>();
    let provider = document.analyzer.name.as_str();
    let mut node_ids = existing_nodes
        .iter()
        .map(|node| node.id().to_string())
        .chain(result.nodes.iter().map(|node| node.id().to_string()))
        .collect::<HashSet<_>>();
    for module in &document.modules {
        let id = external_module_id(provider, &module.id);
        if node_ids.insert(id.clone()) {
            result.nodes.push(Node::ExternalModule(ExternalModuleNode {
                id,
                provider: provider.to_string(),
            }));
        }
    }

    for (index, import) in document.imports.iter().enumerate() {
        let mut violations = Vec::new();
        let source = endpoint_id(
            &import.source,
            provider,
            &declared_modules,
            scope,
            selected_paths,
            existing_nodes,
            existing_edges,
            &mut violations,
        );
        let target = endpoint_id(
            &import.target,
            provider,
            &declared_modules,
            scope,
            selected_paths,
            existing_nodes,
            existing_edges,
            &mut violations,
        );
        let has_external = matches!(
            (&import.source, &import.target),
            (AnalyzerEndpoint::ExternalModule { .. }, _)
                | (_, AnalyzerEndpoint::ExternalModule { .. })
        );
        if !has_external {
            violations.push(
                "analyzer imports edges must include an external-module endpoint".to_string(),
            );
        }
        if !violations.is_empty() {
            result.unestablished.push(condition(
                ConditionKind::ScopeViolation,
                format!("{display}:imports:{index}"),
                violations.join("; "),
                vec!["analyzer-edge-boundary"],
            ));
            continue;
        }

        let (Some(source), Some(target)) = (source, target) else {
            continue;
        };
        result.edges.push(Edge {
            kind: EdgeKind::Imports,
            source,
            target,
            rule_id: Some(format!(
                "analyzer:{}@{}",
                document.analyzer.name, document.analyzer.version
            )),
            module: import.module.clone(),
            line: import.line,
        });
    }
}

#[allow(clippy::too_many_arguments)]
fn endpoint_id(
    endpoint: &AnalyzerEndpoint,
    provider: &str,
    declared_modules: &HashSet<&str>,
    scope: &ScopeMatcher,
    selected_paths: &[String],
    existing_nodes: &[Node],
    existing_edges: &[Edge],
    violations: &mut Vec<String>,
) -> Option<String> {
    match endpoint {
        AnalyzerEndpoint::ExternalModule { id } => {
            if !declared_modules.contains(id.as_str()) {
                violations.push(format!("external module {id} was not declared in modules"));
                None
            } else {
                Some(external_module_id(provider, id))
            }
        }
        AnalyzerEndpoint::File { path } => {
            let normalized = match normalize_repo_path(path) {
                Ok(path) => path,
                Err(error) => {
                    violations.push(format!("file endpoint {path} is invalid: {error}"));
                    return None;
                }
            };
            if !scope.contains(&normalized) {
                violations.push(format!(
                    "file endpoint {normalized} falls outside the declared scope"
                ));
            }
            if !selected_paths
                .iter()
                .any(|candidate| candidate == &normalized)
            {
                violations.push(format!(
                    "file endpoint {normalized} is not in the repository snapshot"
                ));
            }
            if let Some(reason) = owned_boundary(&normalized, existing_nodes, existing_edges) {
                violations.push(format!(
                    "file endpoint {normalized} is a Charness-owned {reason} target"
                ));
            }
            Some(normalized)
        }
    }
}

fn owned_boundary(path: &str, nodes: &[Node], edges: &[Edge]) -> Option<&'static str> {
    if let Some(reason) = edges.iter().find_map(|edge| {
        (edge.target == path).then_some(match edge.kind {
            EdgeKind::Mirrors => "mirror-edge",
            EdgeKind::Invokes => "command-edge",
            _ => return None,
        })
    }) {
        return Some(reason);
    }
    if nodes.iter().any(|node| match node {
        Node::Skill(skill) => skill.id == path || skill.directory == path,
        Node::Adapter(adapter) => adapter.id == path || adapter.declaration_path == path,
        Node::CommandCarrier(carrier) => carrier.id == path || carrier.path == path,
        Node::ValidationCommand(command) => command.id == path || command.carrier_id == path,
        Node::MirrorPair(pair) => pair.id == path || pair.destination == path,
        _ => false,
    }) {
        return Some("skill, adapter, command, or mirror node");
    }
    None
}

fn add_scope_conditions(
    output: &mut Vec<Unestablished>,
    scope: &ScopeMatcher,
    selected_paths: &[String],
    kind: ConditionKind,
    detail: String,
    rules: Vec<&str>,
) {
    let mut members = selected_paths
        .iter()
        .filter(|path| scope.contains(path))
        .cloned()
        .collect::<BTreeSet<_>>();
    members.extend(scope.declared_paths().cloned());
    if members.is_empty() {
        output.push(condition(
            kind,
            format!("scope:{}", scope.describe()),
            detail,
            rules,
        ));
    } else {
        for member in members {
            output.push(condition(kind, member, detail.clone(), rules.clone()));
        }
    }
}

fn overlapping_paths(
    left: &ScopeMatcher,
    right: &ScopeMatcher,
    selected_paths: &[String],
) -> Vec<String> {
    let mut candidates = selected_paths.to_vec();
    candidates.extend(left.declared_paths().cloned());
    candidates.extend(right.declared_paths().cloned());
    candidates.sort();
    candidates.dedup();
    candidates
        .into_iter()
        .filter(|path| left.contains(path) && right.contains(path))
        .collect()
}

fn normalize_scope_values(values: &[String], field: &str) -> Result<Vec<String>, String> {
    let mut normalized = Vec::with_capacity(values.len());
    for value in values {
        if value.split('/').any(|component| component == "..") {
            return Err(format!("{field} cannot contain ..: {value}"));
        }
        normalized.push(normalize_repo_path(value)?);
    }
    normalized.sort();
    normalized.dedup();
    Ok(normalized)
}

fn normalize_repo_path(value: &str) -> Result<String, String> {
    surfaces::normalize_repo_path(value)
        .map_err(|error| error.to_string())
        .and_then(|path| {
            if path == "." {
                Err("path must be non-empty".to_string())
            } else {
                Ok(path)
            }
        })
}

fn validate_endpoint(endpoint: &AnalyzerEndpoint) -> Result<(), String> {
    match endpoint {
        AnalyzerEndpoint::ExternalModule { id } if id.trim().is_empty() => {
            Err("external module id must be non-empty".to_string())
        }
        AnalyzerEndpoint::File { path } if path.trim().is_empty() => {
            Err("file endpoint path must be non-empty".to_string())
        }
        _ => Ok(()),
    }
}

fn external_module_id(provider: &str, module: &str) -> String {
    format!("external-module:{provider}:{module}")
}

fn completeness_label(completeness: Completeness) -> &'static str {
    match completeness {
        Completeness::Complete => "complete",
        Completeness::Partial => "partial",
        Completeness::Failed => "failed",
    }
}

fn parse_condition_kind_label(kind: ParseConditionKind) -> &'static str {
    match kind {
        ParseConditionKind::DynamicImport => "dynamic-import",
        ParseConditionKind::ParseError => "parse-error",
        ParseConditionKind::UnsupportedSyntax => "unsupported-syntax",
        ParseConditionKind::Unreadable => "unreadable",
        ParseConditionKind::Excluded => "excluded",
    }
}

fn condition(
    kind: ConditionKind,
    subject: impl Into<String>,
    detail: String,
    rules: Vec<&str>,
) -> Unestablished {
    Unestablished {
        kind,
        subject: subject.into(),
        detail,
        rules: rules.into_iter().map(str::to_string).collect(),
    }
}

fn display_input_path(repo_root: &Path, path: &Path) -> String {
    let absolute = if path.is_absolute() {
        path.to_path_buf()
    } else {
        std::env::current_dir()
            .unwrap_or_else(|_| PathBuf::from("."))
            .join(path)
    };
    if let Ok(relative) = absolute.strip_prefix(repo_root) {
        let text = relative.to_string_lossy().replace('\\', "/");
        if !text.is_empty() {
            return text;
        }
    }
    path.file_name()
        .and_then(|name| name.to_str())
        .map_or_else(|| "<analyzer-result>".to_string(), str::to_string)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::graph_model::{Edge, EdgeKind, MirrorPairNode, MirrorTransform};

    fn fixture_root() -> PathBuf {
        Path::new(env!("CARGO_MANIFEST_DIR")).join("fixtures")
    }

    fn result_path(name: &str) -> PathBuf {
        fixture_root().join("analyzers").join(name)
    }

    fn selected(paths: &[&str]) -> Vec<String> {
        paths.iter().map(|path| (*path).to_string()).collect()
    }

    fn ingest_fixture(name: &str, paths: &[&str]) -> AnalyzerIngestion {
        ingest(
            &fixture_root(),
            &selected(paths),
            &[],
            &[],
            &[result_path(name)],
        )
    }

    #[test]
    fn complete_result_adds_external_modules_and_bounded_imports() {
        let report = ingest_fixture("complete.json", &["pkg/cycle_a.py", "pkg/cycle_b.py"]);
        assert!(report.unestablished.is_empty());
        assert_eq!(
            report
                .nodes
                .iter()
                .filter(|node| matches!(node, Node::ExternalModule(_)))
                .count(),
            1
        );
        assert_eq!(report.edges.len(), 2);
    }

    #[test]
    fn partial_result_marks_each_claimed_path_unestablished() {
        let report = ingest_fixture("partial.json", &["scripts/helper.py"]);
        assert!(report.unestablished.iter().any(|entry| {
            entry.kind == ConditionKind::AnalyzerIncomplete && entry.subject == "scripts/helper.py"
        }));
        assert!(report
            .unestablished
            .iter()
            .any(|entry| entry.kind == ConditionKind::AnalyzerExcluded));
        assert!(report
            .unestablished
            .iter()
            .any(|entry| entry.kind == ConditionKind::AnalyzerParseFailure));
        assert_eq!(report.edges.len(), 1);
    }

    #[test]
    fn failed_glob_result_is_unestablished_and_does_not_merge_claims() {
        let report = ingest_fixture("failed.json", &["scripts/helper.py", "scripts/first.py"]);
        assert!(report
            .unestablished
            .iter()
            .any(|entry| entry.kind == ConditionKind::AnalyzerIncomplete));
        assert!(report.nodes.is_empty());
        assert!(report.edges.is_empty());
    }

    #[test]
    fn scope_violation_drops_the_edge() {
        let report = ingest_fixture(
            "scope_violation.json",
            &["scripts/helper.py", "scripts/first.py"],
        );
        assert!(report.edges.is_empty());
        assert!(report
            .unestablished
            .iter()
            .any(|entry| entry.kind == ConditionKind::ScopeViolation));
    }

    #[test]
    fn owned_mirror_target_is_a_scope_violation() {
        let existing_nodes = vec![Node::MirrorPair(MirrorPairNode {
            id: "mirror".to_string(),
            rule_id: "mirror-rule".to_string(),
            source: Some("README.md".to_string()),
            destination: "plugins/charness/README.md".to_string(),
            transform: MirrorTransform::ContentTransformed,
            content_transformed: true,
            destination_in_snapshot: true,
        })];
        let existing_edges = vec![Edge {
            kind: EdgeKind::Mirrors,
            source: "README.md".to_string(),
            target: "plugins/charness/README.md".to_string(),
            rule_id: Some("mirror-rule".to_string()),
            module: None,
            line: None,
        }];
        let report = ingest(
            &fixture_root(),
            &selected(&["plugins/charness/README.md"]),
            &existing_nodes,
            &existing_edges,
            &[result_path("overwrite_attempt.json")],
        );
        assert!(report.edges.is_empty());
        assert!(report.unestablished.iter().any(|entry| {
            entry.kind == ConditionKind::ScopeViolation && entry.detail.contains("mirror-edge")
        }));
    }

    #[test]
    fn incompatible_version_zero_modules_and_scope_conflict_are_typed() {
        let version = ingest_fixture("version_mismatch.json", &["scripts/helper.py"]);
        assert!(version
            .unestablished
            .iter()
            .any(|entry| entry.kind == ConditionKind::AnalyzerVersionMismatch));

        let zero = ingest_fixture("zero_modules.json", &["scripts/helper.py"]);
        assert!(zero
            .unestablished
            .iter()
            .any(|entry| entry.kind == ConditionKind::AnalyzerZeroModules));

        let report = ingest(
            &fixture_root(),
            &selected(&["scripts/helper.py"]),
            &[],
            &[],
            &[
                result_path("scope_conflict_a.json"),
                result_path("scope_conflict_b.json"),
            ],
        );
        assert!(report
            .unestablished
            .iter()
            .any(|entry| entry.kind == ConditionKind::ScopeConflict));
        assert_eq!(report.analyzer_inputs.len(), 2);
    }

    #[test]
    fn strict_schema_rejects_unknown_fields_and_enum_values() {
        let unknown = r#"{
            "schema":"repograph.analyzer_result.v1",
            "analyzer":{"name":"x","version":"1"},
            "source":{"commit":"abc"},
            "scope":{"paths":["a.py"]},
            "imports":[],
            "completeness":"complete",
            "unexpected":true
        }"#;
        let unknown_error = serde_json::from_str::<AnalyzerResult>(unknown).unwrap_err();
        assert!(unknown_error.to_string().contains("unexpected"));
        let bad = unknown.replace("\"complete\"", "\"maybe\"");
        assert!(serde_json::from_str::<AnalyzerResult>(&bad).is_err());
    }

    #[test]
    fn documented_rev_dep_shape_matches_expected_ingestion() {
        let document = adapt_rev_dep(include_str!("../fixtures/analyzers/rev_dep.json")).unwrap();
        let scope = document.validate().unwrap();
        let mut actual = AnalyzerIngestion {
            analyzer_inputs: Vec::new(),
            nodes: Vec::new(),
            edges: Vec::new(),
            unestablished: Vec::new(),
        };
        ingest_document(
            &mut actual,
            &document,
            "rev_dep.json",
            &scope,
            &selected(&["pkg/cycle_a.py"]),
            &[],
            &[],
        );
        let expected: serde_json::Value = serde_json::from_str(include_str!(
            "../fixtures/analyzers/expected/rev_dep_ingestion.json"
        ))
        .unwrap();
        assert_eq!(serde_json::to_value(actual).unwrap(), expected);
    }
}
