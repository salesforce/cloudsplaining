<template>
    <div>
        <b-list-group>
            <div v-bind:key="riskName" v-for="riskName in riskNames">
                <template
                    v-if="getRiskAssociatedWithPrincipal(principalId, principalType, riskName).length > 0">
                    <dd class="col-sm-12">
                        <dl class="row">
                            <b-list-group-item
                                :action="true"
                                class="d-flex justify-content-between align-items-center"
                                v-b-toggle="`iam.${principalType}.${getPrincipalMetadata(principalId, principalType)['id']}.risk.${riskName}.collapse`">
                                {{ addSpacesInPascalCaseString(riskName) }}

                                <b-button size="sm" v-bind:variant="getRiskLevel(riskName)"
                                >
                                    {{ getRiskAssociatedWithPrincipal(principalId, principalType,
                                    riskName).length }}
                                </b-button>
                            </b-list-group-item>
                        </dl>
                    </dd>
                    <b-collapse
                        v-bind:id="`iam.${principalType}.${getPrincipalMetadata(principalId, principalType)['id']}.risk.${riskName}.collapse`">
                        <dd class="col-sm-12">
                            <pre><code>{{ getRiskAssociatedWithPrincipal(principalId, principalType, riskName) }}</code></pre>
                        </dd>
                    </b-collapse>
                </template>
            </div>
        </b-list-group>
    </div>
</template>

<script>
    const principalsUtil = require('../../util/principals');
    const otherUtil = require('../../util/other');
    const glossary = require('../../util/glossary');

    export default {
        name: "RisksPerPrincipal",
        props: {
            iam_data: {
                type: Object
            },
            principalType: {
                type: String
            },
            principalId: {
                type: String
            }
        },
        computed: {
            riskNames() {
                let riskDetails = glossary.getRiskDetailsToDisplay();
                let riskNameArray = riskDetails.map(function (risk) { return risk.risk_type; });
                // console.log(`Risk names: ${riskNameArray}`);
                riskNameArray.push("PrivilegeEscalation");
                riskNameArray.sort();
                return riskNameArray;
                // return ["DataExfiltration", "ResourceExposure", "PrivilegeEscalation", "InfrastructureModification"]
            },
        },
        methods: {
            getPrincipalMetadata: function (principalName, principalType) {
                return principalsUtil.getPrincipalMetadata(this.iam_data, principalName, principalType)
            },
            getRiskAssociatedWithPrincipal: function (principalName, principalType, riskType) {
                return principalsUtil.getRiskAssociatedWithPrincipal(this.iam_data, principalName, principalType, riskType)
            },
            getRiskLevel: function (riskType) {
                return glossary.getRiskAlertIndicatorColor(riskType)
                // if (riskType === "DataExfiltration") {
                //     return "warning"
                // }
                // if (riskType === "PrivilegeEscalation") {
                //     return "danger"
                // }
                // if (riskType === "ResourceExposure") {
                //     return "warning"
                // }
                // if (riskType === "InfrastructureModification") {
                //     return "info"
                // }
            },
            addSpacesInPascalCaseString: function (s) {
                return otherUtil.addSpacesInPascalCaseString(s)
            },
        }
    }
</script>

<style scoped>

</style>
