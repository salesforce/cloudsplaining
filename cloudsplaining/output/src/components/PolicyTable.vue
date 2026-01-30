<template>
    <div>
        <b-container>
            <!-- User Interface controls -->
            <b-row>
                <b-col></b-col>
                <b-col></b-col>
                <b-col>
                    <b-form-group
                            label="Per page"
                            label-cols-sm="6"
                            label-cols-md="4"
                            label-cols-lg="3"
                            label-align-sm="end"
                            label-size="sm"
                            label-for="perPageSelect"
                            class="mb-0"
                    >
                        <b-form-select
                                v-model="perPageModel"
                                id="perPageSelect"
                                size="sm"
                                :options="pageOptions"
                        ></b-form-select>
                    </b-form-group>
                </b-col>

            </b-row>
            <b-table
                    :items="safeItems"
                    :fields="fields"
                    v-model:sort-by="sortByModel"
                    :current-page="currentPageModel"
                    :per-page="perPageModel"
                    responsive="sm"
                    :sticky-header=true
                    :no-border-collapse=true
                    small
            >
                <template v-slot:cell(policy_name)="data">
                    {{ data.item.policy_name }}
                </template>
                <template v-slot:cell(attached_to_principals)="data">
                    {{ data.item.attached_to_principals.length }}
                </template>

                <template v-slot:cell(compute_role)="data">
                    {{ data.item.compute_role.join(", ") }}
                </template>
            </b-table>
            <b-row class="mt-3">
                <b-col>
                    <b-pagination
                        v-model="currentPageModel"
                        :per-page="perPageModel"
                        :total-rows="safeItems.length"
                        align="center"
                        size="sm"
                    />
                </b-col>
            </b-row>
        </b-container>
        <br>
        <hr>
        <br>
    </div>
</template>

<script>
    export default {
        name: "PolicyTable",
        props: {
            policyNameMapping: {
                type: Array,
                default: () => []
            },
            perPage: {
                type: Number,
                default: 10
            },
            currentPage: {
                type: Number,
                default: 1
            },
            sortBy: {
                type: Array,
                default: () => [{ key: 'policy_name', order: 'asc' }]
            }
        },
        emits: ['update:perPage', 'update:currentPage', 'update:sortBy'],
        data() {
            return {
                fields: [
                    {key: 'policy_name', sortable: true},
                    {key: 'attached_to_principals', sortable: true},
                    {key: 'services', sortable: true},
                    {key: 'infrastructure_modification', sortable: true},
                    {key: 'service_wildcard', sortable: true},
                    {key: 'privilege_escalation', sortable: true},
                    {key: 'resource_exposure', sortable: true},
                    {key: 'data_exfiltration', sortable: true},
                    {key: 'credentials_exposure', sortable: true},
                    {key: 'compute_role', sortable: true},
                ],
                totalRows: 1,
                pageOptions: [5, 10, 15, 20, 50, 100],
            }
        },
        computed: {
            sortByModel: {
                get() {
                    return this.sortBy;
                },
                set(value) {
                    this.$emit('update:sortBy', value);
                }
            },
            perPageModel: {
                get() {
                    return this.perPage;
                },
                set(value) {
                    this.$emit('update:perPage', value);
                }
            },
            currentPageModel: {
                get() {
                    return this.currentPage;
                },
                set(value) {
                    this.$emit('update:currentPage', value);
                }
            },
            safeItems() {
                return Array.isArray(this.policyNameMapping) ? this.policyNameMapping : [];
            }
        },
        methods: {},

    }

</script>


<style scoped>

</style>
