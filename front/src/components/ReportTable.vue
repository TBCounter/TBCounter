<template>
  <div class="report__main">
    <div ref="table"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from "vue";

import { TabulatorFull as Tabulator } from 'tabulator-tables'; //import Tabulator library

const table = ref<any>(null); //reference to your table element
const tabulator = ref<any>(null); //variable to hold your table


const props = defineProps<{
  tableData: any;
  schema: any;
}>();

const allTables = ref<any>([])

const headers = ref<any>([])

const keyword = ref('')



onMounted(() => {
  allTables.value = props.tableData

  tabulator.value = new Tabulator(table.value, {
    height: "80vh",
    layout: "fitData",
    renderVertical: 'basic',

    data: filteredItems.value,
    columns: [
      { title: "Уровень", field: "level" },

    ],
    rowFormatter: function (row) {
      //create and style holder elements
      const holderEl = document.createElement("div");
      const tableEl = document.createElement("div");

      holderEl.style.boxSizing = "border-box";
      holderEl.style.padding = "10px 2px 10px 2px";
      holderEl.style.borderTop = "1px solid #333";
      holderEl.style.borderBottom = "1px solid #333";


      tableEl.style.border = "1px solid #333";

      holderEl.appendChild(tableEl);

      row.getElement().appendChild(holderEl);

      const subTable = new Tabulator(tableEl, {
        layout: "fitData",
        data: row.getData().data,
        columns: props.schema,

      })
    },
  });
})



const filteredItems = computed(() => {
  if (keyword.value !== '') {
    const result = []
    for (const table of allTables.value) {
      result.push({ data: table.data.filter((item: any) => new RegExp(keyword.value, 'i').test(item.name)), level: table.level })
    }

    return result

  } else {
    return allTables.value
  }
})


</script>


<style scoped lang="scss">
.report__main {
  // background: #f5d98f;
  // margin: auto;
  width: 100%;
  // overflow: scroll;
  // height: calc(100vh - 20px);
}


// :deep(.w-table) {
//   border-collapse: separate;
// }

// :deep(.w-table-wrap) {
//   overflow: visible;
//   border: none;
// }

// :deep(.w-table--fixed-header thead) {
//   z-index: 1;
// }


// :deep(.tabulator-tableHolder) {
//   max-height: 311px !important;
// }
</style>
