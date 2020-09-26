<template>
    <div>
        <div v-bind:key="policyId" v-for="policyId in getManagedPolicyIdsInUse">
                <div class="row">
                    <div class="col-md-5">
                        <div class="card">
                            <FindingCard
                                :policy-id="policyId"
                                :iam_data="iam_data"
                                :managed-by="managedBy"
                            >
                            </FindingCard>
                            <div class="card-footer">
                                <RiskAlertIndicators
                                :iam_data="iam_data"
                                :policy-id="policyId"
                                :managed-by="managedBy"
                                ></RiskAlertIndicators>
                            </div>
                        </div>
                        <br>
                        <br>
                    </div>
                    <div class="col-md-7">
                        <FindingDetails
                            :managed-by="managedBy"
                            :iam_data="iam_data"
                            :policy-id="policyId"
                        ></FindingDetails>
                        <br>
                        <br>
                    </div>
                </div>
            <br>
        </div>
    </div>
</template>

<script>
    import RiskAlertIndicators from "./finding/RiskAlertIndicators";
    import FindingCard from "./finding/FindingCard";
    import FindingDetails from "./finding/FindingDetails";
    // eslint-disable-next-line no-unused-vars
    const managedPoliciesUtil = require('../util/managed-policies');
    // eslint-disable-next-line no-unused-vars
    let glossary = require('../util/glossary');


    export default {
        name: "ManagedPolicies",
        components: {
            RiskAlertIndicators,
            FindingCard,
            FindingDetails
        },
        props: {
            iam_data: {
                type: Object
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
