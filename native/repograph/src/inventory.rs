use std::ffi::OsStr;
use std::fmt;
use std::io;
use std::path::{Component, Path, PathBuf};
use std::process::Command;
use std::str;

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

#[cfg(test)]
mod tests {
    use super::*;
    use std::path::Path;

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
