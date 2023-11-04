<template>
  <!-- <ReportTable v-if="tableData.length" :schema="schema" :tableData="tableData"></ReportTable> -->
  <div class="report">
    <ReportTableWrapper :from="from" :to="to" v-if="tableData.length" :schema="schema" :tableData="tableData">
    </ReportTableWrapper>
  </div>
</template>

<script lang='ts' setup>
import { ref, onMounted } from "vue";
import { getClanReport } from "@/api";

import { useRoute } from 'vue-router'

import ReportTableWrapper from '@/components/ReportTableWrapper.vue'


const route = useRoute()

const hash = route.params.hash as string

const tableData = ref([])
const schema = ref([])

const from = ref('')
const to = ref('')

onMounted(async () => {
  const response = await getClanReport(hash)
  tableData.value = response.data.result.map((table: any) => ({ 'data': JSON.parse(table.data).data, 'level': table.level }))
  schema.value = response.data.schema
  from.value = response.data.from
  to.value = response.data.to
})

</script>

<style scoped lang="scss">
.report {
  width: calc(100vw - 40px);
}
</style>
