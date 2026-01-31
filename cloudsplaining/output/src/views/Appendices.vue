<template>
        <div v-if="appendices_content === 'default'">
            <Glossary />
        </div>
        <div v-else v-html="appendices_content"></div>
</template>

<script>
import Glossary from "../components/Glossary";
export default {
    components: { Glossary },
    data() {
        return {
            // eslint-disable-next-line no-undef
            appendices_content: appendices_content,
        };
    },
};
</script>
