<template>
    <div v-if="policyAssumableByComputeService(policyId).length > 0">
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
    </div>
</template>

<script>
    const managedPoliciesUtil = require('../../util/managed-policies');
    const inlinePoliciesUtil = require('../../util/inline-policies');

    export default {
        name: "AssumeRoleDetails",
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
