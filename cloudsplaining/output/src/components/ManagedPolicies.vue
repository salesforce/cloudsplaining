<template>
    <div>
        <div v-bind:key="policyId" v-for="policyId in getManagedPolicyIdsInUse">
                <div class="row">
                    <div class="col-md-5">
                        <div class="card">
                            <h6 class="card-header" v-bind:id="'managed-policy' + '.' + policyId + '.' + 'card'">
                                Name: {{ managedPolicy(policyId)["PolicyName"] }}
                                <br>
                                <br>
                                PolicyId: {{ policyId }}
                                <br>
                                <br>
                                Attached to Principals:
                                <ul>
                                    <li v-if="principalTypeLeveragingManagedPolicy(policyId, 'Role').length > 0">
                                        Roles:
                                        <ul>
                                            <li v-bind:key="role"
                                                v-for="role in principalTypeLeveragingManagedPolicy(policyId, 'Role')">
                                                {{ role }}
                                            </li>
                                        </ul>
                                    </li>
                                    <li v-if="principalTypeLeveragingManagedPolicy(policyId, 'User').length > 0">
                                        Users:
                                        <ul>
                                            <li v-bind:key="user"
                                                v-for="user in principalTypeLeveragingManagedPolicy(policyId, 'User')">
                                                {{ user }}
                                            </li>
                                        </ul>
                                    </li>
                                    <li v-if="principalTypeLeveragingManagedPolicy(policyId, 'Group').length > 0">
                                        Groups:
                                        <ul>
                                            <li v-bind:key="group"
                                                v-for="group in principalTypeLeveragingManagedPolicy(policyId, 'Group')">
                                                {{ group }}
                                            </li>
                                        </ul>
                                    </li>
                                </ul>
                            </h6>
                            <div class="card-body">
                                <p class="card-text">
                                    Services: {{ servicesAffectedByManagedPolicy(policyId).length
                                    }}
                                    <br>
                                    Infrastructure Modification Actions: {{
                                    managedPolicyFindings(policyId,
                                    "InfrastructureModification").length }}
                                    <br>
                                </p>
                            </div> <!-- /card-text -->
                            <div class="card-footer">
                                <!--Alert for Risk Type: Privilege Escalation Exposure-->
                                <template
                                        v-if="managedPolicyFindings(policyId, 'PrivilegeEscalation').length > 0">
                                    <div class="alert alert-danger popovers" data-html="true" data-placement="top"
                                         data-toggle="popover"
                                         role="alert"
                                         title="Privilege Escalation"
                                         v-bind:data-content="getRiskDefinition('PrivilegeEscalation')">Privilege
                                        Escalation
                                    </div>
                                </template>
                                <!--Alert for Risk Type: Data Exfiltration Escalation-->
                                <template
                                        v-if="managedPolicyFindings(policyId, 'DataExfiltration').length > 0">
                                    <div class="alert alert-warning popovers" data-html="true" data-placement="top"
                                         data-toggle="popover"
                                         role="alert"
                                         title="Data Exfiltration"
                                         v-bind:data-content="getRiskDefinition('DataExfiltration')">Data Exfiltration
                                    </div>
                                </template>
                                <!--Alert for Risk Type: Resource Exposure-->
                                <template
                                        v-if="managedPolicyFindings(policyId, 'ResourceExposure').length > 0">
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
                            </div>
                        </div>
                        <br>
                        <br>
                    </div>
                    <div class="col-md-7">
                        <div v-bind:id="'managed-policy'  + '-' + policyId + '-' + 'card-details'">
                            <div class="card">
                                <!--Policy Document-->
                                <div class="card-header">
                                    <a class="card-link" data-toggle="collapse"
                                       v-bind:data-parent="'#managed-policy' + '-' + policyId + '-' + 'card-details'"
                                       v-bind:href="'#managed-policy' + '-' + policyId + '-' +'policydocument'"
                                    >Policy Document</a>
                                </div>
                                <div class="panel-collapse collapse"
                                     v-bind:id="'managed-policy' + '-' + policyId + '-' +'policydocument'">
                                    <div class="card-body">
<pre><code>
{{ JSON.parse(JSON.stringify(managedPolicyDocument(policyId), undefined, '\t')) }}
</code></pre>
                                    </div>
                                </div><!--Policy Document-->
                                <!--Assumable by Compute Service-->
                                <div v-if="managedPolicyAssumableByComputeService(policyId).length > 0">
                                    <div class="card-header">
                                        <a class="card-link" data-toggle="collapse"
                                           v-bind:data-parent="'#managed-policy' + '-' + policyId + '-' + 'card-details'"
                                           v-bind:href="'#managed-policy' + '-' + policyId + '-' +'assumable'"
                                        >Compute Services that leverage this IAM Policy via AssumeRole</a>
                                    </div>
                                    <div class="panel-collapse collapse"
                                         v-bind:id="'managed-policy' + '-' + policyId + '-' +'assumable'">
                                        <div class="card-body">
<pre><code>
{{ JSON.parse(JSON.stringify(managedPolicyAssumableByComputeService(policyId), undefined, '\t')) }}
</code></pre>
                                        </div>
                                    </div>
                                </div><!--Assumable by Compute Service-->
                                <!--Data Exfiltration-->
                                <div v-if="managedPolicyFindings(policyId, 'DataExfiltration').length > 0">
                                    <div class="card-header">
                                        <a class="card-link" data-toggle="collapse"
                                           v-bind:data-parent="'#managed-policy' + '-' + policyId + '-' + 'card-details'"
                                           v-bind:href="'#managed-policy' + '-' + policyId + '-' +'data-exfiltration'"
                                        >Data Exfiltration</a>
                                    </div>
                                    <div class="panel-collapse collapse"
                                         v-bind:id="'managed-policy' + '-' + policyId + '-' +'data-exfiltration'">
                                        <div class="card-body">
<pre><code>
{{ JSON.parse(JSON.stringify(managedPolicyFindings(policyId, 'DataExfiltration'), undefined, '\t')) }}
</code></pre>
                                        </div>
                                    </div>
                                </div><!--Data Exfiltration-->
                                <!--Infrastructure Modification Actions-->
                                <div class="card-header">
                                    <a class="card-link" data-toggle="collapse"
                                       v-bind:data-parent="'#managed-policy' + '-' + policyId + '-' + 'card-details'"
                                       v-bind:href="'#managed-policy' + '-' + policyId + '-' +'infrastructure-modification-actions'"
                                    >Infrastructure Modification Actions</a>
                                </div>
                                <div class="panel-collapse collapse"
                                     v-bind:id="'managed-policy' + '-' + policyId + '-' +'infrastructure-modification-actions'">
                                    <div class="card-body">
<pre><code>
{{ JSON.parse(JSON.stringify(managedPolicyFindings(policyId, 'InfrastructureModification'), undefined, '\t')) }}
</code></pre>
                                    </div>
                                </div><!--Infrastructure Modification Actions-->
                                <!--PrivilegeEscalation-->
                                <div v-if="managedPolicyFindings(policyId, 'PrivilegeEscalation').length > 0">
                                    <div class="card-header">
                                        <a class="card-link" data-toggle="collapse"
                                           v-bind:data-parent="'#managed-policy' + '-' + policyId + '-' + 'card-details'"
                                           v-bind:href="'#managed-policy' + '-' + policyId + '-' +'privilege-escalation'"
                                        >Privilege Escalation</a>
                                    </div>
                                    <div class="panel-collapse collapse"
                                         v-bind:id="'managed-policy' + '-' + policyId + '-' +'privilege-escalation'">
                                        <!--TODO: Format the Privilege Escalation stuff-->
                                        <div class="card-body">
<pre><code>
{{ JSON.parse(JSON.stringify(managedPolicyFindings(policyId, 'PrivilegeEscalation'), undefined, '\t')) }}
</code></pre>
                                        </div>
                                    </div>
                                </div><!--Privilege Escalation-->
                                <!--ResourceExposure-->
                                <div v-if="managedPolicyFindings(policyId, 'ResourceExposure').length > 0">
                                    <div class="card-header">
                                        <a class="card-link" data-toggle="collapse"
                                           v-bind:data-parent="'#managed-policy' + '-' + policyId + '-' + 'card-details'"
                                           v-bind:href="'#managed-policy' + '-' + policyId + '-' +'resource-exposure'"
                                        >Resource Exposure</a>
                                    </div>
                                    <div class="panel-collapse collapse"
                                         v-bind:id="'managed-policy' + '-' + policyId + '-' +'resource-exposure'">
                                        <div class="card-body">
<pre><code>
{{ JSON.parse(JSON.stringify(managedPolicyFindings(policyId, 'ResourceExposure'), undefined, '\t')) }}
</code></pre>
                                        </div>
                                    </div>
                                </div><!--Resource Exposure-->
                            </div>
                        </div>
                    </div>
                </div>
        </div>
    </div>
</template>

<script>
    // eslint-disable-next-line no-unused-vars
    const managedPoliciesUtil = require('../util/managed-policies');
    // eslint-disable-next-line no-unused-vars
    let glossary = require('../util/glossary');


    export default {
        name: "ManagedPolicies",
        props: {
            iam_data: {
                type: Object
            },
            riskDefinitions: {
                type: Array
            },
            managedBy: {
                type: String
            }
        },
        computed: {
            getManagedPolicyIdsInUse() {
                return managedPoliciesUtil.getManagedPolicyIdsInUse(this.iam_data, this.managedBy);
            },
        },
        methods: {
            managedPolicyDocument(policyId) {
                return managedPoliciesUtil.getManagedPolicyDocument(this.iam_data, this.managedBy, policyId);
            },
            managedPolicy: function (policyId) {
                return managedPoliciesUtil.getManagedPolicy(this.iam_data, this.managedBy, policyId);
            },
            // managedBy: function (policyId) {
            //     return managedPoliciesUtil.managedPolicyManagedBy(this.iam_data, policyId);
            // },
            principalTypeLeveragingManagedPolicy: function (policyId, principalType) {
                return managedPoliciesUtil.getPrincipalTypeLeveragingManagedPolicy(this.iam_data, this.managedBy, policyId, principalType);
            },
            isManagedPolicyLeveraged: function (policyId) {
                return managedPoliciesUtil.isManagedPolicyLeveraged(this.iam_data, this.managedBy, policyId)
            },
            managedPolicyFindings: function (policyId, riskType) {
                return managedPoliciesUtil.getManagedPolicyFindings(this.iam_data, this.managedBy, policyId, riskType);
            },
            servicesAffectedByManagedPolicy: function (policyId) {
                return managedPoliciesUtil.getServicesAffectedByManagedPolicy(this.iam_data, this.managedBy, policyId)
            },
            managedPolicyAssumableByComputeService: function (policyId) {
                return managedPoliciesUtil.managedPolicyAssumableByComputeService(this.iam_data, this.managedBy, policyId);
            },
            getRiskDefinition: function (riskType) {
                return glossary.getRiskDefinition(riskType)
            }
        }
    }
</script>

<style scoped>

</style>