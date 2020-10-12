'use strict';
let roleUtils = require("./roles");
var otherUtils = require("./other")

function getInlinePolicyIds(iam_data) {
    return Object.keys(iam_data["inline_policies"]);
}

function getInlinePolicy(iam_data, policyId) {
    if (Object.prototype.hasOwnProperty.call(iam_data["inline_policies"], policyId)) {
        return Object.assign(iam_data["inline_policies"][policyId]);
    } else {
        return {};
    }
}

function getInlinePolicyName(iam_data, policyId) {
    if (Object.prototype.hasOwnProperty.call(iam_data["inline_policies"], policyId)) {
        return iam_data["inline_policies"][policyId]["PolicyName"].slice();
    } else {
        console.log(`Error: ${policyId} is not available under Inline Policies`)
    }
}

function getInlinePolicyDocument(iam_data, policyId) {
    if (Object.prototype.hasOwnProperty.call(iam_data["inline_policies"], policyId)) {
        return Object.assign(iam_data["inline_policies"][policyId]["PolicyDocument"]);
    } else {
        return {};
    }
}

function getInlinePolicyFindings(iam_data, policyId, riskType) {
    let exclusionStatus = getInlinePolicyExclusionStatus(iam_data, policyId);
    if (exclusionStatus === true) {
        return [];
    } else {
        return Array.from(iam_data["inline_policies"][policyId][riskType]);
    }
}

function getInlinePolicyIdsInUse(iam_data) {
    let result = [];
    let policyIds = [];
    policyIds = Array.from(Object.keys(iam_data["inline_policies"]));
    for(let i = 0; i < policyIds.length; i++){
        if (getInlinePolicyFindings(iam_data, policyIds[i], "InfrastructureModification").length === 0) {
            // console.log(`Policy ID ${policyIds[i]} does not have any findings; excluding from report findings`);
        } else {
            result.push(policyIds[i].slice())
        }
    }
    return Array.from(result);
}


function getInlinePolicyExclusionStatus(iam_data, policyId) {
    if (Object.prototype.hasOwnProperty.call(iam_data["inline_policies"], policyId)) {
        return Object.assign(iam_data["inline_policies"][policyId]["is_excluded"]);
    } else {
        return {};
    }
}

function getServicesAffectedByInlinePolicy(iam_data, policyId) {
    let servicesAffected = [];
    let actions = Array.from(iam_data["inline_policies"][policyId]["InfrastructureModification"]);
    if (actions.length > 0) {
        let action;
        for (action of actions) {
            let service = action.split(':')[0];
            if (!(service in servicesAffected)) {
                servicesAffected.push(service);
            }
        }
        return Array.from(new Set(servicesAffected)).sort();
    }
    else {
        return [];
    }
}

function getRolesLeveragingInlinePolicy(iam_data, policyId) {
    // Look through roles
    let roles;
    roles = Object.keys(iam_data["roles"]);
    const rolesInQuestion = []
    for (let i = 0; i < roles.length; i++){
        let roleId = roles[i];
        let inlinePolicies = Object.assign(iam_data["roles"][roleId]["inline_policies"]);
        if (Object.prototype.hasOwnProperty.call(inlinePolicies, policyId)) {
            rolesInQuestion.push(iam_data["roles"][roleId]["name"])
        }
    }
    return rolesInQuestion
}

function getGroupsLeveragingInlinePolicy(iam_data, policyId) {
    // Look through groups
    let groups;
    groups = Object.keys(iam_data["groups"]);
    const groupsInQuestion = []
    for (let i = 0; i < groups.length; i++){
        let groupId = groups[i];
        let inlinePolicies = Object.assign(iam_data["groups"][groupId]["inline_policies"]);
        if (Object.prototype.hasOwnProperty.call(inlinePolicies, policyId)) {
            groupsInQuestion.push(iam_data["groups"][groupId]["name"])
        }
    }
    return groupsInQuestion
}

function getUsersLeveragingInlinePolicy(iam_data, policyId) {
    // Look through users
    let users;
    users = Object.keys(iam_data["users"]);
    const usersInQuestion = []
    for (let i = 0; i < users.length; i++){
        let userId = users[i];
        let inlinePolicies = Object.assign(iam_data["users"][userId]["inline_policies"]);
        if (Object.prototype.hasOwnProperty.call(inlinePolicies, policyId)) {
            usersInQuestion.push(iam_data["users"][userId]["name"])
        }
    }
    return usersInQuestion
}

function getPrincipalTypeLeveragingInlinePolicy(iam_data, policyId, principalType){
    if (principalType === "Role") {
        return getRolesLeveragingInlinePolicy(iam_data, policyId)
    }
    if (principalType === "Group") {
        return getGroupsLeveragingInlinePolicy(iam_data, policyId)
    }
    if (principalType === "User") {
        return getUsersLeveragingInlinePolicy(iam_data, policyId)
    }
}

function getAllPrincipalTypesLeveragingInlinePolicy(iam_data, policyId){
    let users;
    let roles;
    let groups;
    users = getUsersLeveragingInlinePolicy(iam_data, policyId)
    roles = getRolesLeveragingInlinePolicy(iam_data, policyId)
    groups = getGroupsLeveragingInlinePolicy(iam_data, policyId)
    return users.concat(groups, roles)
}

function inlinePolicyAssumableByComputeService(iam_data, policyId) {
    let roles = getRolesLeveragingInlinePolicy(iam_data, policyId)
    if (!roles.length > 0){
        return []
    }
    else {
        let computeServicesAllowed = [];
        for (let i = 0; i < roles.length; i++) {
            let trustPolicyDocument = roleUtils.getTrustPolicyDocumentForRole(iam_data, roles[i])
            let computeServices = roleUtils.trustPolicyAssumableByComputeService(trustPolicyDocument)
            if (computeServices.length > 0) {
                for (let j = 0; j < computeServices.length; j++) {
                    if (!(computeServices[j] in computeServicesAllowed)) {
                        computeServicesAllowed.push(computeServices[j])
                    }
                }
            }
        }
        return computeServicesAllowed
    }
}

function getInlinePolicyItems(iam_data, inlinePolicyIds) {
    let items = [];
    for (let policyId of inlinePolicyIds){
        let policyName = getInlinePolicyName(iam_data, policyId);
        let attachedToPrincipals = getAllPrincipalTypesLeveragingInlinePolicy(iam_data, policyId);
        let services = getServicesAffectedByInlinePolicy(iam_data, policyId).length
        let infrastructureModification = getInlinePolicyFindings(iam_data, policyId, "InfrastructureModification").length;
        let privilegeEscalation = getInlinePolicyFindings(iam_data, policyId, "PrivilegeEscalation").length;
        let resourceExposure = getInlinePolicyFindings(iam_data, policyId, "ResourceExposure").length;
        let dataExfiltration = getInlinePolicyFindings(iam_data, policyId, "DataExfiltration").length;
        let credentialsExposure = getInlinePolicyFindings(iam_data, policyId, "CredentialsExposure").length;
        let serviceWildcard = getInlinePolicyFindings(iam_data, policyId, "ServiceWildcard").length;
        let computeRole = inlinePolicyAssumableByComputeService(iam_data, policyId);
        let item = {
            policy_name: policyName,
            attached_to_principals: attachedToPrincipals,
            services: services,
            service_wildcard: serviceWildcard,
            privilege_escalation: privilegeEscalation,
            resource_exposure: resourceExposure,
            data_exfiltration: dataExfiltration,
            credentials_exposure: credentialsExposure,
            infrastructure_modification: infrastructureModification,
            compute_role: computeRole,
        }
        items.push(item)
    }
    return items;
}

function getInlinePolicyNameMapping(iam_data) {
    let inlinePolicyIds = getInlinePolicyIdsInUse(iam_data);
    let names = [];
    let policyId;
    for (policyId of inlinePolicyIds) {
        if (!(getInlinePolicyExclusionStatus(iam_data, policyId))) {
            if (Object.prototype.hasOwnProperty.call(iam_data["inline_policies"], policyId)) {
                if (Object.prototype.hasOwnProperty.call(iam_data["inline_policies"][policyId], "PolicyName")) {
                    // policyName = iam_data["inline_policies"][policyId]["PolicyName"].slice();
                    names.push(
                        {
                            policy_name: iam_data["inline_policies"][policyId]["PolicyName"].slice(),
                            policy_id: policyId.slice()
                        }
                    )
                }
            }
        }
    }
    names.sort(otherUtils.compareValues("policy_name", "asc"));
    return getInlinePolicyItems(iam_data, inlinePolicyIds);
}

exports.getInlinePolicyIds = getInlinePolicyIds;
exports.getInlinePolicy = getInlinePolicy;
exports.getInlinePolicyDocument = getInlinePolicyDocument;
exports.getInlinePolicyIdsInUse = getInlinePolicyIdsInUse;
exports.getInlinePolicyFindings = getInlinePolicyFindings;
exports.getServicesAffectedByInlinePolicy = getServicesAffectedByInlinePolicy;
exports.getRolesLeveragingInlinePolicy = getRolesLeveragingInlinePolicy;
exports.getGroupsLeveragingInlinePolicy = getGroupsLeveragingInlinePolicy;
exports.getUsersLeveragingInlinePolicy = getUsersLeveragingInlinePolicy;
exports.getPrincipalTypeLeveragingInlinePolicy = getPrincipalTypeLeveragingInlinePolicy;
exports.getAllPrincipalTypesLeveragingInlinePolicy = getAllPrincipalTypesLeveragingInlinePolicy;
exports.inlinePolicyAssumableByComputeService = inlinePolicyAssumableByComputeService;
exports.getInlinePolicyItems = getInlinePolicyItems;
exports.getInlinePolicyNameMapping = getInlinePolicyNameMapping;
exports.getInlinePolicyExclusionStatus = getInlinePolicyExclusionStatus;
