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
                <div v-bind:key="roleName" v-for="roleName in roleNames">
                    <br>
                    <b-container>
                        <b-row class="px-2">
                            <b-col>
                                <h4>{{ roleName }}
                                    <br>
                                    <small class="text-muted">{{getPrincipalMetadata(roleName, 'Role')['arn']}}</small>
                                </h4>
                            </b-col>
                            <b-col>
                                <b-button
                                        v-b-toggle="'iam.roles' + '.' + getPrincipalMetadata(roleName, 'Role')['id'] + '.' + 'risk' + '.' + 'collapse'">
                                    Show
                                </b-button>
                            </b-col>
                        </b-row>
                        <br>
                        <b-collapse
                                v-bind:id="'iam.roles' + '.' + getPrincipalMetadata(roleName, 'Role')['id'] + '.' + 'risk' + '.' + 'collapse'">
                            <b-row class="px-2">
                                <b-col lg="4">
                                    <h5>Risks</h5>
                                    <b-list-group>
                                        <div v-bind:key="riskName" v-for="riskName in riskNames">
                                            <template
                                                    v-show="getRiskAssociatedWithPrincipal(roleName, 'Role', riskName).length > 0">
                                                <dd class="col-sm-12">
                                                    <dl class="row">
                                                        <b-list-group-item
                                                                class="d-flex justify-content-between align-items-center"
                                                                v-b-toggle="'iam.roles' + '.' + getPrincipalMetadata(roleName, 'Role')['id'] + '.' + 'risk' + '.' + riskName + '.' + 'collapse'"
                                                                :action="true">
                                                            {{ addSpacesInPascalCaseString(riskName) }}

                                                            <b-button v-bind:variant="getRiskLevel(riskName)" size="sm"
                                                                      >
                                                                {{ getRiskAssociatedWithPrincipal(roleName, "Role",
                                                                riskName).length }}
                                                            </b-button>
                                                        </b-list-group-item>
                                                    </dl>
                                                </dd>
                                                <b-collapse
                                                        v-bind:id="'iam.roles' + '.' + getPrincipalMetadata(roleName, 'Role')['id'] + '.' + 'risk' + '.' + riskName + '.' + 'collapse'">
                                                    <dd class="col-sm-12">
                                                        <br>
                                                        <pre><code>{{ getRiskAssociatedWithPrincipal(roleName, "Role", riskName) }}</code></pre>
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
                                        <dt class="col-sm-3">Created</dt>
                                        <dd class="col-sm-9">{{getPrincipalMetadata(roleName, 'Role')['create_date']}}
                                        </dd>

                                        <dt class="col-sm-3">ARN</dt>
                                        <dd class="col-sm-9 text-monospace">{{getPrincipalMetadata(roleName,
                                            'Role')['arn']}}
                                        </dd>

                                        <dt class="col-sm-3">Inline Policies</dt>
                                        <dd class="col-sm-9">
                                            <b-button size="sm"
                                                      v-b-toggle="'iam.roles' + '.' + getPrincipalMetadata(roleName, 'Role')['id'] + '.' + 'inline-policies' + '.' + 'collapse'">
                                                {{ getPrincipalPolicyNames(roleName, "Role", "Inline").length }}
                                            </b-button>
                                            <b-collapse
                                                    v-bind:id="'iam.roles' + '.' + getPrincipalMetadata(roleName, 'Role')['id'] + '.' + 'inline-policies' + '.' + 'collapse'">
                                                <br>
                                                <pre><code>{{ getPrincipalPolicyNames(roleName, "Role", "Inline") }}</code></pre>
                                            </b-collapse>
                                        </dd>

                                        <dt class="col-sm-3">AWS-Managed Policies</dt>
                                        <dd class="col-sm-9">
                                            <b-button size="sm"
                                                      v-b-toggle="'iam.roles' + '.' + getPrincipalMetadata(roleName, 'Role')['id'] + '.' + 'aws-managed-policies' + '.' + 'collapse'">
                                                {{ getPrincipalPolicyNames(roleName, "Role", "AWS").length }}
                                            </b-button>
                                            <b-collapse
                                                    v-bind:id="'iam.roles' + '.' + getPrincipalMetadata(roleName, 'Role')['id'] + '.' + 'aws-managed-policies' + '.' + 'collapse'">
                                                <br>
                                                <pre><code>{{ getPrincipalPolicyNames(roleName, "Role", "AWS") }}</code></pre>
                                            </b-collapse>
                                        </dd>

                                        <dt class="col-sm-3">Customer-Managed Policies</dt>
                                        <dd class="col-sm-9">
                                            <b-button size="sm"
                                                      v-b-toggle="'iam.roles' + '.' + getPrincipalMetadata(roleName, 'Role')['id'] + '.' + 'customer-managed-policies' + '.' + 'collapse'">
                                                {{ getPrincipalPolicyNames(roleName, "Role", "Customer").length }}
                                            </b-button>
                                            <b-collapse
                                                    v-bind:id="'iam.roles' + '.' + getPrincipalMetadata(roleName, 'Role')['id'] + '.' + 'customer-managed-policies' + '.' + 'collapse'">
                                                <br>
                                                <pre><code>{{ getPrincipalPolicyNames(roleName, "Role", "Customer") }}</code></pre>
                                            </b-collapse>
                                        </dd>

                                        <dt class="col-sm-3">Role Trust Policy</dt>
                                        <dd class="col-sm-9">
                                            <b-button size="sm"
                                                      v-b-toggle="'iam.roles' + '.' + getPrincipalMetadata(roleName, 'Role')['id'] + '.' + 'role-trust-policy' + '.' + 'collapse'">
                                                Details
                                            </b-button>
                                            <b-collapse
                                                    v-bind:id="'iam.roles' + '.' + getPrincipalMetadata(roleName, 'Role')['id'] + '.' + 'role-trust-policy' + '.' + 'collapse'">
                                                <br>
                                                <pre><code>{{ JSON.parse(JSON.stringify(getRoleTrustPolicy(roleName))) }}</code></pre>
                                            </b-collapse>
                                        </dd>
                                        <!--Instance Profiles-->
                                        <dt class="col-sm-3">Instance Profiles</dt>
                                        <dd class="col-sm-9">
                                            <b-button size="sm"
                                                      v-b-toggle="'iam.roles' + '.' + getPrincipalMetadata(roleName, 'Role')['id'] + '.' + 'instance-profiles' + '.' + 'collapse'">
                                                {{ getPrincipalMetadata(roleName, 'Role')['instance_profiles'].length }}
                                            </b-button>
                                            <b-collapse
                                                    v-bind:id="'iam.roles' + '.' + getPrincipalMetadata(roleName, 'Role')['id'] + '.' + 'instance-profiles' + '.' + 'collapse'">
                                                <br>
                                                <pre><code>{{ JSON.parse(JSON.stringify(getPrincipalMetadata(roleName, 'Role')['instance_profiles'])) }}</code></pre>
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
            <div v-bind:key="groupName" v-for="groupName in groupNames">
                    <br>
                    <b-container>
                        <b-row class="px-2">
                            <b-col>
                                <h4>{{ groupName }}
                                    <br>
                                    <small class="text-muted">{{getPrincipalMetadata(groupName, 'Group')['arn']}}</small>
                                </h4>
                            </b-col>
                            <b-col>
                                <b-button
                                        v-b-toggle="'iam.groups' + '.' + getPrincipalMetadata(groupName, 'Group')['id'] + '.' + 'risk' + '.' + 'collapse'">
                                    Show
                                </b-button>
                            </b-col>
                        </b-row>
                        <br>
                        <b-collapse
                                v-bind:id="'iam.groups' + '.' + getPrincipalMetadata(groupName, 'Group')['id'] + '.' + 'risk' + '.' + 'collapse'">
                            <b-row class="px-2">
                                <b-col lg="4">
                                    <h5>Risks</h5>
                                    <b-list-group>
                                        <div v-bind:key="riskName" v-for="riskName in riskNames">
                                            <template
                                                    v-show="getRiskAssociatedWithPrincipal(groupName, 'Group', riskName).length > 0">
                                                <dd class="col-sm-12">
                                                    <dl class="row">
                                                        <b-list-group-item
                                                                class="d-flex justify-content-between align-items-center"
                                                                v-b-toggle="'iam.groups' + '.' + getPrincipalMetadata(groupName, 'Group')['id'] + '.' + 'risk' + '.' + riskName + '.' + 'collapse'"
                                                                :action="true">
                                                            {{ addSpacesInPascalCaseString(riskName) }}

                                                            <b-button v-bind:variant="getRiskLevel(riskName)" size="sm">
                                                                {{ getRiskAssociatedWithPrincipal(groupName, "Group",
                                                                riskName).length }}
                                                            </b-button>
                                                        </b-list-group-item>
                                                    </dl>
                                                </dd>
                                                <b-collapse
                                                        v-bind:id="'iam.groups' + '.' + getPrincipalMetadata(groupName, 'Group')['id'] + '.' + 'risk' + '.' + riskName + '.' + 'collapse'">
                                                    <dd class="col-sm-12">
                                                        <br>
                                                        <pre><code>{{ getRiskAssociatedWithPrincipal(groupName, "Group", riskName) }}</code></pre>
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
                                        <dt class="col-sm-3">Created</dt>
                                        <dd class="col-sm-9">{{getPrincipalMetadata(groupName, 'Group')['create_date']}}
                                        </dd>

                                        <dt class="col-sm-3">ARN</dt>
                                        <dd class="col-sm-9 text-monospace">{{getPrincipalMetadata(groupName,
                                            'Group')['arn']}}
                                        </dd>

                                        <dt class="col-sm-3">Inline Policies</dt>
                                        <dd class="col-sm-9">
                                            <b-button size="sm"
                                                      v-b-toggle="'iam.groups' + '.' + getPrincipalMetadata(groupName, 'Group')['id'] + '.' + 'inline-policies' + '.' + 'collapse'">
                                                {{ getPrincipalPolicyNames(groupName, "Group", "Inline").length }}
                                            </b-button>
                                            <b-collapse
                                                    v-bind:id="'iam.groups' + '.' + getPrincipalMetadata(groupName, 'Group')['id'] + '.' + 'inline-policies' + '.' + 'collapse'">
                                                <br>
                                                <pre><code>{{ getPrincipalPolicyNames(groupName, "Group", "Inline") }}</code></pre>
                                            </b-collapse>
                                        </dd>

                                        <dt class="col-sm-3">AWS-Managed Policies</dt>
                                        <dd class="col-sm-9">
                                            <b-button size="sm"
                                                      v-b-toggle="'iam.groups' + '.' + getPrincipalMetadata(groupName, 'Group')['id'] + '.' + 'aws-managed-policies' + '.' + 'collapse'">
                                                {{ getPrincipalPolicyNames(groupName, "Group", "AWS").length }}
                                            </b-button>
                                            <b-collapse
                                                    v-bind:id="'iam.groups' + '.' + getPrincipalMetadata(groupName, 'Group')['id'] + '.' + 'aws-managed-policies' + '.' + 'collapse'">
                                                <br>
                                                <pre><code>{{ getPrincipalPolicyNames(groupName, "Group", "AWS") }}</code></pre>
                                            </b-collapse>
                                        </dd>

                                        <dt class="col-sm-3">Customer-Managed Policies</dt>
                                        <dd class="col-sm-9">
                                            <b-button size="sm"
                                                      v-b-toggle="'iam.groups' + '.' + getPrincipalMetadata(groupName, 'Group')['id'] + '.' + 'customer-managed-policies' + '.' + 'collapse'">
                                                {{ getPrincipalPolicyNames(groupName, "Group", "Customer").length }}
                                            </b-button>
                                            <b-collapse
                                                    v-bind:id="'iam.groups' + '.' + getPrincipalMetadata(groupName, 'Group')['id'] + '.' + 'customer-managed-policies' + '.' + 'collapse'">
                                                <br>
                                                <pre><code>{{ getPrincipalPolicyNames(groupName, "Group", "Customer") }}</code></pre>
                                            </b-collapse>
                                        </dd>

                                        <dt class="col-sm-3">Group Members</dt>
                                        <dd class="col-sm-9">
                                            <b-button size="sm"
                                                      v-b-toggle="'iam.groups' + '.' + getPrincipalMetadata(groupName, 'Group')['id'] + '.' + 'group-members' + '.' + 'collapse'">
                                                Details
                                            </b-button>
                                            <b-collapse
                                                    v-bind:id="'iam.groups' + '.' + getPrincipalMetadata(groupName, 'Group')['id'] + '.' + 'group-members' + '.' + 'collapse'">
                                                <br>
                                                <pre><code>{{ JSON.parse(JSON.stringify(getGroupMembers(groupName))) }}</code></pre>
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
            <div v-bind:key="userName" v-for="userName in userNames">
                    <br>
                    <b-container>
                        <b-row class="px-2">
                            <b-col>
                                <h4>{{ userName }}
                                    <br>
                                    <small class="text-muted">{{getPrincipalMetadata(userName, 'User')['arn']}}</small>
                                </h4>
                            </b-col>
                            <b-col>
                                <b-button
                                        v-b-toggle="'iam.users' + '.' + getPrincipalMetadata(userName, 'User')['id'] + '.' + 'risk' + '.' + 'collapse'">
                                    Show
                                </b-button>
                            </b-col>
                        </b-row>
                        <br>
                        <b-collapse
                                v-bind:id="'iam.users' + '.' + getPrincipalMetadata(userName, 'User')['id'] + '.' + 'risk' + '.' + 'collapse'">
                            <b-row class="px-2">
                                <b-col lg="4">
                                    <h5>Risks</h5>
                                    <b-list-group>
                                        <div v-bind:key="riskName" v-for="riskName in riskNames">
                                            <template
                                                    v-show="getRiskAssociatedWithPrincipal(userName, 'User', riskName).length > 0">
                                                <dd class="col-sm-12">
                                                    <dl class="row">
                                                        <b-list-group-item
                                                                class="d-flex justify-content-between align-items-center"
                                                                v-b-toggle="'iam.users' + '.' + getPrincipalMetadata(userName, 'User')['id'] + '.' + 'risk' + '.' + riskName + '.' + 'collapse'"
                                                                :action="true">
                                                            {{ addSpacesInPascalCaseString(riskName) }}

                                                            <b-button v-bind:variant="getRiskLevel(riskName)" size="sm">
                                                                {{ getRiskAssociatedWithPrincipal(userName, "User",
                                                                riskName).length }}
                                                            </b-button>
                                                        </b-list-group-item>
                                                    </dl>
                                                </dd>
                                                <b-collapse
                                                        v-bind:id="'iam.users' + '.' + getPrincipalMetadata(userName, 'User')['id'] + '.' + 'risk' + '.' + riskName + '.' + 'collapse'">
                                                    <dd class="col-sm-12">
                                                        <br>
                                                        <pre><code>{{ getRiskAssociatedWithPrincipal(userName, "User", riskName) }}</code></pre>
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
                                        <dt class="col-sm-3">Created</dt>
                                        <dd class="col-sm-9">{{getPrincipalMetadata(userName, 'User')['create_date']}}
                                        </dd>

                                        <dt class="col-sm-3">ARN</dt>
                                        <dd class="col-sm-9 text-monospace">{{getPrincipalMetadata(userName,
                                            'User')['arn']}}
                                        </dd>

                                        <dt class="col-sm-3">Inline Policies</dt>
                                        <dd class="col-sm-9">
                                            <b-button size="sm"
                                                      v-b-toggle="'iam.users' + '.' + getPrincipalMetadata(userName, 'User')['id'] + '.' + 'inline-policies' + '.' + 'collapse'">
                                                {{ getPrincipalPolicyNames(userName, "User", "Inline").length }}
                                            </b-button>
                                            <b-collapse
                                                    v-bind:id="'iam.users' + '.' + getPrincipalMetadata(userName, 'User')['id'] + '.' + 'inline-policies' + '.' + 'collapse'">
                                                <br>
                                                <pre><code>{{ getPrincipalPolicyNames(userName, "User", "Inline") }}</code></pre>
                                            </b-collapse>
                                        </dd>

                                        <dt class="col-sm-3">AWS-Managed Policies</dt>
                                        <dd class="col-sm-9">
                                            <b-button size="sm"
                                                      v-b-toggle="'iam.users' + '.' + getPrincipalMetadata(userName, 'User')['id'] + '.' + 'aws-managed-policies' + '.' + 'collapse'">
                                                {{ getPrincipalPolicyNames(userName, "User", "AWS").length }}
                                            </b-button>
                                            <b-collapse
                                                    v-bind:id="'iam.users' + '.' + getPrincipalMetadata(userName, 'User')['id'] + '.' + 'aws-managed-policies' + '.' + 'collapse'">
                                                <br>
                                                <pre><code>{{ getPrincipalPolicyNames(userName, "User", "AWS") }}</code></pre>
                                            </b-collapse>
                                        </dd>

                                        <dt class="col-sm-3">Customer-Managed Policies</dt>
                                        <dd class="col-sm-9">
                                            <b-button size="sm"
                                                      v-b-toggle="'iam.users' + '.' + getPrincipalMetadata(userName, 'User')['id'] + '.' + 'customer-managed-policies' + '.' + 'collapse'">
                                                {{ getPrincipalPolicyNames(userName, "User", "Customer").length }}
                                            </b-button>
                                            <b-collapse
                                                    v-bind:id="'iam.users' + '.' + getPrincipalMetadata(userName, 'User')['id'] + '.' + 'customer-managed-policies' + '.' + 'collapse'">
                                                <br>
                                                <pre><code>{{ getPrincipalPolicyNames(userName, "User", "Customer") }}</code></pre>
                                            </b-collapse>
                                        </dd>

                                        <dt class="col-sm-3">Group Memberships</dt>
                                        <dd class="col-sm-9">
                                            <b-button size="sm"
                                                      v-b-toggle="'iam.users' + '.' + getPrincipalMetadata(userName, 'User')['id'] + '.' + 'group-membership' + '.' + 'collapse'">
                                                Details
                                            </b-button>
                                            <b-collapse
                                                    v-bind:id="'iam.users' + '.' + getPrincipalMetadata(userName, 'User')['id'] + '.' + 'group-membership' + '.' + 'collapse'">
                                                <br>
                                                <p>Group Memberships</p>
                                                <pre><code>{{ JSON.parse(JSON.stringify(getGroupMembers(userName))) }}</code></pre>
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
            roleNames() {
                return principalsUtil.getPrincipalNames(this.iam_data, "Role");
            },
            userNames() {
                return principalsUtil.getPrincipalNames(this.iam_data, "User");
            },
            groupNames() {
                return principalsUtil.getPrincipalNames(this.iam_data, "Group");
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
            getRoleTrustPolicy: function (roleName) {
                return rolesUtil.getTrustPolicyDocumentForRole(this.iam_data, roleName)
            },
            getRiskDefinition: function (riskType) {
                return glossary.getRiskDefinition(riskType)
            },
            getGroupMembers: function (groupName) {
                return groupsUtil.getGroupMembers(this.iam_data, groupName)
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