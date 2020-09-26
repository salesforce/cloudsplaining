<template>
    <div v-if="findings(policyId, 'PrivilegeEscalation').length > 0">
        <div class="card-header">
            <a class="card-link" data-toggle="collapse"
               v-bind:data-parent="'#' + inlineOrManaged.toLowerCase() + '-policy' + '-' + policyId + '-' + 'card-details'"
               v-bind:href="'#' + inlineOrManaged.toLowerCase() + '-policy' + '-' + policyId + '-' +'privilege-escalation'"
            >Privilege Escalation</a>
        </div>
        <div class="panel-collapse collapse"
             v-bind:id="inlineOrManaged.toLowerCase() + '-policy' + '-' + policyId + '-' +'privilege-escalation'">
            <!--TODO: Format the Privilege Escalation stuff-->
            <div class="card-body">
<pre><code>
{{ JSON.parse(JSON.stringify(findings(policyId, 'PrivilegeEscalation'), undefined, '\t')) }}
</code></pre>
            </div>
        </div>
    </div>
</template>

<script>
    const managedPoliciesUtil = require('../../util/managed-policies');
    const inlinePoliciesUtil = require('../../util/inline-policies');

    export default {
        name: "PrivilegeEscalationDetails",
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
        }
    }
</script>

<style scoped>

</style>
