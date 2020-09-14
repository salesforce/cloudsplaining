var managedPolicyUtils = require("./managed-policies");
var otherUtils = require("./other");
// var roleUtils = require("./roles")
// var principalUtils = require("./principals")

function getTaskTableManagedPolicyItems(iam_data, managedBy, managedPolicyIds) {
    let items = [];
    for (let policyId of managedPolicyIds){
        let leveraged = managedPolicyUtils.isManagedPolicyLeveraged(iam_data, managedBy, policyId);
        // if the policy is not leveraged, skip it
        if (leveraged === 0) {
            console.log(`${policyId} has leveraged length of ${leveraged} `)
            continue;
        }
        let policyName = managedPolicyUtils.getManagedPolicyName(iam_data, managedBy, policyId);
        let attachedToPrincipals = managedPolicyUtils.getAllPrincipalsLeveragingManagedPolicy(iam_data, managedBy, policyId);
        let services = managedPolicyUtils.getServicesAffectedByManagedPolicy(iam_data, managedBy, policyId)
        let infrastructureModification = managedPolicyUtils.getManagedPolicyFindings(iam_data, managedBy, policyId, "InfrastructureModification");
        let privilegeEscalation = managedPolicyUtils.getManagedPolicyFindings(iam_data, managedBy, policyId, "PrivilegeEscalation");
        let resourceExposure = managedPolicyUtils.getManagedPolicyFindings(iam_data, managedBy, policyId, "ResourceExposure");
        let dataExfiltration = managedPolicyUtils.getManagedPolicyFindings(iam_data, managedBy, policyId, "DataExfiltration");
        let rolesLeveragingPolicy = [];
        let computeRole = [];
        // if ( managedPolicyUtils.getPrincipalTypeLeveragingManagedPolicy(policyId, 'Role').length > 0 ) {
        rolesLeveragingPolicy = managedPolicyUtils.getPrincipalTypeLeveragingManagedPolicy(policyId, 'Role')
        computeRole = managedPolicyUtils.managedPolicyAssumableByComputeService(iam_data, managedBy, policyId);
        // }
        // let groupMembers = [];
        let groupsLeveragingPolicy;
        // if ( managedPolicyUtils.getPrincipalTypeLeveragingManagedPolicy(policyId, 'Group').length > 0 ) {
        groupsLeveragingPolicy = managedPolicyUtils.getPrincipalTypeLeveragingManagedPolicy(policyId, 'Group')
            // run a for loop on the groups and their group members
        // }
        // let groupMembership = [];
        let usersLeveragingPolicy = [];
        // if ( managedPolicyUtils.getPrincipalTypeLeveragingManagedPolicy(policyId, 'User').length > 0 ) {
        usersLeveragingPolicy = managedPolicyUtils.getPrincipalTypeLeveragingManagedPolicy(policyId, 'User')
            // run a for loop on the groups and their group members
        // }

        let policyDocument = managedPolicyUtils.getManagedPolicyDocument(iam_data, managedBy, policyId)

        let item = {
            policy_name: policyName,
            policy_id: policyId,
            policy_document: policyDocument,
            attached_to_principals: attachedToPrincipals,
            services: services,
            privilege_escalation: privilegeEscalation,
            resource_exposure: resourceExposure,
            data_exfiltration: dataExfiltration,
            infrastructure_modification: infrastructureModification,
            compute_role: computeRole,
            roles_leveraging_policy: rolesLeveragingPolicy,
            groups_leveraging_policy: groupsLeveragingPolicy,
            users_leveraging_policy: usersLeveragingPolicy,
            show_details: 0
        }
        items.push(item)
    }
    return items;
}

function getTaskTableMapping(iam_data, managedBy) {
    let managedPolicyIds = managedPolicyUtils.getManagedPolicyIdsInUse(iam_data, managedBy);
    let names = [];
    let policyId;
    for (policyId of managedPolicyIds) {
        if (managedBy === "AWS") {
            let policyName = Object.assign(iam_data["aws_managed_policies"][policyId]["PolicyName"]);
            names.push({policy_name: policyName, policy_id: policyId})
        } else if (managedBy === "Customer") {
            let policyName = Object.assign(iam_data["customer_managed_policies"][policyId]["PolicyName"]);
            names.push({policy_name: policyName, policy_id: policyId})
        }
    }
    names.sort(otherUtils.compareValues("policy_name", "asc"));
    return getTaskTableManagedPolicyItems(iam_data, managedBy, managedPolicyIds);
}

exports.getTaskTableManagedPolicyItems = getTaskTableManagedPolicyItems;
exports.getTaskTableMapping = getTaskTableMapping;