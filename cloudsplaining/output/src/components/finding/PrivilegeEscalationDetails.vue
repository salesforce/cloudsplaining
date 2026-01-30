<template>
    <div v-if="findings(policyId, 'PrivilegeEscalation').length > 0">
        <div class="card-header">
            <b-button
                class="card-link p-0"
                variant="link"
                v-b-toggle="collapseId"
            >
                Privilege Escalation
            </b-button>
        </div>
        <b-collapse
            v-model="isExpanded"
            :id="collapseId"
            class="panel-collapse"
        >
            <div class="card-body">
                <!--What should I do?-->
                <b-button squared variant="link" v-b-modal="`${inlineOrManaged.toLowerCase()}-policy-${policyId}-privilege-escalation-what-should-i-do`">What should I do?</b-button>
                <b-modal v-bind:id="`${inlineOrManaged.toLowerCase()}-policy-${policyId}-privilege-escalation-what-should-i-do`" ok-only>
                    <p>
                        <span v-html="whatShouldIDoDescription"></span>
                    </p>
                </b-modal>
                <!--Triaging: Identifying False Positives-->
                <b-button squared variant="link" v-b-modal="`${inlineOrManaged.toLowerCase()}-policy-${policyId}-privilege-escalation-identifying-false-positives`">How do I identify False Positives?</b-button>
                <b-modal v-bind:id="`${inlineOrManaged.toLowerCase()}-policy-${policyId}-privilege-escalation-identifying-false-positives`" ok-only>
                    <p>
                        <span v-html="identifyingFalsePositivesDescription"></span>
                    </p>
                </b-modal>
                <!--How do I validate results?-->
                <b-button squared variant="link" v-b-modal="`${inlineOrManaged.toLowerCase()}-policy-${policyId}-privilege-escalation-validating-fixed-policy`">How do I fix it?</b-button>
                <b-modal v-bind:id="`${inlineOrManaged.toLowerCase()}-policy-${policyId}-privilege-escalation-validating-fixed-policy`" ok-only>
                    <p>
                        <span v-html="howDoIValidateResultsDescription"></span>
                    </p>
                </b-modal>
                <br>
                <br>
                <span v-html="getRiskDescription('PrivilegeEscalation')"></span>
                <span>Privilege Escalation Methods:</span>
                <br>
                <br>
                <PrivilegeEscalationFormat v-bind:privilege-escalation-finding="privilegeEscalationFindings(policyId)"></PrivilegeEscalationFormat>
            </div>
        </b-collapse>
    </div>
</template>

<script>
    import whatShouldIDoRaw from "../../assets/what-should-i-do.md";
    import PrivilegeEscalationFormat from "./PrivilegeEscalationFormat";
    const managedPoliciesUtil = require('../../util/managed-policies');
    const inlinePoliciesUtil = require('../../util/inline-policies');
    var md = require('markdown-it')({
        html: true,
        linkify: true,
        typographer: true
    });
    import privilegeEscalationRaw from '../../assets/definition-privilege-escalation.md'
    import identifyingFalsePositivesDescriptionRaw from "../../assets/identifying-false-positives.md";
    import howDoIValidateResultsRaw from "../../assets/how-do-i-validate-results.md";
    const privilegeEscalationDescription = md.render(privilegeEscalationRaw)

    const whatShouldIDoDescription = md.render(whatShouldIDoRaw)
    const identifyingFalsePositivesDescription = md.render(identifyingFalsePositivesDescriptionRaw)
    const howDoIValidateResultsDescription = md.render(howDoIValidateResultsRaw)


    export default {
        name: "PrivilegeEscalationDetails",
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
        components: {
            PrivilegeEscalationFormat
        },
        computed: {
            collapseId() {
                return `${this.inlineOrManaged.toLowerCase()}-policy-${this.policyId}-privilege-escalation`;
            },
            inlineOrManaged() {
                if ((this.managedBy === "AWS") || (this.managedBy === "Customer")) {
                    return "Managed"
                } else {
                    return "Inline"
                }
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
            getRiskDescription: function (riskType) {
                if (riskType === "PrivilegeEscalation") {
                    return privilegeEscalationDescription
                }
            },
            privilegeEscalationFindings: function (policyId) {
                return this.findings(policyId, 'PrivilegeEscalation')
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
