use std::collections::HashSet;
use std::path::Path;

use crate::inventory::{FileInventory, RepoPath};

/// Match the deliberately small, non-recursive repository patterns used by the
/// Python validators. A `*` matches within one path component; it never crosses
/// `/` here.
pub fn path_matches_non_recursive(path: &str, pattern: &str) -> bool {
    let path_parts: Vec<&str> = path.split('/').collect();
    let pattern_parts: Vec<&str> = pattern.split('/').collect();
    path_parts.len() == pattern_parts.len()
        && path_parts
            .iter()
            .zip(pattern_parts)
            .all(|(path, pattern)| component_matches(path, pattern))
}

fn component_matches(value: &str, pattern: &str) -> bool {
    let mut value = value.chars().peekable();
    let mut pattern = pattern.chars().peekable();
    while let Some(pattern_char) = pattern.next() {
        if pattern_char == '*' {
            let remaining: String = pattern.collect();
            if remaining.is_empty() {
                return true;
            }
            let value_remaining: String = value.collect();
            return (0..=value_remaining.chars().count()).any(|offset| {
                let suffix: String = value_remaining.chars().skip(offset).collect();
                component_matches(&suffix, &remaining)
            });
        }
        if value.next() != Some(pattern_char) {
            return false;
        }
    }
    value.next().is_none()
}

/// Select existing files from an already-established inventory.
pub fn matching_files<'a>(
    repo_root: &Path,
    inventory: &'a FileInventory,
    patterns: &[&str],
) -> Vec<&'a RepoPath> {
    let mut seen = HashSet::new();
    let mut paths: Vec<&RepoPath> = inventory
        .paths()
        .iter()
        .filter(|path| {
            path.on_disk(repo_root).is_file()
                && patterns
                    .iter()
                    .any(|pattern| path_matches_non_recursive(path.as_str(), pattern))
        })
        .filter(|path| seen.insert(path.as_str().to_string()))
        .collect();
    paths.sort_by(|left, right| left.as_str().cmp(right.as_str()));
    paths
}

#[cfg(test)]
mod tests {
    use super::path_matches_non_recursive;

    #[test]
    fn stars_do_not_cross_path_components_for_inventory_patterns() {
        assert!(path_matches_non_recursive(
            "scripts/tool.py",
            "scripts/*.py"
        ));
        assert!(!path_matches_non_recursive(
            "scripts/nested/tool.py",
            "scripts/*.py"
        ));
        assert!(path_matches_non_recursive("tool.py", "*.py"));
    }
}
