<template>
    <div class="report__wrapper__main">
        <div class="title1">
            с {{ from }} по {{ to }}
        </div>
        <w-checkbox v-model="dense">плоский вид</w-checkbox>
        <!-- <div>
            <w-checkbox class="mr5" v-for="col in schema">
                {{ col.title }}
            </w-checkbox>
        </div> -->
        <div v-for="table in props.tableData.sort((a: any, b: any) => a.level - b.level)">
            <ReportTableNew :dense="dense" :table-data="table" :schema="schema"></ReportTableNew>
        </div>

    </div>
</template>

<script setup lang="ts">
import ReportTableNew from "./ReportTableNew.vue";

import { ref } from "vue";

const dense = ref(false)

const props = defineProps<{
    tableData: any;
    schema: any;
    from: string;
    to: string;
}>();


</script>
