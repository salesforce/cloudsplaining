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
                     ref="StandardRiskDetailsDiv"
                     v-bind:id="`${inlineOrManaged.toLowerCase()}-policy-${policyId}-${convertStringToKebabCase(risk.risk_type)}`">
                    <div class="card-body">
                        <!--What should I do?-->
                        <b-button squared variant="link" v-b-modal="`${inlineOrManaged.toLowerCase()}-policy-${policyId}-${convertStringToKebabCase(risk.risk_type)}-what-should-i-do`">What should I do?</b-button>
                        <b-modal v-bind:id="`${inlineOrManaged.toLowerCase()}-policy-${policyId}-${convertStringToKebabCase(risk.risk_type)}-what-should-i-do`">
                            <p>
                                <span v-html="whatShouldIDoDescription"></span>
                            </p>
                        </b-modal>
                        <!--Triaging: Identifying False Positives-->
                        <b-button squared variant="link" v-b-modal="`${inlineOrManaged.toLowerCase()}-policy-${policyId}-${convertStringToKebabCase(risk.risk_type)}-identifying-false-positives`">How do I identify False Positives?</b-button>
                        <b-modal v-bind:id="`${inlineOrManaged.toLowerCase()}-policy-${policyId}-${convertStringToKebabCase(risk.risk_type)}-identifying-false-positives`">
                            <p>
                                <span v-html="identifyingFalsePositivesDescription"></span>
                            </p>
                        </b-modal>
                        <!--How do I validate results?-->
                        <b-button squared variant="link" v-b-modal="`${inlineOrManaged.toLowerCase()}-policy-${policyId}-${convertStringToKebabCase(risk.risk_type)}-validating-fixed-policy`">How do I fix it?</b-button>
                        <b-modal v-bind:id="`${inlineOrManaged.toLowerCase()}-policy-${policyId}-${convertStringToKebabCase(risk.risk_type)}-validating-fixed-policy`">
                            <p>
                                <span v-html="howDoIValidateResultsDescription"></span>
                            </p>
                        </b-modal>
                        <br>
                        <br>
                        <span v-html="getRiskDescription(risk.risk_type)"></span>
                        <span>Actions/services:</span>
<!--If the type is ServiceWildcard, that does not list specific IAM actions, it just lists service names.-->
                        <span v-if="risk.risk_type === 'ServiceWildcard'">
<pre><code>
{{ JSON.parse(JSON.stringify(findings(policyId, risk.risk_type), undefined, '\t')) }}
</code></pre>
                        </span>
<!--If the finding type is not ServiceWildcard or Privilege Escalation, it will list IAM action names-->
                        <span v-else>
                            <ul>
                                <li v-bind:key="someAction" v-for="(someActionLink, someAction) in getActionLinks(policyId, risk.risk_type)">
                                    <a v-bind:href="`${someActionLink}`">{{ someAction }}</a>
                                </li>
                            </ul>
                        </span>
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

    var md = require('markdown-it')({
        html: true,
        linkify: true,
        typographer: true
    });
    import resourceExposureRaw from '../../assets/definition-resource-exposure.md'
    import privilegeEscalationRaw from '../../assets/definition-privilege-escalation.md'
    import dataExfiltrationRaw from '../../assets/definition-data-exfiltration.md'
    import infrastructureModificationRaw from '../../assets/definition-infrastructure-modification.md'
    import credentialsExposureRaw from '../../assets/definition-credentials-exposure.md'
    import serviceWildcardRaw from '../../assets/definition-service-wildcard.md'
    import assumableByComputeServiceRaw from '../../assets/definition-assumable-by-compute-service.md'

    const resourceExposureDescription = md.render(resourceExposureRaw)
    const privilegeEscalationDescription = md.render(privilegeEscalationRaw)
    const dataExfiltrationDescription = md.render(dataExfiltrationRaw)
    const infrastructureModificationDescription = md.render(infrastructureModificationRaw)
    const credentialsExposureDescription = md.render(credentialsExposureRaw)
    const serviceWildcardDescription = md.render(serviceWildcardRaw)
    const assumableByComputeServiceDescription = md.render(assumableByComputeServiceRaw)

    import whatShouldIDoRaw from '../../assets/what-should-i-do.md'
    import identifyingFalsePositivesDescriptionRaw from '../../assets/identifying-false-positives.md'
    import howDoIValidateResultsRaw from '../../assets/how-do-i-validate-results.md'

    const whatShouldIDoDescription = md.render(whatShouldIDoRaw)
    const identifyingFalsePositivesDescription = md.render(identifyingFalsePositivesDescriptionRaw)
    const howDoIValidateResultsDescription = md.render(howDoIValidateResultsRaw)

    export default {
        name: "StandardRiskDetails",
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
            },
            riskDetailsToDisplay() {
                return glossary.getRiskDetailsToDisplay()
            },
            whatShouldIDoDescription() {
                return whatShouldIDoDescription
            },
            identifyingFalsePositivesDescription() {
                return identifyingFalsePositivesDescription
            },
            howDoIValidateResultsDescription() {
                return howDoIValidateResultsDescription
            },
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
            },
            getRiskDefinition: function (riskType) {
                return glossary.getRiskDefinition(riskType)
            },
            getRiskDescription: function (riskType) {
                if (riskType === "ResourceExposure") {
                    return resourceExposureDescription
                }
                else if (riskType === "PrivilegeEscalation") {
                    return privilegeEscalationDescription
                }
                else if (riskType === "DataExfiltration") {
                    return dataExfiltrationDescription
                }
                else if (riskType === "InfrastructureModification") {
                    return infrastructureModificationDescription
                }
                else if (riskType === "AssumableByComputeService") {
                    return assumableByComputeServiceDescription
                }
                else if (riskType === "ServiceWildcard") {
                    return serviceWildcardDescription
                }
                else if (riskType === "CredentialsExposure") {
                    return credentialsExposureDescription
                }
                else {
                    return ""
                }
            },
            getActionLinks: function (policyId, risk_type) {
                let actionList = this.findings(policyId, risk_type)
                return otherUtil.getActionLinks(this.iam_data, actionList)
            },
        },
        watch: {
            toggleData: {
                handler(data) {
                    if (data.isAllExpanded && this.$refs['StandardRiskDetailsDiv']) {
                        this.$refs['StandardRiskDetailsDiv'].map(e => e.classList.add('show'))
                    }
                    if (data.isAllCollapsed && this.$refs['StandardRiskDetailsDiv']) {
                        this.$refs['StandardRiskDetailsDiv'].map(e => e.classList.remove('show'));
                    }
                },
                deep: true
            }
        }
    }
</script>

<style scoped>

</style>
