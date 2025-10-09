<template>
    <div v-if="policyAssumableByComputeService(policyId).length > 0">
        <div class="card-header">
            <a class="card-link" data-toggle="collapse"
               v-bind:data-parent="'#' + inlineOrManaged.toLowerCase() + '-policy' + '-' + policyId + '-' + 'card-details'"
               v-bind:href="'#' + inlineOrManaged.toLowerCase() + '-policy' + '-' + policyId + '-' +'assumable'"
            >Compute Services that leverage this IAM Policy via AssumeRole</a>
        </div>
        <div class="panel-collapse collapse"
             ref="AssumeRoleDetailsDiv"
             v-bind:id="inlineOrManaged.toLowerCase() + '-policy' + '-' + policyId + '-' +'assumable'">
            <div class="card-body">
                <span v-html="getRiskDescription('AssumableByComputeService')"></span>
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
    var md = require('markdown-it')({
        html: true,
        linkify: true,
        typographer: true
    });
    import assumableByComputeServiceRaw from '../../assets/definition-assumable-by-compute-service.md'
    const assumableByComputeServiceDescription = md.render(assumableByComputeServiceRaw)


    export default {
        name: "AssumeRoleDetails",
        inject: ['toggleData'],
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
            },
            getRiskDescription: function (riskType) {
                if (riskType === "AssumableByComputeService") {
                    return assumableByComputeServiceDescription
                }
            }
        },
        watch: {
            toggleData: {
                handler(data) {
                    if (data.isAllExpanded && this.$refs['AssumeRoleDetailsDiv']) {
                        this.$refs['AssumeRoleDetailsDiv'].classList.add('show');
                    }
                    if (data.isAllCollapsed && this.$refs['AssumeRoleDetailsDiv']) {
                        this.$refs['AssumeRoleDetailsDiv'].classList.remove('show');
                    }
                },
                deep: true
            }
        }
    }
</script>

<style scoped>

</style>
