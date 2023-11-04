<template>
    <component :is="layout"></component>
</template>

<script setup lang="ts">
import AppLayoutEmpty from "./AppLayoutEmpty.vue";
import AppLayoutDefault from './AppLayoutDefault.vue'
import AppLayoutLogin from './AppLayoutLogin.vue'

import { watch, shallowRef } from "vue";
import { useRoute } from "vue-router";

const layout = shallowRef(AppLayoutEmpty);
const router = useRoute();

watch(
    () => router.meta,
    (meta) => {
        if (meta.layout == 'authorized') {
            layout.value = AppLayoutDefault
        } else if (meta.layout == 'public') {
            layout.value = AppLayoutEmpty
        } else if (meta.layout == 'login') {
            layout.value = AppLayoutLogin
        }
    },
    { immediate: true }
)
</script>