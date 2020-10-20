<template>
    <b-tab>
        <h3>Inline Policies ({{ getInlinePolicyNameMapping().length }})</h3>
        <PolicyTable v-bind:policyNameMapping="getInlinePolicyNameMapping()"/>
        <InlinePolicies v-bind:iam_data="iam_data"/>
    </b-tab>
</template>

<script>
import PolicyTable from '../components/PolicyTable.vue';
import InlinePolicies from '../components/InlinePolicies.vue'

export default {
    inject: ['iam_data', 'getInlinePolicyNameMapping'],
    components: {
        PolicyTable,
        InlinePolicies
    }
}
</script>