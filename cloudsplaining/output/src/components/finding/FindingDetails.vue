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

            <!--Data Exfiltration-->
            <template v-if="findings(policyId, 'DataExfiltration').length > 0">
                <div class="card-header">
                    <a class="card-link" data-toggle="collapse"
                       v-bind:data-parent="'#' + inlineOrManaged.toLowerCase() + '-policy' + '-' + policyId + '-' + 'card-details'"
                       v-bind:href="'#' + inlineOrManaged.toLowerCase() + '-policy' + '-' + policyId + '-' +'data-exfiltration'"
                    >Data Exfiltration</a>
                </div>
                <div class="panel-collapse collapse"
                     v-bind:id="inlineOrManaged.toLowerCase() + '-policy' + '-' + policyId + '-' +'data-exfiltration'">
                    <div class="card-body">
<pre><code>
{{ JSON.parse(JSON.stringify(findings(policyId, 'DataExfiltration'), undefined, '\t')) }}
</code></pre>
                    </div>
                </div>
            </template><!--Data Exfiltration-->

            <!--Infrastructure Modification Actions-->
            <div class="card-header">
                <a class="card-link" data-toggle="collapse"
                   v-bind:data-parent="'#' + inlineOrManaged.toLowerCase() + '-policy' + '-' + policyId + '-' + 'card-details'"
                   v-bind:href="'#' + inlineOrManaged.toLowerCase() + '-policy' + '-' + policyId + '-' +'infrastructure-modification-actions'"
                >Infrastructure Modification Actions</a>
            </div>
            <div class="panel-collapse collapse"
                 v-bind:id="inlineOrManaged.toLowerCase() + '-policy' + '-' + policyId + '-' +'infrastructure-modification-actions'">
                <div class="card-body">
<pre><code>
{{ JSON.parse(JSON.stringify(findings(policyId, 'InfrastructureModification'), undefined, '\t')) }}
</code></pre>
                </div>
            </div><!--Infrastructure Modification Actions-->

            <!--PrivilegeEscalation-->
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
            </div><!--Privilege Escalation-->

            <!--ResourceExposure-->
            <div v-if="findings(policyId, 'ResourceExposure').length > 0">
                <div class="card-header">
                    <a class="card-link" data-toggle="collapse"
                       v-bind:data-parent="'#' + inlineOrManaged.toLowerCase() + '-policy' + '-' + policyId + '-' + 'card-details'"
                       v-bind:href="'#' + inlineOrManaged.toLowerCase() + '-policy' + '-' + policyId + '-' +'resource-exposure'"
                    >Resource Exposure</a>
                </div>
                <div class="panel-collapse collapse"
                     v-bind:id="inlineOrManaged.toLowerCase() + '-policy' + '-' + policyId + '-' +'resource-exposure'">
                    <div class="card-body">
<pre><code>
{{ JSON.parse(JSON.stringify(findings(policyId, 'ResourceExposure'), undefined, '\t')) }}
</code></pre>
                    </div>
                </div>
            </div><!--Resource Exposure-->
        </div>
    </div>

</template>

<script>
    const managedPoliciesUtil = require('../../util/managed-policies');
    const inlinePoliciesUtil = require('../../util/inline-policies');

    export default {
        name: "FindingDetails",
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
