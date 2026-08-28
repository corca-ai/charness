use std::collections::{BTreeMap, BTreeSet};
use std::io::Write;
use std::path::{Path, PathBuf};

use serde::Serialize;

use crate::graph_mirrors::MIRROR_RULES;
use crate::graph_model::MirrorTransform;
use crate::inventory::{FileInventory, InventoryError};

const DOC_GLOBS: &[&str] = &[
    "README.md",
    "AGENTS.md",
    "docs/**/*.md",
    "presets/**/*.md",
    "profiles/**/*.md",
    "skills/**/*.md",
];
const PLUGIN_REFERENCE_PREFIX: &str = "<plugin-dir>/";
const AUTHORING_REFERENCE_PREFIX: &str = "<authoring-repo>/";

const RESOLVED: &str = "resolved";
const TEMPLATED: &str = "templated";
const ESCAPES_PACKAGE_ROOT: &str = "escapes-package-root";
const MISSING: &str = "missing";
const AUTHORING_ONLY: &str = "authoring-only";
const SHIPPED_BUT_MARKED_AUTHORING_ONLY: &str = "shipped-but-marked-authoring-only";

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct Reference {
    pub path: String,
    pub line: usize,
    pub reference: String,
    pub classification: String,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct PluginRefsUnestablished {
    pub path: String,
    pub status: String,
    pub detail: String,
}

#[derive(Debug, Serialize)]
pub struct PluginRefsReport {
    pub schema: &'static str,
    pub repo_root: String,
    pub listing: String,
    pub packages: Vec<String>,
    pub scope_note: String,
    pub scanned_files: usize,
    pub references: Vec<Reference>,
    pub findings: Vec<Reference>,
    pub counts: BTreeMap<String, usize>,
    pub unestablished: Vec<PluginRefsUnestablished>,
}

struct ReportData {
    packages: Vec<String>,
    scope_note: String,
    scanned_files: usize,
    references: Vec<Reference>,
    findings: Vec<Reference>,
    counts: BTreeMap<String, usize>,
    unestablished: Vec<PluginRefsUnestablished>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct CandidateReference {
    line: usize,
    reference: String,
    target: String,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
struct Fence {
    marker: u8,
    length: usize,
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct ScannedLine {
    line: usize,
    content: String,
    in_fence: bool,
}

/// Analyze the inventory-scoped Markdown documents for plugin-root references.
pub fn analyze(repo_root: &Path, inventory: &FileInventory) -> (PluginRefsReport, i32) {
    let (packages, package_paths) = discover_packages(inventory);
    let mut counts = empty_counts();
    let mut references = Vec::new();
    let mut unestablished = Vec::new();

    if packages.is_empty() {
        return (
            report(
                repo_root,
                inventory.source().as_str(),
                ReportData {
                    packages: Vec::new(),
                    scope_note: "no plugins package; nothing was validated".to_string(),
                    scanned_files: 0,
                    references,
                    findings: Vec::new(),
                    counts,
                    unestablished,
                },
            ),
            0,
        );
    }

    let documents = matching_documents(inventory);
    for path in &documents {
        let contents = match std::fs::read_to_string(repo_root.join(path)) {
            Ok(contents) => contents,
            Err(error) => {
                unestablished.push(PluginRefsUnestablished {
                    path: path.clone(),
                    status: "unreadable".to_string(),
                    detail: format!("unreadable: read-error: {error}"),
                });
                continue;
            }
        };
        let lines = iter_doc_lines(&contents);
        for line in lines {
            if line.in_fence {
                continue;
            }
            for candidate in references_in_line(&line.content, PLUGIN_REFERENCE_PREFIX, line.line) {
                let classification = classify_plugin_target(&candidate.target, &package_paths);
                references.push(Reference {
                    path: path.clone(),
                    line: candidate.line,
                    reference: candidate.reference,
                    classification: classification.to_string(),
                });
                *counts.entry(classification.to_string()).or_default() += 1;
            }
            if is_skill_document(path) {
                for candidate in
                    references_in_line(&line.content, AUTHORING_REFERENCE_PREFIX, line.line)
                {
                    let classification =
                        if installed_target_exists(&candidate.target, &packages, &package_paths) {
                            SHIPPED_BUT_MARKED_AUTHORING_ONLY
                        } else {
                            AUTHORING_ONLY
                        };
                    references.push(Reference {
                        path: path.clone(),
                        line: candidate.line,
                        reference: candidate.reference,
                        classification: classification.to_string(),
                    });
                    *counts.entry(classification.to_string()).or_default() += 1;
                }
            }
        }
    }

    references.sort_by(|left, right| {
        left.path
            .cmp(&right.path)
            .then(left.line.cmp(&right.line))
            .then(left.reference.cmp(&right.reference))
    });
    unestablished.sort_by(|left, right| left.path.cmp(&right.path));
    let findings = references
        .iter()
        .filter(|reference| is_finding(&reference.classification))
        .cloned()
        .collect::<Vec<_>>();
    let exit = if !unestablished.is_empty() {
        3
    } else if findings.is_empty() {
        0
    } else {
        1
    };
    let packages = packages.into_iter().collect::<Vec<_>>();
    (
        report(
            repo_root,
            inventory.source().as_str(),
            ReportData {
                packages: packages.clone(),
                scope_note: format!("validated package set: {}", packages.join(", ")),
                scanned_files: documents.len(),
                references,
                findings,
                counts,
                unestablished,
            },
        ),
        exit,
    )
}

fn report(repo_root: &Path, listing: &str, data: ReportData) -> PluginRefsReport {
    PluginRefsReport {
        schema: "repograph.plugin_refs.v1",
        repo_root: repo_root.to_string_lossy().into_owned(),
        listing: listing.to_string(),
        packages: data.packages,
        scope_note: data.scope_note,
        scanned_files: data.scanned_files,
        references: data.references,
        findings: data.findings,
        counts: data.counts,
        unestablished: data.unestablished,
    }
}

fn empty_counts() -> BTreeMap<String, usize> {
    [
        RESOLVED,
        TEMPLATED,
        ESCAPES_PACKAGE_ROOT,
        MISSING,
        AUTHORING_ONLY,
        SHIPPED_BUT_MARKED_AUTHORING_ONLY,
    ]
    .into_iter()
    .map(|classification| (classification.to_string(), 0))
    .collect()
}

fn discover_packages(inventory: &FileInventory) -> (BTreeSet<String>, BTreeSet<String>) {
    let mut packages = BTreeSet::new();
    let mut package_paths = BTreeSet::new();
    for path in inventory.paths() {
        let mut components = path.as_str().split('/');
        if components.next() != Some("plugins") {
            continue;
        }
        let Some(package) = components.next() else {
            continue;
        };
        if package.is_empty() || components.next().is_none() {
            continue;
        }
        packages.insert(package.to_string());
        package_paths.insert(path.as_str().to_string());
    }
    (packages, package_paths)
}

fn matching_documents(inventory: &FileInventory) -> Vec<String> {
    let mut documents = BTreeSet::new();
    for path in inventory.paths() {
        if DOC_GLOBS
            .iter()
            .any(|pattern| matches_doc_glob(path.as_str(), pattern))
        {
            documents.insert(path.as_str().to_string());
        }
    }
    documents.into_iter().collect()
}

fn matches_doc_glob(path: &str, pattern: &str) -> bool {
    match pattern {
        "README.md" | "AGENTS.md" => path == pattern,
        "docs/**/*.md" => path.starts_with("docs/") && path.ends_with(".md"),
        "presets/**/*.md" => path.starts_with("presets/") && path.ends_with(".md"),
        "profiles/**/*.md" => path.starts_with("profiles/") && path.ends_with(".md"),
        "skills/**/*.md" => path.starts_with("skills/") && path.ends_with(".md"),
        _ => false,
    }
}

fn is_skill_document(path: &str) -> bool {
    matches_doc_glob(path, "skills/**/*.md")
}

fn classify_plugin_target(target: &str, package_paths: &BTreeSet<String>) -> &'static str {
    if target.contains('<')
        || target.contains('>')
        || target.contains('…')
        || target.contains("...")
    {
        return TEMPLATED;
    }
    if target.starts_with('/') || target.split('/').any(|component| component == "..") {
        return ESCAPES_PACKAGE_ROOT;
    }
    let normalized = normalize_target(target);
    if package_paths.iter().any(|path| {
        path.splitn(3, '/')
            .nth(2)
            .is_some_and(|member| member == normalized.as_str())
    }) {
        RESOLVED
    } else {
        MISSING
    }
}

fn normalize_target(target: &str) -> String {
    target
        .split('/')
        .filter(|component| !component.is_empty() && *component != ".")
        .collect::<Vec<_>>()
        .join("/")
}

fn installed_target_exists(
    target: &str,
    packages: &BTreeSet<String>,
    package_paths: &BTreeSet<String>,
) -> bool {
    installed_spellings(target).into_iter().any(|candidate| {
        packages.iter().any(|package| {
            package_paths.contains(&format!(
                "plugins/{package}/{}",
                normalize_target(&candidate)
            ))
        })
    })
}

/// Return the authoring spelling and the installed spellings implied by the
/// existing mirror table. D6 intentionally applies the collapsed `skills/`
/// destination to both public and support skill references.
fn installed_spellings(target: &str) -> Vec<String> {
    let mut spellings = vec![target.to_string()];
    let Some(destination_prefix) = collapsed_skill_destination() else {
        return spellings;
    };
    for rule in MIRROR_RULES.iter().filter(|rule| {
        rule.source.starts_with("skills/")
            && rule.source.ends_with("/*")
            && matches!(
                rule.transform,
                MirrorTransform::PathCollapsed | MirrorTransform::FilteredCopy
            )
    }) {
        let source_prefix = rule.source.trim_end_matches('*');
        if let Some(rest) = target.strip_prefix(source_prefix) {
            let candidate = format!("{destination_prefix}{rest}");
            if !spellings.contains(&candidate) {
                spellings.push(candidate);
            }
        }
    }
    spellings
}

fn collapsed_skill_destination() -> Option<&'static str> {
    MIRROR_RULES
        .iter()
        .find(|rule| rule.transform == MirrorTransform::PathCollapsed)
        .and_then(|rule| rule.destination.splitn(3, '/').nth(2))
        .map(|destination| destination.trim_end_matches('*'))
}

fn is_finding(classification: &str) -> bool {
    matches!(
        classification,
        ESCAPES_PACKAGE_ROOT | MISSING | SHIPPED_BUT_MARKED_AUTHORING_ONLY
    )
}

fn references_in_line(line: &str, prefix: &str, line_number: usize) -> Vec<CandidateReference> {
    // Inline backtick code is scanned on purpose: the Python owner matched
    // references inside inline code, and most doc references are backticked;
    // only fenced blocks and HTML comments are skipped (iter_doc_lines).
    let masked = line;
    let mut references = Vec::new();
    let mut search_from = 0;
    while search_from < masked.len() {
        let Some(relative_start) = masked[search_from..].find(prefix) else {
            break;
        };
        let start = search_from + relative_start;
        let target_start = start + prefix.len();
        let mut target_end = target_start;
        for (offset, character) in masked[target_start..].char_indices() {
            if character.is_whitespace() || character == ')' || character == '`' {
                break;
            }
            target_end = target_start + offset + character.len_utf8();
        }
        let raw_target = &masked[target_start..target_end];
        let trimmed_target = raw_target.trim_end_matches(['.', ',', ';', ':', ')']);
        let target = if trimmed_target.is_empty()
            && raw_target.len() >= 3
            && raw_target.chars().all(|character| character == '.')
        {
            // `...` is a templating ellipsis, not an empty target followed by
            // sentence punctuation. Preserve it for the D6 classification.
            raw_target.to_string()
        } else {
            trimmed_target.to_string()
        };
        if !target.is_empty() {
            references.push(CandidateReference {
                line: line_number,
                reference: format!("{prefix}{target}"),
                target,
            });
        }
        search_from = target_end.max(target_start + 1);
    }
    references
}

/// Transcribe `markdown_doc_scan.iter_doc_lines`'s fence and comment walk.
fn iter_doc_lines(contents: &str) -> Vec<ScannedLine> {
    let mut fence = None;
    let mut in_html_comment = false;
    let mut lines = Vec::new();
    for (line_index, raw_line) in contents.lines().enumerate() {
        let line_number = line_index + 1;
        let mut line = raw_line.to_string();
        if in_html_comment {
            let Some(close) = line.find("-->") else {
                continue;
            };
            in_html_comment = false;
            line = line[close + 3..].to_string();
            if line.trim().is_empty() {
                continue;
            }
        }
        let stripped = line.trim();
        if fence.is_none() && stripped.starts_with("<!--") {
            if !stripped.contains("-->") {
                in_html_comment = true;
                continue;
            }
            if remove_html_comment_spans(stripped).trim().is_empty() {
                continue;
            }
        }
        if let Some(found) = fence_marker(&line) {
            match fence {
                None => {
                    fence = Some(found);
                    continue;
                }
                Some(open) if found.marker == open.marker && found.length >= open.length => {
                    fence = None;
                    continue;
                }
                Some(_) => {}
            }
        }
        lines.push(ScannedLine {
            line: line_number,
            content: line,
            in_fence: fence.is_some(),
        });
    }
    lines
}

fn fence_marker(line: &str) -> Option<Fence> {
    let trimmed = line.trim_start().as_bytes();
    let marker = *trimmed.first()?;
    if marker != b'`' && marker != b'~' {
        return None;
    }
    let length = trimmed.iter().take_while(|byte| **byte == marker).count();
    (length >= 3).then_some(Fence { marker, length })
}

fn remove_html_comment_spans(line: &str) -> String {
    let mut remaining = line;
    let mut result = String::new();
    while let Some(start) = remaining.find("<!--") {
        result.push_str(&remaining[..start]);
        let after_start = &remaining[start + 4..];
        let Some(end) = after_start.find("-->") else {
            result.push_str(remaining);
            return result;
        };
        remaining = &after_start[end + 3..];
    }
    result.push_str(remaining);
    result
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

    let inventory = match crate::inventory::acquire(&repo_root, file_list.as_deref()) {
        Ok(inventory) => inventory,
        Err(error) => {
            let report = unestablished_report(&repo_root, &error);
            return if emit_report(&report) { 3 } else { 70 };
        }
    };
    let (report, exit) = analyze(&repo_root, &inventory);
    if emit_report(&report) {
        exit
    } else {
        70
    }
}

fn unestablished_report(repo_root: &Path, error: &InventoryError) -> PluginRefsReport {
    report(
        repo_root,
        "unestablished",
        ReportData {
            packages: Vec::new(),
            scope_note: "file inventory was not established".to_string(),
            scanned_files: 0,
            references: Vec::new(),
            findings: Vec::new(),
            counts: empty_counts(),
            unestablished: vec![PluginRefsUnestablished {
                path: "<inventory>".to_string(),
                status: "inventory".to_string(),
                detail: error.to_string(),
            }],
        },
    )
}

fn emit_report(report: &PluginRefsReport) -> bool {
    let Ok(json) = serde_json::to_string(report) else {
        return false;
    };
    let stdout = std::io::stdout();
    let mut stdout = stdout.lock();
    writeln!(stdout, "{json}").is_ok()
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

pub fn usage() -> &'static str {
    "repograph plugin-refs [--repo-root PATH] [--file-list PATH]"
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::inventory::FileInventory;

    #[test]
    fn classifies_inventory_targets_without_filesystem_fallback() {
        let inventory = FileInventory::from_file_list_bytes(
            b"plugins/renamed/skills/demo/SKILL.md\0docs/guide.md\0",
        )
        .unwrap();
        assert_eq!(
            classify_plugin_target("skills/demo/SKILL.md", &discover_packages(&inventory).1),
            RESOLVED
        );
        assert_eq!(
            classify_plugin_target("skills/<skill>/SKILL.md", &discover_packages(&inventory).1),
            TEMPLATED
        );
        assert_eq!(
            classify_plugin_target("../outside.md", &discover_packages(&inventory).1),
            ESCAPES_PACKAGE_ROOT
        );
        assert_eq!(
            classify_plugin_target("skills/other.md", &discover_packages(&inventory).1),
            MISSING
        );
    }

    #[test]
    fn mirror_table_drives_public_and_support_flattening() {
        assert_eq!(
            installed_spellings("skills/public/demo/SKILL.md"),
            ["skills/public/demo/SKILL.md", "skills/demo/SKILL.md"]
        );
        assert_eq!(
            installed_spellings("skills/support/demo/SKILL.md"),
            ["skills/support/demo/SKILL.md", "skills/demo/SKILL.md"]
        );
    }

    #[test]
    fn fence_and_comment_walk_matches_owner_shapes() {
        let lines = iter_doc_lines(
            "<!--\n<plugin-dir>/comment.md\n-->\n\n```text\n<plugin-dir>/fenced.md\n~~~\n```\n\n<plugin-dir>/live.md\n",
        );
        assert!(lines
            .iter()
            .all(|line| !line.content.contains("comment.md")));
        assert!(lines
            .iter()
            .find(|line| line.content.contains("fenced.md"))
            .is_some_and(|line| line.in_fence));
        assert!(lines.iter().any(|line| line.content.contains("live.md")));
    }

    #[test]
    fn inline_code_is_scanned_like_the_python_owner() {
        let references = references_in_line(
            "live <plugin-dir>/ok.md and `<plugin-dir>/backticked.md`",
            PLUGIN_REFERENCE_PREFIX,
            1,
        );
        assert_eq!(references.len(), 2);
        assert_eq!(references[0].target, "ok.md");
        assert_eq!(references[1].target, "backticked.md");
    }

    #[test]
    fn ascii_ellipsis_is_retained_as_a_templated_target() {
        let references = references_in_line("<plugin-dir>/...", PLUGIN_REFERENCE_PREFIX, 1);
        assert_eq!(references[0].target, "...");
        assert_eq!(classify_plugin_target("...", &BTreeSet::new()), TEMPLATED);
    }
}
