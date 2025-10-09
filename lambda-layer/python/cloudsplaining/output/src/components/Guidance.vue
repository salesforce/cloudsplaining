<template>
    <div style="text-align: justify">
        <!--Guidance: Triaging-->
        <h3 id="triage-guidance">Triaging</h3>
        <p>
            <span v-html="triageGuidance"></span>
        </p>
        <br>
        <br>

        <!--Guidance: Remediation-->
        <h3 id="remediation-guidance">Remediation</h3>
        <p>
            <span v-html="remediationGuidance"></span>
        </p>
        <br>
        <br>

        <!--Guidance: Validation-->
        <h3 id="validation-guidance">Validation</h3>
        <p>
            <span v-html="validationText"></span>
        </p>

        <br>
        <br>
    </div>
</template>

<script>
    var md = require('markdown-it')({
        html: true,
        linkify: true,
        typographer: true
    });
    import overviewRaw from '../assets/1-overview.md';
    import triageGuidanceRaw from '../assets/2-triage-guidance.md';
    import remediationGuidanceRaw from '../assets/3-remediation-guidance.md';
    import validationTextRaw from '../assets/4-validation.md';

    const overview = md.render(overviewRaw);
    const triageGuidance = md.render(triageGuidanceRaw);
    const remediationGuidance = md.render(remediationGuidanceRaw);
    const validationText = md.render(validationTextRaw);

    export default {
        name: "Guidance",
        computed: {
            overview() {
                return overview;
            },
            triageGuidance() {
                return triageGuidance;
            },
            remediationGuidance() {
                return remediationGuidance;
            },
            validationText() {
                return validationText;
            },
        }
    }
</script>

<style scoped>

</style>
