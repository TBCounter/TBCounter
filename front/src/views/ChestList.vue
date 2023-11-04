<template>
  <div>
    <div class="report-table__filter">
      <div style="display: flex;">
        <w-input style="max-width: 240px" class="ma1" type="date" v-model="listFrom"></w-input>
        <w-input style="max-width: 70px" class="ma1" type="time" v-model="listFromTime"></w-input>
      </div>
      <div style="display: flex;">
        <w-input style="max-width: 240px" class="ma1" type="date" v-model="listTo"></w-input>
        <w-input style="max-width: 70px" class="ma1" type="time" v-model="listToTime"></w-input>
      </div>
      <w-button class="ma1" bg-color="primary" @click="getListFileButton">скачать данные </w-button>
      <w-spinner v-if="LOADING"></w-spinner>

      <div class="report-table__pagination">
        <w-button :disabled="page < 2 || LOADING" @click="page--, getChestsRequest()">назад</w-button>
        <span class="report-table__number">{{ page }}</span>
        <w-button :disabled="page >= total_pages || LOADING" @click="page++, getChestsRequest()">далее</w-button>

      </div>
    </div>
    <div>
      <div>
        <w-button :disabled="!statusImage" class="ma1" @click="showStatusImage = !showStatusImage"
          bg-color="primary">последний скриншот</w-button>
        <div>Сегодня открыто: {{ today }} {{ acc?.vip ? 'без ограничений' : `сегодня осталось открыть ${600 - today}` }}
        </div>
      </div>
      <div v-if="showStatusImage">
        <img style="width: 100%" :src="'data:image/png;base64,' + statusImage">
      </div>
    </div>
    <w-table v-if="!LOADING" :headers="[
      { label: 'Имя', key: 'player' },
      { label: 'Сундук', key: 'chest_type' },
      { label: 'Имя сундука', key: 'chest_name' },
      { label: 'Время прихода', key: 'got_at' },
      { label: 'Время открытия', key: 'opened_in' },
    ]" v-model:sort="sorting" :items="chests" :mobile-breakpoint="640" expandable-rows>

      <template #row-expansion="{ item }">
        <img
          :src="item.path.startsWith('H://TotalBattle/') ? API_URL + '/' + item.path.substring(16) : API_URL + '/' + item.path">
        <img v-if="item.check_needed"
          :src="item.check_needed.startsWith('H://TotalBattle/') ? API_URL + '/' + item.check_needed.substring(16) : API_URL + '/' + item.check_needed">
        <w-button @click="saveChest(item)" v-if="item.check_needed">сохранить</w-button>
        <w-button @click="deleteChest(item)" v-if="item.check_needed">удалить</w-button>
      </template>
      <template #item-cell="{ item, label, header, index }">
        <div :class="{ 'red-light5--bg': item.check_needed }">
          {{
            header.key === 'got_at' || header.key === 'opened_in' ?
            processDate(label)
            : label
          }}
        </div>
      </template>

    </w-table>
    <span v-if="total_pages">всего {{ Math.round(total_pages) }} страниц и {{ total }} сундуков</span>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted } from "vue";
import { getListFile, getList, API_URL, WS_URL, getAccountStateImage, saveChestRequest, deleteChestRequest } from "@/api";
import { useAccount, IAccount } from "@/stores/account";
import { useAccountID } from "@/stores/accountID";
const accID = useAccountID()

const LOADING = ref(false)

const showStatusImage = ref(false)
const page = ref(1)
const chests = ref([])
const total_pages = ref(0)
const total = ref(0)
const today = ref(0)
const sorting = ref(undefined)

const listFrom = ref('')
const listTo = ref('')

const listFromTime = ref('00:00')
const listToTime = ref('23:59')


const statusImage = ref('')

const accStore = useAccount()
const acc = ref<IAccount>()
acc.value = accStore.currentAccount

const wsConnection = ref<WebSocket>()


function processDate(date: string) {
  let pr_date = new Date(date)
  return pr_date.toLocaleDateString() + " " + pr_date.toLocaleTimeString()
}

async function getChestsRequest() {
  LOADING.value = true
  await getList(acc.value!.id, page.value, sorting.value ? sorting.value[0] : '-opened_in').then((dt) => {
    const data = dt.data
    chests.value = data.items
    page.value = data.page
    total_pages.value = data.total_pages
    total.value = data.total
    LOADING.value = false
  })
}

async function saveChest(item: any) {
  await saveChestRequest(item.id).then(() => {
    item.check_needed = ''
  })
}


async function deleteChest(item: any) {
  await deleteChestRequest(item.id).then(() => {
    item = {}
  })
}

async function updateChests() {
  wsConnection.value = new WebSocket(WS_URL + 'chests/' + acc.value!.id)
  wsConnection.value.onmessage = async function (event) {
    if (!sorting.value && page.value == 1) {
      const data = JSON.parse(event.data)
      chests.value = data.chests
      page.value = data.page
      total_pages.value = data.total_pages
      total.value = data.total
      today.value = data.today_chests
      await getAccountStateImage(acc.value!.id).then(response => {
        if (statusImage.value && response) {
          statusImage.value = ''
        }
        statusImage.value = response
      })
    }
  }

  wsConnection.value.onopen = function (event) {
    // console.log(event)
    // console.log("Successfully connected to the echo websocket server...")
  }

}

async function getListFileButton() {
  const payload = { account_id: acc.value!.id, from: listFrom.value, to: listTo.value, from_time: listFromTime.value, to_time: listToTime.value, }
  const response = await getListFile(payload)
  const file = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement("a");
  link.href = file

  link.setAttribute('download', `report_${payload.account_id}_${payload.from}_${payload.to}.xlsx`);
  document.body.appendChild(link);
  link.click();

}

onMounted(async () => {
  await updateChests()
})

accID.$subscribe(async (mut, account) => {
  acc.value = accStore.currentAccount
  chests.value = []
  page.value = 1
  total_pages.value = 0
  statusImage.value = ''
  showStatusImage.value = false
  wsConnection.value?.close()
  await updateChests()
});


onUnmounted(() => {
  wsConnection.value?.close()
})

watch(() => sorting, async () => {
  getChestsRequest()
}, { deep: true })


</script>


<style scoped lang="scss">
.report-table {
  width: 80vw;

  @include media(tablet) {
    width: 100%;
  }

  &__filter {
    display: flex;
    flex-wrap: wrap;
    margin-bottom: 8px;
    align-items: center;
    gap: 8px;
  }

  &__pagination {
    margin-left: auto;
    align-items: center;
    display: flex;

  }

  &__number {
    margin: 0 8px;
    font-weight: 700;
    font-size: 24px;
  }
}
</style>
