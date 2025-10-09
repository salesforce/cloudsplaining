<template>
    <div v-bind:id="inlineOrManaged.toLowerCase() + '-policy'  + '-' + policyId + '-' + 'card-details'">
        <div class="card">

            <PolicyDocumentDetails
                :policy-id="policyId"
                :iam_data="iam_data"
                :managed-by="managedBy"
            ></PolicyDocumentDetails>

            <AssumeRoleDetails
                :policy-id="policyId"
                :iam_data="iam_data"
                :managed-by="managedBy"
            ></AssumeRoleDetails>

            <PrivilegeEscalationDetails
                :policy-id="policyId"
                :iam_data="iam_data"
                :managed-by="managedBy"
            ></PrivilegeEscalationDetails>

            <StandardRiskDetails
                :policy-id="policyId"
                :iam_data="iam_data"
                :managed-by="managedBy"
            ></StandardRiskDetails>

        </div>
    </div>

</template>

<script>
    const managedPoliciesUtil = require('../../util/managed-policies');
    const inlinePoliciesUtil = require('../../util/inline-policies');
    import PrivilegeEscalationDetails from "./PrivilegeEscalationDetails";
    import StandardRiskDetails from "./StandardRiskDetails";
    import AssumeRoleDetails from "./AssumeRoleDetails";
    import PolicyDocumentDetails from "./PolicyDocumentDetails";

    export default {
        name: "FindingDetails",
        components: {
            PolicyDocumentDetails,
            AssumeRoleDetails,
            StandardRiskDetails,
            PrivilegeEscalationDetails,
        },
        props: {
            // Either "Inline", "AWS", or "Customer"
            managedBy: {
                type: String
            },
            policyId: {
                type: String
            },
            iam_data: {
                type: Object
            },
        },
        computed: {
            inlineOrManaged() {
                if ((this.managedBy === "AWS") || (this.managedBy === "Customer")) {
                    return "Managed"
                } else {
                    return "Inline"
                }
            }
        },
        methods: {
            findings: function (policyId, riskType) {
                if (this.managedBy === "Inline") {
                    return inlinePoliciesUtil.getInlinePolicyFindings(this.iam_data, policyId, riskType)
                } else {
                    return managedPoliciesUtil.getManagedPolicyFindings(this.iam_data, this.managedBy, policyId, riskType);
                }
            },
            policyDocument: function(policyId) {
                if (this.managedBy === "Inline") {
                    return inlinePoliciesUtil.getInlinePolicyDocument(this.iam_data, policyId);
                } else {
                    return managedPoliciesUtil.getManagedPolicyDocument(this.iam_data, this.managedBy, policyId);
                }
            },
            policyAssumableByComputeService: function(policyId) {
                if (this.managedBy === "Inline") {
                    return inlinePoliciesUtil.inlinePolicyAssumableByComputeService(this.iam_data, policyId);
                } else {
                    return managedPoliciesUtil.managedPolicyAssumableByComputeService(this.iam_data, this.managedBy, policyId);
                }
            }

        }
    }
</script>

<style scoped>

</style>
