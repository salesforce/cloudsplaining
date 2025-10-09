<template>
    <b-tab>
        <h3>Inline Policies ({{ getInlinePolicyNameMapping().length }})</h3>
        <PolicyTable v-bind:policyNameMapping="getInlinePolicyNameMapping()"/>
        <Button v-bind:placeholder="'Expand All'" :class="'mr-3 mb-4'" @clicked="expandAll" />
        <Button v-bind:placeholder="'Collapse All'" :class="'mr-3 mb-4'" @clicked="collapseAll" />
        <InlinePolicies v-bind:iam_data="iam_data"/>
    </b-tab>
</template>

<script>
import PolicyTable from '../components/PolicyTable.vue';
import InlinePolicies from '../components/InlinePolicies.vue';
import Button from '../components/Button';

export default {
    inject: ['iam_data', 'getInlinePolicyNameMapping'],
    components: {
        PolicyTable,
        InlinePolicies,
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
