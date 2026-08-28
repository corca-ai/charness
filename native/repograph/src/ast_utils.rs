use ruff_python_ast::{Expr, Operator};
use ruff_text_size::Ranged;

pub fn string_value(expr: &Expr) -> Option<&str> {
    match expr {
        Expr::StringLiteral(literal) => Some(literal.value.to_str()),
        _ => None,
    }
}

pub fn name_value(expr: &Expr) -> Option<&str> {
    match expr {
        Expr::Name(name) => Some(name.id.as_str()),
        _ => None,
    }
}

pub fn is_div(expr: &Expr) -> bool {
    matches!(expr, Expr::BinOp(binop) if binop.op == Operator::Div)
}

pub fn binop_base(mut expr: &Expr) -> &Expr {
    while let Expr::BinOp(binop) = expr {
        if binop.op != Operator::Div {
            break;
        }
        expr = &binop.left;
    }
    expr
}

pub fn chain_root_name(mut expr: &Expr) -> &Expr {
    loop {
        match expr {
            Expr::Call(call) => expr = &call.func,
            Expr::Attribute(attribute) => expr = &attribute.value,
            _ => return expr,
        }
    }
}

pub fn is_export_rooted(expr: &Expr) -> bool {
    matches!(chain_root_name(binop_base(expr)), Expr::Name(name) if name.id == "REPO_ROOT")
}

pub fn call_argument<'a>(
    call: &'a ruff_python_ast::ExprCall,
    position: usize,
    keyword: &str,
) -> Option<&'a Expr> {
    if call.arguments.args.len() > position {
        return call.arguments.args.get(position);
    }
    call.arguments
        .keywords
        .iter()
        .find(|item| item.arg.as_ref().is_some_and(|arg| arg == keyword))
        .map(|item| &item.value)
}

pub fn is_supported_script_file(expr: &Expr) -> bool {
    if name_value(expr) == Some("__file__") {
        return true;
    }
    let Expr::Call(call) = expr else {
        return false;
    };
    name_value(&call.func) == Some("Path")
        && call.arguments.args.len() == 1
        && call.arguments.keywords.is_empty()
        && call
            .arguments
            .args
            .first()
            .is_some_and(|arg| name_value(arg) == Some("__file__"))
}

pub fn line_number(source: &str, expr: &impl Ranged) -> usize {
    let offset = expr.range().start().to_usize().min(source.len());
    source[..offset]
        .bytes()
        .filter(|byte| *byte == b'\n')
        .count()
        + 1
}

pub fn source_line(source: &str, line: usize) -> String {
    source
        .split('\n')
        .nth(line.saturating_sub(1))
        .unwrap_or_default()
        .trim_end_matches('\r')
        .to_string()
}
