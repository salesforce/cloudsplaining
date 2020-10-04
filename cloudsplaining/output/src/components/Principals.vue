<template>
    <div>
        <h2>Principals</h2>
        <br>
        This page displays IAM Users, Groups, and Roles in the account, their associated policies, the risks associated with each principal, and various metadata that can be expanded per principal.
        <br>
        <br>
        <!--ROLES-->
        <div v-bind:key="principalType" v-for="principalType in ['role', 'group', 'user']">
        <h3>{{ capitalizeFirstLetter(principalType) }}</h3>
            <div v-bind:key="principalId" v-for="principalId in principalTypeIds(principalType)">
                <b-container>
                    <b-row class="px-2">
                        <b-col class="col-sm-5">
                            <h5 v-bind:id="`iam.${principalType}.${getPrincipalMetadata(principalId, principalType)['id']}`">{{ getPrincipalMetadata(principalId, principalType)['name'] }}
                                <br>
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
                                        :principal-type="principalId"
                                        :principal-id="principalType"
                                    ></PrincipalMetadata>
                                </dl>
                            </b-col>
                        </b-row>
                    </b-collapse>
                </b-container>
            </div>
        </div>
<!--            <div id="iam.roles">-->
<!--                <div v-bind:key="roleId" v-for="roleId in principalTypeIds('role')">-->
<!--                    <b-container>-->
<!--                        <b-row class="px-2">-->
<!--                            <b-col class="col-sm-5">-->
<!--                                <h5 v-bind:id="'iam.roles' + '.' + getPrincipalMetadata(roleId, 'Role')['id']">{{ getPrincipalMetadata(roleId, 'Role')['name'] }}-->
<!--                                    <br>-->
<!--                                    <small class="text-muted">{{getPrincipalMetadata(roleId, 'Role')['arn']}}</small>-->
<!--                                </h5>-->
<!--                            </b-col>-->
<!--                            <b-col class="col-sm-7">-->
<!--                                <b-button-->
<!--                                        v-b-toggle="`iam.roles.${getPrincipalMetadata(roleId, 'Role')['id']}.risk.collapse`">-->
<!--                                    Show-->
<!--                                </b-button>-->
<!--                            </b-col>-->
<!--                        </b-row>-->
<!--                        <b-collapse-->
<!--                                v-bind:id="`iam.roles.${getPrincipalMetadata(roleId, 'Role')['id']}.risk.collapse`">-->
<!--                            <b-row class="px-2">-->
<!--                                <b-col class="col-sm-5">-->
<!--                                    <h5>Risks</h5>-->
<!--                                    <RisksPerPrincipal-->
<!--                                        :iam_data="iam_data"-->
<!--                                        :principal-id="roleId"-->
<!--                                        :principal-type="'role'"-->
<!--                                    ></RisksPerPrincipal>-->
<!--                                </b-col>-->
<!--                                <b-col class="col-sm-7">-->
<!--                                    <h5>Metadata</h5>-->
<!--                                    <dl class="row">-->
<!--                                        <PrincipalMetadata-->
<!--                                            :iam_data="iam_data"-->
<!--                                            :principal-type="'role'"-->
<!--                                            :principal-id="roleId"-->
<!--                                        ></PrincipalMetadata>-->
<!--                                    </dl>-->
<!--                                </b-col>-->
<!--                            </b-row>-->
<!--                            <br>-->
<!--                        </b-collapse>-->
<!--                    </b-container>-->
<!--                </div>-->
<!--            </div>-->
<!--        <br>-->
<!--        &lt;!&ndash;GROUPS&ndash;&gt;-->
<!--        <h3>Groups</h3>-->
<!--        <div id="iam.groups">-->
<!--            <div v-bind:key="groupId" v-for="groupId in groupIds">-->
<!--                    <b-container>-->
<!--                        <b-row class="px-2">-->
<!--                            <b-col>-->
<!--                                <h5 v-bind:id="'iam.groups' + '.' + getPrincipalMetadata(groupId, 'Group')['id']">{{ getPrincipalMetadata(groupId, 'Group')['name'] }}-->
<!--                                    <br>-->
<!--                                    <small class="text-muted">{{getPrincipalMetadata(groupId, 'Group')['arn']}}</small>-->
<!--                                </h5>-->
<!--                            </b-col>-->
<!--                            <b-col>-->
<!--                                <b-button-->
<!--                                        v-b-toggle="'iam.groups' + '.' + getPrincipalMetadata(groupId, 'Group')['id'] + '.' + 'risk' + '.' + 'collapse'">-->
<!--                                    Show-->
<!--                                </b-button>-->
<!--                            </b-col>-->
<!--                        </b-row>-->
<!--                        <b-collapse-->
<!--                                v-bind:id="'iam.groups' + '.' + getPrincipalMetadata(groupId, 'Group')['id'] + '.' + 'risk' + '.' + 'collapse'">-->
<!--                            <b-row class="px-2">-->
<!--                                <b-col>-->
<!--                                    <h5>Risks</h5>-->
<!--                                    <b-list-group>-->
<!--                                        <div v-bind:key="groupRiskName" v-for="groupRiskName in riskNames">-->
<!--                                            <template-->
<!--                                                    v-show="getRiskAssociatedWithPrincipal(groupId, 'Group', groupRiskName).length > 0">-->
<!--                                                <dd class="col-sm-12">-->
<!--                                                    <dl class="row">-->
<!--                                                        <b-list-group-item-->
<!--                                                                class="d-flex justify-content-between align-items-center"-->
<!--                                                                v-b-toggle="'iam.groups' + '.' + getPrincipalMetadata(groupId, 'Group')['id'] + '.' + 'risk' + '.' + groupRiskName + '.' + 'collapse'"-->
<!--                                                                :action="true">-->
<!--                                                            {{ addSpacesInPascalCaseString(groupRiskName) }}-->

<!--                                                            <b-button v-bind:variant="getRiskLevel(groupRiskName)" size="sm">-->
<!--                                                                {{ getRiskAssociatedWithPrincipal(groupId, "Group",-->
<!--                                                                groupRiskName).length }}-->
<!--                                                            </b-button>-->
<!--                                                        </b-list-group-item>-->
<!--                                                    </dl>-->
<!--                                                </dd>-->
<!--                                                <b-collapse-->
<!--                                                        v-bind:id="'iam.groups' + '.' + getPrincipalMetadata(groupId, 'Group')['id'] + '.' + 'risk' + '.' + groupRiskName + '.' + 'collapse'">-->
<!--                                                    <dd class="col-sm-12">-->
<!--                                                        <pre><code>{{ getRiskAssociatedWithPrincipal(groupId, "Group", groupRiskName) }}</code></pre>-->
<!--                                                    </dd>-->
<!--                                                </b-collapse>-->
<!--                                            </template>-->
<!--                                        </div>-->
<!--                                    </b-list-group>-->
<!--                                </b-col>-->
<!--                                <b-col>-->
<!--                                    <h5>Metadata</h5>-->
<!--                                    <PrincipalMetadata-->
<!--                                        :iam_data="iam_data"-->
<!--                                        :principal-type="'group'"-->
<!--                                        :principal-id="groupId"-->
<!--                                    ></PrincipalMetadata>-->
<!--                                </b-col>-->
<!--                            </b-row>-->
<!--                            <br>-->
<!--                        </b-collapse>-->
<!--                    </b-container>-->
<!--                </div>-->
<!--        </div>&lt;!&ndash;iam.groups&ndash;&gt;-->
<!--        <br>-->
<!--        &lt;!&ndash;USERS&ndash;&gt;-->
<!--        <h3>Users</h3>-->
<!--        <div id="iam.users">-->
<!--            <div v-bind:key="userId" v-for="userId in userIds">-->
<!--                    <b-container>-->
<!--                        <b-row class="px-2">-->
<!--                            <b-col>-->
<!--                                <h5 v-bind:id="'iam.users' + '.' + getPrincipalMetadata(userId, 'User')['id']">{{ getPrincipalMetadata(userId, 'User')['name'] }}-->
<!--                                    <br>-->
<!--                                    <small class="text-muted">{{getPrincipalMetadata(userId, 'User')['arn']}}</small>-->
<!--                                </h5>-->
<!--                            </b-col>-->
<!--                            <b-col>-->
<!--                                <b-button-->
<!--                                        v-b-toggle="'iam.users' + '.' + getPrincipalMetadata(userId, 'User')['id'] + '.' + 'risk' + '.' + 'collapse'">-->
<!--                                    Show-->
<!--                                </b-button>-->
<!--                            </b-col>-->
<!--                        </b-row>-->
<!--                        <b-collapse-->
<!--                                v-bind:id="'iam.users' + '.' + getPrincipalMetadata(userId, 'User')['id'] + '.' + 'risk' + '.' + 'collapse'">-->
<!--                            <b-row class="px-2">-->
<!--                                <b-col>-->
<!--                                    <h5>Risks</h5>-->
<!--                                    <b-list-group>-->
<!--                                        <div v-bind:key="userRiskName" v-for="userRiskName in riskNames">-->
<!--                                            <template-->
<!--                                                    v-show="getRiskAssociatedWithPrincipal(userId, 'User', userRiskName).length > 0">-->
<!--                                                <dd class="col-sm-12">-->
<!--                                                    <dl class="row">-->
<!--                                                        <b-list-group-item-->
<!--                                                                class="d-flex justify-content-between align-items-center"-->
<!--                                                                v-b-toggle="'iam.users' + '.' + getPrincipalMetadata(userId, 'User')['id'] + '.' + 'risk' + '.' + userRiskName + '.' + 'collapse'"-->
<!--                                                                :action="true">-->
<!--                                                            {{ addSpacesInPascalCaseString(userRiskName) }}-->

<!--                                                            <b-button v-bind:variant="getRiskLevel(userRiskName)" size="sm">-->
<!--                                                                {{ getRiskAssociatedWithPrincipal(userId, "User",-->
<!--                                                                userRiskName).length }}-->
<!--                                                            </b-button>-->
<!--                                                        </b-list-group-item>-->
<!--                                                    </dl>-->
<!--                                                </dd>-->
<!--                                                <b-collapse-->
<!--                                                        v-bind:id="'iam.users' + '.' + getPrincipalMetadata(userId, 'User')['id'] + '.' + 'risk' + '.' + userRiskName + '.' + 'collapse'">-->
<!--                                                    <dd class="col-sm-12">-->
<!--                                                        <pre><code>{{ getRiskAssociatedWithPrincipal(userId, "User", userRiskName) }}</code></pre>-->
<!--                                                    </dd>-->
<!--                                                </b-collapse>-->
<!--                                            </template>-->
<!--                                        </div>-->
<!--                                    </b-list-group>-->
<!--                                </b-col>-->
<!--                                <b-col>-->
<!--                                    <h5>Metadata</h5>-->
<!--                                    <dl class="row">-->
<!--                                        <dt class="col-sm-3">ARN</dt>-->
<!--                                        <dd class="col-sm-9 text-monospace">{{getPrincipalMetadata(userId,-->
<!--                                            'User')['arn']}}-->
<!--                                        </dd>-->

<!--                                        <dt class="col-sm-3">ID</dt>-->
<!--                                        <dd class="col-sm-9 text-monospace">{{getPrincipalMetadata(userId,-->
<!--                                            'User')['id']}}-->
<!--                                        </dd>-->

<!--                                        <dt class="col-sm-3">Excluded from scan?</dt>-->
<!--                                        <dd class="col-sm-9 text-monospace">{{getPrincipalMetadata(userId,-->
<!--                                            'User')['is_excluded']}}-->
<!--                                        </dd>-->

<!--                                        <dt class="col-sm-3">Created</dt>-->
<!--                                        <dd class="col-sm-9">{{getPrincipalMetadata(userId, 'User')['create_date']}}-->
<!--                                        </dd>-->

<!--                                        <dt class="col-sm-3">Inline Policies</dt>-->
<!--                                        <dd class="col-sm-9">-->
<!--                                            <b-button size="sm"-->
<!--                                                      v-b-toggle="'iam.users' + '.' + getPrincipalMetadata(userId, 'User')['id'] + '.' + 'inline-policies' + '.' + 'collapse'">-->
<!--                                                {{ getPrincipalPolicyNames(userId, "User", "Inline").length }}-->
<!--                                            </b-button>-->
<!--                                            <b-collapse-->
<!--                                                    v-bind:id="'iam.users' + '.' + getPrincipalMetadata(userId, 'User')['id'] + '.' + 'inline-policies' + '.' + 'collapse'">-->
<!--                                                <br>-->
<!--                                                <pre><code>{{ getPrincipalPolicyNames(userId, "User", "Inline") }}</code></pre>-->
<!--                                            </b-collapse>-->
<!--                                        </dd>-->

<!--                                        <dt class="col-sm-3">AWS-Managed Policies</dt>-->
<!--                                        <dd class="col-sm-9">-->
<!--                                            <b-button size="sm"-->
<!--                                                      v-b-toggle="'iam.users' + '.' + getPrincipalMetadata(userId, 'User')['id'] + '.' + 'aws-managed-policies' + '.' + 'collapse'">-->
<!--                                                {{ getPrincipalPolicyNames(userId, "User", "AWS").length }}-->
<!--                                            </b-button>-->
<!--                                            <b-collapse-->
<!--                                                    v-bind:id="'iam.users' + '.' + getPrincipalMetadata(userId, 'User')['id'] + '.' + 'aws-managed-policies' + '.' + 'collapse'">-->
<!--                                                <br>-->
<!--                                                <pre><code>{{ getPrincipalPolicyNames(userId, "User", "AWS") }}</code></pre>-->
<!--                                            </b-collapse>-->
<!--                                        </dd>-->

<!--                                        <dt class="col-sm-3">Customer-Managed Policies</dt>-->
<!--                                        <dd class="col-sm-9">-->
<!--                                            <b-button size="sm"-->
<!--                                                      v-b-toggle="'iam.users' + '.' + getPrincipalMetadata(userId, 'User')['id'] + '.' + 'customer-managed-policies' + '.' + 'collapse'">-->
<!--                                                {{ getPrincipalPolicyNames(userId, "User", "Customer").length }}-->
<!--                                            </b-button>-->
<!--                                            <b-collapse-->
<!--                                                    v-bind:id="'iam.users' + '.' + getPrincipalMetadata(userId, 'User')['id'] + '.' + 'customer-managed-policies' + '.' + 'collapse'">-->
<!--                                                <br>-->
<!--                                                <pre><code>{{ getPrincipalPolicyNames(userId, "User", "Customer") }}</code></pre>-->
<!--                                            </b-collapse>-->
<!--                                        </dd>-->

<!--                                        <dt class="col-sm-3">Group Memberships</dt>-->
<!--                                        <dd class="col-sm-9">-->
<!--                                            <b-button size="sm"-->
<!--                                                      v-b-toggle="'iam.users' + '.' + getPrincipalMetadata(userId, 'User')['id'] + '.' + 'group-membership' + '.' + 'collapse'">-->
<!--                                                {{ Object.keys(getGroupMemberships(userId)).length }}-->
<!--                                            </b-button>-->
<!--                                            <b-collapse-->
<!--                                                    v-bind:id="'iam.users' + '.' + getPrincipalMetadata(userId, 'User')['id'] + '.' + 'group-membership' + '.' + 'collapse'"-->
<!--                                                    v-show="Object.keys(getGroupMemberships(userId)).length === 0"-->
<!--                                            >-->
<!--                                                Group Memberships:-->
<!--                                                <ul v-bind:key="groupMembershipEntry" v-for="groupMembershipEntry in getGroupMemberships(userId).length">-->
<!--                                                  <li>{{ getGroupMemberships(userId)[groupMembershipEntry - 1]['group_name'] }} (ID: {{ getGroupMemberships(userId)[groupMembershipEntry - 1]['group_id'] }})</li>-->
<!--                                                </ul>-->
<!--                                            </b-collapse>-->
<!--                                        </dd>-->
<!--                                    </dl>-->
<!--                                </b-col>-->
<!--                            </b-row>-->
<!--                            <br>-->
<!--                        </b-collapse>-->
<!--                    </b-container>-->
<!--                </div>-->
<!--        </div>&lt;!&ndash;iam.users&ndash;&gt;-->
    </div>

</template>

<script>
    import RisksPerPrincipal from "./principals/RisksPerPrincipal";
    import PrincipalMetadata from "./principals/PrincipalMetadata";
    const principalsUtil = require('../util/principals');
    const rolesUtil = require('../util/roles');
    const groupsUtil = require('../util/groups');
    const otherUtil = require('../util/other');
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
            PrincipalMetadata
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
            }
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
            addSpacesInPascalCaseString: function (s) {
                return otherUtil.addSpacesInPascalCaseString(s)
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
