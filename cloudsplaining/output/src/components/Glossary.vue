<template>
    <div style="text-align: justify">
        <!--Guidance: Glossary-->
        <h3 id="overview">Glossary</h3>
        <p>
            <span v-html="glossary"></span>
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
    import glossaryRaw from '../assets/glossary.md';

    const glossary = md.render(glossaryRaw);

    export default {
        name: "Glossary",
        computed: {
            glossary() {
                return glossary;
            },
        }
    }
</script>

<style scoped>

</style>
