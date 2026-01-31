<template>
    <Principals v-bind:iam_data="iam_data"/>
</template>

<script>
import Principals from '../components/Principals';
export default {
    inject: ['iam_data'],
    components: {Principals} 
}
</script>
