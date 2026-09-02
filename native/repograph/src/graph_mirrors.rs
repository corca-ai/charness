use std::collections::HashSet;

use crate::graph_model::{ConditionKind, MirrorTransform, Unestablished};

/// The source-to-destination operations in `packaging_lib.export_plugin_tree`.
/// Keep one row per operation: the path collapse, filters, injections, and
/// rewrites are intentionally not represented as one generic copy rule.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct MirrorRuleSpec {
    pub id: &'static str,
    pub source: &'static str,
    pub destination: &'static str,
    pub transform: MirrorTransform,
    pub content_transformed: bool,
    pub subtractive: bool,
}

pub const MIRROR_RULES: &[MirrorRuleSpec] = &[
    MirrorRuleSpec {
        id: "readme-rewrite",
        source: "README.md",
        destination: "plugins/charness/README.md",
        transform: MirrorTransform::ContentTransformed,
        content_transformed: true,
        subtractive: false,
    },
    MirrorRuleSpec {
        id: "public-skill-collapse",
        source: "skills/public/*",
        destination: "plugins/charness/skills/*",
        transform: MirrorTransform::PathCollapsed,
        content_transformed: false,
        subtractive: false,
    },
    MirrorRuleSpec {
        id: "shared-verbatim",
        source: "skills/shared/*",
        destination: "plugins/charness/shared/*",
        transform: MirrorTransform::Verbatim,
        content_transformed: false,
        subtractive: false,
    },
    MirrorRuleSpec {
        id: "claude-agents-relocation",
        source: ".claude/agents/*",
        destination: "plugins/charness/agents/*",
        transform: MirrorTransform::Relocated,
        content_transformed: false,
        subtractive: false,
    },
    MirrorRuleSpec {
        id: "support-filtered-copy",
        source: "skills/support/*",
        destination: "plugins/charness/support/*",
        transform: MirrorTransform::FilteredCopy,
        content_transformed: true,
        subtractive: true,
    },
    MirrorRuleSpec {
        id: "profiles-copy",
        source: "profiles/*",
        destination: "plugins/charness/profiles/*",
        transform: MirrorTransform::Verbatim,
        content_transformed: false,
        subtractive: false,
    },
    MirrorRuleSpec {
        id: "presets-copy",
        source: "presets/*",
        destination: "plugins/charness/presets/*",
        transform: MirrorTransform::Verbatim,
        content_transformed: false,
        subtractive: false,
    },
    MirrorRuleSpec {
        id: "integrations-tools-copy",
        source: "integrations/tools/*",
        destination: "plugins/charness/integrations/tools/*",
        transform: MirrorTransform::Verbatim,
        content_transformed: false,
        subtractive: false,
    },
    MirrorRuleSpec {
        id: "lock-surface",
        source: "integrations/locks/{.gitkeep,README.md,lock.schema.json}",
        destination: "plugins/charness/integrations/locks/{.gitkeep,README.md,lock.schema.json}",
        transform: MirrorTransform::LockSurface,
        content_transformed: false,
        subtractive: true,
    },
    MirrorRuleSpec {
        id: "worktree-relocation",
        source: "integrations/worktree/*",
        destination: "plugins/charness/integrations/worktree/*",
        transform: MirrorTransform::Relocated,
        content_transformed: false,
        subtractive: false,
    },
    MirrorRuleSpec {
        id: "scripts-copy",
        source: "scripts/*",
        destination: "plugins/charness/scripts/*",
        transform: MirrorTransform::Verbatim,
        content_transformed: false,
        subtractive: false,
    },
    MirrorRuleSpec {
        id: "runtime-bootstrap-shim",
        source: "runtime_bootstrap.py",
        destination: "plugins/charness/runtime_bootstrap.py",
        transform: MirrorTransform::Injected,
        content_transformed: false,
        subtractive: false,
    },
    MirrorRuleSpec {
        id: "yaml-output-shim",
        source: "yaml_output.py",
        destination: "plugins/charness/yaml_output.py",
        transform: MirrorTransform::Injected,
        content_transformed: false,
        subtractive: false,
    },
    MirrorRuleSpec {
        id: "skill-runtime-bootstrap-shim",
        source: "skill_runtime_bootstrap.py",
        destination: "plugins/charness/skill_runtime_bootstrap.py",
        transform: MirrorTransform::Injected,
        content_transformed: false,
        subtractive: false,
    },
    MirrorRuleSpec {
        id: "bootstrap-dependency-contract",
        source: "packaging/{bootstrap-python.json,bootstrap-requirements.txt}",
        destination:
            "plugins/charness/packaging/{bootstrap-python.json,bootstrap-requirements.txt}",
        transform: MirrorTransform::Injected,
        content_transformed: false,
        subtractive: true,
    },
    MirrorRuleSpec {
        id: "manifest-generated-outputs",
        source: "<no file source>",
        destination: ".claude-plugin/*, .codex-plugin/*, marketplace manifests",
        transform: MirrorTransform::ManifestGenerated,
        content_transformed: false,
        subtractive: false,
    },
];

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct MirrorManifest {
    pub public_skills_dir: String,
    pub support_skills_dir: String,
    pub profiles_dir: String,
    pub presets_dir: String,
    pub integrations_dir: String,
    pub plugin_root: String,
    pub claude_plugin_manifest: String,
    pub codex_plugin_manifest: String,
    pub claude_marketplace_manifest: String,
    pub codex_marketplace_manifest: String,
    pub upstream_consumed_support_ids: HashSet<String>,
}

impl Default for MirrorManifest {
    fn default() -> Self {
        Self {
            public_skills_dir: "skills/public".to_string(),
            support_skills_dir: "skills/support".to_string(),
            profiles_dir: "profiles".to_string(),
            presets_dir: "presets".to_string(),
            integrations_dir: "integrations/tools".to_string(),
            plugin_root: "plugins/charness".to_string(),
            claude_plugin_manifest: "plugins/charness/.claude-plugin/plugin.json".to_string(),
            codex_plugin_manifest: "plugins/charness/.codex-plugin/plugin.json".to_string(),
            claude_marketplace_manifest: ".claude-plugin/marketplace.json".to_string(),
            codex_marketplace_manifest: ".agents/plugins/marketplace.json".to_string(),
            upstream_consumed_support_ids: HashSet::new(),
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct MirrorPair {
    pub rule_id: String,
    pub source: Option<String>,
    pub destination: String,
    pub transform: MirrorTransform,
    pub content_transformed: bool,
    pub destination_in_snapshot: bool,
}

#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct MirrorDerivation {
    pub pairs: Vec<MirrorPair>,
    pub destinations: Vec<String>,
    pub unestablished: Vec<Unestablished>,
}

pub fn derive_mirrors(
    selected_paths: &[String],
    snapshot_paths: &HashSet<String>,
    manifest: &MirrorManifest,
) -> MirrorDerivation {
    let mut pairs = Vec::new();
    let mut destinations = HashSet::new();
    let mut unestablished = Vec::new();

    let mut paths = selected_paths.to_vec();
    paths.sort();
    paths.dedup();
    for path in paths {
        if let Some(pair) = map_source(&path, manifest) {
            let mut pair = pair;
            pair.destination_in_snapshot = snapshot_paths.contains(&pair.destination);
            destinations.insert(pair.destination.clone());
            pairs.push(pair);
        } else if is_candidate_source(&path, manifest)
            && !is_intentionally_excluded(&path, manifest)
        {
            unestablished.push(unmodeled(
                &path,
                "no enumerated export rule covers this source",
            ));
        }
    }

    let generated = [
        manifest.claude_plugin_manifest.clone(),
        manifest.codex_plugin_manifest.clone(),
        manifest.claude_marketplace_manifest.clone(),
        manifest.codex_marketplace_manifest.clone(),
    ];
    for destination in generated {
        destinations.insert(destination.clone());
        pairs.push(MirrorPair {
            rule_id: "manifest-generated-outputs".to_string(),
            source: None,
            destination: destination.clone(),
            transform: MirrorTransform::ManifestGenerated,
            content_transformed: false,
            destination_in_snapshot: snapshot_paths.contains(&destination),
        });
    }

    let mut destinations_vec = destinations.into_iter().collect::<Vec<_>>();
    destinations_vec.sort();
    for destination in snapshot_paths {
        if destination.starts_with(&(manifest.plugin_root.clone() + "/"))
            && !destinations_vec.iter().any(|known| known == destination)
        {
            unestablished.push(unmodeled(
                destination,
                "destination is not produced by the enumerated packaging rule table",
            ));
        }
    }

    pairs.sort_by(|left, right| {
        left.destination
            .cmp(&right.destination)
            .then(left.rule_id.cmp(&right.rule_id))
            .then(left.source.cmp(&right.source))
    });
    unestablished.sort_by(|left, right| left.subject.cmp(&right.subject));
    MirrorDerivation {
        pairs,
        destinations: destinations_vec,
        unestablished,
    }
}

fn map_source(path: &str, manifest: &MirrorManifest) -> Option<MirrorPair> {
    let plugin = &manifest.plugin_root;
    let mapped =
        |rule_id: &str, source: Option<&str>, destination: String, transform, content| MirrorPair {
            rule_id: rule_id.to_string(),
            source: source.map(str::to_string),
            destination: destination.clone(),
            transform,
            content_transformed: content,
            destination_in_snapshot: false,
        };

    if path == "README.md" {
        return Some(mapped(
            "readme-rewrite",
            Some(path),
            format!("{plugin}/README.md"),
            MirrorTransform::ContentTransformed,
            true,
        ));
    }
    if let Some(rest) = path.strip_prefix(&(manifest.public_skills_dir.clone() + "/")) {
        if is_directory_member(rest) {
            return Some(mapped(
                "public-skill-collapse",
                Some(path),
                format!("{plugin}/skills/{rest}"),
                MirrorTransform::PathCollapsed,
                false,
            ));
        }
    }
    if let Some(rest) = path.strip_prefix("skills/shared/") {
        return Some(mapped(
            "shared-verbatim",
            Some(path),
            format!("{plugin}/shared/{rest}"),
            MirrorTransform::Verbatim,
            false,
        ));
    }
    if let Some(rest) = path.strip_prefix(".claude/agents/") {
        return Some(mapped(
            "claude-agents-relocation",
            Some(path),
            format!("{plugin}/agents/{rest}"),
            MirrorTransform::Relocated,
            false,
        ));
    }
    if let Some(rest) = path.strip_prefix(&(manifest.support_skills_dir.clone() + "/")) {
        let mut components = rest.splitn(2, '/');
        let skill_id = components.next().unwrap_or_default();
        if skill_id == "generated" || manifest.upstream_consumed_support_ids.contains(skill_id) {
            return None;
        }
        let content = rest.ends_with("/capability.json") || rest == "capability.json";
        return Some(mapped(
            "support-filtered-copy",
            Some(path),
            format!("{plugin}/support/{rest}"),
            if content {
                MirrorTransform::ContentTransformed
            } else {
                MirrorTransform::FilteredCopy
            },
            content,
        ));
    }
    for (rule_id, source_root, destination_root) in [
        ("profiles-copy", manifest.profiles_dir.as_str(), "profiles"),
        ("presets-copy", manifest.presets_dir.as_str(), "presets"),
        (
            "integrations-tools-copy",
            manifest.integrations_dir.as_str(),
            "integrations/tools",
        ),
    ] {
        if let Some(rest) = path.strip_prefix(&(source_root.to_string() + "/")) {
            return Some(mapped(
                rule_id,
                Some(path),
                format!("{plugin}/{destination_root}/{rest}"),
                MirrorTransform::Verbatim,
                false,
            ));
        }
    }
    if let Some(name) = path.strip_prefix("integrations/locks/") {
        if [".gitkeep", "README.md", "lock.schema.json"].contains(&name) {
            return Some(mapped(
                "lock-surface",
                Some(path),
                format!("{plugin}/integrations/locks/{name}"),
                MirrorTransform::LockSurface,
                false,
            ));
        }
        return None;
    }
    if let Some(rest) = path.strip_prefix("integrations/worktree/") {
        return Some(mapped(
            "worktree-relocation",
            Some(path),
            format!("{plugin}/integrations/worktree/{rest}"),
            MirrorTransform::Relocated,
            false,
        ));
    }
    if let Some(name) = path.strip_prefix("scripts/") {
        return Some(mapped(
            "scripts-copy",
            Some(path),
            format!("{plugin}/scripts/{name}"),
            MirrorTransform::Verbatim,
            false,
        ));
    }
    for (source, destination, rule_id) in [
        (
            "runtime_bootstrap.py",
            "runtime_bootstrap.py",
            "runtime-bootstrap-shim",
        ),
        ("yaml_output.py", "yaml_output.py", "yaml-output-shim"),
        (
            "skill_runtime_bootstrap.py",
            "skill_runtime_bootstrap.py",
            "skill-runtime-bootstrap-shim",
        ),
    ] {
        if path == source {
            return Some(mapped(
                rule_id,
                Some(path),
                format!("{plugin}/{destination}"),
                MirrorTransform::Injected,
                false,
            ));
        }
    }
    if [
        "packaging/bootstrap-python.json",
        "packaging/bootstrap-requirements.txt",
    ]
    .contains(&path)
    {
        return Some(mapped(
            "bootstrap-dependency-contract",
            Some(path),
            format!("{plugin}/{path}"),
            MirrorTransform::Injected,
            false,
        ));
    }
    None
}

fn is_candidate_source(path: &str, manifest: &MirrorManifest) -> bool {
    path == "README.md"
        || path
            .strip_prefix(&(manifest.public_skills_dir.clone() + "/"))
            .is_some_and(is_directory_member)
        || path.starts_with("skills/shared/")
        || path.starts_with(".claude/agents/")
        || path.starts_with(&(manifest.support_skills_dir.clone() + "/"))
        || path.starts_with(&(manifest.profiles_dir.clone() + "/"))
        || path.starts_with(&(manifest.presets_dir.clone() + "/"))
        || path.starts_with(&(manifest.integrations_dir.clone() + "/"))
        || path.starts_with("integrations/locks/")
        || path.starts_with("integrations/worktree/")
        || path.starts_with("scripts/")
        || [
            "runtime_bootstrap.py",
            "yaml_output.py",
            "skill_runtime_bootstrap.py",
            "packaging/bootstrap-python.json",
            "packaging/bootstrap-requirements.txt",
        ]
        .contains(&path)
}

fn is_directory_member(rest: &str) -> bool {
    let mut components = rest.split('/');
    let directory = components.next().unwrap_or_default();
    !directory.is_empty() && !directory.starts_with('.') && components.next().is_some()
}

fn is_intentionally_excluded(path: &str, manifest: &MirrorManifest) -> bool {
    if let Some(rest) = path.strip_prefix(&(manifest.support_skills_dir.clone() + "/")) {
        let skill_id = rest.split('/').next().unwrap_or_default();
        return skill_id == "generated"
            || manifest.upstream_consumed_support_ids.contains(skill_id);
    }
    false
}

fn unmodeled(path: &str, detail: &str) -> Unestablished {
    Unestablished {
        kind: ConditionKind::UnmodeledMirrorRule,
        subject: path.to_string(),
        detail: detail.to_string(),
        rules: Vec::new(),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn derives_collapse_and_subtractive_pairs_from_manifest_paths() {
        let manifest = MirrorManifest::default();
        let selected = vec![
            "README.md".to_string(),
            "skills/public/demo/SKILL.md".to_string(),
            "scripts/helper.py".to_string(),
            "tools/suggest_public_skill_validation.py".to_string(),
        ];
        let snapshot = selected.iter().cloned().collect();
        let result = derive_mirrors(&selected, &snapshot, &manifest);
        assert!(result.pairs.iter().any(|pair| {
            pair.rule_id == "public-skill-collapse"
                && pair.destination == "plugins/charness/skills/demo/SKILL.md"
        }));
        assert!(result.pairs.iter().any(|pair| {
            pair.rule_id == "scripts-copy" && pair.source.as_deref() == Some("scripts/helper.py")
        }));
        assert!(
            !result
                .pairs
                .iter()
                .any(|pair| pair.source.as_deref()
                    == Some("tools/suggest_public_skill_validation.py"))
        );
    }

    #[test]
    fn unknown_lock_file_is_not_silently_treated_as_a_mirror() {
        let selected = vec!["integrations/locks/local.lock".to_string()];
        let result = derive_mirrors(
            &selected,
            &selected.iter().cloned().collect(),
            &MirrorManifest::default(),
        );
        assert_eq!(
            result.unestablished[0].kind,
            ConditionKind::UnmodeledMirrorRule
        );
    }
}
