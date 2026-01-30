<template>
    <div>
        <div v-bind:key="policyId" v-for="policyId in pagedInlinePolicyIdsInUse">
            <div class="row">
                <div class="col-md-5">
                    <div class="card">
                        <FindingCard
                            :iam_data="iam_data"
                            :managed-by="'Inline'"
                            :policy-id="policyId"
                        ></FindingCard>
                        <div class="card-footer">
                            <RiskAlertIndicators
                                :iam_data="iam_data"
                                :managed-by="'Inline'"
                                :policy-id="policyId"
                            ></RiskAlertIndicators>
                        </div>
                    </div>
                    <br>
                </div>
                <div class="col-md-7">
                    <FindingDetails
                        :managed-by="'Inline'"
                        :iam_data="iam_data"
                        :policy-id="policyId"
                    ></FindingDetails>
                    <br>
                    <br>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
    // eslint-disable-next-line no-unused-vars
    import RiskAlertIndicators from "./finding/RiskAlertIndicators";
    import FindingCard from "./finding/FindingCard";
    import FindingDetails from "./finding/FindingDetails";

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
        components: {
            RiskAlertIndicators,
            FindingCard,
            FindingDetails
        },
        props: {
            iam_data: {
                type: Object
            },
            perPage: {
                type: Number,
                default: 0
            },
            currentPage: {
                type: Number,
                default: 1
            },
            policyIds: {
                type: Array,
                default: null
            },
        },
        computed: {
            inlinePolicyIds() {
                return inlinePoliciesUtil.getInlinePolicyIds(this.iam_data);
            },
            summary() {
                return summary;
            },
            inlinePolicyIdsInUse() {
                return inlinePoliciesUtil.getInlinePolicyIdsInUse(this.iam_data);
            },
            policyIdsToRender() {
                return Array.isArray(this.policyIds) ? this.policyIds : this.inlinePolicyIdsInUse;
            },
            pagedInlinePolicyIdsInUse() {
                const items = this.policyIdsToRender;
                if (!this.perPage || this.perPage <= 0) {
                    return items;
                }
                const start = (this.currentPage - 1) * this.perPage;
                return items.slice(start, start + this.perPage);
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
