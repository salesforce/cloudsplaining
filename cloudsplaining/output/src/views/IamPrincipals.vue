<template>
    <b-tab key="iam-principals">
        <Principals v-bind:iam_data="iam_data"/>
    </b-tab>
</template>

<script>
import Principals from '../components/Principals';
export default {
    inject: ['iam_data'],
    components: {Principals} 
}
</script>