use std::ffi::OsStr;
use std::fmt;
use std::io;
use std::io::Write;
use std::path::{Component, Path, PathBuf};
use std::process::Command;
use std::str;

use serde::Serialize;

/// The source used to establish the repository file universe.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ListingSource {
    Git,
    FileList,
}

impl ListingSource {
    pub const fn as_str(self) -> &'static str {
        match self {
            Self::Git => "git",
            Self::FileList => "file-list",
        }
    }
}

/// A validated repository-relative POSIX path.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct RepoPath(String);

impl RepoPath {
    pub fn as_str(&self) -> &str {
        &self.0
    }

    pub fn on_disk(&self, repo_root: &Path) -> PathBuf {
        repo_root.join(&self.0)
    }
}

/// The one file universe used by an analysis process.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct FileInventory {
    source: ListingSource,
    paths: Vec<RepoPath>,
}

impl FileInventory {
    pub fn source(&self) -> ListingSource {
        self.source
    }

    pub fn paths(&self) -> &[RepoPath] {
        &self.paths
    }

    /// Retain one established inventory while narrowing its analysis scope.
    pub fn filtered<F>(&self, mut keep: F) -> Self
    where
        F: FnMut(&str) -> bool,
    {
        let mut seen = std::collections::HashSet::new();
        let paths = self
            .paths
            .iter()
            .filter(|path| keep(path.as_str()) && seen.insert(path.as_str()))
            .cloned()
            .collect();
        Self {
            source: self.source,
            paths,
        }
    }

    /// Add a normalized query path to the in-process graph projection.
    pub fn with_path(&self, path: &str) -> Result<Self, InventoryError> {
        validate_repo_path(path, "query path")?;
        if self
            .paths
            .iter()
            .any(|candidate| candidate.as_str() == path)
        {
            return Ok(self.clone());
        }
        let mut paths = self.paths.clone();
        paths.push(RepoPath(path.to_string()));
        Ok(Self {
            source: self.source,
            paths,
        })
    }

    pub fn from_file_list_bytes(bytes: &[u8]) -> Result<Self, InventoryError> {
        Ok(Self {
            source: ListingSource::FileList,
            paths: parse_nul_paths(bytes, "file list")?,
        })
    }

    fn from_git_bytes(bytes: &[u8]) -> Result<Self, InventoryError> {
        Ok(Self {
            source: ListingSource::Git,
            paths: parse_nul_paths(bytes, "git listing")?,
        })
    }
}

/// A typed failure to establish the inventory.
#[derive(Debug)]
pub enum InventoryError {
    GitLaunch {
        program: String,
        source: io::Error,
    },
    GitFailed {
        status: String,
        stderr: String,
    },
    FileListRead {
        path: PathBuf,
        source: io::Error,
    },
    InvalidUtf8 {
        source_name: String,
        offset: usize,
    },
    InvalidPath {
        source_name: String,
        path: String,
        reason: String,
    },
}

impl fmt::Display for InventoryError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::GitLaunch { program, source } => write!(
                f,
                "inventory-unestablished: could not execute {program:?}: {source}"
            ),
            Self::GitFailed { status, stderr } => write!(
                f,
                "inventory-unestablished: git listing failed ({status}): {stderr}"
            ),
            Self::FileListRead { path, source } => write!(
                f,
                "inventory-unestablished: could not read file list {}: {source}",
                path.display()
            ),
            Self::InvalidUtf8 {
                source_name,
                offset,
            } => write!(
                f,
                "inventory-unestablished: {source_name} contains a non-UTF-8 path at byte {offset}"
            ),
            Self::InvalidPath {
                source_name,
                path,
                reason,
            } => write!(
                f,
                "inventory-unestablished: {source_name} contains invalid path {path:?}: {reason}"
            ),
        }
    }
}

impl std::error::Error for InventoryError {}

/// Establish an inventory from one Git listing, or from the supplied NUL list.
pub fn acquire(
    repo_root: &Path,
    file_list: Option<&Path>,
) -> Result<FileInventory, InventoryError> {
    acquire_with_git_program(repo_root, file_list, OsStr::new("git"))
}

/// Test seam for proving the unavailable-Git exit path without changing PATH.
pub fn acquire_with_git_program(
    repo_root: &Path,
    file_list: Option<&Path>,
    git_program: &OsStr,
) -> Result<FileInventory, InventoryError> {
    if let Some(file_list) = file_list {
        let bytes = std::fs::read(file_list).map_err(|source| InventoryError::FileListRead {
            path: file_list.to_path_buf(),
            source,
        })?;
        return FileInventory::from_file_list_bytes(&bytes);
    }

    let output = Command::new(git_program)
        .current_dir(repo_root)
        .args([
            "ls-files",
            "-z",
            "--cached",
            "--others",
            "--exclude-standard",
        ])
        .output()
        .map_err(|source| InventoryError::GitLaunch {
            program: git_program.to_string_lossy().into_owned(),
            source,
        })?;

    if !output.status.success() {
        let status = output.status.code().map_or_else(
            || "terminated by signal".to_string(),
            |code| code.to_string(),
        );
        return Err(InventoryError::GitFailed {
            status,
            stderr: one_line_lossy(&output.stderr),
        });
    }

    FileInventory::from_git_bytes(&output.stdout)
}

fn parse_nul_paths(bytes: &[u8], source_name: &str) -> Result<Vec<RepoPath>, InventoryError> {
    let mut paths = Vec::new();
    for raw_path in bytes.split(|byte| *byte == 0) {
        if raw_path.is_empty() {
            continue;
        }
        let path = str::from_utf8(raw_path).map_err(|error| InventoryError::InvalidUtf8 {
            source_name: source_name.to_string(),
            offset: error.valid_up_to(),
        })?;
        validate_repo_path(path, source_name)?;
        paths.push(RepoPath(path.to_string()));
    }
    Ok(paths)
}

fn validate_repo_path(path: &str, source_name: &str) -> Result<(), InventoryError> {
    let reason = if path.is_empty() {
        Some("empty path")
    } else if path.starts_with('/') {
        Some("absolute path")
    } else if path.split('/').any(|component| component == "..") {
        Some("parent traversal")
    } else if Path::new(path)
        .components()
        .any(|component| matches!(component, Component::RootDir | Component::Prefix(_)))
    {
        Some("rooted path")
    } else {
        None
    };

    if let Some(reason) = reason {
        return Err(InventoryError::InvalidPath {
            source_name: source_name.to_string(),
            path: path.to_string(),
            reason: reason.to_string(),
        });
    }
    Ok(())
}

fn one_line_lossy(bytes: &[u8]) -> String {
    let value = String::from_utf8_lossy(bytes);
    value
        .chars()
        .map(|character| match character {
            character if character.is_control() => ' ',
            character => character,
        })
        .collect()
}

/// Machine-readable output for `repograph inventory`.
#[derive(Debug, Serialize)]
pub struct InventoryReport {
    pub schema: &'static str,
    pub repo_root: String,
    pub listing: String,
    /// `established` | `empty-scope` | `unestablished`. A listing that found
    /// nothing is a real answer to a real question, but it may not be reported
    /// as though files were inspected.
    pub status: &'static str,
    pub regular_files_only: bool,
    pub paths_listed: usize,
    pub dropped_by_stat: usize,
    pub path_count: usize,
    pub paths: Vec<String>,
    pub unestablished: Option<String>,
}

/// Compare like Python's `PurePath`: by `/`-separated components, not bytewise.
///
/// Measured on this repo on 2026-08-29: byte-string order and `Path` order
/// disagree at 222 of 6,701 positions (`a/b.py` sorts before `a-b/c.py` as a
/// Path and after it as a string), so a bytewise sort would silently reorder
/// the listing for every consumer of `repo_file_listing.iter_repo_files`.
/// Allocation-free: a `Vec` key per comparison cost ~170k heap allocations on
/// this repo's 6,701 paths and made the native listing SLOWER than the Python
/// one it replaces. Walk the components instead.
fn compare_path_components(left: &str, right: &str) -> std::cmp::Ordering {
    let mut left = left.split('/');
    let mut right = right.split('/');
    loop {
        match (left.next(), right.next()) {
            (None, None) => return std::cmp::Ordering::Equal,
            (None, Some(_)) => return std::cmp::Ordering::Less,
            (Some(_), None) => return std::cmp::Ordering::Greater,
            (Some(left), Some(right)) => match left.cmp(right) {
                std::cmp::Ordering::Equal => continue,
                ordering => return ordering,
            },
        }
    }
}

/// Reproduce `pathlib.Path.is_file()`: follow symlinks, require a regular file.
/// Dangling links and directory symlinks are dropped, which is the semantic the
/// Python owner has always applied.
fn is_regular_file(repo_root: &Path, path: &RepoPath) -> bool {
    std::fs::metadata(path.on_disk(repo_root)).is_ok_and(|metadata| metadata.is_file())
}

/// Build the inventory report.
///
/// **Blind class.** This command sees the git listing and one `stat` per path.
/// It cannot see anything about a file's CONTENT, cannot distinguish a file git
/// does not know about from one that does not exist, and — when `--file-list`
/// is supplied — does not verify that the list came from this repository at
/// all. It reports the universe it was handed, not the universe that is true.
pub fn build_report(
    repo_root: &Path,
    inventory: &FileInventory,
    regular_files_only: bool,
) -> InventoryReport {
    let paths_listed = inventory.paths().len();
    let mut paths = inventory
        .paths()
        .iter()
        .filter(|path| !regular_files_only || is_regular_file(repo_root, path))
        .map(|path| path.as_str().to_string())
        .collect::<Vec<_>>();
    paths.sort_by(|left, right| compare_path_components(left, right));
    let path_count = paths.len();
    InventoryReport {
        schema: "repograph.inventory.v1",
        repo_root: repo_root.to_string_lossy().into_owned(),
        listing: inventory.source().as_str().to_string(),
        status: if path_count == 0 {
            "empty-scope"
        } else {
            "established"
        },
        regular_files_only,
        paths_listed,
        dropped_by_stat: paths_listed - path_count,
        path_count,
        paths,
        unestablished: None,
    }
}

fn unestablished_report(repo_root: &Path, error: &InventoryError) -> InventoryReport {
    InventoryReport {
        schema: "repograph.inventory.v1",
        repo_root: repo_root.to_string_lossy().into_owned(),
        listing: "unestablished".to_string(),
        status: "unestablished",
        regular_files_only: false,
        paths_listed: 0,
        dropped_by_stat: 0,
        path_count: 0,
        paths: Vec::new(),
        unestablished: Some(error.to_string()),
    }
}

/// Stream to stdout rather than materializing the whole document: this report
/// carries every repository path (446 KB on this repo), and `to_string` builds
/// that twice before a byte reaches the consumer.
fn emit_report(report: &InventoryReport) -> bool {
    let stdout = std::io::stdout();
    let mut stdout = std::io::BufWriter::with_capacity(1 << 16, stdout.lock());
    if serde_json::to_writer(&mut stdout, report).is_err() {
        return false;
    }
    stdout.write_all(b"\n").is_ok() && stdout.flush().is_ok()
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
    let mut regular_files_only = false;
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
            "--regular-files-only" => regular_files_only = true,
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

    let inventory = match acquire(&repo_root, file_list.as_deref()) {
        Ok(inventory) => inventory,
        Err(error) => {
            let report = unestablished_report(&repo_root, &error);
            return if emit_report(&report) { 3 } else { 70 };
        }
    };
    let report = build_report(&repo_root, &inventory, regular_files_only);
    if emit_report(&report) {
        0
    } else {
        70
    }
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
    "repograph inventory [--repo-root PATH] [--file-list PATH] [--regular-files-only]"
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::path::Path;

    #[test]
    fn path_order_matches_pythons_pathlib_not_bytewise() {
        // The exact disagreement measured on this repo: as Paths, `a/b.py`
        // precedes `a-b/c.py`; as byte strings the order reverses.
        let inventory = FileInventory::from_file_list_bytes(
            b"a-b/c.py\0a/b.py\0skills-old/x.md\0skills/x.md\0",
        )
        .unwrap();
        let report = build_report(Path::new("."), &inventory, false);
        assert_eq!(
            report.paths,
            ["a/b.py", "a-b/c.py", "skills/x.md", "skills-old/x.md"]
        );
        // Control: a bytewise sort would have produced this instead.
        let mut bytewise = report.paths.clone();
        bytewise.sort();
        assert_ne!(report.paths, bytewise);
    }

    #[test]
    fn an_established_listing_of_zero_files_is_not_reported_as_inspected() {
        let inventory = FileInventory::from_file_list_bytes(b"").unwrap();
        let report = build_report(Path::new("."), &inventory, false);
        assert_eq!(report.status, "empty-scope");
        assert_eq!(report.path_count, 0);

        // Control: a real listing says `established`, so the status is not a
        // constant that would pass the assertion above whatever happened.
        let populated = FileInventory::from_file_list_bytes(b"a.py\0").unwrap();
        assert_eq!(
            build_report(Path::new("."), &populated, false).status,
            "established"
        );
    }

    #[test]
    fn rejects_parent_traversal() {
        let error = FileInventory::from_file_list_bytes(b"../outside.py\0").unwrap_err();
        assert!(error.to_string().contains("parent traversal"));
    }

    #[test]
    fn unavailable_git_is_a_typed_failure() {
        let error = acquire_with_git_program(
            Path::new("."),
            None,
            OsStr::new("repograph-command-that-does-not-exist"),
        )
        .unwrap_err();
        assert!(matches!(error, InventoryError::GitLaunch { .. }));
    }
}
