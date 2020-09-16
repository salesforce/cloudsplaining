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
                            label-align-sm="right"
                            label-size="sm"
                            label-for="perPageSelect"
                            class="mb-0"
                    >
                        <b-form-select
                                v-model="perPage"
                                id="perPageSelect"
                                size="sm"
                                :options="pageOptions"
                        ></b-form-select>
                    </b-form-group>
                </b-col>

            </b-row>

            <b-table
                    :items="policyNameMapping"
                    :fields="fields"
                    :sort-by.sync="sortBy"
                    :sort-desc.sync="sortDesc"
                    :current-page="currentPage"
                    :per-page="perPage"
                    responsive="sm"
                    small
            >
              <template v-slot:cell(attached_to_principals)="data">
                {{ data.item.attached_to_principals.length }}
                <!--{{ data.item.attached_to_principals.join(", ") }}-->
              </template>

              <template v-slot:cell(compute_role)="data">
                {{ data.item.compute_role.join(", ") }}
              </template>
            </b-table>
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
                type: Array
            }
        },
        data() {
            return {
                sortBy: 'policy_name',
                sortDesc: false,
                fields: [
                    {key: 'policy_name', sortable: true},
                    {key: 'attached_to_principals', sortable: true},
                    {key: 'services', sortable: true},
                    {key: 'infrastructure_modification', sortable: true},
                    {key: 'privilege_escalation', sortable: true},
                    {key: 'resource_exposure', sortable: true},
                    {key: 'data_exfiltration', sortable: true},
                    {key: 'compute_role', sortable: true},
                ],
                totalRows: 1,
                currentPage: 1,
                perPage: 10,
                pageOptions: [5, 10, 15, 20, 50, 100],
            }
        },
        methods: {},

    }

</script>


<style scoped>

</style>