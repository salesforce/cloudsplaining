<template>
    <div>
        <h2>Principals</h2>
        <br>
        This page displays IAM Users, Groups, and Roles in the account, their associated policies, the risks associated with each principal, and various metadata that can be expanded per principal.
        <br>
        <br>
        <!--ROLES-->
        <h3>Roles</h3>
            <div id="iam.roles">
                <div v-bind:key="roleId" v-for="roleId in roleIds">
                    <br>
                    <b-container>
                        <b-row class="px-2">
                            <b-col>
                                <h4>{{ getPrincipalMetadata(roleId, 'Role')['name'] }}
                                    <br>
                                    <small class="text-muted">{{getPrincipalMetadata(roleId, 'Role')['arn']}}</small>
                                </h4>
                            </b-col>
                            <b-col>
                                <b-button
                                        v-b-toggle="'iam.roles' + '.' + getPrincipalMetadata(roleId, 'Role')['id'] + '.' + 'risk' + '.' + 'collapse'">
                                    Show
                                </b-button>
                            </b-col>
                        </b-row>
                        <br>
                        <b-collapse
                                v-bind:id="'iam.roles' + '.' + getPrincipalMetadata(roleId, 'Role')['id'] + '.' + 'risk' + '.' + 'collapse'">
                            <b-row class="px-2">
                                <b-col lg="4">
                                    <h5>Risks</h5>
                                    <b-list-group>
                                        <div v-bind:key="roleRiskName" v-for="roleRiskName in riskNames">
                                            <template
                                                    v-show="getRiskAssociatedWithPrincipal(roleId, 'Role', roleRiskName).length > 0">
                                                <dd class="col-sm-12">
                                                    <dl class="row">
                                                        <b-list-group-item
                                                                class="d-flex justify-content-between align-items-center"
                                                                v-b-toggle="'iam.roles' + '.' + getPrincipalMetadata(roleId, 'Role')['id'] + '.' + 'risk' + '.' + roleRiskName + '.' + 'collapse'"
                                                                :action="true">
                                                            {{ addSpacesInPascalCaseString(roleRiskName) }}

                                                            <b-button v-bind:variant="getRiskLevel(roleRiskName)" size="sm"
                                                                      >
                                                                {{ getRiskAssociatedWithPrincipal(roleId, "Role",
                                                                roleRiskName).length }}
                                                            </b-button>
                                                        </b-list-group-item>
                                                    </dl>
                                                </dd>
                                                <b-collapse
                                                        v-bind:id="'iam.roles' + '.' + getPrincipalMetadata(roleId, 'Role')['id'] + '.' + 'risk' + '.' + roleRiskName + '.' + 'collapse'">
                                                    <dd class="col-sm-12">
                                                        <br>
                                                        <pre><code>{{ getRiskAssociatedWithPrincipal(roleId, "Role", roleRiskName) }}</code></pre>
                                                        <br>
                                                    </dd>
                                                </b-collapse>
                                            </template>
                                        </div>
                                    </b-list-group>
                                </b-col>
                                <b-col>
                                    <h5>Metadata</h5>
                                    <dl class="row">
                                        <dt class="col-sm-3">ARN</dt>
                                        <dd class="col-sm-9 text-monospace">{{getPrincipalMetadata(roleId,
                                            'Role')['arn']}}
                                        </dd>

                                        <dt class="col-sm-3">ID</dt>
                                        <dd class="col-sm-9 text-monospace">{{getPrincipalMetadata(roleId,
                                            'Role')['id']}}
                                        </dd>

                                        <dt class="col-sm-3">Excluded from scan?</dt>
                                        <dd class="col-sm-8 text-monospace">{{getPrincipalMetadata(roleId,
                                            'Role')['is_excluded']}}
                                        </dd>

                                        <dt class="col-sm-3">Created</dt>
                                        <dd class="col-sm-9">{{getPrincipalMetadata(roleId, 'Role')['create_date']}}
                                        </dd>


                                        <dt class="col-sm-3">Inline Policies</dt>
                                        <dd class="col-sm-9">
                                            <b-button size="sm"
                                                      v-b-toggle="'iam.roles' + '.' + getPrincipalMetadata(roleId, 'Role')['id'] + '.' + 'inline-policies' + '.' + 'collapse'">
                                                {{ getPrincipalPolicyNames(roleId, "Role", "Inline").length }}
                                            </b-button>
                                            <b-collapse
                                                    v-bind:id="'iam.roles' + '.' + getPrincipalMetadata(roleId, 'Role')['id'] + '.' + 'inline-policies' + '.' + 'collapse'">
                                                <br>
                                                <pre><code>{{ getPrincipalPolicyNames(roleId, "Role", "Inline") }}</code></pre>
                                            </b-collapse>
                                        </dd>

                                        <dt class="col-sm-3">AWS-Managed Policies</dt>
                                        <dd class="col-sm-9">
                                            <b-button size="sm"
                                                      v-b-toggle="'iam.roles' + '.' + getPrincipalMetadata(roleId, 'Role')['id'] + '.' + 'aws-managed-policies' + '.' + 'collapse'">
                                                {{ getPrincipalPolicyNames(roleId, "Role", "AWS").length }}
                                            </b-button>
                                            <b-collapse
                                                    v-bind:id="'iam.roles' + '.' + getPrincipalMetadata(roleId, 'Role')['id'] + '.' + 'aws-managed-policies' + '.' + 'collapse'">
                                                <br>
                                                <pre><code>{{ getPrincipalPolicyNames(roleId, "Role", "AWS") }}</code></pre>
                                            </b-collapse>
                                        </dd>

                                        <dt class="col-sm-3">Customer-Managed Policies</dt>
                                        <dd class="col-sm-9">
                                            <b-button size="sm"
                                                      v-b-toggle="'iam.roles' + '.' + getPrincipalMetadata(roleId, 'Role')['id'] + '.' + 'customer-managed-policies' + '.' + 'collapse'">
                                                {{ getPrincipalPolicyNames(roleId, "Role", "Customer").length }}
                                            </b-button>
                                            <b-collapse
                                                    v-bind:id="'iam.roles' + '.' + getPrincipalMetadata(roleId, 'Role')['id'] + '.' + 'customer-managed-policies' + '.' + 'collapse'">
                                                <br>
                                                <pre><code>{{ getPrincipalPolicyNames(roleId, "Role", "Customer") }}</code></pre>
                                            </b-collapse>
                                        </dd>

                                        <dt class="col-sm-3">Role Trust Policy</dt>
                                        <dd class="col-sm-9">
                                            <b-button size="sm"
                                                      v-b-toggle="'iam.roles' + '.' + getPrincipalMetadata(roleId, 'Role')['id'] + '.' + 'role-trust-policy' + '.' + 'collapse'">
                                                Details
                                            </b-button>
                                            <b-collapse
                                                    v-bind:id="'iam.roles' + '.' + getPrincipalMetadata(roleId, 'Role')['id'] + '.' + 'role-trust-policy' + '.' + 'collapse'">
                                                <br>
                                                <pre><code>{{ JSON.parse(JSON.stringify(getRoleTrustPolicy(roleId))) }}</code></pre>
                                            </b-collapse>
                                        </dd>
                                        <!--Instance Profiles-->
                                        <dt class="col-sm-3">Instance Profiles</dt>
                                        <dd class="col-sm-9">
                                            <b-button size="sm"
                                                      v-b-toggle="'iam.roles' + '.' + getPrincipalMetadata(roleId, 'Role')['id'] + '.' + 'instance-profiles' + '.' + 'collapse'">
                                                {{ getPrincipalMetadata(roleId, 'Role')['instance_profiles'].length }}
                                            </b-button>
                                            <b-collapse
                                                    v-bind:id="'iam.roles' + '.' + getPrincipalMetadata(roleId, 'Role')['id'] + '.' + 'instance-profiles' + '.' + 'collapse'">
                                                <br>
                                                <pre><code>{{ JSON.parse(JSON.stringify(getPrincipalMetadata(roleId, 'Role')['instance_profiles'])) }}</code></pre>
                                            </b-collapse>
                                        </dd>
                                    </dl>
                                </b-col>
                            </b-row>
                            <br>
                            <br>
                        </b-collapse>
                    </b-container>
                </div>
            </div>
        <br>
        <!--GROUPS-->
        <h3>Groups</h3>
        <div id="iam.groups">
            <div v-bind:key="groupId" v-for="groupId in groupIds">
                    <br>
                    <b-container>
                        <b-row class="px-2">
                            <b-col>
                                <h4>{{ getPrincipalMetadata(groupId, 'Group')['name'] }}
                                    <br>
                                    <small class="text-muted">{{getPrincipalMetadata(groupId, 'Group')['arn']}}</small>
                                </h4>
                            </b-col>
                            <b-col>
                                <b-button
                                        v-b-toggle="'iam.groups' + '.' + getPrincipalMetadata(groupId, 'Group')['id'] + '.' + 'risk' + '.' + 'collapse'">
                                    Show
                                </b-button>
                            </b-col>
                        </b-row>
                        <br>
                        <b-collapse
                                v-bind:id="'iam.groups' + '.' + getPrincipalMetadata(groupId, 'Group')['id'] + '.' + 'risk' + '.' + 'collapse'">
                            <b-row class="px-2">
                                <b-col lg="4">
                                    <h5>Risks</h5>
                                    <b-list-group>
                                        <div v-bind:key="groupRiskName" v-for="groupRiskName in riskNames">
                                            <template
                                                    v-show="getRiskAssociatedWithPrincipal(groupId, 'Group', groupRiskName).length > 0">
                                                <dd class="col-sm-12">
                                                    <dl class="row">
                                                        <b-list-group-item
                                                                class="d-flex justify-content-between align-items-center"
                                                                v-b-toggle="'iam.groups' + '.' + getPrincipalMetadata(groupId, 'Group')['id'] + '.' + 'risk' + '.' + groupRiskName + '.' + 'collapse'"
                                                                :action="true">
                                                            {{ addSpacesInPascalCaseString(groupRiskName) }}

                                                            <b-button v-bind:variant="getRiskLevel(groupRiskName)" size="sm">
                                                                {{ getRiskAssociatedWithPrincipal(groupId, "Group",
                                                                groupRiskName).length }}
                                                            </b-button>
                                                        </b-list-group-item>
                                                    </dl>
                                                </dd>
                                                <b-collapse
                                                        v-bind:id="'iam.groups' + '.' + getPrincipalMetadata(groupId, 'Group')['id'] + '.' + 'risk' + '.' + groupRiskName + '.' + 'collapse'">
                                                    <dd class="col-sm-12">
                                                        <br>
                                                        <pre><code>{{ getRiskAssociatedWithPrincipal(groupId, "Group", groupRiskName) }}</code></pre>
                                                        <br>
                                                    </dd>
                                                </b-collapse>
                                            </template>
                                        </div>
                                    </b-list-group>
                                </b-col>
                                <b-col>
                                    <h5>Metadata</h5>
                                    <dl class="row">
                                        <dt class="col-sm-3">ARN</dt>
                                        <dd class="col-sm-9 text-monospace">{{getPrincipalMetadata(groupId,
                                            'Group')['arn']}}
                                        </dd>

                                        <dt class="col-sm-3">Excluded from scan?</dt>
                                        <dd class="col-sm-9 text-monospace">{{getPrincipalMetadata(groupId,
                                            'Group')['is_excluded']}}
                                        </dd>

                                        <dt class="col-sm-3">ID</dt>
                                        <dd class="col-sm-9 text-monospace">{{getPrincipalMetadata(groupId,
                                            'Group')['id']}}
                                        </dd>

                                        <dt class="col-sm-3">Created</dt>
                                        <dd class="col-sm-9">{{getPrincipalMetadata(groupId, 'Group')['create_date']}}
                                        </dd>

                                        <dt class="col-sm-3">Inline Policies</dt>
                                        <dd class="col-sm-9">
                                            <b-button size="sm"
                                                      v-b-toggle="'iam.groups' + '.' + getPrincipalMetadata(groupId, 'Group')['id'] + '.' + 'inline-policies' + '.' + 'collapse'">
                                                {{ getPrincipalPolicyNames(groupId, "Group", "Inline").length }}
                                            </b-button>
                                            <b-collapse
                                                    v-bind:id="'iam.groups' + '.' + getPrincipalMetadata(groupId, 'Group')['id'] + '.' + 'inline-policies' + '.' + 'collapse'">
                                                <br>
                                                <pre><code>{{ getPrincipalPolicyNames(groupId, "Group", "Inline") }}</code></pre>
                                            </b-collapse>
                                        </dd>

                                        <dt class="col-sm-3">AWS-Managed Policies</dt>
                                        <dd class="col-sm-9">
                                            <b-button size="sm"
                                                      v-b-toggle="'iam.groups' + '.' + getPrincipalMetadata(groupId, 'Group')['id'] + '.' + 'aws-managed-policies' + '.' + 'collapse'">
                                                {{ getPrincipalPolicyNames(groupId, "Group", "AWS").length }}
                                            </b-button>
                                            <b-collapse
                                                    v-bind:id="'iam.groups' + '.' + getPrincipalMetadata(groupId, 'Group')['id'] + '.' + 'aws-managed-policies' + '.' + 'collapse'">
                                                <br>
                                                <pre><code>{{ getPrincipalPolicyNames(groupId, "Group", "AWS") }}</code></pre>
                                            </b-collapse>
                                        </dd>

                                        <dt class="col-sm-3">Customer-Managed Policies</dt>
                                        <dd class="col-sm-9">
                                            <b-button size="sm"
                                                      v-b-toggle="'iam.groups' + '.' + getPrincipalMetadata(groupId, 'Group')['id'] + '.' + 'customer-managed-policies' + '.' + 'collapse'">
                                                {{ getPrincipalPolicyNames(groupId, "Group", "Customer").length }}
                                            </b-button>
                                            <b-collapse
                                                    v-bind:id="'iam.groups' + '.' + getPrincipalMetadata(groupId, 'Group')['id'] + '.' + 'customer-managed-policies' + '.' + 'collapse'">
                                                <br>
                                                <pre><code>{{ getPrincipalPolicyNames(groupId, "Group", "Customer") }}</code></pre>
                                            </b-collapse>
                                        </dd>

                                        <dt class="col-sm-3">Group Members</dt>
                                        <dd class="col-sm-9">
                                            <b-button size="sm"
                                                      v-b-toggle="'iam.groups' + '.' + getPrincipalMetadata(groupId, 'Group')['id'] + '.' + 'group-members' + '.' + 'collapse'">
                                              {{ getGroupMembers(groupId).length }}
                                            </b-button>
                                            <b-collapse
                                                    v-bind:id="'iam.groups' + '.' + getPrincipalMetadata(groupId, 'Group')['id'] + '.' + 'group-members' + '.' + 'collapse'">
                                                Group Members:
                                                <ul v-bind:key="groupMemberEntry" v-for="groupMemberEntry in getGroupMembers(groupId).length">
                                                  <li>{{ getGroupMembers(groupId)[groupMemberEntry - 1]['user_name'] }} (ID: {{ getGroupMembers(groupId)[groupMemberEntry - 1]['user_id'] }})</li>
                                                </ul>
                                            </b-collapse>
                                        </dd>
                                    </dl>
                                </b-col>
                            </b-row>
                            <br>
                            <br>
                        </b-collapse>
                    </b-container>
                </div>
        </div><!--iam.groups-->
        <br>
        <!--USERS-->
        <h3>Users</h3>
            <div v-bind:key="userId" v-for="userId in userIds">
                    <br>
                    <b-container>
                        <b-row class="px-2">
                            <b-col>
                                <h4>{{ getPrincipalMetadata(userId, 'User')['name'] }}
                                    <br>
                                    <small class="text-muted">{{getPrincipalMetadata(userId, 'User')['arn']}}</small>
                                </h4>
                            </b-col>
                            <b-col>
                                <b-button
                                        v-b-toggle="'iam.users' + '.' + getPrincipalMetadata(userId, 'User')['id'] + '.' + 'risk' + '.' + 'collapse'">
                                    Show
                                </b-button>
                            </b-col>
                        </b-row>
                        <br>
                        <b-collapse
                                v-bind:id="'iam.users' + '.' + getPrincipalMetadata(userId, 'User')['id'] + '.' + 'risk' + '.' + 'collapse'">
                            <b-row class="px-2">
                                <b-col lg="4">
                                    <h5>Risks</h5>
                                    <b-list-group>
                                        <div v-bind:key="userRiskName" v-for="userRiskName in riskNames">
                                            <template
                                                    v-show="getRiskAssociatedWithPrincipal(userId, 'User', userRiskName).length > 0">
                                                <dd class="col-sm-12">
                                                    <dl class="row">
                                                        <b-list-group-item
                                                                class="d-flex justify-content-between align-items-center"
                                                                v-b-toggle="'iam.users' + '.' + getPrincipalMetadata(userId, 'User')['id'] + '.' + 'risk' + '.' + userRiskName + '.' + 'collapse'"
                                                                :action="true">
                                                            {{ addSpacesInPascalCaseString(userRiskName) }}

                                                            <b-button v-bind:variant="getRiskLevel(userRiskName)" size="sm">
                                                                {{ getRiskAssociatedWithPrincipal(userId, "User",
                                                                userRiskName).length }}
                                                            </b-button>
                                                        </b-list-group-item>
                                                    </dl>
                                                </dd>
                                                <b-collapse
                                                        v-bind:id="'iam.users' + '.' + getPrincipalMetadata(userId, 'User')['id'] + '.' + 'risk' + '.' + userRiskName + '.' + 'collapse'">
                                                    <dd class="col-sm-12">
                                                        <br>
                                                        <pre><code>{{ getRiskAssociatedWithPrincipal(userId, "User", userRiskName) }}</code></pre>
                                                        <br>
                                                    </dd>
                                                </b-collapse>
                                            </template>
                                        </div>
                                    </b-list-group>
                                </b-col>
                                <b-col>
                                    <h5>Metadata</h5>
                                    <dl class="row">


                                        <dt class="col-sm-3">ARN</dt>
                                        <dd class="col-sm-9 text-monospace">{{getPrincipalMetadata(userId,
                                            'User')['arn']}}
                                        </dd>

                                        <dt class="col-sm-3">ID</dt>
                                        <dd class="col-sm-9 text-monospace">{{getPrincipalMetadata(userId,
                                            'User')['id']}}
                                        </dd>

                                        <dt class="col-sm-3">Excluded from scan?</dt>
                                        <dd class="col-sm-9 text-monospace">{{getPrincipalMetadata(userId,
                                            'User')['is_excluded']}}
                                        </dd>

                                        <dt class="col-sm-3">Created</dt>
                                        <dd class="col-sm-9">{{getPrincipalMetadata(userId, 'User')['create_date']}}
                                        </dd>

                                        <dt class="col-sm-3">Inline Policies</dt>
                                        <dd class="col-sm-9">
                                            <b-button size="sm"
                                                      v-b-toggle="'iam.users' + '.' + getPrincipalMetadata(userId, 'User')['id'] + '.' + 'inline-policies' + '.' + 'collapse'">
                                                {{ getPrincipalPolicyNames(userId, "User", "Inline").length }}
                                            </b-button>
                                            <b-collapse
                                                    v-bind:id="'iam.users' + '.' + getPrincipalMetadata(userId, 'User')['id'] + '.' + 'inline-policies' + '.' + 'collapse'">
                                                <br>
                                                <pre><code>{{ getPrincipalPolicyNames(userId, "User", "Inline") }}</code></pre>
                                            </b-collapse>
                                        </dd>

                                        <dt class="col-sm-3">AWS-Managed Policies</dt>
                                        <dd class="col-sm-9">
                                            <b-button size="sm"
                                                      v-b-toggle="'iam.users' + '.' + getPrincipalMetadata(userId, 'User')['id'] + '.' + 'aws-managed-policies' + '.' + 'collapse'">
                                                {{ getPrincipalPolicyNames(userId, "User", "AWS").length }}
                                            </b-button>
                                            <b-collapse
                                                    v-bind:id="'iam.users' + '.' + getPrincipalMetadata(userId, 'User')['id'] + '.' + 'aws-managed-policies' + '.' + 'collapse'">
                                                <br>
                                                <pre><code>{{ getPrincipalPolicyNames(userId, "User", "AWS") }}</code></pre>
                                            </b-collapse>
                                        </dd>

                                        <dt class="col-sm-3">Customer-Managed Policies</dt>
                                        <dd class="col-sm-9">
                                            <b-button size="sm"
                                                      v-b-toggle="'iam.users' + '.' + getPrincipalMetadata(userId, 'User')['id'] + '.' + 'customer-managed-policies' + '.' + 'collapse'">
                                                {{ getPrincipalPolicyNames(userId, "User", "Customer").length }}
                                            </b-button>
                                            <b-collapse
                                                    v-bind:id="'iam.users' + '.' + getPrincipalMetadata(userId, 'User')['id'] + '.' + 'customer-managed-policies' + '.' + 'collapse'">
                                                <br>
                                                <pre><code>{{ getPrincipalPolicyNames(userId, "User", "Customer") }}</code></pre>
                                            </b-collapse>
                                        </dd>

                                        <dt class="col-sm-3">Group Memberships</dt>
                                        <dd class="col-sm-9">
                                            <b-button size="sm"
                                                      v-b-toggle="'iam.users' + '.' + getPrincipalMetadata(userId, 'User')['id'] + '.' + 'group-membership' + '.' + 'collapse'">
                                                {{ Object.keys(getGroupMemberships(userId)).length }}
                                            </b-button>
                                            <b-collapse
                                                    v-bind:id="'iam.users' + '.' + getPrincipalMetadata(userId, 'User')['id'] + '.' + 'group-membership' + '.' + 'collapse'"
                                                    v-show="Object.keys(getGroupMemberships(userId)).length === 0"
                                            >
                                                Group Memberships:
                                                <ul v-bind:key="groupMembershipEntry" v-for="groupMembershipEntry in getGroupMemberships(userId).length">
                                                  <li>{{ getGroupMemberships(userId)[groupMembershipEntry - 1]['group_name'] }} (ID: {{ getGroupMemberships(userId)[groupMembershipEntry - 1]['group_id'] }})</li>
                                                </ul>
                                            </b-collapse>
                                        </dd>
                                    </dl>
                                </b-col>
                            </b-row>
                            <br>
                            <br>
                        </b-collapse>
                    </b-container>
                </div>
        <div id="iam.users">
        </div><!--iam.users-->
    </div>

</template>

<script>
    const principalsUtil = require('../util/principals');
    // const managedPoliciesUtil = require('../util/managed-policies');
    // const inlinePoliciesUtil = require('../util/inline-policies');
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
            }
        }
    }
</script>

<style scoped>

</style>
