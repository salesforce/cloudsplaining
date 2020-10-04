<template>
    <div>
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
                            <pre><code>{{ getRiskAssociatedWithPrincipal(roleId, "Role", roleRiskName) }}</code></pre>
                        </dd>
                    </b-collapse>
                </template>
            </div>
        </b-list-group>
    </div>
</template>

<script>
    export default {
        name: "RisksPerPrincipal"
    }
</script>

<style scoped>

</style>
