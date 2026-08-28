use std::path::Path;

use crate::graph_model::{ConditionKind, Role, TopologyConfig, Unestablished};
use crate::surfaces::fnmatch;

/// Read the intentionally small frontmatter subset used for skill identity.
/// The first line must open a frontmatter block, and only a `name:` line in
/// that first block is meaningful; this is not a general YAML reader.
pub fn skill_frontmatter_name(contents: &str) -> Option<String> {
    let mut lines = contents.lines();
    if lines.next().map(str::trim) != Some("---") {
        return None;
    }
    let mut name = None;
    for line in lines {
        let trimmed = line.trim();
        if trimmed == "---" {
            return name;
        }
        if let Some(value) = trimmed.strip_prefix("name:") {
            let value = value.trim();
            if !value.is_empty() && !value.contains('#') {
                name = Some(value.trim_matches(['\"', '\'']).to_string());
            }
        }
    }
    None
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct RoleResolution {
    pub role: Role,
    pub condition: Option<Unestablished>,
}

/// Resolve one path using D1a's ordered role table.
pub fn classify_role(
    path: &str,
    package_member: bool,
    generated_surface: bool,
    config: &TopologyConfig,
) -> RoleResolution {
    let explicit_matches = [
        ("topology.test_globs", &config.test_globs, Role::Test),
        (
            "topology.production_globs",
            &config.production_globs,
            Role::Production,
        ),
        (
            "topology.generated_globs",
            &config.generated_globs,
            Role::Generated,
        ),
    ]
    .into_iter()
    .filter(|(_, patterns, _)| patterns.iter().any(|pattern| fnmatch(path, pattern)))
    .map(|(name, _, role)| (name.to_string(), role))
    .collect::<Vec<_>>();

    if explicit_matches.len() > 1 {
        let rules = explicit_matches
            .iter()
            .map(|(name, _)| name.clone())
            .collect::<Vec<_>>();
        return unestablished_role(
            path,
            ConditionKind::RoleConflict,
            format!("role conflict: {} matched", rules.join(" and ")),
            rules,
        );
    }
    if let Some((_, role)) = explicit_matches.first() {
        return established(*role);
    }

    if generated_surface {
        return established(Role::Generated);
    }

    let convention_matches = language_convention_matches(path);
    if !convention_matches.is_empty() {
        return established(Role::Test);
    }

    if is_document(path) {
        return established(Role::Doc);
    }

    if package_member {
        return established(Role::Production);
    }

    unestablished_role(
        path,
        ConditionKind::RoleUnestablished,
        "no D1a role rule applies".to_string(),
        Vec::new(),
    )
}

fn established(role: Role) -> RoleResolution {
    RoleResolution {
        role,
        condition: None,
    }
}

fn unestablished_role(
    path: &str,
    kind: ConditionKind,
    detail: String,
    rules: Vec<String>,
) -> RoleResolution {
    RoleResolution {
        role: Role::Unestablished,
        condition: Some(Unestablished {
            kind,
            subject: path.to_string(),
            detail,
            rules,
        }),
    }
}

fn is_document(path: &str) -> bool {
    Path::new(path)
        .extension()
        .is_some_and(|extension| extension == "md")
}

fn language_convention_matches(path: &str) -> Vec<&'static str> {
    let path_obj = Path::new(path);
    let file_name = path_obj
        .file_name()
        .and_then(|name| name.to_str())
        .unwrap_or("");
    let mut matches = Vec::new();

    if path.starts_with("tests/") {
        matches.push("python-testpaths");
    }
    if file_name.starts_with("test_") && file_name.ends_with(".py") {
        matches.push("python-test-name");
    }
    if file_name.ends_with("_test.py") || file_name == "conftest.py" {
        matches.push("python-test-name");
    }
    if file_name.ends_with("_test.go") {
        matches.push("go-test-name");
    }
    if path_obj
        .components()
        .any(|component| component.as_os_str() == "testdata")
    {
        matches.push("go-testdata");
    }
    if path_obj
        .components()
        .any(|component| component.as_os_str() == "__tests__")
    {
        matches.push("js-tests-directory");
    }
    if is_js_or_ts_test_name(file_name) {
        matches.push("js-test-name");
    }
    matches
}

fn is_js_or_ts_test_name(file_name: &str) -> bool {
    let extensions = [".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"];
    extensions.iter().any(|extension| {
        let test_marker = format!(".test{extension}");
        let spec_marker = format!(".spec{extension}");
        file_name.ends_with(&test_marker) || file_name.ends_with(&spec_marker)
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::graph_model::TopologyDocument;

    fn config(
        test_globs: &[&str],
        production_globs: &[&str],
        generated_globs: &[&str],
    ) -> TopologyConfig {
        TopologyConfig {
            test_globs: test_globs
                .iter()
                .map(|value| (*value).to_string())
                .collect(),
            production_globs: production_globs
                .iter()
                .map(|value| (*value).to_string())
                .collect(),
            generated_globs: generated_globs
                .iter()
                .map(|value| (*value).to_string())
                .collect(),
        }
    }

    #[test]
    fn every_ordered_role_rule_is_represented() {
        assert_eq!(
            classify_role("src/unit.py", true, false, &config(&["src/*.py"], &[], &[])).role,
            Role::Test
        );
        assert_eq!(
            classify_role("src/unit.py", true, false, &config(&[], &["src/*.py"], &[])).role,
            Role::Production
        );
        assert_eq!(
            classify_role("src/out.py", true, false, &config(&[], &[], &["src/*.py"])).role,
            Role::Generated
        );
        assert_eq!(
            classify_role(
                "tests/test_unit.py",
                true,
                false,
                &TopologyConfig::default()
            )
            .role,
            Role::Test
        );
        assert_eq!(
            classify_role("scripts/x.go", true, false, &TopologyConfig::default()).role,
            Role::Production
        );
        assert_eq!(
            classify_role("scripts/x_test.go", true, false, &TopologyConfig::default()).role,
            Role::Test
        );
        assert_eq!(
            classify_role(
                "scripts/testdata/sample.txt",
                true,
                false,
                &TopologyConfig::default()
            )
            .role,
            Role::Test
        );
        assert_eq!(
            classify_role(
                "src/widget.test.ts",
                true,
                false,
                &TopologyConfig::default()
            )
            .role,
            Role::Test
        );
        assert_eq!(
            classify_role(
                "src/__tests__/widget.ts",
                true,
                false,
                &TopologyConfig::default()
            )
            .role,
            Role::Test
        );
        assert_eq!(
            classify_role("docs/guide.md", false, false, &TopologyConfig::default()).role,
            Role::Doc
        );
        assert_eq!(
            classify_role("scripts/tool.py", true, false, &TopologyConfig::default()).role,
            Role::Production
        );
        assert_eq!(
            classify_role(
                "unknown/data.toml",
                false,
                false,
                &TopologyConfig::default()
            )
            .role,
            Role::Unestablished
        );
    }

    #[test]
    fn earlier_explicit_rule_wins_over_later_conventions() {
        assert_eq!(
            classify_role(
                "tests/test_generated.py",
                true,
                false,
                &config(&[], &[], &["tests/*.py"]),
            )
            .role,
            Role::Generated
        );
        assert_eq!(
            classify_role("plugins/test.js", true, true, &TopologyConfig::default()).role,
            Role::Generated
        );
    }

    #[test]
    fn explicit_conflict_names_both_rules() {
        let resolution = classify_role(
            "src/conflict.py",
            true,
            false,
            &config(&["src/*.py"], &["src/*.py"], &[]),
        );
        let condition = resolution.condition.unwrap();
        assert_eq!(resolution.role, Role::Unestablished);
        assert_eq!(condition.kind, ConditionKind::RoleConflict);
        assert_eq!(
            condition.rules,
            ["topology.test_globs", "topology.production_globs"]
        );
    }

    #[test]
    fn frontmatter_requires_the_closing_delimiter() {
        assert_eq!(skill_frontmatter_name("---\nname: incomplete\n"), None);
        assert_eq!(
            skill_frontmatter_name("---\nname: complete\n---\n# Skill\n"),
            Some("complete".to_string())
        );
    }

    #[test]
    fn topology_inputs_reject_unknown_fields() {
        let error = serde_json::from_str::<TopologyDocument>(
            r#"{"topology":{"test_globs":[],"unexpected":[]}}"#,
        )
        .unwrap_err();
        assert!(error.to_string().contains("unknown field"));
    }
}
