use std::any::Any;
use std::fmt;
use std::panic::{catch_unwind, AssertUnwindSafe};
use std::path::Path;

use ruff_python_ast::{PySourceType, PythonVersion};
use ruff_python_parser::{ParseError, ParseOptions, UnsupportedSyntaxError};
use serde::Serialize;

/// The typed outcome of parsing one selected file.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize)]
#[serde(rename_all = "kebab-case")]
pub enum ParseStatus {
    Parsed,
    ParseError,
    UnsupportedSyntax,
    Panicked,
    Unreadable,
}

/// A path and its typed parser result.
#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct FileParseResult {
    pub path: String,
    pub status: ParseStatus,
    pub detail: String,
}

pub(crate) enum ParseObservation {
    Parsed,
    ParseError { detail: String },
    UnsupportedSyntax { detail: String },
}

/// Read and parse one repository-relative file.
pub fn parse_file(repo_root: &Path, path: &str) -> FileParseResult {
    let on_disk = repo_root.join(path);
    let bytes = match std::fs::read(&on_disk) {
        Ok(bytes) => bytes,
        Err(error) => {
            return FileParseResult {
                path: path.to_string(),
                status: ParseStatus::Unreadable,
                detail: format!("unreadable: read-error: {error}"),
            };
        }
    };

    let source = match String::from_utf8(bytes) {
        Ok(source) => source,
        Err(error) => {
            return FileParseResult {
                path: path.to_string(),
                status: ParseStatus::Unreadable,
                detail: format!(
                    "unreadable: invalid-utf8 at byte {}",
                    error.utf8_error().valid_up_to()
                ),
            };
        }
    };

    parse_source(path, &source)
}

/// Parse UTF-8 Python source with a panic boundary around the Ruff parser.
pub fn parse_source(path: &str, source: &str) -> FileParseResult {
    parse_source_with(path, source, parse_with_ruff)
}

pub(crate) fn parse_source_with<F>(path: &str, source: &str, parser: F) -> FileParseResult
where
    F: FnOnce(&str) -> ParseObservation,
{
    let result = catch_unwind(AssertUnwindSafe(|| parser(source)));
    match result {
        Ok(ParseObservation::Parsed) => FileParseResult {
            path: path.to_string(),
            status: ParseStatus::Parsed,
            detail: "ok".to_string(),
        },
        Ok(ParseObservation::ParseError { detail }) => FileParseResult {
            path: path.to_string(),
            status: ParseStatus::ParseError,
            detail,
        },
        Ok(ParseObservation::UnsupportedSyntax { detail }) => FileParseResult {
            path: path.to_string(),
            status: ParseStatus::UnsupportedSyntax,
            detail,
        },
        Err(payload) => FileParseResult {
            path: path.to_string(),
            status: ParseStatus::Panicked,
            detail: format!("panicked: {}", panic_payload(&payload)),
        },
    }
}

fn parse_with_ruff(source: &str) -> ParseObservation {
    let options =
        ParseOptions::from(PySourceType::Python).with_target_version(PythonVersion::PY310);
    let parsed = ruff_python_parser::parse_unchecked(source, options)
        .try_into_module()
        .expect("Python source options must produce a module");

    if let Some(error) = parsed.errors().first() {
        return ParseObservation::ParseError {
            detail: parse_error_detail(error, source),
        };
    }
    if let Some(error) = parsed.unsupported_syntax_errors().first() {
        return ParseObservation::UnsupportedSyntax {
            detail: unsupported_syntax_detail(error, source),
        };
    }
    ParseObservation::Parsed
}

fn parse_error_detail(error: &ParseError, source: &str) -> String {
    let offset = error.location.start().to_usize();
    format!(
        "parse-error: {} at {}",
        one_line(error.to_string()),
        source_location(source, offset)
    )
}

fn unsupported_syntax_detail(error: &UnsupportedSyntaxError, source: &str) -> String {
    let offset = error.range.start().to_usize();
    format!(
        "unsupported-syntax: {:?} at {}",
        error.kind,
        source_location(source, offset)
    )
}

fn source_location(source: &str, byte_offset: usize) -> String {
    let offset = byte_offset.min(source.len());
    let line = source[..offset]
        .bytes()
        .filter(|byte| *byte == b'\n')
        .count()
        + 1;
    let line_start = source[..offset].rfind('\n').map_or(0, |index| index + 1);
    let column = source[line_start..offset].chars().count() + 1;
    format!("line {line}, column {column}, byte {offset}")
}

fn one_line(value: String) -> String {
    value
        .chars()
        .map(|character| match character {
            character if character.is_control() => ' ',
            character => character,
        })
        .collect()
}

fn panic_payload(payload: &Box<dyn Any + Send>) -> String {
    if let Some(message) = payload.downcast_ref::<&str>() {
        return one_line((*message).to_string());
    }
    if let Some(message) = payload.downcast_ref::<String>() {
        return one_line(message.clone());
    }
    "non-string panic payload".to_string()
}

impl fmt::Display for ParseStatus {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let value = match self {
            Self::Parsed => "parsed",
            Self::ParseError => "parse-error",
            Self::UnsupportedSyntax => "unsupported-syntax",
            Self::Panicked => "panicked",
            Self::Unreadable => "unreadable",
        };
        f.write_str(value)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parser_panic_becomes_a_file_result() {
        let result = parse_source_with("panic.py", "", |_source| panic!("synthetic parser panic"));
        assert_eq!(result.status, ParseStatus::Panicked);
        assert_eq!(result.detail, "panicked: synthetic parser panic");
    }

    #[test]
    fn syntax_error_has_a_location() {
        let result = parse_source("broken.py", "def broken(:\n");
        assert_eq!(result.status, ParseStatus::ParseError);
        assert!(result.detail.contains("line 1"));
    }

    #[test]
    fn syntax_for_a_newer_target_is_typed_as_unsupported() {
        let result = parse_source("type_parameters.py", "class Box[T]:\n    pass\n");
        assert_eq!(result.status, ParseStatus::UnsupportedSyntax);
        assert!(result.detail.starts_with("unsupported-syntax:"));
    }
}
