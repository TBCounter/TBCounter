<template>
  <div class="report-table__wrap">
    <div class="report-table__filter">
      <div style="display: flex;">
        <w-input class="ma1" style="max-width: 240px" type="date" v-model="rep.query.from" />
        <w-input style="max-width: 70px" class="ma1" type="time" v-model="rep.query.from_time"></w-input>
      </div>
      <div style="display: flex;">
        <w-input class="ma1" style="max-width: 240px" type="date" v-model="rep.query.to" />
        <w-input style="max-width: 70px" class="ma1" type="time" v-model="rep.query.to_time"></w-input>
      </div>
      <w-button class="ma1" type="button" @click="reportQuery">получить отчет</w-button>
      <w-button class="ma1" type="button" @click="saveQuery">сохранить отчет</w-button>
      <a :href="'clan-report/' + link" v-if="link">ссылка</a>

    </div>
    <div class="report-table__container" v-if="tableData.length">
      <ReportTableWrapper :from="''" :to="''" :schema="rep.schema" :tableData="tableData"></ReportTableWrapper>
    </div>
    <!-- <div class="report-table">
      <ReportTable v-if="tableData.length" :schema="rep.schema" :tableData="tableData"></ReportTable>
    </div> -->
  </div>
</template>

<script setup lang='ts'>
import { ref, computed, onMounted } from "vue";
import { useReport } from "@/stores/report";
import ReportTable from '@/components/ReportTable.vue'
import ReportTableWrapper from "@/components/ReportTableWrapper.vue";


const link = ref('')

const rep = useReport();

const tableData = computed(() => rep.data);

onMounted(() => {
  rep.data = []
})

async function reportQuery() {
  await rep.getReportWithQuery()
}

async function saveQuery() {
  await rep.saveReportQuery().then((reportLink) => {
    link.value = reportLink
  })
}


</script>

<style lang="scss" scoped>
.report-table {
  &__container {

    width: 80vw;
  }

  &__filter {
    display: flex;
  }
}
</style>