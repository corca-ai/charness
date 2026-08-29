pub mod ast_utils;
pub mod edges;
pub mod export_safe;
pub mod graph;
pub mod graph_analyzer;
pub mod graph_carriers;
pub mod graph_components;
pub mod graph_imports;
pub mod graph_mirrors;
pub mod graph_model;
pub mod graph_queries;
pub mod graph_roles;
pub mod inventory;
pub mod parser;
pub mod plugin_refs;
pub mod selection;
pub mod standalone;
pub mod surfaces;
pub mod what_reads;

use std::ffi::OsStr;
use std::io::Write;
use std::path::{Path, PathBuf};

use inventory::{FileInventory, InventoryError};
use parser::{parse_file, FileParseResult, ParseStatus};
use serde::Serialize;

const DEFAULT_EXCLUDE_PREFIX: &str = "plugins/";

/// Machine-readable output for `parse-corpus`.
#[derive(Debug, Serialize)]
pub struct ParseCorpusReport {
    pub schema: &'static str,
    pub repo_root: String,
    pub listing: &'static str,
    pub files_total: usize,
    pub parsed: usize,
    pub failed: usize,
    pub files: Vec<FileParseResult>,
}

/// Run the command line interface and return its process exit code.
pub fn run<I>(args: I) -> i32
where
    I: IntoIterator<Item = String>,
{
    run_with_git_program(args, OsStr::new("git"))
}

fn run_with_git_program<I>(args: I, git_program: &OsStr) -> i32
where
    I: IntoIterator<Item = String>,
{
    let mut args = args.into_iter();
    let Some(command) = args.next() else {
        eprintln!("usage error: a subcommand is required\n{}", usage());
        return 2;
    };

    if command == "--help" || command == "-h" {
        println!("{}", usage());
        return 0;
    }
    let remaining = args.collect::<Vec<_>>();
    match command.as_str() {
        "parse-corpus" => run_parse_corpus(remaining, git_program),
        "inventory" => inventory::run(remaining),
        "export-safe" => export_safe::run(remaining),
        "match-surfaces" => surfaces::run(remaining),
        "standalone-targets" => standalone::run(remaining),
        "graph" => graph::run(remaining),
        "classify" => graph_queries::run_classify(remaining),
        "changed" => graph_queries::run_changed(remaining),
        "carriers" => graph_carriers::run(remaining),
        "components" => graph_components::run_components(remaining),
        "explain" => graph_components::run_explain(remaining),
        "plugin-refs" => plugin_refs::run(remaining),
        "what-reads" => what_reads::run(remaining),
        _ => {
            eprintln!("usage error: unknown subcommand {command:?}\n{}", usage());
            2
        }
    }
}

fn run_parse_corpus(args: Vec<String>, git_program: &OsStr) -> i32 {
    let args = args.into_iter();

    let options = match parse_corpus_options(args) {
        Ok(options) => options,
        Err(message) => {
            eprintln!("usage error: {message}\n{}", parse_usage());
            return 2;
        }
    };
    if options.help {
        println!("{}", parse_usage());
        return 0;
    }

    let inventory = match inventory::acquire_with_git_program(
        &options.repo_root,
        options.file_list.as_deref(),
        git_program,
    ) {
        Ok(inventory) => inventory,
        Err(error) => {
            report_inventory_error(error);
            return 3;
        }
    };

    let report = build_parse_corpus_report(&options.repo_root, &inventory, &options.excludes);
    let failed = report.failed > 0;
    let stdout = std::io::stdout();
    let mut stdout = stdout.lock();
    if let Err(error) = serde_json::to_writer(&mut stdout, &report)
        .and_then(|()| writeln!(stdout).map_err(serde_json::Error::io))
    {
        eprintln!("internal error: could not write JSON output: {error}");
        return 70;
    }
    if failed {
        3
    } else {
        0
    }
}

fn report_inventory_error(error: InventoryError) {
    eprintln!("{error}");
}

struct ParseCorpusOptions {
    repo_root: PathBuf,
    file_list: Option<PathBuf>,
    excludes: Vec<String>,
    help: bool,
}

fn parse_corpus_options<I>(args: I) -> Result<ParseCorpusOptions, String>
where
    I: Iterator<Item = String>,
{
    let mut repo_root = std::env::current_dir()
        .map_err(|error| format!("could not determine current directory: {error}"))?;
    let mut file_list = None;
    let mut excludes = Vec::new();
    let mut help = false;
    let mut args = args.peekable();

    while let Some(argument) = args.next() {
        match argument.as_str() {
            "--repo-root" => {
                repo_root = PathBuf::from(required_value(&mut args, "--repo-root")?);
            }
            "--file-list" => {
                file_list = Some(PathBuf::from(required_value(&mut args, "--file-list")?));
            }
            "--exclude-prefix" => {
                excludes.push(required_value(&mut args, "--exclude-prefix")?);
            }
            "--help" | "-h" => help = true,
            argument if argument.starts_with('-') => {
                return Err(format!("unknown option {argument:?}"));
            }
            argument => return Err(format!("unexpected positional argument {argument:?}")),
        }
    }

    if excludes.is_empty() {
        excludes.push(DEFAULT_EXCLUDE_PREFIX.to_string());
    }
    Ok(ParseCorpusOptions {
        repo_root,
        file_list,
        excludes,
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

fn build_parse_corpus_report(
    repo_root: &Path,
    inventory: &FileInventory,
    excludes: &[String],
) -> ParseCorpusReport {
    let mut paths: Vec<&str> = inventory
        .paths()
        .iter()
        .map(|path| path.as_str())
        .filter(|path| path.ends_with(".py"))
        .filter(|path| !excludes.iter().any(|prefix| path.starts_with(prefix)))
        .collect();
    paths.sort_by(|left, right| left.as_bytes().cmp(right.as_bytes()));

    let files: Vec<FileParseResult> = paths
        .into_iter()
        .map(|path| parse_file(repo_root, path))
        .collect();
    let parsed = files
        .iter()
        .filter(|file| file.status == ParseStatus::Parsed)
        .count();

    ParseCorpusReport {
        schema: "repograph.parse_corpus.v1",
        repo_root: repo_root.to_string_lossy().into_owned(),
        listing: inventory.source().as_str(),
        files_total: files.len(),
        parsed,
        failed: files.len() - parsed,
        files,
    }
}

fn usage() -> &'static str {
    "repograph <inventory|parse-corpus|export-safe|match-surfaces|standalone-targets|graph|classify|changed|carriers|components|explain|plugin-refs|what-reads> [options]"
}

fn parse_usage() -> &'static str {
    "repograph parse-corpus [--repo-root PATH] [--file-list PATH] [--exclude-prefix PREFIX]..."
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::ffi::OsStr;

    const FIXTURE_ROOT: &str = concat!(env!("CARGO_MANIFEST_DIR"), "/fixtures");

    #[test]
    fn fixture_file_list_reports_all_selected_files_and_typed_failures() {
        let bytes = include_bytes!("../fixtures/file-list.nul");
        let inventory = FileInventory::from_file_list_bytes(bytes).unwrap();
        let report = build_parse_corpus_report(
            Path::new(FIXTURE_ROOT),
            &inventory,
            &[DEFAULT_EXCLUDE_PREFIX.to_string()],
        );
        let expected_count = inventory
            .paths()
            .iter()
            .filter(|path| path.as_str().ends_with(".py"))
            .filter(|path| !path.as_str().starts_with(DEFAULT_EXCLUDE_PREFIX))
            .count();
        assert_eq!(report.files.len(), expected_count);
        assert_eq!(report.files_total, expected_count);

        let statuses: std::collections::BTreeMap<_, _> = report
            .files
            .iter()
            .map(|file| (file.path.as_str(), file.status))
            .collect();
        assert_eq!(statuses["syntax_error.py"], ParseStatus::ParseError);
        assert_eq!(statuses["non_utf8.py"], ParseStatus::Unreadable);
        assert_eq!(statuses["null_byte.py"], ParseStatus::ParseError);
        assert!(!statuses.contains_key("plugins/generated_mirror.py"));
    }

    #[test]
    fn missing_git_without_a_file_list_maps_to_exit_three() {
        let exit = run_with_git_program(
            [
                "parse-corpus".to_string(),
                "--repo-root".to_string(),
                FIXTURE_ROOT.to_string(),
            ],
            OsStr::new("repograph-command-that-does-not-exist"),
        );
        assert_eq!(exit, 3);
    }
}
