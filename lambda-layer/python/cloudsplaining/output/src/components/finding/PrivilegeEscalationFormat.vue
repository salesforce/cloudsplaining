<template>
    <ol>
        <li v-bind:key="someFinding.type" v-for="someFinding in privilegeEscalationFinding">
            <a v-bind:href="`https://cloudsplaining.readthedocs.io/en/latest/glossary/privilege-escalation/#${someFinding.type}`" >{{ someFinding.type }}</a>
        (<span v-bind:key="someAction" v-for="(someAction, index) in someFinding.actions">
            <span v-if="index !== 0">, </span>
            <span><code>{{someAction}}</code></span>
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
                type: Array
            }
        }
    }
</script>

<style scoped>

</style>
