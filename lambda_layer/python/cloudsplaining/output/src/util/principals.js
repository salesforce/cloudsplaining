'use strict';
let inlinePolicyUtils = require("./inline-policies");
let managedPolicyUtils = require("./managed-policies");
let otherUtils = require("./other");

function getPrincipalMetadata(iam_data, principalName, principalType) {
    if (principalType.toLowerCase() === "role") {
        return iam_data["roles"][principalName]
    }
    if (principalType.toLowerCase() === "group") {
        return iam_data["groups"][principalName]
    }
    if (principalType.toLowerCase() === "user") {
        return iam_data["users"][principalName]
    }
}

function getPrincipalNames(iam_data, principalType) {
    let result = [];
    if (principalType.toLowerCase() === "role") {
        let principalIds = Object.keys(iam_data["roles"])
        for (let principalId of principalIds) {
            result.push(iam_data["roles"][principalId]["name"])
        }
        return result.sort();
    }
    if (principalType.toLowerCase() === "group") {
        let principalIds = Object.keys(iam_data["groups"]);
        for (let principalId of principalIds) {
            result.push(iam_data["groups"][principalId]["name"])
        }
        result.sort();
        return result
    }
    if (principalType.toLowerCase() === "user") {
        let principalIds = Object.keys(iam_data["users"]);
        for (let principalId of principalIds) {
            result.push(iam_data["users"][principalId]["name"])
        }
        result.sort();
        return result
    }
}

function getPrincipalIds(iam_data, principalType) {
    let result;
    if (principalType.toLowerCase() === "role") {
        result = Object.keys(iam_data["roles"])
        return result.sort();
    }
    if (principalType.toLowerCase() === "group") {
        result = Object.keys(iam_data["groups"]);
        result.sort();
        return result
    }
    if (principalType.toLowerCase() === "user") {
        result = Object.keys(iam_data["users"]);
        result.sort();
        return result
    }
}

function getPrincipalPolicies(iam_data, principalName, principalType, policyType) {
    let thePrincipalType;
    if (principalType.toLowerCase() === "role") {
        thePrincipalType = "roles";
    } else if (principalType.toLowerCase() === "group") {
        thePrincipalType = "groups";
    } else if (principalType.toLowerCase() === "user") {
        thePrincipalType = "users";
    }

    let thePolicyType;
    if (policyType.toLowerCase() === "inline") {
        thePolicyType = "inline_policies";
    } else if (policyType === "Customer") {
        thePolicyType = "customer_managed_policies";
    } else if (policyType === "AWS") {
        thePolicyType = "aws_managed_policies";
    }
    let policies = iam_data[thePrincipalType][principalName][thePolicyType];
    let result = Array.from(Object.keys(policies));
    result.sort()
    return result
}

function getPrincipalPolicyNames(iam_data, principalName, principalType, policyType) {
    let policyNames = [];
    let policyIds = getPrincipalPolicies(iam_data, principalName, principalType, policyType);
    let policyId;
    if (policyType.toLowerCase() === "inline") {
        for (policyId in policyIds) {
            policyNames.push(inlinePolicyUtils.getInlinePolicy(iam_data, policyIds[policyId])["PolicyName"])
        }
    } else if (policyType === "AWS") {
        for (policyId in policyIds) {
            policyNames.push(managedPolicyUtils.getManagedPolicyName(iam_data, "AWS", policyIds[policyId]))
        }
    } else if (policyType === "Customer") {
        for (policyId in policyIds) {
            policyNames.push(managedPolicyUtils.getManagedPolicyName(iam_data, "Customer", policyIds[policyId]))
        }
    }
    policyNames.sort();
    return policyNames;
}

function getRiskAssociatedWithPrincipal(iam_data, principalName, principalType, riskType) {
    /*
    riskName: DataExfiltration, PrivilegeEscalation, ResourceExposure, InfrastructureModification
     */
    let inlinePolicyIdsAssociatedWithPrincipal = getPrincipalPolicies(iam_data, principalName, principalType, "Inline");
    let customerManagedPoliciesAssociatedWithPrincipal = getPrincipalPolicies(iam_data, principalName, principalType, "Customer");
    let awsManagedPoliciesAssociatedWithPrincipal = getPrincipalPolicies(iam_data, principalName, principalType, "AWS");
    let findings = [];
    if (inlinePolicyIdsAssociatedWithPrincipal.length > 0) {
        let policyId;
        for (policyId of inlinePolicyIdsAssociatedWithPrincipal) {
            let theseInlinePolicyFindings = inlinePolicyUtils.getInlinePolicyFindings(iam_data, policyId, riskType);
            let item;
            for (item of theseInlinePolicyFindings) {
                if (!(item in findings)){
                    findings.push(item);
                }
            }
        }
    }
    if (customerManagedPoliciesAssociatedWithPrincipal.length > 0) {
        let policyId;
        for (policyId of customerManagedPoliciesAssociatedWithPrincipal) {
            let theseManagedPolicyFindings = managedPolicyUtils.getManagedPolicyFindings(iam_data, "Customer", policyId, riskType);
            let item;
            for (item of theseManagedPolicyFindings) {
                if (!(item in findings)){
                    findings.push(item);
                }
            }
        }
    }
    if (awsManagedPoliciesAssociatedWithPrincipal.length > 0) {
        let policyId;
        for (policyId of awsManagedPoliciesAssociatedWithPrincipal) {
            let theseManagedPolicyFindings = managedPolicyUtils.getManagedPolicyFindings(iam_data, "AWS", policyId, riskType);
            let item;
            for (item of theseManagedPolicyFindings) {
                if (!(item in findings)){
                    findings.push(item);
                }
            }
        }
    }
    if (findings.length > 0) {
        findings.sort();
        findings = otherUtils.removeDuplicatesFromArray(findings)
        return findings;
    } else {
        return []
    }
}

exports.getPrincipalMetadata = getPrincipalMetadata;
exports.getPrincipalNames = getPrincipalNames;
exports.getPrincipalIds = getPrincipalIds;
exports.getPrincipalPolicies = getPrincipalPolicies;
exports.getRiskAssociatedWithPrincipal = getRiskAssociatedWithPrincipal;
exports.getPrincipalPolicyNames = getPrincipalPolicyNames;
