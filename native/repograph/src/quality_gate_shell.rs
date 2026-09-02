//! Bounded shell token helpers shared by the quality carrier readers.

use std::collections::HashSet;

const QUALITY_AGGREGATE_LABELS: &[&str] = &[
    "run-quality-read-only",
    "run-quality-read-only-release",
    "run-quality-full",
    "run-quality-full-release",
];

pub(super) fn add_quality_aggregate_labels(labels: &mut Vec<super::QualityLabel>) {
    let existing = labels
        .iter()
        .map(|entry| entry.label.clone())
        .collect::<HashSet<_>>();
    labels.extend(
        QUALITY_AGGREGATE_LABELS
            .iter()
            .filter(|label| !existing.iter().any(|entry| entry.as_str() == **label))
            .map(|label| super::QualityLabel {
                label: (*label).to_string(),
                source: "run-quality.sh:aggregate".to_string(),
                line: None,
            }),
    );
}

pub(super) fn logical_lines(text: &str) -> Vec<(usize, String)> {
    let mut result = Vec::new();
    let mut pending = None::<String>;
    let mut pending_line = 0;
    for (index, raw) in text.lines().enumerate() {
        let line = index + 1;
        if pending.is_none() {
            pending = Some(raw.to_string());
            pending_line = line;
        } else if let Some(value) = pending.as_mut() {
            value.push(' ');
            value.push_str(raw.trim());
        }
        if pending
            .as_deref()
            .is_some_and(|value| value.ends_with('\\') && !value.trim_start().starts_with('#'))
        {
            if let Some(value) = pending.as_mut() {
                value.pop();
                while value.ends_with(char::is_whitespace) {
                    value.pop();
                }
            }
            continue;
        }
        if let Some(value) = pending.take() {
            result.push((pending_line, value));
        }
    }
    if let Some(value) = pending {
        result.push((pending_line, value));
    }
    result
}

pub(super) fn function_open_name(line: &str) -> Option<String> {
    let name = line.strip_suffix('{')?.trim_end();
    let name = name.strip_suffix(")")?;
    let name = name.strip_suffix('(')?;
    (!name.is_empty()
        && name.chars().enumerate().all(|(index, character)| {
            character == '_'
                || character.is_ascii_alphanumeric() && index > 0
                || character.is_ascii_alphabetic() && index == 0
        }))
    .then_some(name.to_string())
}

pub(super) fn queue_call<'a>(
    line: &'a str,
    functions: &[&'static str],
) -> Option<(&'static str, &'a str)> {
    let line = line.trim_start();
    functions.iter().find_map(|function| {
        let rest = line.strip_prefix(function)?;
        if !rest.chars().next().is_some_and(char::is_whitespace) {
            return None;
        }
        Some((*function, rest.trim_start()))
    })
}

pub(super) fn split_first_token(text: &str) -> Option<(&str, &str)> {
    let mut split = text.splitn(2, char::is_whitespace);
    let first = split.next()?.trim();
    let rest = split.next().unwrap_or("").trim();
    (!first.is_empty()).then_some((first, rest))
}

pub(super) fn literal_quality_label(token: &str) -> Option<String> {
    let value = token.strip_prefix('"')?.strip_suffix('"')?;
    is_quality_label(value).then_some(value.to_string())
}

pub(super) fn is_quality_label(value: &str) -> bool {
    !value.is_empty()
        && !value.contains('$')
        && value.chars().enumerate().all(|(index, character)| {
            (character.is_ascii_lowercase() || character.is_ascii_digit()) && index == 0
                || character.is_ascii_lowercase()
                || character.is_ascii_digit()
                || matches!(character, '.' | '_' | '-')
        })
}
