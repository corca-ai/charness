use ruff_python_ast::visitor::{walk_expr, Visitor};
use ruff_python_ast::{Expr, ModModule};
use serde::Serialize;

use crate::ast_utils::{call_argument, line_number, source_line, string_value};

/// A literal glob consumer found in parsed Python source.
#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct GlobConsumerEdge {
    pub line: usize,
    pub method: String,
    pub pattern: String,
    pub source: String,
}

/// Extract only the direct literal-pattern `glob`/`rglob` call edges.
pub fn extract_glob_consumer_edges(module: &ModModule, source: &str) -> Vec<GlobConsumerEdge> {
    let mut extractor = Extractor {
        source,
        edges: Vec::new(),
    };
    extractor.visit_body(&module.body);
    extractor
        .edges
        .sort_by_key(|edge| (edge.line, edge.method.clone()));
    extractor.edges
}

struct Extractor<'a> {
    source: &'a str,
    edges: Vec<GlobConsumerEdge>,
}

impl<'a> Visitor<'a> for Extractor<'a> {
    fn visit_expr(&mut self, expr: &'a Expr) {
        if let Expr::Call(call) = expr {
            let method = match call.func.as_ref() {
                Expr::Name(name) if name.id == "glob" || name.id == "rglob" => {
                    Some(name.id.as_str())
                }
                Expr::Attribute(attribute)
                    if attribute.attr.as_str() == "glob" || attribute.attr.as_str() == "rglob" =>
                {
                    Some(attribute.attr.as_str())
                }
                _ => None,
            };
            if let Some(method) = method {
                if let Some(pattern) = call_argument(call, 0, "pattern").and_then(string_value) {
                    let line = line_number(self.source, call);
                    self.edges.push(GlobConsumerEdge {
                        line,
                        method: method.to_string(),
                        pattern: pattern.to_string(),
                        source: source_line(self.source, line),
                    });
                }
            }
        }
        walk_expr(self, expr);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn extracts_named_and_path_glob_edges() {
        let source = "from glob import glob\nfrom pathlib import Path\nfiles = glob(\"pkg/*.py\")\nother = Path(\".\").rglob(\"*.py\")\n";
        let module = crate::parser::parse_module_source("glob.py", source).unwrap();
        let edges = extract_glob_consumer_edges(&module, source);
        assert_eq!(edges.len(), 2);
        assert_eq!(edges[0].method, "glob");
        assert_eq!(edges[0].pattern, "pkg/*.py");
        assert_eq!(edges[1].method, "rglob");
        assert_eq!(edges[1].pattern, "*.py");
    }
}
