<template>
        <Summary v-bind:iam_data="iam_data" :policy-filter="policyFilter"/>
</template>

<script>
import Summary from '../components/Summary'

export default {
    inject: ['iam_data'],
    components: {
        Summary
    },
    data() {
        return {
            policyFilter: "none"
        }
    },
}
</script>