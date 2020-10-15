<template>
    <b-tab>
        <h3>Customer-Managed Policies ({{ getManagedPolicyNameMapping('Customer').length }})</h3>
        <PolicyTable v-bind:policyNameMapping="getManagedPolicyNameMapping('Customer')"/>
        <ManagedPolicies v-bind:iam_data="iam_data" managedBy="Customer"/>
    </b-tab>
</template>

<script>
import PolicyTable from '../components/PolicyTable';
import ManagedPolicies from '../components/ManagedPolicies'

export default {
    inject: ['iam_data', 'getManagedPolicyNameMapping'],
    components: {
        PolicyTable,
        ManagedPolicies
    }
}
</script>