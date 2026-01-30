<template>
    <div v-if="policyAssumableByComputeService(policyId).length > 0">
        <div class="card-header">
            <b-button
                class="card-link p-0"
                variant="link"
                v-b-toggle="collapseId"
            >
                Compute Services that leverage this IAM Policy via AssumeRole
            </b-button>
        </div>
        <b-collapse
            v-model="isExpanded"
            :id="collapseId"
            class="panel-collapse"
        >
            <div class="card-body">
                <span v-html="getRiskDescription('AssumableByComputeService')"></span>
<pre><code>
{{ JSON.parse(JSON.stringify(policyAssumableByComputeService(policyId), undefined, '\t')) }}
</code></pre>
            </div>
        </b-collapse>
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
            collapseId() {
                return `${this.inlineOrManaged.toLowerCase()}-policy-${this.policyId}-assumable`;
            },
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
        data() {
            return {
                isExpanded: false
            }
        },
        watch: {
            toggleData: {
                handler(data) {
                    if (data.isAllExpanded) {
                        this.isExpanded = true;
                    }
                    if (data.isAllCollapsed) {
                        this.isExpanded = false;
                    }
                },
                deep: true
            }
        }
    }
</script>

<style scoped>

</style>
