//! Minimal block-style reader for the declared quality gate list.
//!
//! The native crate deliberately does not grow a YAML dependency for this small
//! carrier surface. The reader accepts the schema's `phases`/`gates` rows and
//! only the `label` and block-list `command` fields needed by the carrier graph.

pub(super) struct DeclaredQualityGate {
    pub(super) label: String,
    pub(super) command: Vec<String>,
    pub(super) line: usize,
    pub(super) raw: String,
}

#[derive(Debug)]
struct QualityGateDraft {
    label: Option<String>,
    command: Vec<String>,
    command_pending: Option<(String, usize)>,
    command_seen: bool,
    command_indent: Option<usize>,
    command_item_indent: Option<usize>,
    command_mode: bool,
    line: usize,
    raw: Vec<String>,
}

pub(super) fn parse_quality_gate_list(text: &str) -> Result<Vec<DeclaredQualityGate>, String> {
    let mut gates = Vec::new();
    let mut in_gates = false;
    let mut gates_indent = 0;
    let mut row_indent = None;
    let mut current = None::<QualityGateDraft>;

    for (index, source_line) in text.lines().enumerate() {
        let line = index + 1;
        if source_line.contains('\t') {
            return Err(format!("line {line} uses tabs; block YAML requires spaces"));
        }
        let content = yaml_without_comment(source_line).trim_end();
        if content.trim().is_empty() {
            continue;
        }
        let indent = content.len() - content.trim_start().len();
        let trimmed = content.trim_start();

        if !in_gates {
            if trimmed == "gates:" {
                in_gates = true;
                gates_indent = indent;
                row_indent = None;
            }
            continue;
        }

        if indent < gates_indent || (indent == gates_indent && !trimmed.starts_with('-')) {
            finish_quality_gate(&mut current, &mut gates)?;
            in_gates = trimmed == "gates:";
            if in_gates {
                gates_indent = indent;
                row_indent = None;
            }
            continue;
        }

        let expected_row_indent = *row_indent.get_or_insert_with(|| {
            if trimmed.starts_with('-') {
                indent
            } else {
                gates_indent + 2
            }
        });
        if indent == expected_row_indent && trimmed.starts_with('-') {
            finish_quality_gate(&mut current, &mut gates)?;
            current = Some(start_quality_gate(trimmed, line, indent)?);
            continue;
        }
        let Some(draft) = current.as_mut() else {
            return Err(format!("line {line} is not a gate row under `gates:`"));
        };
        draft.raw.push(source_line.to_string());

        if draft.command_mode
            && indent >= draft.command_indent.unwrap_or(indent)
            && trimmed.starts_with('-')
        {
            let value = trimmed.strip_prefix('-').unwrap_or("").trim_start();
            draft.command_item_indent = Some(indent);
            if yaml_scalar_is_incomplete(value) {
                draft.command_pending = Some((value.to_string(), line));
            } else {
                draft.command.push(parse_yaml_scalar(value, line)?);
            }
            continue;
        }

        if draft.command_mode
            && indent
                > draft
                    .command_item_indent
                    .unwrap_or(draft.command_indent.unwrap_or(indent))
        {
            if let Some((pending, _pending_line)) = draft.command_pending.as_mut() {
                pending.push(' ');
                pending.push_str(trimmed);
                if !yaml_scalar_is_incomplete(pending) {
                    let (value, source_line) = draft.command_pending.take().unwrap();
                    draft
                        .command
                        .push(parse_yaml_scalar(&value, source_line.max(line))?);
                }
                continue;
            }
            if let Some(previous) = draft.command.last_mut() {
                previous.push(' ');
                previous.push_str(trimmed);
                continue;
            }
            return Err(format!(
                "line {line} has a command continuation without a list entry"
            ));
        }

        draft.command_mode = false;
        if trimmed.starts_with('-') {
            // A block list under a field other than `command` (for example
            // `condition: mode_in:`); the carrier graph reads only label and
            // command, so nested lists are skipped, not refused.
            continue;
        }
        let Some((key, value)) = yaml_mapping_entry(trimmed) else {
            return Err(format!("line {line} is not a mapping field in a gate row"));
        };
        match key {
            "label" => {
                if draft.label.is_some() {
                    return Err(format!("line {line} repeats the gate `label` field"));
                }
                let label = parse_yaml_scalar(value, line)?;
                if !super::quality_gate_shell::is_quality_label(&label) {
                    return Err(format!("line {line} has invalid gate label {label:?}"));
                }
                draft.label = Some(label);
            }
            "command" => {
                if draft.command_seen {
                    return Err(format!("line {line} repeats the gate `command` field"));
                }
                if !value.trim().is_empty() {
                    return Err(format!(
                        "line {line} uses an inline command; use a block-style YAML list"
                    ));
                }
                draft.command_seen = true;
                draft.command_indent = Some(indent);
                draft.command_mode = true;
            }
            _ => {}
        }
    }

    finish_quality_gate(&mut current, &mut gates)?;
    if gates.is_empty() {
        return Err("the gate list has no declared gates".to_string());
    }
    Ok(gates)
}

fn start_quality_gate(
    line: &str,
    source_line: usize,
    row_indent: usize,
) -> Result<QualityGateDraft, String> {
    let mapping = line
        .strip_prefix('-')
        .map(str::trim_start)
        .and_then(yaml_mapping_entry)
        .ok_or_else(|| format!("line {source_line} does not start a gate mapping"))?;
    let (key, value) = mapping;
    let mut draft = QualityGateDraft {
        label: None,
        command: Vec::new(),
        command_pending: None,
        command_seen: false,
        command_indent: None,
        command_item_indent: None,
        command_mode: false,
        line: source_line,
        raw: vec![line.to_string()],
    };
    match key {
        "label" => {
            let label = parse_yaml_scalar(value, source_line)?;
            if !super::quality_gate_shell::is_quality_label(&label) {
                return Err(format!(
                    "line {source_line} has invalid gate label {label:?}"
                ));
            }
            draft.label = Some(label);
        }
        "command" => {
            if !value.trim().is_empty() {
                return Err(format!(
                    "line {source_line} uses an inline command; use a block-style YAML list"
                ));
            }
            draft.command_seen = true;
            draft.command_indent = Some(row_indent);
            draft.command_mode = true;
        }
        _ => {}
    }
    Ok(draft)
}

fn finish_quality_gate(
    current: &mut Option<QualityGateDraft>,
    gates: &mut Vec<DeclaredQualityGate>,
) -> Result<(), String> {
    let Some(mut draft) = current.take() else {
        return Ok(());
    };
    if let Some((value, line)) = draft.command_pending.take() {
        draft.command.push(parse_yaml_scalar(&value, line)?);
    }
    let label = draft
        .label
        .ok_or_else(|| format!("line {} has no gate label", draft.line))?;
    if !draft.command_seen || draft.command.is_empty() {
        return Err(format!(
            "line {} gate {label:?} has no non-empty block-style command",
            draft.line
        ));
    }
    gates.push(DeclaredQualityGate {
        label,
        command: draft.command,
        line: draft.line,
        raw: draft.raw.join("\n"),
    });
    Ok(())
}

fn yaml_mapping_entry(value: &str) -> Option<(&str, &str)> {
    let separator = value.find(':')?;
    let key = value[..separator].trim();
    (!key.is_empty()).then_some((key, &value[separator + 1..]))
}

fn yaml_without_comment(value: &str) -> &str {
    let mut quote = None;
    let mut characters = value.char_indices().peekable();
    while let Some((index, character)) = characters.next() {
        match (quote, character) {
            (None, '\'' | '"') => quote = Some(character),
            (Some(active), character) if character == active => {
                if active == '\'' && characters.peek().is_some_and(|(_, next)| *next == '\'') {
                    characters.next();
                } else {
                    quote = None;
                }
            }
            (None, '#') if index == 0 || value[..index].ends_with(char::is_whitespace) => {
                return &value[..index];
            }
            _ => {}
        }
    }
    value
}

fn parse_yaml_scalar(value: &str, line: usize) -> Result<String, String> {
    let value = yaml_without_comment(value).trim();
    if value.is_empty() {
        return Err(format!("line {line} has an empty YAML scalar"));
    }
    if value.starts_with('[') || value.starts_with('{') {
        return Err(format!("line {line} uses an inline YAML collection"));
    }
    if value.starts_with('\'') {
        if !value.ends_with('\'') || value.len() < 2 {
            return Err(format!(
                "line {line} has an unterminated single-quoted scalar"
            ));
        }
        return Ok(value[1..value.len() - 1].replace("''", "'"));
    }
    if value.starts_with('"') {
        if !value.ends_with('"') || value.len() < 2 {
            return Err(format!(
                "line {line} has an unterminated double-quoted scalar"
            ));
        }
        let mut parsed = String::new();
        let mut characters = value[1..value.len() - 1].chars();
        while let Some(character) = characters.next() {
            if character != '\\' {
                parsed.push(character);
                continue;
            }
            let Some(escaped) = characters.next() else {
                return Err(format!("line {line} has a trailing YAML escape"));
            };
            parsed.push(match escaped {
                'n' => '\n',
                'r' => '\r',
                't' => '\t',
                '\\' => '\\',
                '"' => '"',
                other => {
                    return Err(format!(
                        "line {line} uses unsupported YAML escape \\{other}"
                    ));
                }
            });
        }
        return Ok(parsed);
    }
    Ok(value.to_string())
}

fn yaml_scalar_is_incomplete(value: &str) -> bool {
    let value = yaml_without_comment(value).trim();
    (value.starts_with('\'') && !value.ends_with('\''))
        || (value.starts_with('"') && !value.ends_with('"'))
}

pub(super) fn shell_quote(value: &str) -> String {
    if !value.is_empty()
        && value.chars().all(|character| {
            character.is_ascii_alphanumeric()
                || matches!(
                    character,
                    '/' | '.' | '_' | '-' | '+' | '=' | ':' | '@' | '%'
                )
        })
    {
        return value.to_string();
    }
    if value.starts_with('$')
        && value.chars().all(|character| {
            character.is_ascii_alphanumeric()
                || matches!(character, '$' | '{' | '}' | '[' | ']' | '@' | '_')
        })
    {
        return value.to_string();
    }
    format!("'{}'", value.replace('\'', "'\"'\"'"))
}
