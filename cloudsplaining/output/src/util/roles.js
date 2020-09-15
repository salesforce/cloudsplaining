'use strict';
// var managedPolicies = require("./managed-policies")
// var inlinePolicies = require("./inline-policies")
const SERVICE_PREFIXES_WITH_COMPUTE_ROLES = ["ec2", "eks", "ecs-tasks", "lambda"]

function getTrustPolicyDocumentForRole(iam_data, roleId) {
    let result;
    if (Object.prototype.hasOwnProperty.call(iam_data["roles"], roleId)) {
        if (Object.prototype.hasOwnProperty.call(iam_data["roles"][roleId], "assume_role_policy")) {
            result = iam_data["roles"][roleId]["assume_role_policy"]["PolicyDocument"];
        }
    }
    return result
}

function trustPolicyAssumableByComputeService(assumeRolePolicyDocument) {
    let statements;
    let computeServicesAllowed = [];
    if (typeof assumeRolePolicyDocument === 'object' && assumeRolePolicyDocument !== null) {
        if (Object.prototype.hasOwnProperty.call(assumeRolePolicyDocument, "Statement")) {
            statements = assumeRolePolicyDocument["Statement"]
            for (let i = 0; i < statements.length; i++){
                var statement = statements[i];
                if (Object.prototype.hasOwnProperty.call(statement, "Action")){
                    if (Array.isArray(statement["Action"])) {
                        if (!("sts:AssumeRole" in statement["Action"])) {
                            return [];
                        }
                    }
                    else if (typeof statement["Action"] == 'string') {
                        if (!("sts:AssumeRole" === statement["Action"])) {
                            return [];
                        }
                    }

                }
                if (Object.prototype.hasOwnProperty.call(statement, "Action")){
                    if (Object.prototype.hasOwnProperty.call(statement["Principal"], "Service")) {
                        if (Array.isArray(statement["Principal"]["Service"])) {
                            for (let j = 0; j < statement["Principal"]["Service"].length; j++) {
                                let service = statement["Principal"]["Service"][j]
                                if (service.endsWith(".amazonaws.com")) {
                                    let servicePrefixToEvaluate = service.split(".")
                                    if (servicePrefixToEvaluate in SERVICE_PREFIXES_WITH_COMPUTE_ROLES) {
                                        computeServicesAllowed.push(servicePrefixToEvaluate)
                                    }
                                }
                            }
                        }
                        else if (typeof statement["Principal"]["Service"] == 'string') {
                            let service = statement["Principal"]["Service"]
                            if (service.endsWith(".amazonaws.com")) {
                                let servicePrefixToEvaluate = service.split(".")[0]
                                if (SERVICE_PREFIXES_WITH_COMPUTE_ROLES.includes(servicePrefixToEvaluate)) {
                                    computeServicesAllowed.push(servicePrefixToEvaluate)
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    return computeServicesAllowed
}

exports.getTrustPolicyDocumentForRole = getTrustPolicyDocumentForRole;
exports.trustPolicyAssumableByComputeService = trustPolicyAssumableByComputeService;
