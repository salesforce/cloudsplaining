<template>
    <div v-bind:id="inlineOrManaged.toLowerCase() + '-policy'  + '-' + policyId + '-' + 'card-details'">
        <div class="card">
            <!--Policy Document-->
            <div class="card-header">
                <a class="card-link" data-toggle="collapse"
                   v-bind:data-parent="'#' + inlineOrManaged.toLowerCase() + '-policy' + '-' + policyId + '-' + 'card-details'"
                   v-bind:href="'#' + inlineOrManaged.toLowerCase() + '-policy' + '-' + policyId + '-' +'policydocument'"
                >Policy Document</a>
            </div>
            <div class="panel-collapse collapse"
                 v-bind:id="inlineOrManaged.toLowerCase() + '-policy' + '-' + policyId + '-' +'policydocument'">
                <div class="card-body">
<pre><code>
{{ JSON.parse(JSON.stringify(policyDocument(policyId), undefined, '\t')) }}
</code></pre>
                </div>
            </div><!--Policy Document-->

            <!--Assumable by Compute Service-->
            <template v-if="policyAssumableByComputeService(policyId).length > 0">
                <div class="card-header">
                    <a class="card-link" data-toggle="collapse"
                       v-bind:data-parent="'#' + inlineOrManaged.toLowerCase() + '-policy' + '-' + policyId + '-' + 'card-details'"
                       v-bind:href="'#' + inlineOrManaged.toLowerCase() + '-policy' + '-' + policyId + '-' +'assumable'"
                    >Compute Services that leverage this IAM Policy via AssumeRole</a>
                </div>
                <div class="panel-collapse collapse"
                     v-bind:id="inlineOrManaged.toLowerCase() + '-policy' + '-' + policyId + '-' +'assumable'">
                    <div class="card-body">
<pre><code>
{{ JSON.parse(JSON.stringify(policyAssumableByComputeService(policyId), undefined, '\t')) }}
</code></pre>
                    </div>
                </div>
            </template><!--Assumable by Compute Service-->

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

    export default {
        name: "FindingDetails",
        components: {
            PrivilegeEscalationDetails,
            StandardRiskDetails
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
