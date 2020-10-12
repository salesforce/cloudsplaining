<template>
    <div>
        <!--Alert boxes for different risks-->
        <div v-for="riskType in highRisksToDisplayAlertsFor" :key="riskType">
            <template v-if="findings(policyId, riskType).length > 0">
                <div v-bind:class="'alert alert-' + getRiskAlertIndicatorColor(riskType) + ' popovers'" data-html="true" data-placement="top"
                     data-toggle="popover"
                     role="alert"
                     :title="convertStringToSpaceCase(riskType)"
                     v-bind:data-content="getRiskDefinition(riskType)">{{ convertStringToSpaceCase(riskType) }}
                </div>
            </template>
        </div>
        <!--Alert for Assumable By Compute Service-->
        <template v-if="policyAssumableByComputeService(policyId).length > 0">
            <div v-bind:class="'alert alert-' + getRiskAlertIndicatorColor('AssumableByComputeService') + ' popovers'" data-html="true" data-placement="top"
                 data-toggle="popover"
                 role="alert"
                 title="Policy leveraged by Compute Service Role"
                 v-bind:data-content="getRiskDefinition('AssumableByComputeService')">Policy
                leveraged by Compute Service Role
            </div>
        </template>
    </div>
</template>

<script>
    let glossary = require('../../util/glossary');
    let otherUtil = require('../../util/other');
    const inlinePoliciesUtil = require('../../util/inline-policies');
    const managedPoliciesUtil = require('../../util/managed-policies');

    var highRisksToDisplayAlertsFor = [
        "CredentialsExposure",
        "DataExfiltration",
        "ResourceExposure",
        "ServiceWildcard",
        "PrivilegeEscalation",
    ]

    export default {
        name: "RiskAlertIndicators",
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
            highRisksToDisplayAlertsFor() {
                return highRisksToDisplayAlertsFor
            }
        },
        methods: {
            getRiskDefinition: function (riskType) {
                return glossary.getRiskDefinition(riskType)
            },
            getRiskAlertIndicatorColor: function (riskType) {
                return glossary.getRiskAlertIndicatorColor(riskType)
            },
            findings: function (policyId, riskType) {
                if (this.managedBy === "Inline") {
                    return inlinePoliciesUtil.getInlinePolicyFindings(this.iam_data, policyId, riskType)
                } else {
                    return managedPoliciesUtil.getManagedPolicyFindings(this.iam_data, this.managedBy, policyId, riskType);
                }
            },
            policyAssumableByComputeService: function (policyId) {
                if (this.managedBy === "Inline") {
                    return inlinePoliciesUtil.inlinePolicyAssumableByComputeService(this.iam_data, policyId);
                } else {
                    return managedPoliciesUtil.managedPolicyAssumableByComputeService(this.iam_data, this.managedBy, policyId);
                }
            },
            convertStringToSpaceCase: function(string) {
                return otherUtil.convertStringToSpaceCase(string)
            }

        }
    }
</script>

<style scoped>

</style>
