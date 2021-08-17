<template>
    <b-tab>
        <h3>Customer-Managed Policies ({{ getManagedPolicyNameMapping('Customer').length }})</h3>
        <PolicyTable v-bind:policyNameMapping="getManagedPolicyNameMapping('Customer')"/>
        <Button v-bind:placeholder="'Expand All'" :class="'mr-3 mb-4'" @clicked="expandAll" />
        <Button v-bind:placeholder="'Collapse All'" :class="'mr-3 mb-4'" @clicked="collapseAll" />
        <ManagedPolicies v-bind:iam_data="iam_data" managedBy="Customer"/>
    </b-tab>
</template>

<script>
import PolicyTable from '../components/PolicyTable';
import ManagedPolicies from '../components/ManagedPolicies';
import Button from '../components/Button';

export default {
    inject: ['iam_data', 'getManagedPolicyNameMapping'],
    components: {
        PolicyTable,
        ManagedPolicies,
        Button
    },
    data() {
        return {
            toggleData: {
                isAllExpanded: false,
                isAllCollapsed: false
            }
        }
    },
    methods: {
        expandAll() {
            this.toggleData.isAllExpanded = this.toggleData.isAllCollapsed = undefined;
            this.toggleData.isAllExpanded = true;
            this.toggleData.isAllCollapsed = false;
        },
        collapseAll() {
            this.toggleData.isAllExpanded = this.toggleData.isAllCollapsed = undefined;
            this.toggleData.isAllExpanded = false;
            this.toggleData.isAllCollapsed = true;
        }
    },
    provide() {
        return {
            toggleData: this.toggleData
        }
    }
}
</script>
