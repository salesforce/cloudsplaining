<template>
    <ol>
        <li v-bind:key="someFinding" v-for="someFinding in privilegeEscalationFinding">
            {{ someFinding.type }}
            <br>
            <ul>
                <li>Actions:
                    <ul>
                        <li v-bind:key="action" v-for="action in someFinding.actions">
                            {{ action }}
                        </li>
                    </ul>
                </li>
            </ul>
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
