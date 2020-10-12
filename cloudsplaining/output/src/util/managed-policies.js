'use strict';
var roleUtils = require("./roles")
var otherUtils = require("./other")

function getManagedPolicyIds(iam_data, managedBy) {
    let result = [];
    if (managedBy === "AWS") {
        result = Object.keys(iam_data["aws_managed_policies"]);
    }
    else if (managedBy === "Customer") {
        result = Object.keys(iam_data["customer_managed_policies"]);
    }
    return result;
}

function getManagedPolicyIdsInUse(iam_data, managedBy) {
    let result = [];
    let policyIds = [];
    if (managedBy === "AWS") {
        policyIds = Array.from(Object.keys(iam_data["aws_managed_policies"]));
    } else if (managedBy === "Customer") {
        policyIds = Array.from(Object.keys(iam_data["customer_managed_policies"]));
    }
    for(let i = 0; i < policyIds.length; i++){
        let leveraged = isManagedPolicyLeveraged(iam_data, managedBy, policyIds[i])
        if (leveraged > 0) {
            if (getManagedPolicyFindings(iam_data, managedBy, policyIds[i], "InfrastructureModification").length === 0) {
                // console.log(`Policy ID ${policyIds[i]} does not have any findings; excluding from report findings`);
            } else {
                result.push(policyIds[i].slice())
            }
        } else {
            // console.log(`Policy ID ${policyIds[i]} is not used; excluding from report findings`);
        }
    }
    return Array.from(result);
}

function getManagedPolicyExclusionStatus(iam_data, managedBy, policyId) {
    if (managedBy === "AWS") {
        return iam_data["aws_managed_policies"][policyId]["is_excluded"];
    } else if (managedBy === "Customer") {
        return iam_data["customer_managed_policies"][policyId]["is_excluded"];
    }
}

function isManagedPolicyLeveraged(iam_data, managedBy, policyId) {
    let groupCount = getPrincipalTypeLeveragingManagedPolicy(iam_data, managedBy, policyId, 'Group').length;
    let userCount = getPrincipalTypeLeveragingManagedPolicy(iam_data, managedBy, policyId, 'User').length;
    let roleCount = getPrincipalTypeLeveragingManagedPolicy(iam_data, managedBy, policyId, 'Role').length;
    return groupCount + userCount + roleCount
}

// function getManagedPolicyNames(iam_data, managedBy) {
//     let managedPolicyIds = getManagedPolicyIds(iam_data);
//     let names = [];
//     for (let i = 0; i < managedPolicyIds.length; i++) {
//         names.push(iam_data["managed-policies"][managedPolicyIds[i]]["PolicyName"])
//     }
//     names.sort();
//     return names;
// }

function getManagedPolicy(iam_data, managedBy, policyId) {
    if (managedBy === "AWS") {
        return Object.assign(iam_data["aws_managed_policies"][policyId]);
    }
    else if (managedBy === "Customer") {
        return Object.assign(iam_data["customer_managed_policies"][policyId]);
    }
}

function getManagedPolicyDocument(iam_data, managedBy, policyId) {
    if (managedBy === "AWS") {
        return Object.assign(iam_data["aws_managed_policies"][policyId]["PolicyVersionList"][0]["Document"]);
    }
    else if (managedBy === "Customer") {
        return Object.assign(iam_data["customer_managed_policies"][policyId]["PolicyVersionList"][0]["Document"]);
    }
}

function getManagedPolicyFindings(iam_data, managedBy, policyId, riskType) {
    let result = [];
    let exclusionStatus = getManagedPolicyExclusionStatus(iam_data, managedBy, policyId);
    if (exclusionStatus === true) {
        return [];
    } else {
        if (managedBy === "AWS") {
            result = Array.from(iam_data["aws_managed_policies"][policyId][riskType]);
        }
        else if (managedBy === "Customer") {
            result = Array.from(iam_data["customer_managed_policies"][policyId][riskType]);
        }
        result.sort();
        return result;
    }
}

function getManagedPolicyName(iam_data, managedBy, policyId) {
    if (managedBy === "AWS") {
        return iam_data["aws_managed_policies"][policyId]["PolicyName"].slice();
    }
    else if (managedBy === "Customer") {
        return iam_data["customer_managed_policies"][policyId]["PolicyName"].slice();
    }
}

function getServicesAffectedByManagedPolicy(iam_data, managedBy, policyId) {
    let servicesAffected = [];
    let actions = [];
    if (managedBy === "AWS") {
        actions = Array.from(iam_data["aws_managed_policies"][policyId]["InfrastructureModification"]);
    }
    else if (managedBy === "Customer") {
        actions = Array.from(iam_data["customer_managed_policies"][policyId]["InfrastructureModification"]);
    }
    let action;
    for (action of actions) {
        let service = action.split(':')[0];
        if (!(service in servicesAffected)) {
            servicesAffected.push(service);
        }
    }
    return Array.from(new Set(servicesAffected)).sort();
}

function getPrincipalTypeLeveragingManagedPolicy(iam_data, managedBy, policyId, principalType){
    if (principalType === "Role") {
        return getRolesLeveragingManagedPolicy(iam_data, managedBy, policyId)
    }
    if (principalType === "Group") {
        return getGroupsLeveragingManagedPolicy(iam_data, managedBy, policyId)
    }
    if (principalType === "User") {
        return getUsersLeveragingManagedPolicy(iam_data, managedBy, policyId)
    }
}

function getRolesLeveragingManagedPolicy(iam_data, managedBy, policyId) {
    // Look through roles
    let roles;
    roles = Array.from(Object.keys(iam_data["roles"]));
    // console.log(roles);
    var rolesInQuestion = [];
    for (let i = 0; i < roles.length; i++){
        var roleId = roles[i];
        let managedPolicies = [];
        let exclusionStatus = getManagedPolicyExclusionStatus(iam_data, managedBy, policyId);
        if (exclusionStatus === true) {
            return [];
        }
        // if it is not excluded, continue
        if (managedBy === "AWS") {
            managedPolicies = Object.assign(iam_data["roles"][roleId]["aws_managed_policies"]);
        }
        else if (managedBy === "Customer") {
            managedPolicies = Object.assign(iam_data["roles"][roleId]["customer_managed_policies"]);
        }
        if (Object.prototype.hasOwnProperty.call(managedPolicies, policyId)) {
            rolesInQuestion.push(iam_data["roles"][roleId]["name"]);
        }
    }
    return rolesInQuestion
}

function getUsersLeveragingManagedPolicy(iam_data, managedBy, policyId) {
    let users;
    users = Array.from(Object.keys(iam_data["users"]));
    var usersInQuestion = [];
    for (let i = 0; i < users.length; i++){
        var userId = users[i];
        let managedPolicies = [];
        let exclusionStatus = getManagedPolicyExclusionStatus(iam_data, managedBy, policyId);
        if (exclusionStatus === true) {
            return [];
        }
        // if it is not excluded, continue
        if (managedBy === "AWS") {
            managedPolicies = Object.assign(iam_data["users"][userId]["aws_managed_policies"]);
        }
        else if (managedBy === "Customer") {
            managedPolicies = Object.assign(iam_data["users"][userId]["customer_managed_policies"]);
        }
        if (Object.prototype.hasOwnProperty.call(managedPolicies, policyId)) {
            usersInQuestion.push(iam_data["users"][userId]["name"]);
        }
    }
    return usersInQuestion
}

function getGroupsLeveragingManagedPolicy(iam_data, managedBy, policyId) {
    let groups;
    groups = Object.keys(iam_data["groups"]);
    var groupsInQuestion = [];
    for (let i = 0; i < groups.length; i++){
        var groupId = groups[i];
        let managedPolicies = [];
        let exclusionStatus = getManagedPolicyExclusionStatus(iam_data, managedBy, policyId);
        if (exclusionStatus === true) {
            return [];
        }
        // if it is not excluded, continue
        if (managedBy === "AWS") {
            managedPolicies = Object.assign(iam_data["groups"][groupId]["aws_managed_policies"]);
        }
        else if (managedBy === "Customer") {
            managedPolicies = Object.assign(iam_data["groups"][groupId]["customer_managed_policies"]);
        }
        if (Object.prototype.hasOwnProperty.call(managedPolicies, policyId)) {
            groupsInQuestion.push(iam_data["groups"][groupId]["name"]);
        }
    }
    return groupsInQuestion
}

function getAllPrincipalsLeveragingManagedPolicy(iam_data, managedBy, policyId) {
    let users;
    let groups;
    let roles;
    users = getUsersLeveragingManagedPolicy(iam_data, managedBy, policyId)
    groups = getGroupsLeveragingManagedPolicy(iam_data, managedBy, policyId)
    roles = getRolesLeveragingManagedPolicy(iam_data, managedBy, policyId)
    return users.concat(groups, roles)
}

function managedPolicyAssumableByComputeService(iam_data, managedBy, policyId) {
    let roles = getRolesLeveragingManagedPolicy(iam_data, managedBy, policyId)
    if (!roles.length > 0){
        // console.log(`computeServicesAllowed by ${policyId}: []`)
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
        // console.log(`computeServicesAllowed by ${policyId}: ${computeServicesAllowed}`)
        return computeServicesAllowed
    }
}

function getManagedPolicyItems(iam_data, managedBy, managedPolicyIds) {
    let items = [];
    for (let policyId of managedPolicyIds){
        let policyName = getManagedPolicyName(iam_data, managedBy, policyId);
        let attachedToPrincipals = getAllPrincipalsLeveragingManagedPolicy(iam_data, managedBy, policyId);
        let services = getServicesAffectedByManagedPolicy(iam_data, managedBy, policyId).length
        let infrastructureModification = getManagedPolicyFindings(iam_data, managedBy, policyId, "InfrastructureModification").length;
        let privilegeEscalation = getManagedPolicyFindings(iam_data, managedBy, policyId, "PrivilegeEscalation").length;
        let resourceExposure = getManagedPolicyFindings(iam_data, managedBy, policyId, "ResourceExposure").length;
        let dataExfiltration = getManagedPolicyFindings(iam_data, managedBy, policyId, "DataExfiltration").length;
        let credentialsExposure = getManagedPolicyFindings(iam_data, managedBy, policyId, "CredentialsExposure").length;
        let serviceWildcard = getManagedPolicyFindings(iam_data, managedBy, policyId, "ServiceWildcard").length;
        let computeRole = managedPolicyAssumableByComputeService(iam_data, managedBy, policyId);
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
            compute_role: computeRole
        }
        items.push(item)
    }
    return items;
}

function getManagedPolicyNameMapping(iam_data, managedBy) {
    let managedPolicyIds = getManagedPolicyIdsInUse(iam_data, managedBy);
    let names = [];
    let policyId;
    for (policyId of managedPolicyIds) {
        if (managedBy === "AWS") {
            let policyName = iam_data["aws_managed_policies"][policyId]["PolicyName"];
            names.push({policy_name: policyName, policy_id: policyId})
        } else if (managedBy === "Customer") {
            let policyName = iam_data["customer_managed_policies"][policyId]["PolicyName"];
            names.push({policy_name: policyName, policy_id: policyId})
        }
    }
    names.sort(otherUtils.compareValues("policy_name", "asc"));
    return getManagedPolicyItems(iam_data, managedBy, managedPolicyIds);
}

exports.getManagedPolicyIds = getManagedPolicyIds;
exports.getManagedPolicyIdsInUse = getManagedPolicyIdsInUse;
exports.getManagedPolicyFindings = getManagedPolicyFindings;
exports.getManagedPolicy = getManagedPolicy;
exports.getManagedPolicyDocument = getManagedPolicyDocument;
exports.getRolesLeveragingManagedPolicy = getRolesLeveragingManagedPolicy;
exports.getServicesAffectedByManagedPolicy = getServicesAffectedByManagedPolicy;
exports.getManagedPolicyName = getManagedPolicyName;
exports.getUsersLeveragingManagedPolicy = getUsersLeveragingManagedPolicy;
exports.getGroupsLeveragingManagedPolicy = getGroupsLeveragingManagedPolicy;
exports.isManagedPolicyLeveraged = isManagedPolicyLeveraged;
exports.getPrincipalTypeLeveragingManagedPolicy = getPrincipalTypeLeveragingManagedPolicy;
exports.managedPolicyAssumableByComputeService = managedPolicyAssumableByComputeService;
exports.getAllPrincipalsLeveragingManagedPolicy = getAllPrincipalsLeveragingManagedPolicy;
exports.getManagedPolicyItems = getManagedPolicyItems;
exports.getManagedPolicyNameMapping = getManagedPolicyNameMapping;
exports.getManagedPolicyExclusionStatus = getManagedPolicyExclusionStatus;
