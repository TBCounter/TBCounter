<template>
  <div class="report__main mb10">
    <div class="report__heading w-flex mb1">

      <div class="title2">Уровень: {{ props.tableData.level }}</div>
      <div class="ml5">

        <w-button class="mr1" @click="downloadXLSX" id="download-xlsx">Download XLSX</w-button>
        <!-- <w-button class="mr1" @click="downloadPDF" id="download-pdf">Download PDF</w-button> -->

      </div>
    </div>
    <div ref="table"></div>
  </div>
</template>

<script setup lang="ts">

import { ref, onMounted, watch } from "vue";

import { TabulatorFull as Tabulator } from 'tabulator-tables'; //import Tabulator library
import { DownloadModule } from 'tabulator-tables';
const table = ref<any>(null); //reference to your table element
const tabulator = ref<any>(null); //variable to hold your table

const columnsList = ref([])

const props = defineProps<{
  tableData: any;
  schema: any;
  dense: boolean;
}>();

watch(() => props.dense, (first, second) => {
  drawTable()
});


function drawTable() {
  Tabulator.extendModule("download", "downloaders", {
    string: function (columns: any, data: any, options: any) {
      var fileContents = data.toString();
      return 'data:application/txt;charset=utf-8,' + encodeURIComponent(fileContents);
    }
  });
  // Tabulator.extendModule('move')
  tabulator.value = new Tabulator(table.value, {
    height: "100vh",
    layout: "fitData",
    data: props.tableData.data,
    columns: props.schema,
    autoColumns: props.dense,
    autoColumnsDefinitions: [
      {
        title: 'Очки',
        field: 'scores',
        minWidth: 60,
        headerFilter: "number",
        headerFilterPlaceholder: "минимум",
        headerFilterFunc: ">="
      },
      {
        title: 'Сумма',
        field: 'sum',
        minWidth: 60,
        headerFilter: "number",
        headerFilterPlaceholder: "минимум",
        headerFilterFunc: ">="
      },
      {
        title: 'Имя',
        field: 'name',
        headerFilter: "input",
        frozen: true
      }
    ]
  })
  tabulator.value.on('dataLoaded', (data: any) => {
    columnsList.value = tabulator.value.getColumns(true)
    columnsList.value.forEach((element: any) => {
      const innerColumns = element.getSubColumns()



      // element.updateDefinition({ title: "Updated Title" })
      innerColumns.forEach((column: any) => {
        // column.updateDefinition({ title: "Updated Title" })
      })
      // for (const column of innerColumns) {
      // }
    })
    // tabulator.value.updateColumnDefinition("name", { title: "Updated Title" })

  })


}


onMounted(() => {
  drawTable()
})
function downloadXLSX() {
  tabulator.value.download("xlsx", "data.xlsx", { sheetName: "My Data" });
}

// function downloadPDF() {
//   tabulator.value.download("pdf", "data.pdf", {
//     orientation: "portrait", //set page orientation to portrait
//     title: "Example Report", //add title to report
//   });
// }

// //trigger download of data.xlsx file
// document.getElementById("download-xlsx").addEventListener("click", function () {
//   table.download("xlsx", "data.xlsx", { sheetName: "My Data" });
// });

// //trigger download of data.pdf file
// document.getElementById("download-pdf").addEventListener("click", function () {
//   table.download("pdf", "data.pdf", {
//     orientation: "portrait", //set page orientation to portrait
//     title: "Example Report", //add title to report
//   });
// });



</script>


<style lang="scss" >
$colors: rgba(134, 163, 184, 0.2),
  rgba(232, 210, 166, 0.2),
  rgba(244, 132, 132, 0.2),
  rgba(194, 118, 100, 0.2),
  rgba(60, 125, 147, 0.2),
  rgba(168, 135, 36, 0.2),
  rgba(17, 33, 92, 0.2),
  rgba(199, 199, 172, 0.2),
  rgba(51, 13, 18, 0.2),
  rgba(60, 108, 63, 0.2),
  rgba(227, 199, 112, 0.2),
  rgba(63, 0, 113, 0.2),
  rgba(251, 37, 118, 0.2);


.report__main .tabulator .report-table__column {
  // &--name {
  //   background-color: rgba(0, 0, 255, 0.346)
  // }

  @each $color in $colors {
    $i: index($colors, $color );

    &--index#{$i} {
      background-color: $color;

      & .tabulator-col {
        background-color: $color;
      }
    }
  }

  &--scores {
    background-color: rgba(154, 61, 154, 0.345);
  }

  &--sum {
    background-color: rgba(217, 217, 82, 0.263);
  }
}
</style>