<template>
    <div class="changelog">
        <w-spinner color="orange" v-if="changelog.length < 1" />
        <div v-for="log in changelog" class="changelog__log mb5">
            <div class="title3 changelog__date">
                {{ log.Date }}
            </div>
            <ul class="changelog__news">
                <li v-for="news in log.Text" class="changelog__news-element ml4">
                    {{ news }}
                </li>
            </ul>

        </div>
    </div>
</template>
<script lang="ts" setup>
import type { Log } from "@/views/Login.vue"

const props = defineProps<{
    changelog: Log[];
}>();

</script>
<style lang="scss">
.changelog {
    margin: 25px;
    overflow: auto;

    min-height: 250px;

}
</style>