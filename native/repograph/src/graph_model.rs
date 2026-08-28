use std::collections::BTreeMap;

use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize)]
#[serde(rename_all = "kebab-case")]
pub enum Role {
    Production,
    Test,
    Generated,
    Doc,
    Unestablished,
}

impl Role {
    pub const fn as_str(self) -> &'static str {
        match self {
            Self::Production => "production",
            Self::Test => "test",
            Self::Generated => "generated",
            Self::Doc => "doc",
            Self::Unestablished => "unestablished",
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize)]
#[serde(rename_all = "kebab-case")]
pub enum PackageKind {
    Skill,
    SharedLibrary,
    Scripts,
    Cli,
    Tests,
    PluginExport,
    NativeCrate,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize)]
#[serde(rename_all = "kebab-case")]
pub enum SkillStatus {
    Modeled,
    MalformedSkill,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize)]
#[serde(rename_all = "kebab-case")]
pub enum AdapterStatus {
    Modeled,
    UnmodeledDeclaration,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize)]
#[serde(rename_all = "kebab-case")]
pub enum MirrorTransform {
    Verbatim,
    PathCollapsed,
    Relocated,
    FilteredCopy,
    ContentTransformed,
    Injected,
    LockSurface,
    ManifestGenerated,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize)]
#[serde(rename_all = "kebab-case")]
pub enum RootKind {
    ProductRuntime,
    Validation,
    Tests,
    Generated,
    HostDiscovered,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize)]
#[serde(rename_all = "kebab-case")]
pub enum CarrierTier {
    StructuredUnparsed,
    Tokenizable,
    Opaque,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize)]
#[serde(rename_all = "kebab-case")]
pub enum CarrierSourceKind {
    StructuredPlan,
    GitHook,
    CiWorkflow,
    PackageScript,
    SurfaceCommand,
    IntegrationCheck,
    QualityGate,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize)]
#[serde(rename_all = "kebab-case")]
pub enum EdgeKind {
    Imports,
    Invokes,
    Packages,
    Mirrors,
    Documents,
    Tests,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize)]
#[serde(rename_all = "kebab-case")]
pub enum ConditionKind {
    AnalyzerNotParsed,
    AnalyzerParseFailure,
    AnalyzerVersionMismatch,
    AnalyzerIncomplete,
    AnalyzerZeroModules,
    ScopeViolation,
    AnalyzerExcluded,
    Inventory,
    MalformedSkill,
    ParseFailure,
    RoleConflict,
    RoleUnestablished,
    ScopeConflict,
    TopologyConfig,
    UnmodeledDeclaration,
    UnmodeledMirrorRule,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
#[serde(tag = "class", rename_all = "kebab-case")]
pub enum Node {
    File(FileNode),
    Package(PackageNode),
    Skill(SkillNode),
    Adapter(AdapterNode),
    MirrorPair(MirrorPairNode),
    Test(TestNode),
    RuntimeProbe(RuntimeProbeNode),
    ExternalModule(ExternalModuleNode),
    CommandCarrier(CommandCarrierNode),
    ValidationCommand(ValidationCommandNode),
}

impl Node {
    pub fn class_name(&self) -> &'static str {
        match self {
            Self::File(_) => "file",
            Self::Package(_) => "package",
            Self::Skill(_) => "skill",
            Self::Adapter(_) => "adapter",
            Self::MirrorPair(_) => "mirror-pair",
            Self::Test(_) => "test",
            Self::RuntimeProbe(_) => "runtime-probe",
            Self::ExternalModule(_) => "external-module",
            Self::CommandCarrier(_) => "command-carrier",
            Self::ValidationCommand(_) => "validation-command",
        }
    }

    pub fn id(&self) -> &str {
        match self {
            Self::File(node) => &node.id,
            Self::Package(node) => &node.id,
            Self::Skill(node) => &node.id,
            Self::Adapter(node) => &node.id,
            Self::MirrorPair(node) => &node.id,
            Self::Test(node) => &node.id,
            Self::RuntimeProbe(node) => &node.id,
            Self::ExternalModule(node) => &node.id,
            Self::CommandCarrier(node) => &node.id,
            Self::ValidationCommand(node) => &node.id,
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct FileNode {
    pub id: String,
    pub path: String,
    pub role: Role,
    pub packages: Vec<String>,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct PackageNode {
    pub id: String,
    pub package_kind: PackageKind,
    pub path: String,
    pub members: Vec<String>,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct SkillNode {
    pub id: String,
    pub directory: String,
    pub frontmatter_name: Option<String>,
    pub status: SkillStatus,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct AdapterNode {
    pub id: String,
    pub declaration_path: String,
    pub owner: Option<String>,
    pub status: AdapterStatus,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct MirrorPairNode {
    pub id: String,
    pub rule_id: String,
    pub source: Option<String>,
    pub destination: String,
    pub transform: MirrorTransform,
    pub content_transformed: bool,
    pub destination_in_snapshot: bool,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct TestNode {
    pub id: String,
    pub file: String,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct RuntimeProbeNode {
    pub id: String,
    pub path: String,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct ExternalModuleNode {
    pub id: String,
    pub provider: String,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct CommandCarrierNode {
    pub id: String,
    pub path: String,
    pub source_kind: CarrierSourceKind,
    pub tier: CarrierTier,
    pub name: String,
    pub line: Option<usize>,
    pub raw: String,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct ValidationCommandNode {
    pub id: String,
    pub carrier_id: String,
    pub label: Option<String>,
    pub command: String,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct Edge {
    pub kind: EdgeKind,
    pub source: String,
    pub target: String,
    pub rule_id: Option<String>,
    pub module: Option<String>,
    pub line: Option<usize>,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct Root {
    pub kind: RootKind,
    pub id: String,
    pub target: String,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct Unestablished {
    pub kind: ConditionKind,
    pub subject: String,
    pub detail: String,
    pub rules: Vec<String>,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct AnalyzerInput {
    pub path: String,
    pub identity: String,
    pub scope: String,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct UnresolvedCarrier {
    pub kind: &'static str,
    pub carrier_id: String,
    pub tier: CarrierTier,
    pub reason: String,
    pub raw: String,
    pub line: Option<usize>,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct CarrierPathReference {
    pub kind: &'static str,
    pub carrier_id: String,
    pub path: String,
    pub raw: String,
    pub line: Option<usize>,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct QualityLabel {
    pub label: String,
    pub source: String,
    pub line: Option<usize>,
}

/// Optional role declarations. This is deliberately a small JSON boundary;
/// YAML adapter contents remain identity-only in v1.
#[derive(Debug, Clone, Default, PartialEq, Eq, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct TopologyConfig {
    #[serde(default)]
    pub test_globs: Vec<String>,
    #[serde(default)]
    pub production_globs: Vec<String>,
    #[serde(default)]
    pub generated_globs: Vec<String>,
}

#[derive(Debug, Clone, PartialEq, Eq, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct TopologyDocument {
    pub topology: TopologyConfig,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct GraphReport {
    pub schema: &'static str,
    pub repo_root: String,
    pub listing: String,
    pub excludes: Vec<String>,
    pub nodes: Vec<Node>,
    pub edges: Vec<Edge>,
    pub roots: Vec<Root>,
    pub mirror_destinations: Vec<String>,
    pub mirror_destination_count: usize,
    pub analyzer_inputs: Vec<AnalyzerInput>,
    pub role_census: BTreeMap<String, usize>,
    pub unresolved_carriers: Vec<UnresolvedCarrier>,
    pub carrier_path_references: Vec<CarrierPathReference>,
    pub quality_labels: Vec<QualityLabel>,
    pub unestablished: Vec<Unestablished>,
}
