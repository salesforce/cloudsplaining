<template>
    <div>
        <template v-if="managedBy === 'AWS' || managedBy === 'Customer'">
                <!--Alert for Risk Type: Privilege Escalation Exposure-->
                <template v-if="managedPolicyFindings(policyId, 'PrivilegeEscalation').length > 0">
                    <div class="alert alert-danger popovers" data-html="true" data-placement="top"
                         data-toggle="popover"
                         role="alert"
                         title="Privilege Escalation"
                         v-bind:data-content="getRiskDefinition('PrivilegeEscalation')">Privilege Escalation
                    </div>
                </template>
                <!--Alert for Risk Type: Data Exfiltration Escalation-->
                <template v-if="managedPolicyFindings(policyId, 'DataExfiltration').length > 0">
                    <div class="alert alert-warning popovers" data-html="true" data-placement="top"
                         data-toggle="popover"
                         role="alert"
                         title="Data Exfiltration"
                         v-bind:data-content="getRiskDefinition('DataExfiltration')">Data Exfiltration
                    </div>
                </template>
                <!--Alert for Risk Type: Resource Exposure-->
                <template v-if="managedPolicyFindings(policyId, 'ResourceExposure').length > 0">
                    <div class="alert alert-danger popovers" data-html="true" data-placement="top"
                         data-toggle="popover"
                         role="alert"
                         title="Resource Exposure"
                         v-bind:data-content="getRiskDefinition('ResourceExposure')">Resource Exposure
                    </div>
                </template>
                <!--Alert for Assumable By Compute Service-->
                <template v-if="managedPolicyAssumableByComputeService(policyId).length > 0">
                    <div class="alert alert-info popovers" data-html="true" data-placement="top"
                         data-toggle="popover"
                         role="alert"
                         title="Policy leveraged by Compute Service Role"
                         v-bind:data-content="getRiskDefinition('AssumableByComputeService')">Policy
                        leveraged by Compute Service Role
                    </div>
                </template>
        </template>
        <template v-if="managedBy === 'Inline'">
            <!--Alert for Risk Type: Privilege Escalation Exposure-->
            <template v-if="inlinePolicyFindings(policyId, 'PrivilegeEscalation').length > 0">
                <div class="alert alert-danger popovers" data-html="true" data-placement="top"
                     data-toggle="popover"
                     role="alert"
                     title="Privilege Escalation"
                     v-bind:data-content="getRiskDefinition('PrivilegeEscalation')">Privilege Escalation
                </div>
            </template>
            <!--Alert for Risk Type: Data Exfiltration Escalation-->
            <template v-if="inlinePolicyFindings(policyId, 'DataExfiltration').length > 0">
                <div class="alert alert-warning popovers" data-html="true" data-placement="top"
                     data-toggle="popover"
                     role="alert"
                     title="Data Exfiltration"
                     v-bind:data-content="getRiskDefinition('DataExfiltration')">Data Exfiltration
                </div>
            </template>
            <!--Alert for Risk Type: Resource Exposure-->
            <template v-if="inlinePolicyFindings(policyId, 'ResourceExposure').length > 0">
                <div class="alert alert-danger popovers" data-html="true" data-placement="top"
                     data-toggle="popover"
                     role="alert"
                     title="Resource Exposure"
                     v-bind:data-content="getRiskDefinition('ResourceExposure')">Resource Exposure
                </div>
            </template>
            <!--Alert for Assumable By Compute Service-->
            <template v-if="inlinePolicyAssumableByComputeService(policyId).length > 0">
                <div class="alert alert-info popovers" data-html="true" data-placement="top"
                     data-toggle="popover"
                     role="alert"
                     title="Policy leveraged by Compute Service Role"
                     v-bind:data-content="getRiskDefinition('AssumableByComputeService')">Policy
                    leveraged by Compute Service Role
                </div>
            </template>
        </template>
    </div>
</template>

<script>
    let glossary = require('../../util/glossary');
    const inlinePoliciesUtil = require('../../util/inline-policies');
    const managedPoliciesUtil = require('../../util/managed-policies');

    export default {
        name: "RiskAlertIndicators",
        props: {
            // riskDefinitions: {
            //     type: Array
            // },
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
        methods: {
            getRiskDefinition: function (riskType) {
                return glossary.getRiskDefinition(riskType)
            },
            inlinePolicyFindings: function (policyId, riskType) {
                return inlinePoliciesUtil.getInlinePolicyFindings(this.iam_data, policyId, riskType);
            },
            managedPolicyFindings: function (policyId, riskType) {
                return managedPoliciesUtil.getManagedPolicyFindings(this.iam_data, this.managedBy, policyId, riskType);
            },
            inlinePolicyAssumableByComputeService: function (policyId) {
                return inlinePoliciesUtil.inlinePolicyAssumableByComputeService(this.iam_data, policyId);
            },
            managedPolicyAssumableByComputeService: function (policyId) {
                return managedPoliciesUtil.managedPolicyAssumableByComputeService(this.iam_data, this.managedBy, policyId);
            },
        }
    }
</script>

<style scoped>

</style>
