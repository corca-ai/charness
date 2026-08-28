use std::path::{Path, PathBuf};

use ruff_python_ast::visitor::{walk_expr, walk_stmt, Visitor};
use ruff_python_ast::{Expr, Stmt};
use ruff_text_size::Ranged;
use serde::Serialize;

use crate::ast_utils::{
    call_argument, is_div, is_export_rooted, is_supported_script_file, line_number, name_value,
    source_line, string_value,
};
use crate::inventory::FileInventory;
use crate::parser::{parse_module_file, FileParseResult};
use crate::selection::matching_files;

pub const EXPORT_SAFE_PATTERNS: &[&str] = &[
    "scripts/*.py",
    "skills/public/*/scripts/*.py",
    "skills/support/*/scripts/*.py",
    "skills/shared/scripts/*.py",
];

const FORBIDDEN_PREFIX: &str = "skills.public";

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct Violation {
    pub path: String,
    pub line: usize,
    pub kind: String,
    pub source: String,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct Unestablished {
    pub path: String,
    pub status: String,
    pub detail: String,
}

#[derive(Debug, Serialize)]
pub struct ExportSafeReport {
    pub schema: &'static str,
    pub repo_root: String,
    pub listing: String,
    pub files_total: usize,
    pub analyzed_files: usize,
    pub violations: Vec<Violation>,
    pub unestablished: Vec<Unestablished>,
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
    let mut file_list = None;
    let mut help = false;
    while let Some(argument) = args.next() {
        match argument.as_str() {
            "--repo-root" => match required_value(&mut args, "--repo-root") {
                Ok(value) => repo_root = PathBuf::from(value),
                Err(error) => return usage_error(&error),
            },
            "--file-list" => match required_value(&mut args, "--file-list") {
                Ok(value) => file_list = Some(PathBuf::from(value)),
                Err(error) => return usage_error(&error),
            },
            "--help" | "-h" => help = true,
            argument if argument.starts_with('-') => {
                return usage_error(&format!("unknown option {argument:?}"));
            }
            argument => {
                return usage_error(&format!("unexpected positional argument {argument:?}"))
            }
        }
    }
    if help {
        println!("{}", usage());
        return 0;
    }

    let repo_root = repo_root;
    let inventory = match crate::inventory::acquire(&repo_root, file_list.as_deref()) {
        Ok(inventory) => inventory,
        Err(error) => {
            let report = empty_report(&repo_root, Some(&error.to_string()));
            emit_report(&report);
            eprintln!("{error}");
            return 3;
        }
    };
    let (report, exit) = analyze(&repo_root, &inventory);
    emit_report(&report);
    exit
}

pub fn analyze(repo_root: &Path, inventory: &FileInventory) -> (ExportSafeReport, i32) {
    let targets = matching_files(repo_root, inventory, EXPORT_SAFE_PATTERNS);
    if targets.is_empty() {
        let report = ExportSafeReport {
            schema: "repograph.export_safe.v1",
            repo_root: repo_root.to_string_lossy().into_owned(),
            listing: inventory.source().as_str().to_string(),
            files_total: 0,
            analyzed_files: 0,
            violations: Vec::new(),
            unestablished: vec![Unestablished {
                path: "<scope>".to_string(),
                status: "zero-scope".to_string(),
                detail: "no export-safe Python files were selected".to_string(),
            }],
        };
        return (report, 3);
    }

    let mut violations = Vec::new();
    let mut unestablished = Vec::new();
    let mut analyzed_files = 0;
    for path in targets {
        let relative = path.as_str();
        match parse_module_file(repo_root, relative) {
            Ok(module) => {
                analyzed_files += 1;
                let source = match std::fs::read_to_string(path.on_disk(repo_root)) {
                    Ok(source) => source,
                    Err(error) => {
                        unestablished.push(Unestablished {
                            path: relative.to_string(),
                            status: "unreadable".to_string(),
                            detail: format!("unreadable: read-error: {error}"),
                        });
                        continue;
                    }
                };
                violations.extend(find_violations(relative, &source, &module));
            }
            Err(result) => unestablished.push(unestablished_from_parse(result)),
        }
    }
    violations.sort_by(|left, right| {
        left.path
            .cmp(&right.path)
            .then(left.line.cmp(&right.line))
            .then(left.kind.cmp(&right.kind))
            .then(left.source.cmp(&right.source))
    });
    unestablished.sort_by(|left, right| left.path.cmp(&right.path));

    let exit = if !unestablished.is_empty() {
        3
    } else if violations.is_empty() {
        0
    } else {
        1
    };
    (
        ExportSafeReport {
            schema: "repograph.export_safe.v1",
            repo_root: repo_root.to_string_lossy().into_owned(),
            listing: inventory.source().as_str().to_string(),
            files_total: analyzed_files + unestablished.len(),
            analyzed_files,
            violations,
            unestablished,
        },
        exit,
    )
}

fn unestablished_from_parse(result: FileParseResult) -> Unestablished {
    Unestablished {
        path: result.path,
        status: result.status.to_string(),
        detail: result.detail,
    }
}

fn find_violations(
    path: &str,
    source: &str,
    module: &ruff_python_ast::ModModule,
) -> Vec<Violation> {
    let probes_both_layouts = probes_both_layouts(module);
    let mut detector = Detector {
        path,
        source,
        probes_both_layouts,
        violations: Vec::new(),
    };
    detector.visit_body(&module.body);
    detector.violations
}

struct Detector<'a> {
    path: &'a str,
    source: &'a str,
    probes_both_layouts: bool,
    violations: Vec<Violation>,
}

impl Detector<'_> {
    fn violation(&self, expression: &impl Ranged, kind: &str) -> Violation {
        let line = line_number(self.source, expression);
        Violation {
            path: self.path.to_string(),
            line,
            kind: kind.to_string(),
            source: source_line(self.source, line),
        }
    }
}

impl<'a> Visitor<'a> for Detector<'a> {
    fn visit_stmt(&mut self, stmt: &'a Stmt) {
        match stmt {
            Stmt::ImportFrom(import) => {
                if import
                    .module
                    .as_ref()
                    .is_some_and(|module| is_forbidden(module.as_str()))
                {
                    self.violations
                        .push(self.violation(import, "forbidden-from-import"));
                }
            }
            Stmt::Import(import)
                if import
                    .names
                    .iter()
                    .any(|alias| is_forbidden(alias.name.as_str())) =>
            {
                self.violations
                    .push(self.violation(import, "forbidden-import"));
            }
            _ => {}
        }
        walk_stmt(self, stmt);
    }

    fn visit_expr(&mut self, expr: &'a Expr) {
        if !self.probes_both_layouts && forbidden_path_literal(expr).is_some() {
            self.violations
                .push(self.violation(expr, "forbidden-asset-path"));
        }
        if let Expr::Call(call) = expr {
            if forbidden_import_repo_module_call(call) {
                self.violations
                    .push(self.violation(call, "forbidden-import-repo-module"));
            }
        }
        walk_expr(self, expr);
    }
}

fn is_forbidden(module: &str) -> bool {
    module == FORBIDDEN_PREFIX || module.starts_with("skills.public.")
}

fn forbidden_import_repo_module_call(call: &ruff_python_ast::ExprCall) -> bool {
    if name_value(&call.func) != Some("import_repo_module") {
        return false;
    }
    let Some(script_file) = call_argument(call, 0, "script_file") else {
        return false;
    };
    let Some(module_name) = call_argument(call, 1, "module_name") else {
        return false;
    };
    if !is_supported_script_file(script_file) {
        return false;
    }
    string_value(module_name).is_some_and(is_forbidden)
}

fn forbidden_path_literal(expr: &Expr) -> Option<&str> {
    let Expr::BinOp(binop) = expr else {
        return None;
    };
    if !is_div(expr) || !is_export_rooted(expr) {
        return None;
    }
    if let Some(right) = string_value(&binop.right) {
        let normalized = right.replace('\\', "/");
        if normalized == "skills/public" || normalized.starts_with("skills/public/") {
            return Some(right);
        }
    }
    let Expr::BinOp(left) = binop.left.as_ref() else {
        return None;
    };
    if left.op == ruff_python_ast::Operator::Div
        && string_value(&left.right) == Some("skills")
        && string_value(&binop.right) == Some("public")
    {
        return Some("skills\" / \"public");
    }
    None
}

fn probes_both_layouts(module: &ruff_python_ast::ModModule) -> bool {
    let mut probe = LayoutProbe { found: false };
    probe.visit_body(&module.body);
    probe.found
}

struct LayoutProbe {
    found: bool,
}

impl<'a> Visitor<'a> for LayoutProbe {
    fn visit_expr(&mut self, expr: &'a Expr) {
        if let Expr::BinOp(binop) = expr {
            if is_export_rooted(expr)
                && is_div(expr)
                && string_value(&binop.right) != Some("public")
                && is_div(&binop.left)
                && string_value(match binop.left.as_ref() {
                    Expr::BinOp(left) => &left.right,
                    _ => unreachable!(),
                }) == Some("skills")
            {
                self.found = true;
            }
        }
        walk_expr(self, expr);
    }
}

fn empty_report(repo_root: &Path, error: Option<&str>) -> ExportSafeReport {
    ExportSafeReport {
        schema: "repograph.export_safe.v1",
        repo_root: repo_root.to_string_lossy().into_owned(),
        listing: "unestablished".to_string(),
        files_total: 0,
        analyzed_files: 0,
        violations: Vec::new(),
        unestablished: vec![Unestablished {
            path: "<inventory>".to_string(),
            status: "inventory".to_string(),
            detail: error
                .unwrap_or("file inventory was not established")
                .to_string(),
        }],
    }
}

fn emit_report(report: &ExportSafeReport) {
    match serde_json::to_string(report) {
        Ok(json) => println!("{json}"),
        Err(error) => {
            eprintln!("internal error: could not write JSON output: {error}");
        }
    }
}

fn required_value<I>(args: &mut I, flag: &str) -> Result<String, String>
where
    I: Iterator<Item = String>,
{
    match args.next() {
        Some(value) if !value.starts_with('-') => Ok(value),
        Some(value) => Err(format!("{flag} requires a value, got {value:?}")),
        None => Err(format!("{flag} requires a value")),
    }
}

fn usage_error(message: &str) -> i32 {
    eprintln!("usage error: {message}\n{}", usage());
    2
}

fn usage() -> &'static str {
    "repograph export-safe [--repo-root PATH] [--file-list PATH]"
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::inventory::FileInventory;

    #[test]
    fn reports_all_import_and_path_families() {
        let source = r#"from skills.public.foo import thing
import skills.public.bar
import_repo_module(__file__, "skills.public.baz")
broken = REPO_ROOT / "skills" / "public" / "asset"
joined = REPO_ROOT / "skills/public/joined"
"#;
        let module = crate::parser::parse_module_source("fixture.py", source).unwrap();
        let violations = find_violations("fixture.py", source, &module);
        assert_eq!(violations.len(), 5);
        assert_eq!(
            violations
                .iter()
                .map(|violation| violation.kind.as_str())
                .collect::<Vec<_>>(),
            [
                "forbidden-from-import",
                "forbidden-import",
                "forbidden-import-repo-module",
                "forbidden-asset-path",
                "forbidden-asset-path"
            ]
        );
    }

    #[test]
    fn both_layout_probe_suppresses_assets_but_not_imports() {
        let source = r#"from skills.public.foo import thing
broken = REPO_ROOT / "skills" / "public" / "asset"
working = REPO_ROOT / "skills" / "foo" / "asset"
"#;
        let module = crate::parser::parse_module_source("fixture.py", source).unwrap();
        let violations = find_violations("fixture.py", source, &module);
        assert_eq!(violations.len(), 1);
        assert_eq!(violations[0].kind, "forbidden-from-import");
    }

    #[test]
    fn malformed_in_scope_file_is_unestablished() {
        let bytes = b"scripts/broken.py\0";
        let inventory = FileInventory::from_file_list_bytes(bytes).unwrap();
        let root = Path::new(env!("CARGO_MANIFEST_DIR")).join("fixtures");
        let (report, exit) = analyze(&root, &inventory);
        assert_eq!(exit, 3);
        assert_eq!(
            report.unestablished[0].status,
            crate::parser::ParseStatus::ParseError.to_string()
        );
    }
}
