<template>
    <b-tab>
        <h3>AWS-Managed Policies ({{ getManagedPolicyNameMapping('AWS').length }})</h3>
        <PolicyTable
            v-bind:policyNameMapping="getManagedPolicyNameMapping('AWS')"
            v-model:per-page="perPage"
            v-model:current-page="currentPage"
            v-model:sort-by="sortBy"
        />
        <Button v-bind:placeholder="'Expand All'" :class="'me-3 mb-4'" @clicked="expandAll" />
        <Button v-bind:placeholder="'Collapse All'" :class="'me-3 mb-4'" @clicked="collapseAll" />
        <ManagedPolicies
            v-bind:iam_data="iam_data"
            managedBy="AWS"
            v-bind:per-page="perPage"
            v-bind:current-page="currentPage"
            v-bind:policy-ids="sortedPolicyIds"
        />
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
            },
            perPage: 10,
            currentPage: 1,
            sortBy: [{ key: 'policy_name', order: 'asc' }]
        }
    },
    computed: {
        sortedPolicyIds() {
            const items = this.getManagedPolicyNameMapping('AWS');
            const sortedItems = this.sortPolicyItems(items);
            return sortedItems.map((item) => item.policy_id);
        }
    },
    methods: {
        normalizeSortValue(value) {
            if (value === null || value === undefined) {
                return '';
            }
            if (typeof value === 'object') {
                return JSON.stringify(value);
            }
            return value.toString();
        },
        sortPolicyItems(items) {
            const sortByItems = (this.sortBy || []).filter((el) => el && el.order);
            if (!sortByItems.length) {
                return items;
            }
            return [...items].sort((a, b) => {
                for (const sortOption of sortByItems) {
                    const aValue = this.normalizeSortValue(a[sortOption.key]);
                    const bValue = this.normalizeSortValue(b[sortOption.key]);
                    const comparison = aValue.localeCompare(bValue, undefined, { numeric: true });
                    if (comparison !== 0) {
                        return sortOption.order === 'desc' ? -comparison : comparison;
                    }
                }
                return 0;
            });
        },
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
