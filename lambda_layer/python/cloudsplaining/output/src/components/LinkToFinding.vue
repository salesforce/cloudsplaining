<template>
    <span v-b-hover="hoverCB" class="link2finding">
        <slot></slot>
        <span>
            <router-link v-if="active" :to=deepLink>
                <b-icon-link45deg aria-hidden="true"></b-icon-link45deg>
            </router-link>
        </span>
    </span>
</template>

<script>
import { BIconLink45deg } from 'bootstrap-vue'

export default {
    name: "LinkToFinding",
    components: {
        BIconLink45deg
    },
    props: {
        findingId: {
            type: String
        }
    },
    computed: {
        deepLink() {
            return `#${this.findingId}`
        }
    },
    data() {
        return {
            active: false
        }
    },

    methods: {
        hoverCB(hovered) {
            this.active = hovered
        }
    }

}
</script>

<style scoped>
.link2finding {
    position: relative;
    display: block;
}
</style>
