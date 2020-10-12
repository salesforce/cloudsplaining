<template>
    <div>
        <div v-for="risk in riskDetailsToDisplay" :key="risk.risk_type">
            <template v-if="findings(policyId, risk.risk_type).length > 0">
                <div class="card-header">
                <a class="card-link" data-toggle="collapse"
                   v-bind:data-parent="`#${inlineOrManaged.toLowerCase()}-policy-${policyId}-card-details`"
                   v-bind:href="`#${inlineOrManaged.toLowerCase()}-policy-${policyId}-${convertStringToKebabCase(risk.risk_type)}`"
                >{{ convertStringToSpaceCase(risk.risk_type) }}</a>
                </div>
            </template>
            <template v-if="findings(policyId, risk.risk_type).length > 0">
                <div class="panel-collapse collapse"
                     v-bind:id="`${inlineOrManaged.toLowerCase()}-policy-${policyId}-${convertStringToKebabCase(risk.risk_type)}`">
                    <div class="card-body">
<pre><code>
{{ JSON.parse(JSON.stringify(findings(policyId, risk.risk_type), undefined, '\t')) }}
</code></pre>
                    </div>
                </div>
            </template>
        </div>
    </div>
</template>

<script>
    const managedPoliciesUtil = require('../../util/managed-policies');
    const inlinePoliciesUtil = require('../../util/inline-policies');
    const glossary = require('../../util/glossary');
    let otherUtil = require('../../util/other');

    export default {
        name: "StandardRiskDetails",
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
            },
            riskDetailsToDisplay() {
                return glossary.getRiskDetailsToDisplay()
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
            convertStringToSpaceCase: function(string) {
                return otherUtil.convertStringToSpaceCase(string)
            },
            convertStringToKebabCase: function(string) {
                return otherUtil.convertStringToKebabCase(string)
            }
        }
    }
</script>

<style scoped>

</style>
