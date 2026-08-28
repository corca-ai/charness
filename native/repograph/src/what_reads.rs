//! Lexical path-reference evidence with a typed topology projection.
//!
//! This is deliberately the path-target slice of the retired Python owner.
//! Symbol and config-key searches are not part of this command.  Lexical
//! evidence and graph evidence remain separate: neither proves runtime use.

use std::collections::{BTreeMap, HashMap};
use std::path::{Path, PathBuf};

use serde::Serialize;

use crate::graph;
use crate::graph_components::{self, ExplainProjection};
use crate::graph_model::{ConditionKind, EdgeKind, GraphReport, Node, Unestablished};
use crate::inventory::{FileInventory, InventoryError};
use crate::surfaces;

const TEXT_SUFFIXES: &[&str] = &[
    ".py", ".sh", ".bash", ".zsh", ".md", ".yaml", ".yml", ".json", ".jsonc", ".toml", ".cfg",
    ".ini", ".txt", ".mjs", ".js", ".ts", "",
];
const SKIP_DIR_NAMES: &[&str] = &[
    ".git",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    "mutants",
    ".charness",
];
const MIRROR_PREFIX: &str = "plugins/";
const UNSCANNED_SURFACES: &[&str] = &[
    "git history — a consumer in a deleted or older revision is invisible here",
    "consumer repositories outside this checkout, including installed copies of this package",
    "names composed at runtime: f-strings, `getattr`, and paths built from variables",
    "binary files and any file that is not valid UTF-8",
    "`node_modules/**`, `mutants/**`, and cache directories, which are vendored or scratch copies",
    "files whose extension is outside this tool's text allowlist: tracked `.jsonl` ledgers and `.html` templates are valid UTF-8 and are NOT scanned",
    "for a path query: extension-only globs such as `*.json`, which match this file but say nothing about it",
    "for a path query: globs written outside source, config, and test files — a pattern in prose is not a program that opens the file",
];
const MIRROR_UNSCANNED: &str =
    "the exported `plugins/**` mirror, which reads what the source reads (pass --include-mirrors to include it)";
const ZERO_RESULT_CAVEAT: &str = "No reference was found in the scanned surfaces. That is not 'nothing reads this': read `unscanned_surfaces` before proposing a removal.";

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct PathHit {
    pub kind: String,
    pub line: usize,
    pub source: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub glob: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub carrier_id: Option<String>,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct FileReferences {
    pub file: String,
    pub surface: String,
    pub hits: Vec<PathHit>,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct WhatReadsReport {
    pub schema: &'static str,
    pub repo_root: String,
    pub listing: String,
    pub target_kind: &'static str,
    pub target: String,
    pub include_mirrors: bool,
    pub files_scanned: usize,
    pub reference_count: usize,
    pub reference_kinds: BTreeMap<String, usize>,
    pub files_with_references: Vec<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub references: Option<Vec<FileReferences>>,
    pub unscanned_surfaces: Vec<String>,
    pub zero_result_caveat: Option<&'static str>,
    pub graph: ExplainProjection,
    pub unresolved_carriers: Vec<crate::graph_model::UnresolvedCarrier>,
    pub unestablished: Vec<Unestablished>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct WhatReadsOptions {
    repo_root: PathBuf,
    file_list: Option<PathBuf>,
    path: Option<String>,
    include_mirrors: bool,
    detail: bool,
    help: bool,
}

/// Run `repograph what-reads`.
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
    let Some(raw_path) = options.path.as_deref() else {
        return cli_error("--path is required");
    };
    let path = match surfaces::normalize_repo_path(raw_path) {
        Ok(path) if !path.split('/').any(|component| component == "..") => path,
        Ok(_) => return emit_usage_error("path must stay within the repository"),
        Err(error) => return emit_usage_error(&error.to_string()),
    };
    let repo_root_argument = options.repo_root.clone();
    let repo_root = std::fs::canonicalize(&options.repo_root).unwrap_or(options.repo_root.clone());
    let inventory = match crate::inventory::acquire(&repo_root, options.file_list.as_deref()) {
        Ok(inventory) => inventory,
        Err(error) => {
            let report = empty_report(
                &repo_root_argument,
                &path,
                options.include_mirrors,
                inventory_condition(error),
            );
            return emit_json(&report, 3);
        }
    };

    let scan_inventory = inventory
        .filtered(|candidate| should_scan_path(&repo_root, candidate, options.include_mirrors));
    let graph_inventory = match scan_inventory.with_path(&path) {
        Ok(inventory) => inventory,
        Err(error) => return emit_usage_error(&error.to_string()),
    };
    // The topology declaration is consumed as graph configuration, not as a
    // repository vertex.  Excluding it from the selected graph paths avoids
    // the generic `.agents/*` adapter fallback while preserving its snapshot
    // visibility for the graph builder.
    let mut graph_excludes = vec![".agents/topology.json".to_string()];
    if !options.include_mirrors {
        graph_excludes.push(MIRROR_PREFIX.to_string());
    }
    let topology = graph::build(&repo_root, &graph_inventory, &graph_excludes, &[]);
    let (mut references, unreadable) = scan_references(&repo_root, &scan_inventory, &path);
    classify_carrier_hits(&mut references, &topology, &path);

    let mut reference_kinds = BTreeMap::new();
    let mut files_with_references = Vec::new();
    let mut reference_count = 0;
    for entry in &references {
        if entry.hits.is_empty() {
            continue;
        }
        files_with_references.push(entry.file.clone());
        reference_count += entry.hits.len();
        for hit in &entry.hits {
            *reference_kinds.entry(hit.kind.clone()).or_insert(0) += 1;
        }
    }

    let unscanned_surfaces = unscanned_surfaces(options.include_mirrors, &unreadable);
    let projection = graph_components::explain_projection(&topology, &path);
    let has_unestablished =
        !topology.unestablished.is_empty() || !topology.unresolved_carriers.is_empty();
    let report = WhatReadsReport {
        schema: "repograph.what_reads.v1",
        repo_root: graph::display_repo_root(&repo_root_argument),
        listing: scan_inventory.source().as_str().to_string(),
        target_kind: "path",
        target: path,
        include_mirrors: options.include_mirrors,
        files_scanned: scan_inventory.paths().len(),
        reference_count,
        reference_kinds,
        files_with_references,
        references: options.detail.then_some(references),
        unscanned_surfaces,
        zero_result_caveat: (reference_count == 0).then_some(ZERO_RESULT_CAVEAT),
        graph: projection,
        unresolved_carriers: topology.unresolved_carriers,
        unestablished: topology.unestablished,
    };
    emit_json(&report, if has_unestablished { 3 } else { 0 })
}

fn parse_options<I>(args: I) -> Result<WhatReadsOptions, String>
where
    I: Iterator<Item = String>,
{
    let mut repo_root = std::env::current_dir()
        .map_err(|error| format!("could not determine current directory: {error}"))?;
    let mut file_list = None;
    let mut path = None;
    let mut include_mirrors = false;
    let mut detail = false;
    let mut help = false;
    let mut args = args.peekable();
    while let Some(argument) = args.next() {
        match argument.as_str() {
            "--repo-root" => repo_root = PathBuf::from(required_value(&mut args, "--repo-root")?),
            "--file-list" => {
                file_list = Some(PathBuf::from(required_value(&mut args, "--file-list")?))
            }
            "--path" => {
                if path.is_some() {
                    return Err("--path may be supplied only once".to_string());
                }
                path = Some(required_value(&mut args, "--path")?);
            }
            "--include-mirrors" => include_mirrors = true,
            "--detail" => detail = true,
            "--help" | "-h" => help = true,
            argument if argument.starts_with('-') => {
                return Err(format!("unknown option {argument:?}"));
            }
            argument => return Err(format!("unexpected positional argument {argument:?}")),
        }
    }
    Ok(WhatReadsOptions {
        repo_root,
        file_list,
        path,
        include_mirrors,
        detail,
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

fn emit_usage_error(message: &str) -> i32 {
    eprintln!("usage error: {message}\n{}", usage());
    2
}

fn usage() -> &'static str {
    "repograph what-reads --path PATH [--repo-root PATH] [--file-list PATH] [--include-mirrors] [--detail]"
}

fn empty_report(
    repo_root: &Path,
    path: &str,
    include_mirrors: bool,
    condition: Unestablished,
) -> WhatReadsReport {
    WhatReadsReport {
        schema: "repograph.what_reads.v1",
        repo_root: graph::display_repo_root(repo_root),
        listing: "unestablished".to_string(),
        target_kind: "path",
        target: path.to_string(),
        include_mirrors,
        files_scanned: 0,
        reference_count: 0,
        reference_kinds: BTreeMap::new(),
        files_with_references: Vec::new(),
        references: None,
        unscanned_surfaces: unscanned_surfaces(include_mirrors, &[]),
        zero_result_caveat: Some(ZERO_RESULT_CAVEAT),
        graph: ExplainProjection {
            root_paths: Vec::new(),
            path_limit: graph_components::MAX_EXPLAIN_PATHS,
            paths_bounded: false,
            dependents: Vec::new(),
        },
        unresolved_carriers: Vec::new(),
        unestablished: vec![condition],
    }
}

fn inventory_condition(error: InventoryError) -> Unestablished {
    Unestablished {
        kind: ConditionKind::Inventory,
        subject: "<inventory>".to_string(),
        detail: error.to_string(),
        rules: Vec::new(),
    }
}

fn emit_json(report: &WhatReadsReport, exit: i32) -> i32 {
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

fn should_scan_path(repo_root: &Path, path: &str, include_mirrors: bool) -> bool {
    let relative = Path::new(path);
    if !relative
        .components()
        .filter_map(|component| component.as_os_str().to_str())
        .all(|component| !SKIP_DIR_NAMES.contains(&component))
    {
        return false;
    }
    if !include_mirrors && path.starts_with(MIRROR_PREFIX) {
        return false;
    }
    repo_root.join(path).is_file() && text_suffix(path)
}

fn text_suffix(path: &str) -> bool {
    let filename = path.rsplit('/').next().unwrap_or(path);
    let suffix = filename
        .rfind('.')
        .filter(|index| *index > 0)
        .map_or("", |index| &filename[index..]);
    let suffix = suffix.to_ascii_lowercase();
    TEXT_SUFFIXES.iter().any(|allowed| *allowed == suffix)
}

fn surface_of(path: &str) -> &'static str {
    if path.starts_with("tests/") {
        return "test";
    }
    if path.starts_with(MIRROR_PREFIX) {
        return "mirror";
    }
    if path.ends_with(".md") {
        return "doc";
    }
    let extension = path.rsplit_once('.').map_or("", |(_, extension)| extension);
    if matches!(
        extension,
        "yaml" | "yml" | "json" | "jsonc" | "toml" | "cfg" | "ini"
    ) {
        "config"
    } else {
        "source"
    }
}

fn scan_references(
    repo_root: &Path,
    inventory: &FileInventory,
    target: &str,
) -> (Vec<FileReferences>, Vec<String>) {
    let mut paths = inventory
        .paths()
        .iter()
        .map(|path| path.as_str().to_string())
        .collect::<Vec<_>>();
    paths.sort();
    let mut references = Vec::new();
    let mut unreadable = Vec::new();
    for path in paths {
        let text = match std::fs::read_to_string(repo_root.join(&path)) {
            Ok(text) => text,
            Err(_) => {
                unreadable.push(path);
                continue;
            }
        };
        let hits = path_hits(&text, target, surface_of(&path));
        if hits.is_empty() {
            continue;
        }
        references.push(FileReferences {
            file: path.clone(),
            surface: surface_of(&path).to_string(),
            hits,
        });
    }
    (references, unreadable)
}

fn unscanned_surfaces(include_mirrors: bool, unreadable: &[String]) -> Vec<String> {
    let mut surfaces = UNSCANNED_SURFACES
        .iter()
        .map(|surface| (*surface).to_string())
        .collect::<Vec<_>>();
    if !include_mirrors {
        surfaces.insert(0, MIRROR_UNSCANNED.to_string());
    }
    if !unreadable.is_empty() {
        let sample = unreadable.iter().take(5).cloned().collect::<Vec<_>>();
        surfaces.push(format!(
            "{} file(s) this scan could not read -- not valid UTF-8, or not openable: {sample:?}",
            unreadable.len()
        ));
    }
    surfaces
}

fn path_hits(text: &str, target: &str, surface: &str) -> Vec<PathHit> {
    let basename = target.rsplit('/').next().unwrap_or(target);
    let suffix = path_suffix(target);
    let scan_globs = matches!(surface, "source" | "config" | "test");
    let mut hits = Vec::new();
    for (line_number, line) in text.lines().enumerate() {
        let line_number = line_number + 1;
        let mut recorded = false;
        if line.contains(target) {
            hits.push(PathHit {
                kind: "literal-path".to_string(),
                line: line_number,
                source: source_line(line),
                glob: None,
                carrier_id: None,
            });
            recorded = true;
        }
        if scan_globs {
            for glob in quoted_globs(line) {
                let anchored = glob.contains('/');
                if !anchored && too_generic_glob(&glob, suffix) {
                    continue;
                }
                let subject = if anchored { target } else { basename };
                if glob_matches(&glob, subject) {
                    hits.push(PathHit {
                        kind: if anchored {
                            "glob-consumption"
                        } else {
                            "basename-glob"
                        }
                        .to_string(),
                        line: line_number,
                        source: source_line(line),
                        glob: Some(glob),
                        carrier_id: None,
                    });
                    recorded = true;
                }
            }
        }
        if !recorded
            && basename != target
            && !basename.is_empty()
            && contains_basename_reference(line, basename)
        {
            hits.push(PathHit {
                kind: "basename-reference".to_string(),
                line: line_number,
                source: source_line(line),
                glob: None,
                carrier_id: None,
            });
        }
    }
    hits
}

fn source_line(line: &str) -> String {
    line.trim().chars().take(200).collect()
}

fn path_suffix(path: &str) -> &str {
    let basename = path.rsplit('/').next().unwrap_or(path);
    basename
        .rfind('.')
        .filter(|index| *index > 0)
        .map_or("", |index| &basename[index..])
}

fn too_generic_glob(glob: &str, suffix: &str) -> bool {
    let literal = glob
        .chars()
        .filter(|character| *character != '*' && *character != '?')
        .collect::<String>();
    literal.trim_matches('.').is_empty() || literal == suffix
}

fn quoted_globs(line: &str) -> Vec<String> {
    let chars = line.chars().collect::<Vec<_>>();
    let mut globs = Vec::new();
    let mut index = 0;
    while index < chars.len() {
        if !matches!(chars[index], '\'' | '"' | '`') {
            index += 1;
            continue;
        }
        let start = index + 1;
        let Some(end_offset) = chars[start..]
            .iter()
            .position(|character| matches!(character, '\'' | '"' | '`'))
        else {
            index += 1;
            continue;
        };
        let end = start + end_offset;
        let value = chars[start..end].iter().collect::<String>();
        if value
            .chars()
            .any(|character| matches!(character, '*' | '?'))
        {
            globs.push(value);
            // A successful regex match consumes its closing delimiter. A
            // failed candidate advances by one below, allowing the second
            // delimiter of Markdown spans and nested quote forms to become
            // the next candidate just as `finditer` does. The Python owner's
            // pattern permits a different quote character to close a match;
            // this intentionally follows that lexical behavior.
            index = end + 1;
        } else {
            index += 1;
        }
    }
    globs
}

fn contains_basename_reference(line: &str, basename: &str) -> bool {
    line.match_indices(basename).any(|(index, _)| {
        let before = line[..index].chars().next_back();
        let after = line[index + basename.len()..].chars().next();
        !before.is_some_and(is_word_or_slash) && !after.is_some_and(is_word_or_slash)
    })
}

fn is_word_or_slash(character: char) -> bool {
    character == '/' || character == '_' || character.is_alphanumeric()
}

fn glob_matches(pattern: &str, value: &str) -> bool {
    let pattern = pattern.chars().collect::<Vec<_>>();
    let value = value.chars().collect::<Vec<_>>();
    let mut memo = HashMap::new();
    fn matches(
        pattern: &[char],
        value: &[char],
        pattern_index: usize,
        value_index: usize,
        memo: &mut HashMap<(usize, usize), bool>,
    ) -> bool {
        if let Some(result) = memo.get(&(pattern_index, value_index)) {
            return *result;
        }
        let result = if pattern_index == pattern.len() {
            value_index == value.len()
        } else if pattern[pattern_index] == '*' {
            if pattern_index + 1 < pattern.len() && pattern[pattern_index + 1] == '*' {
                if pattern_index + 2 < pattern.len() && pattern[pattern_index + 2] == '/' {
                    if matches(pattern, value, pattern_index + 3, value_index, memo) {
                        true
                    } else {
                        let mut next = value_index;
                        let mut found = false;
                        while next < value.len() {
                            if value[next] == '/' {
                                next += 1;
                                if matches(pattern, value, pattern_index, next, memo) {
                                    found = true;
                                    break;
                                }
                            }
                            next += 1;
                        }
                        found
                    }
                } else {
                    (value_index..=value.len())
                        .any(|next| matches(pattern, value, pattern_index + 2, next, memo))
                }
            } else {
                let mut next = value_index;
                let mut found = false;
                while next <= value.len() && (next == value_index || value[next - 1] != '/') {
                    if matches(pattern, value, pattern_index + 1, next, memo) {
                        found = true;
                        break;
                    }
                    next += 1;
                }
                found
            }
        } else if pattern[pattern_index] == '?' {
            value_index < value.len()
                && value[value_index] != '/'
                && matches(pattern, value, pattern_index + 1, value_index + 1, memo)
        } else {
            value_index < value.len()
                && pattern[pattern_index] == value[value_index]
                && matches(pattern, value, pattern_index + 1, value_index + 1, memo)
        };
        memo.insert((pattern_index, value_index), result);
        result
    }
    matches(&pattern, &value, 0, 0, &mut memo)
}

fn classify_carrier_hits(references: &mut [FileReferences], topology: &GraphReport, target: &str) {
    let mut carrier_locations = BTreeMap::<(String, usize), String>::new();
    let mut carrier_nodes = HashMap::<String, (String, Option<usize>)>::new();
    let mut command_sources = HashMap::<String, String>::new();
    for node in &topology.nodes {
        match node {
            Node::CommandCarrier(carrier) => {
                carrier_nodes.insert(carrier.id.clone(), (carrier.path.clone(), carrier.line));
                command_sources.insert(carrier.id.clone(), carrier.id.clone());
            }
            Node::ValidationCommand(command) => {
                command_sources.insert(command.id.clone(), command.carrier_id.clone());
            }
            _ => {}
        }
    }
    for reference in &topology.carrier_path_references {
        if reference.path != target {
            continue;
        }
        if let Some((path, carrier_line)) = carrier_nodes.get(&reference.carrier_id) {
            if let Some(line) = reference.line.or(*carrier_line) {
                carrier_locations
                    .entry((path.clone(), line))
                    .or_insert_with(|| reference.carrier_id.clone());
            }
        }
    }
    for edge in topology
        .edges
        .iter()
        .filter(|edge| edge.kind == EdgeKind::Invokes && edge.target == target)
    {
        let Some(carrier_id) = command_sources.get(&edge.source) else {
            continue;
        };
        let Some((path, carrier_line)) = carrier_nodes.get(carrier_id) else {
            continue;
        };
        if let Some(line) = edge.line.or(*carrier_line) {
            carrier_locations
                .entry((path.clone(), line))
                .or_insert_with(|| carrier_id.clone());
        }
    }
    for entry in references {
        for hit in &mut entry.hits {
            if hit.kind != "literal-path" {
                continue;
            }
            if let Some(carrier_id) = carrier_locations.get(&(entry.file.clone(), hit.line)) {
                hit.kind = "command-carrier".to_string();
                hit.carrier_id = Some(carrier_id.clone());
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn path_globs_use_path_semantics_and_filter_generic_basename_globs() {
        let text = r#"
Path(".").glob("data/nested/*.fixture.json")
Path(".").glob("data/*fixture.json")
Path(".").glob("*.json")
Path("data/nested").glob("*.fixture.json")
"#;
        let hits = path_hits(text, "data/nested/item.fixture.json", "source");
        assert_eq!(
            hits.iter().map(|hit| hit.kind.as_str()).collect::<Vec<_>>(),
            ["glob-consumption", "basename-glob"]
        );
        assert_eq!(hits[0].glob.as_deref(), Some("data/nested/*.fixture.json"));
        assert_eq!(hits[1].glob.as_deref(), Some("*.fixture.json"));
    }

    #[test]
    fn recursive_double_star_keeps_the_owner_path_semantics() {
        assert!(glob_matches("a/**/b/*.json", "a/b/item.json"));
        assert!(glob_matches("a/**/b/*.json", "a/deep/b/item.json"));
        assert!(!glob_matches("a/*/b/*.json", "a/deep/more/b/item.json"));
    }

    #[test]
    fn basename_fallback_requires_path_boundaries() {
        assert!(contains_basename_reference(
            "read target.py now",
            "target.py"
        ));
        assert!(!contains_basename_reference(
            "read target.pyx now",
            "target.py"
        ));
        assert!(!contains_basename_reference(
            "read scripts/target.py now",
            "target.py"
        ));
    }
}
