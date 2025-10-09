<template>
    <div :id="findingId">
        <div class="card-header">
            <h4>
                 <LinkToFinding :finding-id="findingId">
                     {{ policyName(policyId) }}
                 </LinkToFinding>
            </h4>
            <p v-show="inlineOrManaged === 'Managed'" class="policy-identifier">
                Policy Id: {{ policyId }}
            </p>
            <p v-show="inlineOrManaged === 'Inline'" class="policy-identifier">
                Policy Document SHA-256:
                <small style="display:block">{{ policyId }}</small>
            </p>
            Attached to Principals:
            <ul>
                <li v-if="principalLeveragingPolicy(policyId, 'Role').length > 0">
                    Roles:
                    <ul>
                        <li v-bind:key="role"
                            v-for="role in principalLeveragingPolicy(policyId, 'Role')">
                            {{ role }}
                        </li>
                    </ul>
                </li>
                <li v-if="principalLeveragingPolicy(policyId, 'User').length > 0">
                    Users:
                    <ul>
                        <li v-bind:key="user"
                            v-for="user in principalLeveragingPolicy(policyId, 'User')">
                            {{ user }}
                        </li>
                    </ul>
                </li>
                <li v-if="principalLeveragingPolicy(policyId, 'Group').length > 0">
                    Groups:
                    <ul>
                        <li v-bind:key="group"
                            v-for="group in principalLeveragingPolicy(policyId, 'Group')">
                            {{ group }}
                        </li>
                    </ul>
                </li>
            </ul>
        </div>
        <div class="card-body">
            <p class="card-text">
                Services:
                {{ servicesAffectedByPolicy(policyId).length}}
                <br>
                Infrastructure Modification Actions:
                {{ findings(policyId,"InfrastructureModification").length }}
                <br>
            </p>
        </div>
    </div>

</template>

<script>
    import LinkToFinding from "../LinkToFinding";

    const managedPoliciesUtil = require('../../util/managed-policies');
    const inlinePoliciesUtil = require('../../util/inline-policies');
    const {createFindingId} = require('../../util/other');

    export default {
        name: "FindingCard",
        components: {
            LinkToFinding
        },
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
                return ((this.managedBy === "AWS") || (this.managedBy === "Customer"))
                    ? "Managed"
                    : "Inline";
            },
            findingId() {
                return createFindingId(this.policyId, this.inlineOrManaged.toLowerCase())
            }
        },
        methods: {
            principalLeveragingPolicy: function(policyId, principalType) {
                if ((this.managedBy === "AWS") || ( this.managedBy === "Customer")) {
                    return managedPoliciesUtil.getPrincipalTypeLeveragingManagedPolicy(this.iam_data, this.managedBy, policyId, principalType);
                }
                else if (this.managedBy === "Inline") {
                    return inlinePoliciesUtil.getPrincipalTypeLeveragingInlinePolicy(this.iam_data, policyId, principalType);
                }
            },
            managedPolicy: function (policyId) {
                return managedPoliciesUtil.getManagedPolicy(this.iam_data, this.managedBy, policyId);
            },
            inlinePolicy: function (policyId) {
                return inlinePoliciesUtil.getInlinePolicy(this.iam_data, policyId);
            },
            policyName: function(policyId) {
                if (this.managedBy === "Inline") {
                    return this.inlinePolicy(policyId).PolicyName;
                }
                else {
                    return this.managedPolicy(policyId).PolicyName;
                }
            },
            findings: function(policyId, riskType) {
                if (this.managedBy === "Inline") {
                    return inlinePoliciesUtil.getInlinePolicyFindings(this.iam_data, policyId, riskType)
                }
                else {
                    return managedPoliciesUtil.getManagedPolicyFindings(this.iam_data, this.managedBy, policyId, riskType);
                }
            },
            servicesAffectedByPolicy: function(policyId) {
                if (this.managedBy === "Inline") {
                    return inlinePoliciesUtil.getServicesAffectedByInlinePolicy(this.iam_data, policyId);
                }
                else {
                    return managedPoliciesUtil.getServicesAffectedByManagedPolicy(this.iam_data, this.managedBy, policyId);
                }
            }

        }
    }
</script>

<style scoped>

.policy-identifier > small {
    margin-left: 1.5rem;
    display: block;
}

</style>
