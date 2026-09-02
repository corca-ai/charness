use std::collections::HashSet;
use std::path::{Path, PathBuf};

use ruff_python_ast::visitor::{walk_expr, walk_stmt, Visitor};
use ruff_python_ast::{Expr, ModModule, Stmt};
use serde::Serialize;

use crate::ast_utils::{
    call_argument, is_supported_script_file, line_number, name_value, string_value,
};

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct ImportReference {
    pub module: String,
    pub imported: Option<String>,
    pub form: String,
    pub line: usize,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ResolvedImport {
    pub reference: ImportReference,
    pub target: String,
}

/// Extract the static forms owned by lane A. Calls and path insertions are
/// retained as typed observations; dynamic imports outside these forms are not
/// guessed.
pub fn extract_import_references(
    module: &ModModule,
    source: &str,
) -> (Vec<ImportReference>, Vec<String>) {
    let mut extractor = Extractor {
        source,
        imports: Vec::new(),
        inserted_paths: Vec::new(),
    };
    extractor.visit_body(&module.body);
    extractor.imports.sort_by(|left, right| {
        left.line
            .cmp(&right.line)
            .then(left.module.cmp(&right.module))
            .then(left.form.cmp(&right.form))
    });
    extractor.inserted_paths.sort();
    extractor.inserted_paths.dedup();
    (extractor.imports, extractor.inserted_paths)
}

pub fn resolve_imports(
    repo_root: &Path,
    source_path: &str,
    references: &[ImportReference],
    inserted_paths: &[String],
    snapshot_paths: &HashSet<String>,
) -> Vec<ResolvedImport> {
    let mut resolved = Vec::new();
    for reference in references {
        let mut roots = vec![PathBuf::from(".")];
        roots.push(PathBuf::from("scripts"));
        roots.push(PathBuf::from("tools"));
        roots.extend(inserted_paths.iter().map(PathBuf::from));
        if let Some(target) =
            resolve_reference(repo_root, source_path, reference, &roots, snapshot_paths)
        {
            resolved.push(ResolvedImport {
                reference: reference.clone(),
                target,
            });
        }
    }
    resolved.sort_by(|left, right| {
        left.target
            .cmp(&right.target)
            .then(left.reference.line.cmp(&right.reference.line))
            .then(left.reference.module.cmp(&right.reference.module))
    });
    resolved
}

fn resolve_reference(
    _repo_root: &Path,
    source_path: &str,
    reference: &ImportReference,
    roots: &[PathBuf],
    snapshot_paths: &HashSet<String>,
) -> Option<String> {
    let module = reference.module.replace('.', "/");
    let mut module_candidates = vec![module.clone()];
    if let Some(imported) = &reference.imported {
        module_candidates.insert(0, format!("{module}/{}", imported.replace('.', "/")));
    }

    // A sys.path insertion is allowed to point at a repository-relative
    // directory. The normal pytest roots remain in the list as well.
    for root in roots {
        for candidate in &module_candidates {
            let base = root.join(candidate);
            let file = format_path(base.with_extension("py"));
            if snapshot_paths.contains(&file) {
                return Some(file);
            }
            let package = format_path(base.join("__init__.py"));
            if snapshot_paths.contains(&package) {
                return Some(package);
            }
        }
    }

    // Relative source placement is useful for a small fixture package even
    // when its import is written in the usual absolute-looking form.
    if let Some(parent) = Path::new(source_path).parent() {
        let mut parent = parent.to_path_buf();
        while parent.components().next().is_some() {
            for candidate in &module_candidates {
                let file = format_path(parent.join(candidate).with_extension("py"));
                if snapshot_paths.contains(&file) {
                    return Some(file);
                }
            }
            if !parent.pop() {
                break;
            }
        }
    }
    None
}

fn format_path(path: PathBuf) -> String {
    path.to_string_lossy()
        .replace('\\', "/")
        .trim_start_matches("./")
        .to_string()
}

struct Extractor<'a> {
    source: &'a str,
    imports: Vec<ImportReference>,
    inserted_paths: Vec<String>,
}

impl<'a> Visitor<'a> for Extractor<'a> {
    fn visit_stmt(&mut self, stmt: &'a Stmt) {
        match stmt {
            Stmt::Import(import) => {
                for alias in &import.names {
                    self.imports.push(ImportReference {
                        module: alias.name.to_string(),
                        imported: None,
                        form: "import".to_string(),
                        line: line_number(self.source, import),
                    });
                }
            }
            Stmt::ImportFrom(import) => {
                if let Some(module) = &import.module {
                    for alias in &import.names {
                        self.imports.push(ImportReference {
                            module: module.to_string(),
                            imported: Some(alias.name.to_string()),
                            form: "from".to_string(),
                            line: line_number(self.source, import),
                        });
                    }
                }
            }
            _ => {}
        }
        walk_stmt(self, stmt);
    }

    fn visit_expr(&mut self, expr: &'a Expr) {
        if let Expr::Call(call) = expr {
            if is_sys_path_insert(&call.func) {
                if let Some(path) = call.arguments.args.get(1).and_then(path_literal) {
                    self.inserted_paths.push(path);
                }
            }
            if name_value(&call.func) == Some("import_repo_module")
                && call_argument(call, 0, "script_file").is_some_and(is_supported_script_file)
            {
                if let Some(module_name) =
                    call_argument(call, 1, "module_name").and_then(string_value)
                {
                    self.imports.push(ImportReference {
                        module: module_name.to_string(),
                        imported: None,
                        form: "import_repo_module".to_string(),
                        line: line_number(self.source, call),
                    });
                }
            }
        }
        walk_expr(self, expr);
    }
}

fn is_sys_path_insert(expr: &Expr) -> bool {
    let Expr::Attribute(insert) = expr else {
        return false;
    };
    if insert.attr.as_str() != "insert" {
        return false;
    }
    let Expr::Attribute(path) = insert.value.as_ref() else {
        return false;
    };
    path.attr.as_str() == "path" && name_value(path.value.as_ref()) == Some("sys")
}

fn path_literal(expr: &Expr) -> Option<String> {
    if let Some(value) = string_value(expr) {
        return Some(value.to_string());
    }
    let Expr::Call(call) = expr else {
        return None;
    };
    if name_value(&call.func) == Some("Path") {
        return call
            .arguments
            .args
            .first()
            .and_then(string_value)
            .map(str::to_string);
    }
    if name_value(&call.func) == Some("str") {
        return call.arguments.args.first().and_then(path_literal);
    }
    None
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn extracts_plain_from_dynamic_and_path_insert_forms() {
        let source = "import sys\nfrom pkg import mod\nsys.path.insert(0, \"pkg\")\nx = import_repo_module(__file__, \"pkg.mod\")\n";
        let module = crate::parser::parse_module_source("source.py", source).unwrap();
        let (imports, inserted) = extract_import_references(&module, source);
        assert_eq!(imports.len(), 3);
        assert_eq!(imports[0].form, "import");
        assert_eq!(imports[1].form, "from");
        assert_eq!(imports[2].form, "import_repo_module");
        assert_eq!(inserted, ["pkg"]);
    }

    #[test]
    fn resolves_pytest_root_and_scripts_pythonpath() {
        let refs = vec![ImportReference {
            module: "ordinary_imports".to_string(),
            imported: None,
            form: "import".to_string(),
            line: 1,
        }];
        let paths = ["ordinary_imports.py".to_string()].into_iter().collect();
        let resolved = resolve_imports(Path::new("."), "main.py", &refs, &[], &paths);
        assert_eq!(resolved[0].target, "ordinary_imports.py");
    }
}
