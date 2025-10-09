<template>
    <div>
        <!--Policy Document-->
        <div class="card-header">
            <a class="card-link" data-toggle="collapse"
               v-bind:data-parent="'#' + inlineOrManaged.toLowerCase() + '-policy' + '-' + policyId + '-' + 'card-details'"
               v-bind:href="'#' + inlineOrManaged.toLowerCase() + '-policy' + '-' + policyId + '-' +'policydocument'">
               Policy Document
            </a>
        </div>
        <div 
            class="panel-collapse collapse"
            ref="PolicyDocumentDetailsDiv"
            v-bind:id="inlineOrManaged.toLowerCase() + '-policy' + '-' + policyId + '-' +'policydocument'">
            <div class="card-body">
<pre><code>
{{ JSON.parse(JSON.stringify(policyDocument(policyId), undefined, '\t')) }}
</code></pre>
            </div>
        </div><!--Policy Document-->
    </div>
</template>

<script>
    const managedPoliciesUtil = require('../../util/managed-policies');
    const inlinePoliciesUtil = require('../../util/inline-policies');
    export default {
        name: "PolicyDocumentDetails",
        inject: ['toggleData'],
        props: {
            // Either "Inline", "AWS", or "Customer"
            managedBy: {
                type: String
            },
            policyId: {
                type: String
            },
            iam_data: {
                type: Object
            },
        },
        computed: {
            inlineOrManaged() {
                if ((this.managedBy === "AWS") || (this.managedBy === "Customer")) {
                    return "Managed"
                } else {
                    return "Inline"
                }
            }
        },
        methods: {
            policyDocument: function(policyId) {
                if (this.managedBy === "Inline") {
                    return inlinePoliciesUtil.getInlinePolicyDocument(this.iam_data, policyId);
                } else {
                    return managedPoliciesUtil.getManagedPolicyDocument(this.iam_data, this.managedBy, policyId);
                }
            },
        },
        watch: {
            toggleData: {
                handler(data) {
                    if (data.isAllExpanded && this.$refs['PolicyDocumentDetailsDiv']) {
                        this.$refs['PolicyDocumentDetailsDiv'].classList.add('show');
                    }
                    if (data.isAllCollapsed && this.$refs['PolicyDocumentDetailsDiv']) {
                        this.$refs['PolicyDocumentDetailsDiv'].classList.remove('show');
                    }
                },
                deep: true
            }
        }
    }
</script>

<style scoped>

</style>
