<template>
    <ol>
        <li v-bind:key="someFinding" v-for="someFinding in privilegeEscalationFinding">
            <a v-bind:href="`https://cloudsplaining.readthedocs.io/en/latest/glossary/privilege-escalation/#${someFinding.type}`" >{{ someFinding.type }}</a>
        (<span v-bind:key="action" v-for="(action, index) in someFinding.actions">
            <span v-if="index !== 0">, </span>
            <span><code>{{action}}</code></span>
        </span>)
            <br>
            <br>
        </li>
    </ol>
</template>

<script>
    export default {
        name: "PrivilegeEscalationFormat",
        props: {
            privilegeEscalationFinding: {
                type: Object
            }
        }
    }
</script>

<style scoped>

</style>
