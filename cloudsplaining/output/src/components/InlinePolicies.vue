<template>
    <div>
        <div v-bind:key="policyId" v-for="policyId in inlinePolicyIds">
            <div class="row">
                <div class="col-md-5">
                    <div class="card">
                        <h6 class="card-header" v-bind:id="'inline-policy' + '.' + policyId + '.' + 'card'">
                            Name: {{ inlinePolicy(policyId).PolicyName }}
                            <br>
                          <br>
                          Policy Document SHA-256:
                          <ul>
                            <li><span><small>{{ policyId }}</small></span></li>
                          </ul>
                            Attached to Principals:
                            <ul>
                                <li v-if="principalTypeLeveragingInlinePolicy(policyId, 'Role').length > 0">
                                    Roles:
                                    <ul>
                                        <li v-bind:key="role"
                                            v-for="role in principalTypeLeveragingInlinePolicy(policyId, 'Role')">
                                            {{ role }}
                                        </li>
                                    </ul>
                                </li>
                                <li v-if="principalTypeLeveragingInlinePolicy(policyId, 'User').length > 0">
                                    Users:
                                    <ul>
                                        <li v-bind:key="user"
                                            v-for="user in principalTypeLeveragingInlinePolicy(policyId, 'User')">
                                            {{ user }}
                                        </li>
                                    </ul>
                                </li>
                                <li v-if="principalTypeLeveragingInlinePolicy(policyId, 'Group').length > 0">
                                    Groups:
                                    <ul>
                                        <li v-bind:key="group"
                                            v-for="group in principalTypeLeveragingInlinePolicy(policyId, 'Group')">
                                            {{ group }}
                                        </li>
                                    </ul>
                                </li>
                            </ul>
                        </h6>
                        <div class="card-body">
                            <p class="card-text">
                                Services: {{ servicesAffectedByInlinePolicy(policyId).length }}
                                <br>
                                <br>
                                Infrastructure Modification Actions: {{ inlinePolicyFindings(policyId,
                                "InfrastructureModification").length }}
                                <br>
                            </p>
                        </div> <!-- /card-text -->
                        <div class="card-footer">
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
                        </div>
                    </div>
                    <br>
                    <br>
                </div>
                <div class="col-md-7">
                    <div v-bind:id="'inline-policy'  + '-' + policyId + '-' + 'card-details'">
                        <div class="card">
                            <!--Policy Document-->
                            <div class="card-header">
                                <a class="card-link" data-toggle="collapse"
                                   v-bind:data-parent="'#inline-policy' + '-' + policyId + '-' + 'card-details'"
                                   v-bind:href="'#inline-policy' + '-' + policyId + '-' +'policydocument'"
                                >Policy Document</a>
                            </div>
                            <div class="panel-collapse collapse"
                                 v-bind:id="'inline-policy' + '-' + policyId + '-' +'policydocument'">
                                <div class="card-body">
<pre><code>
{{ JSON.parse(JSON.stringify(inlinePolicyDocument(policyId), undefined, '\t')) }}
</code></pre>
                                </div>
                            </div><!--Policy Document-->
                            <!--Assumable by Compute Service-->
                            <template v-if="inlinePolicyAssumableByComputeService(policyId).length > 0">
                                <div class="card-header">
                                    <a class="card-link" data-toggle="collapse"
                                       v-bind:data-parent="'#inline-policy' + '-' + policyId + '-' + 'card-details'"
                                       v-bind:href="'#inline-policy' + '-' + policyId + '-' +'assumable'"
                                    >Compute Services that leverage this IAM Policy via AssumeRole</a>
                                </div>
                                <div class="panel-collapse collapse"
                                     v-bind:id="'inline-policy' + '-' + policyId + '-' +'assumable'">
                                    <div class="card-body">
<pre><code>
{{ JSON.parse(JSON.stringify(inlinePolicyAssumableByComputeService(policyId), undefined, '\t')) }}
</code></pre>
                                    </div>
                                </div>
                            </template><!--Assumable by Compute Service-->
                            <!--Data Exfiltration-->
                            <template v-if="inlinePolicyFindings(policyId, 'DataExfiltration').length > 0">
                                <div class="card-header">
                                    <a class="card-link" data-toggle="collapse"
                                       v-bind:data-parent="'#inline-policy' + '-' + policyId + '-' + 'card-details'"
                                       v-bind:href="'#inline-policy' + '-' + policyId + '-' +'data-exfiltration'"
                                    >Data Exfiltration</a>
                                </div>
                                <div class="panel-collapse collapse"
                                     v-bind:id="'inline-policy' + '-' + policyId + '-' +'data-exfiltration'">
                                    <div class="card-body">
<pre><code>
{{ JSON.parse(JSON.stringify(inlinePolicyFindings(policyId, 'DataExfiltration'), undefined, '\t')) }}
</code></pre>
                                    </div>
                                </div>
                            </template><!--Data Exfiltration-->
                            <!--Infrastructure Modification Actions-->
                            <div class="card-header">
                                <a class="card-link" data-toggle="collapse"
                                   v-bind:data-parent="'#inline-policy' + '-' + policyId + '-' + 'card-details'"
                                   v-bind:href="'#inline-policy' + '-' + policyId + '-' +'infrastructure-modification-actions'"
                                >Infrastructure Modification Actions</a>
                            </div>
                            <div class="panel-collapse collapse"
                                 v-bind:id="'inline-policy' + '-' + policyId + '-' +'infrastructure-modification-actions'">
                                <div class="card-body">
<pre><code>
{{ JSON.parse(JSON.stringify(inlinePolicyFindings(policyId, 'InfrastructureModification'), undefined, '\t')) }}
</code></pre>
                                </div>
                            </div><!--Infrastructure Modification Actions-->
                            <!--PrivilegeEscalation-->
                            <div v-if="inlinePolicyFindings(policyId, 'PrivilegeEscalation').length > 0">
                                <div class="card-header">
                                    <a class="card-link" data-toggle="collapse"
                                       v-bind:data-parent="'#inline-policy' + '-' + policyId + '-' + 'card-details'"
                                       v-bind:href="'#inline-policy' + '-' + policyId + '-' +'privilege-escalation'"
                                    >Privilege Escalation</a>
                                </div>
                                <div class="panel-collapse collapse"
                                     v-bind:id="'inline-policy' + '-' + policyId + '-' +'privilege-escalation'">
                                    <!--TODO: Format the Privilege Escalation stuff-->
                                    <div class="card-body">
<pre><code>
{{ JSON.parse(JSON.stringify(inlinePolicyFindings(policyId, 'PrivilegeEscalation'), undefined, '\t')) }}
</code></pre>
                                    </div>
                                </div>
                            </div><!--Privilege Escalation-->
                            <!--ResourceExposure-->
                            <div v-if="inlinePolicyFindings(policyId, 'ResourceExposure').length > 0">
                                <div class="card-header">
                                    <a class="card-link" data-toggle="collapse"
                                       v-bind:data-parent="'#inline-policy' + '-' + policyId + '-' + 'card-details'"
                                       v-bind:href="'#inline-policy' + '-' + policyId + '-' +'resource-exposure'"
                                    >Resource Exposure</a>
                                </div>
                                <div class="panel-collapse collapse"
                                     v-bind:id="'inline-policy' + '-' + policyId + '-' +'resource-exposure'">
                                    <div class="card-body">
<pre><code>
{{ JSON.parse(JSON.stringify(inlinePolicyFindings(policyId, 'ResourceExposure'), undefined, '\t')) }}
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
    const inlinePoliciesUtil = require('../util/inline-policies');
    // eslint-disable-next-line no-unused-vars
    let glossary = require('../util/glossary');

    var md = require('markdown-it')({
        html: true,
        linkify: true,
        typographer: true
    });
    import summaryRaw from '../assets/summary.md';

    const summary = md.render(summaryRaw);

    export default {
        name: "InlinePolicies",
        props: {
            iam_data: {
                type: Object
            },
            riskDefinitions: {
                type: Array
            }
        },
        computed: {
            inlinePolicyIds() {
                return inlinePoliciesUtil.getInlinePolicyIds(this.iam_data);
            },
            summary() {
                return summary;
            }
        },
        methods: {
            inlinePolicyDocument(policyId) {
                return inlinePoliciesUtil.getInlinePolicyDocument(this.iam_data, policyId);
            },
            inlinePolicy: function (policyId) {
                return inlinePoliciesUtil.getInlinePolicy(this.iam_data, policyId);
            },
            inlinePolicyFindings: function (policyId, riskType) {
                return inlinePoliciesUtil.getInlinePolicyFindings(this.iam_data, policyId, riskType);
            },
            servicesAffectedByInlinePolicy: function (policyId) {
                return inlinePoliciesUtil.getServicesAffectedByInlinePolicy(this.iam_data, policyId)
            },
            principalTypeLeveragingInlinePolicy: function (policyId, principalType) {
                return inlinePoliciesUtil.getPrincipalTypeLeveragingInlinePolicy(this.iam_data, policyId, principalType);
            },
            inlinePolicyAssumableByComputeService: function (policyId) {
                return inlinePoliciesUtil.inlinePolicyAssumableByComputeService(this.iam_data, policyId);
            },
            getRiskDefinition: function (riskType) {
                return glossary.getRiskDefinition(riskType)
            },
        }
    }
</script>

<style scoped>

</style>
