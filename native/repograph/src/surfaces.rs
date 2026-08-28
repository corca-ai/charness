use std::collections::{HashMap, HashSet};
use std::fmt;
use std::path::{Path, PathBuf};

use serde::Serialize;
use serde_json::Value;

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct SurfaceError(pub String);

impl fmt::Display for SurfaceError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        formatter.write_str(&self.0)
    }
}

impl std::error::Error for SurfaceError {}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct GeneratedMarkdown {
    pub source_path: String,
    pub derived_path: String,
    pub generator: String,
    pub sync_command: String,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Surface {
    pub surface_id: String,
    pub description: String,
    pub source_paths: Vec<String>,
    pub derived_paths: Vec<String>,
    pub sync_commands: Vec<String>,
    pub verify_commands: Vec<String>,
    pub notes: Vec<String>,
    pub generated_markdown: Vec<GeneratedMarkdown>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct SurfaceManifest {
    pub version: String,
    pub surfaces: Vec<Surface>,
    pub path: PathBuf,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct MatchedSurface {
    pub surface_id: String,
    pub description: String,
    pub matched_source_paths: Vec<String>,
    pub matched_derived_paths: Vec<String>,
    pub source_paths: Vec<String>,
    pub derived_paths: Vec<String>,
    pub sync_commands: Vec<String>,
    pub verify_commands: Vec<String>,
    pub notes: Vec<String>,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct MatchSurfacesReport {
    pub schema: &'static str,
    pub changed_paths: Vec<String>,
    pub matched_surfaces: Vec<MatchedSurface>,
    pub sync_commands: Vec<String>,
    pub verify_commands: Vec<String>,
    pub unmatched_paths: Vec<String>,
}

pub fn load_surfaces(
    repo_root: &Path,
    surfaces_path: &Path,
) -> Result<SurfaceManifest, SurfaceError> {
    let manifest_path = if surfaces_path.is_absolute() {
        surfaces_path.to_path_buf()
    } else {
        repo_root.join(surfaces_path)
    };
    let text = std::fs::read_to_string(&manifest_path).map_err(|error| {
        SurfaceError(format!(
            "could not read surfaces manifest `{}`: {error}",
            manifest_path.display()
        ))
    })?;
    let raw: Value = serde_json::from_str(&text).map_err(|error| {
        SurfaceError(format!(
            "invalid JSON in `{}`: {error}",
            manifest_path.display()
        ))
    })?;
    let object = raw
        .as_object()
        .ok_or_else(|| SurfaceError("surfaces manifest must be a JSON object".to_string()))?;
    let version = object
        .get("version")
        .filter(|value| value.as_f64() == Some(1.0))
        .ok_or_else(|| SurfaceError("surfaces manifest `version` must be 1".to_string()))?;
    let version = version.to_string();
    let surfaces_raw = object
        .get("surfaces")
        .and_then(Value::as_array)
        .filter(|surfaces| !surfaces.is_empty())
        .ok_or_else(|| {
            SurfaceError("surfaces manifest `surfaces` must be a non-empty list".to_string())
        })?;

    let mut surfaces = Vec::with_capacity(surfaces_raw.len());
    let mut seen_ids = HashSet::new();
    for (index, value) in surfaces_raw.iter().enumerate() {
        let surface = validate_surface(value, index)?;
        if !seen_ids.insert(surface.surface_id.clone()) {
            return Err(SurfaceError(format!(
                "duplicate surface id `{}`",
                surface.surface_id
            )));
        }
        surfaces.push(surface);
    }
    Ok(SurfaceManifest {
        version,
        surfaces,
        path: manifest_path,
    })
}

pub fn match_surfaces(
    manifest: &SurfaceManifest,
    changed_paths: &[String],
) -> Result<MatchSurfacesReport, SurfaceError> {
    let normalized_paths = dedupe_preserve_order(
        changed_paths
            .iter()
            .map(|path| normalize_repo_path(path))
            .collect::<Result<Vec<_>, _>>()?,
    );
    let mut matched_surfaces = Vec::new();
    let mut matched_path_set = HashSet::new();

    for surface in &manifest.surfaces {
        let matched_source_paths = normalized_paths
            .iter()
            .filter(|path| path_matches_patterns(path, &surface.source_paths))
            .cloned()
            .collect::<Vec<_>>();
        let matched_derived_paths = normalized_paths
            .iter()
            .filter(|path| path_matches_patterns(path, &surface.derived_paths))
            .cloned()
            .collect::<Vec<_>>();
        if matched_source_paths.is_empty() && matched_derived_paths.is_empty() {
            continue;
        }
        matched_path_set.extend(matched_source_paths.iter().cloned());
        matched_path_set.extend(matched_derived_paths.iter().cloned());
        matched_surfaces.push(MatchedSurface {
            surface_id: surface.surface_id.clone(),
            description: surface.description.clone(),
            matched_source_paths,
            matched_derived_paths,
            source_paths: surface.source_paths.clone(),
            derived_paths: surface.derived_paths.clone(),
            sync_commands: surface.sync_commands.clone(),
            verify_commands: surface.verify_commands.clone(),
            notes: surface.notes.clone(),
        });
    }

    let sync_commands = dedupe_preserve_order(
        matched_surfaces
            .iter()
            .flat_map(|surface| surface.sync_commands.iter().cloned())
            .collect(),
    );
    let verify_commands = dedupe_preserve_order(
        matched_surfaces
            .iter()
            .flat_map(|surface| surface.verify_commands.iter().cloned())
            .collect(),
    );
    let unmatched_paths = normalized_paths
        .iter()
        .filter(|path| !matched_path_set.contains(*path))
        .cloned()
        .collect();
    Ok(MatchSurfacesReport {
        schema: "repograph.match_surfaces.v1",
        changed_paths: normalized_paths,
        matched_surfaces,
        sync_commands,
        verify_commands,
        unmatched_paths,
    })
}

pub fn path_matches_patterns(path: &str, patterns: &[String]) -> bool {
    patterns.iter().any(|pattern| fnmatch(path, pattern))
}

pub fn normalize_repo_path(value: &str) -> Result<String, SurfaceError> {
    if value.starts_with('/') {
        return Err(SurfaceError(format!(
            "surface path must stay within the repo: `{value}`"
        )));
    }
    let normalized = value
        .split('/')
        .filter(|component| !component.is_empty() && *component != ".")
        .collect::<Vec<_>>()
        .join("/");
    let normalized = if normalized.is_empty() {
        ".".to_string()
    } else {
        normalized
    };
    if normalized.starts_with("../") {
        return Err(SurfaceError(format!(
            "surface path must stay within the repo: `{value}`"
        )));
    }
    Ok(normalized)
}

fn validate_surface(value: &Value, index: usize) -> Result<Surface, SurfaceError> {
    let field = format!("surfaces[{index}]");
    let object = value
        .as_object()
        .ok_or_else(|| SurfaceError(format!("`{field}` must be an object")))?;
    let surface_id = required_string(object.get("surface_id"), &format!("{field}.surface_id"))?;
    let description = required_string(object.get("description"), &format!("{field}.description"))?;
    let source_paths =
        required_string_list(object.get("source_paths"), &format!("{field}.source_paths"))?
            .into_iter()
            .map(|path| normalize_repo_path(&path))
            .collect::<Result<Vec<_>, _>>()?;
    let derived_paths = required_string_list(
        object.get("derived_paths"),
        &format!("{field}.derived_paths"),
    )?
    .into_iter()
    .map(|path| normalize_repo_path(&path))
    .collect::<Result<Vec<_>, _>>()?;
    check_surface_idiom(&source_paths, &format!("{field}.source_paths"))?;
    check_surface_idiom(&derived_paths, &format!("{field}.derived_paths"))?;
    let sync_commands = required_string_list(
        object.get("sync_commands"),
        &format!("{field}.sync_commands"),
    )?;
    let verify_commands = required_string_list(
        object.get("verify_commands"),
        &format!("{field}.verify_commands"),
    )?;
    let notes = required_string_list(object.get("notes"), &format!("{field}.notes"))?;
    let generated_raw = object
        .get("generated_markdown")
        .map_or(Ok(Vec::new()), |value| {
            value
                .as_array()
                .ok_or_else(|| {
                    SurfaceError(format!("`{field}.generated_markdown` must be a list"))
                })?
                .iter()
                .enumerate()
                .map(|(entry_index, entry)| {
                    validate_generated_markdown(
                        entry,
                        &format!("{field}.generated_markdown[{entry_index}]"),
                    )
                })
                .collect::<Result<Vec<_>, _>>()
        })?;
    for entry in &generated_raw {
        if !path_matches_patterns(&entry.source_path, &source_paths) {
            return Err(SurfaceError(format!(
                "`{field}.generated_markdown` source `{}` must also appear in `source_paths`",
                entry.source_path
            )));
        }
        if !path_matches_patterns(&entry.derived_path, &derived_paths) {
            return Err(SurfaceError(format!(
                "`{field}.generated_markdown` derived `{}` must also appear in `derived_paths`",
                entry.derived_path
            )));
        }
    }
    Ok(Surface {
        surface_id,
        description,
        source_paths,
        derived_paths,
        sync_commands,
        verify_commands,
        notes,
        generated_markdown: generated_raw,
    })
}

fn validate_generated_markdown(
    value: &Value,
    field: &str,
) -> Result<GeneratedMarkdown, SurfaceError> {
    let object = value
        .as_object()
        .ok_or_else(|| SurfaceError(format!("`{field}` must be an object")))?;
    Ok(GeneratedMarkdown {
        source_path: normalize_repo_path(&required_string(
            object.get("source_path"),
            &format!("{field}.source_path"),
        )?)?,
        derived_path: normalize_repo_path(&required_string(
            object.get("derived_path"),
            &format!("{field}.derived_path"),
        )?)?,
        generator: required_string(object.get("generator"), &format!("{field}.generator"))?,
        sync_command: required_string(
            object.get("sync_command"),
            &format!("{field}.sync_command"),
        )?,
    })
}

fn required_string(value: Option<&Value>, field: &str) -> Result<String, SurfaceError> {
    let value = value
        .and_then(Value::as_str)
        .filter(|value| !value.trim().is_empty())
        .ok_or_else(|| SurfaceError(format!("`{field}` must be a non-empty string")))?;
    Ok(value.to_string())
}

fn required_string_list(value: Option<&Value>, field: &str) -> Result<Vec<String>, SurfaceError> {
    let values = value
        .and_then(Value::as_array)
        .ok_or_else(|| SurfaceError(format!("`{field}` must be a list")))?;
    values
        .iter()
        .enumerate()
        .map(|(index, value)| required_string(Some(value), &format!("{field}[{index}]")))
        .collect()
}

fn check_surface_idiom(patterns: &[String], field: &str) -> Result<(), SurfaceError> {
    let pattern_set: HashSet<&str> = patterns.iter().map(String::as_str).collect();
    for pattern in patterns {
        let Some((directory, extension)) = recursive_extension_pattern(pattern) else {
            continue;
        };
        let sibling = if directory.is_empty() {
            format!("*{extension}")
        } else {
            format!("{directory}/*{extension}")
        };
        if !pattern_set.contains(sibling.as_str()) {
            return Err(SurfaceError(format!(
                "`{field}` pattern `{pattern}` uses the non-recursive-fnmatch footgun without its sibling `{sibling}`"
            )));
        }
    }
    Ok(())
}

fn recursive_extension_pattern(pattern: &str) -> Option<(&str, &str)> {
    let marker = "**/*";
    let index = pattern.find(marker)?;
    if pattern[index + marker.len()..].contains('/')
        || pattern[index + marker.len()..].contains('*')
    {
        return None;
    }
    let extension = &pattern[index + marker.len()..];
    if !extension.starts_with('.') || extension.is_empty() {
        return None;
    }
    let prefix = &pattern[..index];
    if prefix.is_empty() {
        Some(("", extension))
    } else if let Some(directory) = prefix.strip_suffix('/') {
        if directory.is_empty() {
            None
        } else {
            Some((directory, extension))
        }
    } else {
        None
    }
}

fn dedupe_preserve_order(values: Vec<String>) -> Vec<String> {
    let mut result = Vec::new();
    let mut seen = HashSet::new();
    for value in values {
        if seen.insert(value.clone()) {
            result.push(value);
        }
    }
    result
}

/// Python's POSIX `fnmatch.fnmatch`: case-sensitive on this host and with `*`
/// matching `/` as an ordinary character.
pub fn fnmatch(value: &str, pattern: &str) -> bool {
    let value: Vec<char> = value.chars().collect();
    let pattern: Vec<char> = pattern.chars().collect();
    let mut memo = HashMap::new();
    fn match_at(
        value: &[char],
        pattern: &[char],
        value_index: usize,
        pattern_index: usize,
        memo: &mut HashMap<(usize, usize), bool>,
    ) -> bool {
        if let Some(result) = memo.get(&(value_index, pattern_index)) {
            return *result;
        }
        let result = if pattern_index == pattern.len() {
            value_index == value.len()
        } else {
            match pattern[pattern_index] {
                '*' => (value_index..=value.len())
                    .any(|next| match_at(value, pattern, next, pattern_index + 1, memo)),
                '?' => {
                    value_index < value.len()
                        && match_at(value, pattern, value_index + 1, pattern_index + 1, memo)
                }
                '[' => match_class(value, pattern, value_index, pattern_index, memo),
                literal => {
                    value_index < value.len()
                        && value[value_index] == literal
                        && match_at(value, pattern, value_index + 1, pattern_index + 1, memo)
                }
            }
        };
        memo.insert((value_index, pattern_index), result);
        result
    }

    fn match_class(
        value: &[char],
        pattern: &[char],
        value_index: usize,
        pattern_index: usize,
        memo: &mut HashMap<(usize, usize), bool>,
    ) -> bool {
        let Some(class) = parse_class(pattern, pattern_index) else {
            return value_index < value.len()
                && value[value_index] == '['
                && match_at(value, pattern, value_index + 1, pattern_index + 1, memo);
        };
        let matched = value_index < value.len()
            && class.ranges.iter().any(|(start, finish)| {
                *start <= value[value_index] && value[value_index] <= *finish
            });
        value_index < value.len()
            && (matched != class.negated)
            && match_at(value, pattern, value_index + 1, class.end, memo)
    }

    struct CharacterClass {
        end: usize,
        negated: bool,
        ranges: Vec<(char, char)>,
    }

    fn parse_class(pattern: &[char], start: usize) -> Option<CharacterClass> {
        let mut index = start + 1;
        if index >= pattern.len() {
            return None;
        }
        let negated = pattern[index] == '!';
        if negated {
            index += 1;
        }
        if index < pattern.len() && pattern[index] == ']' {
            index += 1;
        }
        let content_start = index;
        while index < pattern.len() && pattern[index] != ']' {
            index += 1;
        }
        if index >= pattern.len() || index == content_start {
            return None;
        }
        let content = &pattern[content_start..index];
        let mut ranges = Vec::new();
        let mut content_index = 0;
        while content_index < content.len() {
            if content_index + 2 < content.len() && content[content_index + 1] == '-' {
                ranges.push((content[content_index], content[content_index + 2]));
                content_index += 3;
            } else {
                ranges.push((content[content_index], content[content_index]));
                content_index += 1;
            }
        }
        Some(CharacterClass {
            end: index + 1,
            negated,
            ranges,
        })
    }

    match_at(&value, &pattern, 0, 0, &mut memo)
}

pub fn run<I>(args: I) -> i32
where
    I: IntoIterator<Item = String>,
{
    let mut args = args.into_iter();
    let mut repo_root = match std::env::current_dir() {
        Ok(path) => path,
        Err(error) => {
            eprintln!("usage error: could not determine current directory: {error}");
            return 2;
        }
    };
    let mut surfaces_path = PathBuf::from(".agents/surfaces.json");
    let mut changed_paths = Vec::new();
    let mut help = false;
    while let Some(argument) = args.next() {
        match argument.as_str() {
            "--repo-root" => match required_cli_value(&mut args, "--repo-root") {
                Ok(value) => repo_root = PathBuf::from(value),
                Err(error) => return cli_error(&error),
            },
            "--surfaces" => match required_cli_value(&mut args, "--surfaces") {
                Ok(value) => surfaces_path = PathBuf::from(value),
                Err(error) => return cli_error(&error),
            },
            "--path" => match required_cli_value(&mut args, "--path") {
                Ok(value) => changed_paths.push(value),
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
    let manifest = match load_surfaces(&repo_root, &surfaces_path) {
        Ok(manifest) => manifest,
        Err(error) => {
            eprintln!("{error}");
            return 3;
        }
    };
    let report = match match_surfaces(&manifest, &changed_paths) {
        Ok(report) => report,
        Err(error) => {
            eprintln!("{error}");
            return 3;
        }
    };
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

fn required_cli_value<I>(args: &mut I, flag: &str) -> Result<String, String>
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
    "repograph match-surfaces [--repo-root PATH] [--surfaces PATH] [--path PATH]..."
}

#[cfg(test)]
mod tests {
    use super::*;

    fn manifest() -> SurfaceManifest {
        SurfaceManifest {
            version: "1.0".to_string(),
            path: PathBuf::from("fixtures/surfaces.json"),
            surfaces: vec![Surface {
                surface_id: "first".to_string(),
                description: "first".to_string(),
                source_paths: vec!["dir/*.py".to_string(), "dir/**/*.py".to_string()],
                derived_paths: vec!["out/*.md".to_string(), "out/**/*.md".to_string()],
                sync_commands: vec!["sync-a".to_string(), "shared".to_string()],
                verify_commands: vec!["verify-a".to_string()],
                notes: vec!["note".to_string()],
                generated_markdown: Vec::new(),
            }],
        }
    }

    #[test]
    fn fnmatch_star_crosses_slash_but_recursive_pattern_misses_top_level_file() {
        assert!(fnmatch("dir/sub/file.py", "dir/**/*.py"));
        assert!(!fnmatch("dir/file.py", "dir/**/*.py"));
        assert!(fnmatch("dir/file.py", "dir/*.py"));
    }

    #[test]
    fn matching_deduplicates_commands_and_accepts_numeric_version_one_point_zero() {
        let report = match_surfaces(&manifest(), &["dir/file.py".to_string()]).unwrap();
        assert_eq!(report.sync_commands, ["sync-a", "shared"]);
        assert_eq!(
            report.matched_surfaces[0].matched_source_paths,
            ["dir/file.py"]
        );
    }

    #[test]
    fn normalization_keeps_embedded_parent_components_like_python() {
        assert_eq!(normalize_repo_path("one/../two").unwrap(), "one/../two");
        assert!(normalize_repo_path("../two").is_err());
    }
}
