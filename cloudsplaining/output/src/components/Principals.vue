<template>
    <div>
        <h2>Principals</h2>
        <p>
            This page displays IAM Users, Groups, and Roles in the account, their associated policies, the risks associated with each principal, and various metadata that can be expanded per principal.
        </p>

        <div v-bind:key="principalType" v-for="principalType in principalTypes">
        <h3>{{ capitalizeFirstLetter(principalType) }}</h3>
            <div v-bind:key="principalId" v-for="principalId in principalTypeIds(principalType)">
                <b-container>
                    <b-row class="px-2" :id="principalId">
                        <b-col class="col-sm-5">
                            <h5 v-bind:id="`iam.${principalType}.${getPrincipalMetadata(principalId, principalType)['id']}`">
                                <LinkToFinding v-bind:finding-id=principalId>
                                    {{ getPrincipalMetadata(principalId, principalType)['name'] }}
                                </LinkToFinding>
                                <small class="text-muted">{{getPrincipalMetadata(principalId, principalType)['arn']}}</small>
                            </h5>
                        </b-col>
                        <b-col class="col-sm-7">
                            <b-button v-b-toggle="`iam.${principalType}.${getPrincipalMetadata(principalId, principalType)['id']}.risk.collapse`">
                                Show
                            </b-button>
                        </b-col>
                    </b-row>
                    <b-collapse
                        v-bind:id="`iam.${principalType}.${getPrincipalMetadata(principalId, principalType)['id']}.risk.collapse`">
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
        },
        methods: {
            principalTypeIds: function(principalType) {
                // principalType should be role, group, or user
                return principalsUtil.getPrincipalIds(this.iam_data, principalType);
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
            },

        }
    }
</script>

<style scoped>

</style>
