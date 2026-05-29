<template>
    <ol>
        <li v-bind:key="someFinding.type" v-for="someFinding in privilegeEscalationFinding">
            <a v-if="methodUrl(someFinding.type)" v-bind:href="methodUrl(someFinding.type)" target="_blank" rel="noopener noreferrer">{{ someFinding.type }}</a>
            <span v-else>{{ someFinding.type }}</span>
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
    const pathfinding = require('../../util/pathfinding');

    export default {
        name: "PrivilegeEscalationFormat",
        props: {
            privilegeEscalationFinding: {
                type: Array
            }
        },
        methods: {
            // Link each detected method to its pathfinding.cloud writeup; methods with
            // no pathfinding.cloud path render as plain text (handled by v-else).
            methodUrl(methodType) {
                return pathfinding.pathfindingUrl(methodType);
            }
        }
    }
</script>

<style scoped>

</style>
