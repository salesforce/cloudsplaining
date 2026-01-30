<template>
    <div>
        <!--Policy Document-->
        <div class="card-header">
            <b-button
                class="card-link p-0"
                variant="link"
                v-b-toggle="collapseId"
            >
                Policy Document
            </b-button>
        </div>
        <b-collapse
            v-model="isExpanded"
            :id="collapseId"
            class="panel-collapse"
        >
            <div class="card-body">
<pre><code>
{{ JSON.parse(JSON.stringify(policyDocument(policyId), undefined, '\t')) }}
</code></pre>
            </div>
        </b-collapse><!--Policy Document-->
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
            collapseId() {
                return `${this.inlineOrManaged.toLowerCase()}-policy-${this.policyId}-policydocument`;
            },
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
        data() {
            return {
                isExpanded: false
            }
        },
        watch: {
            toggleData: {
                handler(data) {
                    if (data.isAllExpanded) {
                        this.isExpanded = true;
                    }
                    if (data.isAllCollapsed) {
                        this.isExpanded = false;
                    }
                },
                deep: true
            }
        }
    }
</script>

<style scoped>

</style>
