<template>
    <div>
        <h2>Principals</h2>
        <p>
            This page displays IAM Users, Groups, and Roles in the account, their associated policies, the risks associated with each principal, and various metadata that can be expanded per principal.
        </p>

        <!-- Summary Table -->
        <div class="mb-4">
            <h3>Summary</h3>
            <div class="mb-3">
                <b-form-group label="Filter by Risk Type:" label-cols="2">
                    <b-form-select v-model="selectedRiskFilter" :options="riskFilterOptions" @change="applyFilters"></b-form-select>
                </b-form-group>
                <b-form-group label="Filter by Principal Type:" label-cols="2">
                    <b-form-select v-model="selectedTypeFilter" :options="typeFilterOptions" @change="applyFilters"></b-form-select>
                </b-form-group>
                <b-form-group label="Search:" label-cols="2">
                    <b-form-input v-model="searchQuery" placeholder="Search by principal name..." @input="applyFilters"></b-form-input>
                </b-form-group>
            </div>
            
            <b-table
                :items="filteredSummaryData"
                :fields="summaryFields"
                :sort-by.sync="sortBy"
                :sort-desc.sync="sortDesc"
                striped
                hover
                responsive
                :per-page="perPage"
                :current-page="currentPage"
                show-empty
                empty-text="No principals match the current filters"
            >
                <template #cell(name)="data">
                    <LinkToFinding :finding-id="data.item.id">
                        {{ data.item.name }}
                    </LinkToFinding>
                </template>
                <template #cell(risks)="data">
                    <b-badge v-for="risk in data.item.riskSummary" :key="risk.name" :variant="getRiskVariant(risk.name)" class="mr-1">
                        {{ risk.name }}: {{ risk.count }}
                    </b-badge>
                </template>
                <template #cell(actions)="data">
                    <b-button size="sm" @click="scrollToPrincipal(data.item.id)" variant="outline-primary">
                        View Details
                    </b-button>
                </template>
            </b-table>
            
            <b-pagination
                v-model="currentPage"
                :total-rows="filteredSummaryData.length"
                :per-page="perPage"
                align="center"
                class="mt-3"
            ></b-pagination>
        </div>

        <!-- Expand/Collapse All Controls -->
        <div class="mb-3">
            <b-button-group>
                <b-button @click="expandAll" variant="outline-success">Expand All</b-button>
                <b-button @click="collapseAll" variant="outline-secondary">Collapse All</b-button>
            </b-button-group>
            <span class="ml-3 text-muted">Showing {{ filteredPrincipalsCount }} of {{ totalPrincipals }} principals</span>
        </div>

        <!-- Principal Details -->
        <div v-bind:key="principalType" v-for="principalType in principalTypes">
            <h3>{{ capitalizeFirstLetter(principalType) }}</h3>
            <div v-bind:key="principalId" v-for="principalId in getFilteredPrincipalIds(principalType)">
                <b-container>
                    <b-row class="px-2" :id="principalId">
                        <b-col class="col-sm-5">
                            <h5 v-bind:id="`iam.${principalType}.${getPrincipalMetadata(principalId, principalType)['id']}`">
                                <LinkToFinding v-bind:finding-id=principalId>
                                    {{ getPrincipalMetadata(principalId, principalType)['name'] }}
                                </LinkToFinding>
                                <small class="text-muted">{{getPrincipalMetadata(principalId, principalType)['arn']}}</small>
                            </h5>
                            <!-- Risk indicators -->
                            <div class="mt-2">
                                <b-badge v-for="risk in getPrincipalRiskSummary(principalId, principalType)" 
                                         :key="risk.name" 
                                         :variant="getRiskVariant(risk.name)" 
                                         class="mr-1">
                                    {{ risk.name }}: {{ risk.count }}
                                </b-badge>
                            </div>
                        </b-col>
                        <b-col class="col-sm-7">
                            <b-button 
                                v-b-toggle="`iam.${principalType}.${getPrincipalMetadata(principalId, principalType)['id']}.risk.collapse`"
                                :ref="`toggle-${principalId}`"
                            >
                                Show
                            </b-button>
                        </b-col>
                    </b-row>
                    <b-collapse
                        v-bind:id="`iam.${principalType}.${getPrincipalMetadata(principalId, principalType)['id']}.risk.collapse`"
                        :ref="`collapse-${principalId}`"
                    >
                        <b-row class="px-2">
                            <b-col class="col-sm-5">
                                <h5>Risks</h5>
                                <RisksPerPrincipal
                                    :iam_data="iam_data"
                                    :principal-id="principalId"
                                    :principal-type="principalType"
                                ></RisksPerPrincipal>
                            </b-col>
                            <b-col class="col-sm-7">
                                <h5>Metadata</h5>
                                <dl class="row">
                                    <PrincipalMetadata
                                        :iam_data="iam_data"
                                        :principal-id="principalId"
                                        :principal-type="principalType"
                                    ></PrincipalMetadata>
                                </dl>
                            </b-col>
                        </b-row>
                    </b-collapse>
                </b-container>
            </div>
        </div>
    </div>

</template>

<script>
    import RisksPerPrincipal from "./principals/RisksPerPrincipal";
    import PrincipalMetadata from "./principals/PrincipalMetadata";
    import LinkToFinding from "./LinkToFinding";
    const principalsUtil = require('../util/principals');
    const rolesUtil = require('../util/roles');
    const groupsUtil = require('../util/groups');
    // eslint-disable-next-line no-unused-vars
    let glossary = require('../util/glossary');

    export default {
        name: "Principals",
        props: {
            iam_data: {
                type: Object
            },
        },
        components: {
            RisksPerPrincipal,
            PrincipalMetadata,
            LinkToFinding,
        },
        data() {
            return {
                selectedRiskFilter: 'all',
                selectedTypeFilter: 'all',
                searchQuery: '',
                sortBy: 'totalRisks',
                sortDesc: true,
                currentPage: 1,
                perPage: 20,
                filteredPrincipals: [],
                summaryFields: [
                    { key: 'name', label: 'Principal Name', sortable: true },
                    { key: 'type', label: 'Type', sortable: true },
                    { key: 'totalRisks', label: 'Total Risks', sortable: true },
                    { key: 'risks', label: 'Risk Breakdown', sortable: false },
                    { key: 'actions', label: 'Actions', sortable: false }
                ]
            }
        },
        computed: {
            roleIds() {
                return principalsUtil.getPrincipalIds(this.iam_data, "Role");
            },
            userIds() {
                return principalsUtil.getPrincipalIds(this.iam_data, "User");
            },
            groupIds() {
                return principalsUtil.getPrincipalIds(this.iam_data, "Group");
            },
            riskNames() {
                return ["DataExfiltration", "ResourceExposure", "PrivilegeEscalation", "InfrastructureModification"]
            },
            principalTypes() {
                return ["role", "group", "user"]
            },
            totalPrincipals() {
                return this.roleIds.length + this.userIds.length + this.groupIds.length;
            },
            riskFilterOptions() {
                return [
                    { value: 'all', text: 'All Risks' },
                    { value: 'DataExfiltration', text: 'Data Exfiltration' },
                    { value: 'PrivilegeEscalation', text: 'Privilege Escalation' },
                    { value: 'ResourceExposure', text: 'Resource Exposure' },
                    { value: 'InfrastructureModification', text: 'Infrastructure Modification' }
                ];
            },
            typeFilterOptions() {
                return [
                    { value: 'all', text: 'All Types' },
                    { value: 'role', text: 'Roles' },
                    { value: 'user', text: 'Users' },
                    { value: 'group', text: 'Groups' }
                ];
            },
            summaryData() {
                let data = [];
                
                for (let principalType of this.principalTypes) {
                    let principalIds = this.principalTypeIds(principalType);
                    for (let principalId of principalIds) {
                        let metadata = this.getPrincipalMetadata(principalId, principalType);
                        let riskSummary = this.getPrincipalRiskSummary(principalId, principalType);
                        let totalRisks = riskSummary.reduce((sum, risk) => sum + risk.count, 0);
                        
                        data.push({
                            id: principalId,
                            name: metadata.name,
                            type: this.capitalizeFirstLetter(principalType),
                            arn: metadata.arn,
                            totalRisks: totalRisks,
                            riskSummary: riskSummary,
                            principalType: principalType
                        });
                    }
                }
                
                return data;
            },
            filteredSummaryData() {
                let filtered = this.summaryData;
                
                // Filter by risk type
                if (this.selectedRiskFilter !== 'all') {
                    filtered = filtered.filter(item => {
                        return item.riskSummary.some(risk => 
                            risk.name === this.selectedRiskFilter && risk.count > 0
                        );
                    });
                }
                
                // Filter by principal type
                if (this.selectedTypeFilter !== 'all') {
                    filtered = filtered.filter(item => 
                        item.principalType === this.selectedTypeFilter
                    );
                }
                
                // Filter by search query
                if (this.searchQuery) {
                    const query = this.searchQuery.toLowerCase();
                    filtered = filtered.filter(item => 
                        item.name.toLowerCase().includes(query) ||
                        item.arn.toLowerCase().includes(query)
                    );
                }
                
                return filtered;
            },
            filteredPrincipalsCount() {
                return this.filteredSummaryData.length;
            }
        },
        watch: {
            filteredSummaryData: {
                handler(newVal) {
                    this.filteredPrincipals = newVal;
                },
                immediate: true
            }
        },
        mounted() {
            this.applyFilters();
        },
        methods: {
            principalTypeIds: function(principalType) {
                // principalType should be role, group, or user
                return principalsUtil.getPrincipalIds(this.iam_data, principalType);
            },
            getFilteredPrincipalIds: function(principalType) {
                let allIds = this.principalTypeIds(principalType);
                return allIds.filter(id => {
                    return this.filteredPrincipals.some(item => 
                        item.id === id && item.principalType === principalType
                    );
                });
            },
            getPrincipalRiskSummary: function(principalId, principalType) {
                let summary = [];
                for (let riskName of this.riskNames) {
                    let risks = this.getRiskAssociatedWithPrincipal(principalId, principalType, riskName);
                    if (risks.length > 0) {
                        summary.push({
                            name: riskName,
                            count: risks.length,
                            displayName: this.addSpacesInPascalCaseString(riskName)
                        });
                    }
                }
                return summary;
            },
            getRiskVariant: function(riskType) {
                const variants = {
                    'DataExfiltration': 'warning',
                    'PrivilegeEscalation': 'danger',
                    'ResourceExposure': 'warning',
                    'InfrastructureModification': 'info'
                };
                return variants[riskType] || 'secondary';
            },
            applyFilters: function() {
                // Trigger computed property recalculation
                this.$nextTick(() => {
                    this.currentPage = 1;
                });
            },
            scrollToPrincipal: function(principalId) {
                const element = document.getElementById(principalId);
                if (element) {
                    element.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    // Optionally expand the principal details
                    this.$nextTick(() => {
                        const toggleButton = this.$refs[`toggle-${principalId}`];
                        if (toggleButton && toggleButton[0]) {
                            toggleButton[0].click();
                        }
                    });
                }
            },
            expandAll: function() {
                for (let principalType of this.principalTypes) {
                    let principalIds = this.getFilteredPrincipalIds(principalType);
                    for (let principalId of principalIds) {
                        let collapseId = `iam.${principalType}.${this.getPrincipalMetadata(principalId, principalType)['id']}.risk.collapse`;
                        this.$root.$emit('bv::toggle::collapse', collapseId);
                    }
                }
            },
            collapseAll: function() {
                for (let principalType of this.principalTypes) {
                    let principalIds = this.getFilteredPrincipalIds(principalType);
                    for (let principalId of principalIds) {
                        let collapseId = `iam.${principalType}.${this.getPrincipalMetadata(principalId, principalType)['id']}.risk.collapse`;
                        this.$root.$emit('bv::toggle::collapse', collapseId);
                    }
                }
            },
            addSpacesInPascalCaseString: function(s) {
                return s.replace(/([A-Z])/g, ' $1').trim();
            },
            getPrincipalMetadata: function (principalName, principalType) {
                return principalsUtil.getPrincipalMetadata(this.iam_data, principalName, principalType)
            },
            getPrincipalPolicies: function (principalName, principalType, policyType) {
                return principalsUtil.getPrincipalPolicies(this.iam_data, principalName, principalType, policyType)
            },
            getRiskAssociatedWithPrincipal: function (principalName, principalType, riskType) {
                return principalsUtil.getRiskAssociatedWithPrincipal(this.iam_data, principalName, principalType, riskType)
            },
            getRoleTrustPolicy: function (roleId) {
                return rolesUtil.getTrustPolicyDocumentForRole(this.iam_data, roleId)
            },
            getRiskDefinition: function (riskType) {
                return glossary.getRiskDefinition(riskType)
            },
            getGroupMembers: function (groupId) {
                return groupsUtil.getGroupMembers(this.iam_data, groupId)
            },
            getGroupMemberships: function (groupId) {
                return groupsUtil.getGroupMemberships(this.iam_data, groupId)
            },
            getPrincipalPolicyNames: function (principalName, principalType, policyType) {
                return principalsUtil.getPrincipalPolicyNames(this.iam_data, principalName, principalType, policyType)
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
            },
            capitalizeFirstLetter: function(string) {
                return string.charAt(0).toUpperCase() + string.slice(1);
            }
        }
    }
</script>

<style scoped>

</style>
