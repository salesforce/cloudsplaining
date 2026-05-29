"""Generate a proposed PRIVILEGE_ESCALATION_METHODS additions block for cloudsplaining,
derived from the 39 'new' pathfinding.cloud paths (action lists are the source of truth
from gap-analysis.json; method names + notes are curated here).

Run: uv run python research/pathfinding-cloud/generate_proposed.py
"""

from __future__ import annotations

import json
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent
gap = json.load((OUT_DIR / "gap-analysis.json").open())

# Curated: pathfinding id -> (ProposedMethodName, note)
# Action lists are pulled from gap-analysis.json so they stay exact.
NAME_MAP: dict[str, tuple[str, str]] = {
    # --- new-passrole: pass a role to a NEWLY created resource ---
    "apprunner-001": ("PassExistingRoleToNewAppRunnerService", ""),
    "bedrock-001": ("PassExistingRoleToNewBedrockCodeInterpreter", ""),
    "cloudformation-003": ("PassExistingRoleToNewCloudFormationStackSet", ""),
    "cloudformation-004": (
        "PassRoleToUpdateCloudFormationStackSet",
        "modifies existing stack set but passes a new role",
    ),
    "codebuild-001": ("PassExistingRoleToNewCodeBuildProjectThenBuild", ""),
    "codebuild-004": ("PassExistingRoleToNewCodeBuildProjectThenBuildBatch", ""),
    "ec2-003": ("PassExistingRoleToNewEC2SpotInstance", ""),
    "ecs-001": (
        "PassExistingRoleToNewECSClusterServiceTask",
        "VARIANT of ecs-003 (adds ecs:CreateCluster) -> overlaps ecs-003",
    ),
    "ecs-002": (
        "PassExistingRoleToNewECSClusterRunTask",
        "VARIANT of ecs-004 (adds ecs:CreateCluster) -> overlaps ecs-004",
    ),
    "ecs-003": ("PassExistingRoleToNewECSService", ""),
    "ecs-004": ("PassExistingRoleToNewECSTaskViaRunTask", ""),
    "ecs-005": ("PassExistingRoleToNewECSTaskViaStartTask", ""),
    "glue-003": ("PassExistingRoleToNewGlueJobThenRun", ""),
    "glue-004": ("PassExistingRoleToNewGlueJobViaTrigger", ""),
    "lambda-006": ("PassExistingRoleToNewLambdaThenAddPermission", ""),
    "sagemaker-001": ("PassExistingRoleToNewSageMakerNotebookInstance", ""),
    "sagemaker-002": ("PassExistingRoleToNewSageMakerTrainingJob", ""),
    "sagemaker-003": ("PassExistingRoleToNewSageMakerProcessingJob", ""),
    # --- existing-passrole: abuse an EXISTING resource that already has a role ---
    "apprunner-002": ("UpdateExistingAppRunnerService", ""),
    "cloudformation-002": ("UpdateExistingCloudFormationStack", ""),
    "cloudformation-005": ("ExecuteCloudFormationChangeSet", ""),
    "codebuild-002": ("StartExistingCodeBuildProject", ""),
    "codebuild-003": ("StartExistingCodeBuildProjectBatch", ""),
    "ec2-002": ("ModifyEC2InstanceUserDataThenRestart", ""),
    "ec2-004": ("ModifyExistingEC2LaunchTemplate", ""),
    "glue-005": ("UpdateExistingGlueJobThenRun", ""),
    "glue-006": ("UpdateExistingGlueJobViaTrigger", ""),
    "sagemaker-005": ("UpdateSageMakerNotebookLifecycleConfig", ""),
    # --- principal/credential access on existing resources ---
    "bedrock-002": ("AccessExistingBedrockCodeInterpreter", ""),
    "ec2instanceconnect-003": ("EC2InstanceConnectSendSSHPublicKey", ""),
    "ecs-006": ("ECSExecuteCommandOnRunningTask", ""),
    "sagemaker-004": ("CreatePresignedSageMakerNotebookUrl", ""),
    "ssm-001": ("SSMStartSessionOnInstance", ""),
    "ssm-002": ("SSMSendCommandToInstance", ""),
    # --- IAM role-policy techniques cloudsplaining bundles with sts:AssumeRole ---
    # pathfinding documents these as standalone (role may be service-assumable / already assumable)
    "iam-005": (
        "PutRolePolicyWithoutAssume",
        "cloudsplaining PutRolePolicy bundles sts:assumerole; this is the standalone case",
    ),
    "iam-009": (
        "AttachRolePolicyWithoutAssume",
        "cloudsplaining AttachRolePolicy bundles sts:assumerole; this is the standalone case",
    ),
    "iam-012": (
        "UpdateAssumeRolePolicyWithoutAssume",
        "cloudsplaining UpdateRolePolicyToAssumeIt bundles sts:assumerole; standalone case",
    ),
    "iam-019": ("AttachRolePolicyThenUpdateAssume", "VARIANT of iam-009; superset of AttachRolePolicyWithoutAssume"),
    "iam-021": ("PutRolePolicyThenUpdateAssume", "VARIANT of iam-005; superset of PutRolePolicyWithoutAssume"),
}

# index actions by id from gap analysis
actions_by_id = {p["id"]: p["required_actions"] for p in gap["by_status"]["new"]}

lines = []
lines.append("# Proposed additions to PRIVILEGE_ESCALATION_METHODS")
lines.append("# Source: DataDog/pathfinding.cloud (39 paths not currently detected as named methods)")
lines.append("# Action lists are exact; method NAMES are proposals (editable).")
lines.append("# NOTE: entries flagged VARIANT overlap a primary technique and will produce a")
lines.append("#       second finding on the same policy -- decide whether to include them.")
lines.append("")
lines.append("PRIVILEGE_ESCALATION_METHODS_PATHFINDING_ADDITIONS = {")

# group by category for readability
order = ["new-passrole", "existing-passrole", "principal-access", "credential-access", "self-escalation"]
new_paths = {p["id"]: p for p in gap["by_status"]["new"]}
by_cat: dict[str, list[str]] = {}
for pid, p in new_paths.items():
    by_cat.setdefault(p["category"], []).append(pid)

cat_titles = {
    "new-passrole": "iam:PassRole + create NEW resource",
    "existing-passrole": "abuse EXISTING resource that already has a role",
    "principal-access": "gain access to existing principals / sessions",
    "credential-access": "extract credentials from existing resources",
    "self-escalation": "modify own permissions directly",
}

for cat in order:
    pids = sorted(by_cat.get(cat, []))
    if not pids:
        continue
    lines.append(f"    # --- {cat}: {cat_titles.get(cat, cat)} ---")
    for pid in pids:
        name, note = NAME_MAP.get(pid, (pid.replace("-", "_"), "UNMAPPED"))
        acts = actions_by_id[pid]
        acts_repr = ", ".join(f'"{a}"' for a in acts)
        comment = f"  # {pid}"
        if note:
            comment += f" -- {note}"
        lines.append(f'    "{name}": [{acts_repr}],{comment}')
    lines.append("")

lines.append("}")

out = OUT_DIR / "proposed-privilege-escalation-methods.py"
out.write_text("\n".join(lines) + "\n")
print(f"Wrote {out.relative_to(Path(__file__).resolve().parents[2])} with {len(new_paths)} entries")
# sanity: ensure every new path got mapped
unmapped = [pid for pid in new_paths if pid not in NAME_MAP]
print("Unmapped:", unmapped or "none")
