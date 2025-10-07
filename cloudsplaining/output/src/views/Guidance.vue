<template>
    <b-tab>
        <div v-if="guidance_content === 'default'">
            <Guidance />
        </div>
        <div v-else v-html="guidance_content"></div>
    </b-tab>
</template>

<script>
import Guidance from "../components/Guidance";
export default {
    components: { Guidance },
    data() {
        return {
            // eslint-disable-next-line no-undef
            guidance_content: guidance_content,
        };
    },
};
</script>
