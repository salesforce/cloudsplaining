<template>
    <span class="link2finding" @mouseenter="setHover(true)" @mouseleave="setHover(false)">
        <slot></slot>
        <span>
            <router-link v-if="active" :to=deepLink>
                <i class="bi bi-link-45deg" aria-hidden="true"></i>
            </router-link>
        </span>
    </span>
</template>

<script>
export default {
    name: "LinkToFinding",
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
        setHover(hovered) {
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
