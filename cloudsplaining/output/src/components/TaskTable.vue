<template>
    <div>
        <b-container v-bind:id="'iam.task' + '.' + managedBy">
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
                    :items="items_mapping"
                    :fields="fields"
                    small
                    :sort-by.sync="sortBy"
                    :sort-desc.sync="sortDesc"
                    :current-page="currentPage"
                    :per-page="perPage"
                    responsive="sm"
            >

                <template v-slot:cell(policy_document)="data">
                    {{ JSON.parse(JSON.stringify(data.item.policy_document)) }}
                </template>

                <template v-slot:cell(policy_document)="row">
                    <b-button size="sm" @click="info(row.item, row.index, $event.target, 'policy_document')"
                              class="mr-1">
                        See Policy Document
                    </b-button>
                </template>

                <template v-slot:cell(infrastructure_modification)="data">
                    {{ data.item.infrastructure_modification.length}}
                </template>

                <template v-slot:cell(resource_exposure)="data">
                    {{ data.item.resource_exposure.length}}
                </template>
                <template v-slot:cell(data_exfiltration)="data">
                    {{ data.item.data_exfiltration.length}}
                </template>
                <template v-slot:cell(privilege_escalation)="data">
                    {{ data.item.privilege_escalation.length}}
                </template>

                <template v-slot:cell(services)="data">
                    {{ data.item.services.length }}
                </template>

                <template v-slot:cell(compute_role)="data">
                    {{ data.item.compute_role.join(", ") }}
                </template>

                <template v-slot:cell(show_details)="row">
                    <b-button size="sm" @click="row.toggleDetails" class="mr-2">
                        {{ row.detailsShowing ? 'Hide' : 'Show'}} Details
                    </b-button>
                </template>


                <template v-slot:row-details="row">
                    <b-card>
                        <b-row class="mb-2">
                            <b-col sm="3" class="text-sm-right"><b>Risks</b></b-col>
                            <b-col>
                                <b-list-group>
                                    <div v-bind:key="riskName" v-for="riskName in riskNames">
                                        <template v-show="row.item[convertStringToSnakeCase(riskName)].length > 0">
                                            <dd class="col-sm-12">
                                                <dl class="row">
                                                    <b-list-group-item
                                                            class="d-flex justify-content-between align-items-center"
                                                            v-b-toggle="'iam.tasks' + '.' + row.item.policy_id + '.' + 'risk' + '.' + riskName + '.' + 'collapse'"
                                                            :action="true">
                                                        {{ addSpacesInPascalCaseString(riskName) }}

                                                        <b-button v-bind:variant="getRiskLevel(riskName)" size="sm"
                                                        >
                                                            {{ row.item[convertStringToSnakeCase(riskName)].length }}
                                                        </b-button>
                                                    </b-list-group-item>
                                                </dl>
                                            </dd>
                                            <b-collapse
                                                    v-bind:id="'iam.tasks' + '.' + row.item.policy_id + '.' + 'risk' + '.' + riskName + '.' + 'collapse'">
                                                <dd class="col-sm-12">
                                                    <br>
                                                    <pre><code>{{ row.item[convertStringToSnakeCase(riskName)] }}</code></pre>
                                                    <br>
                                                </dd>
                                            </b-collapse>
                                        </template>
                                    </div>
                                </b-list-group>
                            </b-col>
                        </b-row>

                        <b-button size="sm" @click="row.toggleDetails">Hide Details</b-button>
                    </b-card>
                </template>
            </b-table>

            <!-- Info modal -->
            <b-modal :id="infoModal.id" :title="infoModal.title" ok-only @hide="resetInfoModal">
                <pre>{{ infoModal.content }}</pre>
            </b-modal>
        </b-container>
        <br>
        <hr>
        <br>
    </div>
</template>

<script>
    const managedPoliciesUtil = require('../util/managed-policies');
    const otherUtil = require('../util/other');

    export default {
        name: "TaskTable",
        props: {
            items_mapping: {
                type: Array
            },
            managedBy: {
                type: String
            }
        },
        data() {
            return {
                sortBy: 'services',
                sortDesc: false,
                fields: [
                    {key: 'policy_name', sortable: true},
                    {key: 'policy_document', sortable: false},
                    // {key: 'attached_to_principals', sortable: true},
                    {key: 'services', sortable: true},
                    {key: 'privilege_escalation', sortable: true},
                    {key: 'resource_exposure', sortable: true},
                    {key: 'data_exfiltration', sortable: true},
                    {key: 'infrastructure_modification', sortable: true},
                    {key: 'compute_role', sortable: true},
                    {key: 'show_details', sortable: false},
                    // {key: 'roles_leveraging_policy', sortable: true},
                    // {key: 'groups_leveraging_policy', sortable: true},
                    // {key: 'users_leveraging_policy', sortable: true},
                ],
                totalRows: 1,
                currentPage: 1,
                perPage: 20,
                pageOptions: [5, 10, 15, 20, 50, 100],
                infoModal: {
                    id: 'info-modal',
                    title: '',
                    content: ''
                }
            }
        },
        computed: {
            riskNames() {
                return ["DataExfiltration", "ResourceExposure", "PrivilegeEscalation", "InfrastructureModification"]
            }
        },
        methods: {
            info(item, index, button, column_name) {
                this.infoModal.title = `${column_name}`
                this.infoModal.content = JSON.stringify(item[column_name], null, 2)
                this.$root.$emit('bv::show::modal', this.infoModal.id, button)
            },
            managedPolicyFindings: function (policyId, riskType) {
                return managedPoliciesUtil.getManagedPolicyFindings(this.iam_data, this.managedBy, policyId, riskType);
            },
            resetInfoModal() {
                this.infoModal.title = ''
                this.infoModal.content = ''
            },
            addSpacesInPascalCaseString: function (s) {
                return otherUtil.addSpacesInPascalCaseString(s)
            },
            convertStringToSnakeCase: function (s) {
                return otherUtil.convertStringToSnakeCase(s)
            },
            getRiskLevel: function (riskType) {
                if (riskType === "DataExfiltration") {
                    return "warning"
                }
                if (riskType === "PrivilegeEscalation") {
                    return "danger"
                }
                if (riskType === "ResourceExposure") {
                    return "warning"
                }
                if (riskType === "InfrastructureModification") {
                    return "info"
                }
            }
        },

    }

</script>


<style scoped>

</style>
