<template>
    <b-tab>
        <h3>AWS-Managed Policies ({{ getManagedPolicyNameMapping('AWS').length }})</h3>
        <PolicyTable v-bind:policyNameMapping="getManagedPolicyNameMapping('AWS')"/>
        <ManagedPolicies v-bind:iam_data="iam_data" managedBy="AWS"/>
    </b-tab>
</template>


<script>
import PolicyTable from '../components/PolicyTable';
import ManagedPolicies from '../components/ManagedPolicies';

export default {
    inject: ['iam_data', 'getManagedPolicyNameMapping'],
    components: {
        PolicyTable,
        ManagedPolicies
    }
}
</script>