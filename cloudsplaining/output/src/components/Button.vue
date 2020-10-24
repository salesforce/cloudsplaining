<template>
    <a :class="propStyle" class="button-link" v-on:click="updateLog">{{placeholder}}</a>
</template>

<script>

export default {
    props: ['placeholder' , 'propStyle'],
    methods: {
        updateLog() {
            this.$emit('clicked');
        }
    }
}
</script>

<style scoped>
    .button-link {
        color: #007BFF;
        display: inline-block;
        cursor: pointer;
    }

    .button-link:hover {
        color: #002854;
    }
</style>

