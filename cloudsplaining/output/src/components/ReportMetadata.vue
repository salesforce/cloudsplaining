<template>
    <div class="report-metadata" id="report-metadata">
        <h4>Metadata</h4>
        <ul>
            <li>Created: {{ reportDate }}</li>
            <li>Account ID: {{ accountId }}</li>
        </ul>
    </div>
</template>

<script>
    export default {
        name: "ReportMetadata",
        props: {
            accountId: String,
            reportDate: String,
        }
    }
</script>

<style scoped>

</style>