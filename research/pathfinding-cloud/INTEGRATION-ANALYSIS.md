# Integrating pathfinding.cloud privilege-escalation paths into Cloudsplaining

**Source:** [`DataDog/pathfinding.cloud`](https://github.com/DataDog/pathfinding.cloud) — "the definitive source of truth for AWS IAM privilege escalation paths" (66 attack paths as validated YAML, building on Rhino Security Labs' original 21 methods).

**Goal of this document:** catalog the IAM actions/combinations pathfinding.cloud documents, diff them against what Cloudsplaining detects today, and map exactly where new detections would land — Python → JavaScript → tests.

> Note: pathfinding.cloud's own YAMLs already cite Cloudsplaining as a detection tool (e.g. `iam-001` links to `cloudsplaining/shared/constants.py#L117`). This is a natural, mutually-aware integration.

---

## 1. TL;DR

| | Count |
|---|---|
| Pathfinding paths analyzed | **66** |
| Already detected by an existing Cloudsplaining method (exact action-set match) | **18** |
| Detectable today via a *narrower* existing method (subset already fires) | **8** |
| Already covered by CredentialsExposure (`sts:assumerole`) | **1** |
| **Genuinely new — not detected today** | **39** |
| Distinct required IAM actions across all 66 paths | **70** |
| Required actions Cloudsplaining doesn't recognize for privesc today | **47** |
| Cloudsplaining `PRIVILEGE_ESCALATION_METHODS` entries today | **22** |

**Where the work goes:**
- **Python:** one file — append entries to `PRIVILEGE_ESCALATION_METHODS` in `cloudsplaining/shared/constants.py`. **No logic change.** The matcher (`PolicyDocument.allows_privilege_escalation`) iterates the dict generically.
- **JavaScript:** **no code change required** — the report is fully data-driven; `PrivilegeEscalationFormat.vue` renders whatever `{type, actions}` objects the Python side emits. (Optional: refresh the risk-description text + rebuild `dist/`.)
- **Tests:** add focused unit tests; **fix ~10 brittle assertions** that hard-code exact privesc finding lists; regenerate `sampleData.js`.

---

## 2. Coverage breakdown

### 2a. Already covered exactly (18) — no action needed

| pathfinding | technique | existing Cloudsplaining method |
|---|---|---|
| iam-001 | iam:CreatePolicyVersion | CreateNewPolicyVersion |
| iam-002 | iam:CreateAccessKey | CreateAccessKey |
| iam-004 | iam:CreateLoginProfile | CreateLoginProfile |
| iam-006 | iam:UpdateLoginProfile | UpdateLoginProfile |
| iam-007 | iam:PutUserPolicy | PutUserPolicy |
| iam-008 | iam:AttachUserPolicy | AttachUserPolicy |
| iam-010 | iam:AttachGroupPolicy | AttachGroupPolicy |
| iam-011 | iam:PutGroupPolicy | PutGroupPolicy |
| iam-013 | iam:AddUserToGroup | AddUserToGroup |
| iam-014 | iam:AttachRolePolicy + sts:AssumeRole | AttachRolePolicy |
| iam-017 | iam:PutRolePolicy + sts:AssumeRole | PutRolePolicy |
| ec2-001 | iam:PassRole + ec2:RunInstances | CreateEC2WithExistingIP |
| lambda-001 | iam:PassRole + lambda:CreateFunction + lambda:InvokeFunction | PassExistingRoleToNewLambdaThenInvoke |
| lambda-002 | iam:PassRole + lambda:CreateFunction + lambda:CreateEventSourceMapping | PassExistingRoleToNewLambdaThenTriggerWithExistingDynamo |
| lambda-003 | lambda:UpdateFunctionCode | EditExistingLambdaFunctionWithRole |
| glue-001 | iam:PassRole + glue:CreateDevEndpoint | PassExistingRoleToNewGlueDevEndpoint |
| glue-002 | glue:UpdateDevEndpoint | UpdateExistingGlueDevEndpoint |
| cloudformation-001 | iam:PassRole + cloudformation:CreateStack | PassExistingRoleToCloudFormation |

### 2b. Detectable today via a narrower existing method (8) — already flagged, adding would duplicate

These are pathfinding **variants** that *add* required permissions on top of a primary technique Cloudsplaining already detects. A policy granting the variant's actions already trips the narrower method, so adding them as separate entries would emit a redundant second finding. **Recommendation: skip** (or fold into docs only).

| pathfinding | technique | already fires |
|---|---|---|
| iam-003 | iam:CreateAccessKey + iam:DeleteAccessKey | CreateAccessKey |
| iam-015 | iam:AttachUserPolicy + iam:CreateAccessKey | AttachUserPolicy / CreateAccessKey |
| iam-016 | iam:CreatePolicyVersion + sts:AssumeRole | CreateNewPolicyVersion |
| iam-018 | iam:PutUserPolicy + iam:CreateAccessKey | CreateAccessKey / PutUserPolicy |
| iam-020 | iam:CreatePolicyVersion + iam:UpdateAssumeRolePolicy | CreateNewPolicyVersion |
| lambda-004 | lambda:UpdateFunctionCode + lambda:InvokeFunction | EditExistingLambdaFunctionWithRole |
| lambda-005 | lambda:UpdateFunctionCode + lambda:AddPermission | EditExistingLambdaFunctionWithRole |
| datapipeline-001 | iam:PassRole + datapipeline:CreatePipeline + PutPipelineDefinition + ActivatePipeline | PassExistingRoleToNewDataPipeline |

### 2c. Covered by CredentialsExposure (1)

| pathfinding | technique | covered by |
|---|---|---|
| sts-001 | sts:AssumeRole | `ACTIONS_THAT_RETURN_CREDENTIALS` (constants.py) |

### 2d. **New — not detected today (39)**

These are the actionable additions. Full machine-readable list with exact action sets is in [`proposed-privilege-escalation-methods.py`](./proposed-privilege-escalation-methods.py); writeups are in [`pathfinding-paths-catalog.yaml`](./pathfinding-paths-catalog.yaml). Grouped by category:

**`new-passrole` — pass a role to a newly created resource (18):**
AppRunner (`apprunner-001`), Bedrock AgentCore code interpreter (`bedrock-001`), CloudFormation StackSets (`cloudformation-003`, `cloudformation-004`), CodeBuild (`codebuild-001`, `codebuild-004`), EC2 spot (`ec2-003`), ECS (`ecs-001`–`ecs-005`), Glue jobs (`glue-003`–`glue-006`), Lambda+AddPermission (`lambda-006`), SageMaker notebook/training/processing (`sagemaker-001`–`003`).

**`existing-passrole` — abuse an existing resource that already has a role (10):**
`apprunner-002`, `cloudformation-002`, `cloudformation-005`, `codebuild-002`, `codebuild-003`, `ec2-002`, `ec2-004`, `glue-005`, `glue-006`, `sagemaker-005`.

**`principal-access` / `credential-access` — reach existing principals or sessions (8):**
`bedrock-002`, `ec2instanceconnect-003`, `ecs-006`, `sagemaker-004`, `ssm-001`, `ssm-002`, plus the IAM role-policy cases below.

**IAM role-policy techniques Cloudsplaining bundles with `sts:assumerole` (5):**
`iam-005` (PutRolePolicy alone), `iam-009` (AttachRolePolicy alone), `iam-012` (UpdateAssumeRolePolicy alone), `iam-019`, `iam-021`.

---

## 3. The most important finding: the `sts:assumerole` bundling gap

Cloudsplaining's role-policy methods **require `sts:assumerole` in addition** to the IAM write:

```python
"AttachRolePolicy": ["iam:attachrolepolicy", "sts:assumerole"],
"PutRolePolicy":    ["iam:putrolepolicy", "sts:assumerole"],
"UpdateRolePolicyToAssumeIt": ["iam:updateassumerolepolicy", "sts:assumerole"],
```

pathfinding.cloud documents `iam:AttachRolePolicy`, `iam:PutRolePolicy`, and `iam:UpdateAssumeRolePolicy` as **standalone** escalations (`iam-009`, `iam-005`, `iam-012`) — because the target role may already be assumable (by a service, or by the actor), so the attacker never needs `sts:AssumeRole` in their own policy.

**Consequence:** Cloudsplaining today produces **no privesc finding** for a policy that grants `iam:AttachRolePolicy` on `*` without also granting `sts:AssumeRole`. That's a real detection gap, not just a naming difference. See the catalog entries for `iam-005/009/012` for the exploit reasoning. Resolving this is a small policy decision (add standalone variants vs. relax the existing entries) and is the highest-value single change in this set.

---

## 4. Where it goes in Cloudsplaining

### 4a. Python (the only required change)

**File:** `cloudsplaining/shared/constants.py` — `PRIVILEGE_ESCALATION_METHODS` dict (lines ~110–161).
**Edit:** append `"MethodName": ["service:action", ...]` entries. Nothing else.

Why nothing else: the matcher is generic.

```python
# cloudsplaining/scan/policy_document.py:149-167
@property
def allows_privilege_escalation(self) -> list[dict[str, Any]]:
    escalations = []
    all_allowed_unrestricted_actions_lowercase = [ x.lower() for ... ]
    for escalation_type, actions in PRIVILEGE_ESCALATION_METHODS.items():
        if set(actions).issubset(all_allowed_unrestricted_actions_lowercase):
            escalations.append({"type": escalation_type, "actions": actions})
    return escalations
```

Rules for new entries (confirmed against the matcher):
1. **Values must be exact lowercase** `service:action` strings (wildcards are already expanded upstream by policy_sentry; the comparison list is `.lower()`-ed). The generator enforces this.
2. **Keys are arbitrary labels** — used as the finding `type` and as the readthedocs URL anchor (`.../glossary/privilege-escalation/#<type>`). Use PascalCase like the existing entries.
3. Matching is **subset-of-allowed-unrestricted-actions** — every action in the list must be granted on `Resource: "*"` without a `Condition` (unless `--flag-resource-arn-statements` / `--flag-conditional-statements`).
4. **Severity & description need no change.** `ISSUE_SEVERITY["PrivilegeEscalation"]="high"` and `RISK_DEFINITION["PrivilegeEscalation"]` are keyed on the *category*, not per method — every new method inherits them automatically.

**Credentials-exposure adjacents:** if a path simply returns credentials (e.g. `sts-001`), the right home is the flat `ACTIONS_THAT_RETURN_CREDENTIALS` list in the same file (already contains `sts:assumerole`), not `PRIVILEGE_ESCALATION_METHODS`.

> ResourceExposure and InfrastructureModification are *not* static lists — they're derived from policy_sentry access-level labels in `cloudsplaining/scan/statement_detail.py`, so no constants to touch for those.

### 4b. JavaScript / Vue report — **no change required**

The rendering of individual methods is fully data-driven:

```html
<!-- cloudsplaining/output/src/components/finding/PrivilegeEscalationFormat.vue:3-8 -->
<li v-for="someFinding in privilegeEscalationFinding" ...>
  {{ someFinding.type }}  <!-- method name, e.g. CreateAccessKey -->
  ... someFinding.actions ...
</li>
```

No method names are hard-coded anywhere in the frontend — only the *category* string `"PrivilegeEscalation"` is referenced (in `util/*.js`, `Summary.vue`, `Principals.vue`, `TaskTable.vue`, `glossary.js`, etc.). Since every new method falls under the existing `PrivilegeEscalation` category, **the report just works**.

Two optional follow-ups (only if you change text/links):
- The risk-description text lives **duplicated** in the frontend at `cloudsplaining/output/src/util/glossary.js` and `cloudsplaining/output/src/assets/definition-privilege-escalation.md` (it is *not* read from the injected `iam_data`). If you want it to credit pathfinding.cloud, edit there.
- Any frontend change requires rebuilding the committed bundle: `just build-js` regenerates `cloudsplaining/output/dist/` (webpack + the `InlineSourcePlugin` from `vue.config.js`). The `dist/` artifact is what Python embeds in the report.

**Verdict: adding methods needs zero JS edits and zero `dist/` rebuild.**

### 4c. Tests

**Add (low-level unit tests):** `test/scanning/test_policy_document.py`, following `test_allows_privilege_escalation` (line ~110): build a minimal policy granting exactly the new method's actions at `Resource:"*"`, then `assertListEqual(policy_document.allows_privilege_escalation, [{"type": "...", "actions": [...]}])`. Add a negative test (missing one action ⇒ `[]`).

**Fix (brittle existing assertions that hard-code exact privesc lists).** These break if a newly added method's action set is a subset of the test policy's actions:

| file | line(s) | what it expects | breaks if a new method needs… |
|---|---|---|---|
| `test/scanning/test_policy_document.py` | 146 | exact 2-item list | a subset of `iam:passrole, lambda:createfunction, lambda:createeventsourcemapping, dynamodb:createtable, dynamodb:putitem` |
| `test/scanning/test_policy_document.py` | 522-525 | exact 1-item list (`CreateEC2WithExistingIP`) | a subset of `ec2:getpassworddata, s3:getobject, ec2:authorizesecuritygroupingress, ec2:runinstances, iam:passrole, ec2:createnetworkinterfacepermission` |
| `test/scanning/test_policy_document.py` | 406 | `allows_privilege_escalation[0]` == `UpdateRolePolicyToAssumeIt` | new method on `iam:updateassumerolepolicy, sts:assumerole` ordering — **`iam-012` standalone `UpdateAssumeRolePolicyWithoutAssume` will affect this** |
| `test/scanning/test_authorization_details.py` | 126-127 | exact 1-item (`UpdateRolePolicyToAssumeIt`) | same as above — **`iam-012` addition will break this** |
| `test/command/test_scan_policy_file.py` | 298-299 | exact 1-item (`UpdateRolePolicyToAssumeIt`) | same — **`iam-012` addition will break this** |
| `test/output/test_policy_finding.py` | 114-119 | exact (`CreateNewPolicyVersion`) | new single-action method on `iam:createpolicyversion` |
| `test/command/test_scan_policy_file.py` | 102, 152 | exact (`CreateAccessKey`) | new method on `iam:createaccesskey` |
| `cloudsplaining/output/src/test/inline-policies-test.js` | 43-53 | exact (`CreateAccessKey`) | the `OverprivilegedEC2` sample policy picking up new findings |

> There is **no** test asserting `len(PRIVILEGE_ESCALATION_METHODS)` or comparing the whole dict — so the count itself is safe to grow.

**Regenerate fixtures:** `sampleData.js` (and `utils/example-iam-data.json`) are generated from `examples/files/example.json` via `just generate-report`. Re-run it after adding methods so the JS mocha fixtures reflect new findings, then update the hard-coded `expectedResult` in `inline-policies-test.js` if needed.

---

## 5. Caveats & judgment calls before merging

1. **Variant overlap (4 entries).** `ecs-001/002` and `iam-019/021` are supersets of other proposed entries (`ecs-003/004`, `iam-009/005`). Including both makes a single policy emit two findings for one underlying escalation. Cloudsplaining's existing dict deliberately lists only primaries — recommend matching that convention and **dropping the 4 variant entries** (or keeping only the primary). Flagged inline in the generated `.py`.

2. **Broad single-action `existing-passrole` methods are high-noise.** `cloudformation:updatestack`, `codebuild:startbuild`, `ssm:sendcommand`, `ssm:startsession`, `apprunner:updateservice` etc. escalate **only if** a privileged target resource already exists — something Cloudsplaining (policy-text-only) can't verify. They will flag many benign policies. There's precedent (`UpdateExistingGlueDevEndpoint`, `EditExistingLambdaFunctionWithRole` are already single-action), but `ssm:sendcommand`/`codebuild:startbuild` are far more common. Consider gating these behind a flag or accepting them as lower-confidence.

3. **`sts:assumerole` bundling (§3)** is a policy decision: add standalone IAM role-policy variants, or relax the three existing entries. Adding standalone variants will **break the 3 `UpdateRolePolicyToAssumeIt` assertions** noted above — expected and easy to update.

4. **New service prefixes.** `bedrock-agentcore`, `apprunner`, `ec2-instance-connect`, `codebuild`, `sagemaker`, `ecs` actions must be valid in the installed policy_sentry action database for wildcard expansion to map them. Verify (`bedrock-agentcore` is newest and most likely to need a policy_sentry bump).

---

## 6. Recommended phasing

1. **Phase 1 (high value, low noise):** the 18 `new-passrole` "pass role to new resource" methods + the `sts:assumerole` standalone IAM fix (§3). These mirror existing patterns and are the clearest true positives.
2. **Phase 2:** `existing-passrole` multi-action methods (e.g. `ec2-002`, `ec2-004`, glue update+run) — still reasonably specific.
3. **Phase 3 (opt-in / discuss):** broad single-action methods (§5.2) and the credential-style ones, possibly behind a flag.
4. Drop the 4 variant supersets (§5.1) and the 8 already-detected variants (§2b).

---

## 7. Deliverables in this folder

| file | what |
|---|---|
| `pathfinding-paths-catalog.yaml` | All 66 paths: id, name, category, services, exact lowercase required/additional actions, parent, **description, recommendation, limitations, references**, plus a `cloudsplaining_coverage` block per path. |
| `gap-analysis.json` | Machine-readable diff: per-status path lists, category counts, the 70-action universe, and the 47 actions Cloudsplaining doesn't yet recognize. |
| `proposed-privilege-escalation-methods.py` | Ready-to-review dict of the 39 new entries (exact action lists, proposed names, inline variant/overlap notes). |
| `extract_catalog.py` | Reproducible extractor + classifier (reads the cloned repo + Cloudsplaining constants). |
| `generate_proposed.py` | Reproducible generator for the proposed additions. |
| `INTEGRATION-ANALYSIS.md` | This document. |

Regenerate everything: `uv run python research/pathfinding-cloud/extract_catalog.py && uv run python research/pathfinding-cloud/generate_proposed.py`

*Source repo cloned to `repos/pathfinding.cloud/` (gitignored via `repos/**`).*
