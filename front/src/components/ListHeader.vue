<template>
  <div class="account">
    <div class="account-tabs">
      <div class="account-tabs__container">
        <div class="account_tab" :class="{ 'account_tab--active': tab == 'list' || tab == 'home' }"
          @click="chooseTab('list')">Список</div>
        <div class="account_tab" :class="{ 'account_tab--active': tab == 'report' }" @click="chooseTab('report')">Отчет
        </div>
        <div class="account_tab" :class="{ 'account_tab--active': tab == 'players' }" @click="chooseTab('players')">Клан
        </div>
        <div class="account_tab" :class="{ 'account_tab--active': tab == 'scores' }" @click="chooseTab('scores')">Очки
        </div>
        <div class="account_tab" :class="{ 'account_tab--active': tab == 'norms' }" @click="chooseTab('norms')">Нормы
        </div>
      </div>
      <Trigger class="account_trigger" :disabled="acc?.unavailable" :locked="acc!.is_locked" @click="openChests()">
      </Trigger>
    </div>
    <div class="account__main">
      {{ msg }}
      <slot />
    </div>
  </div>
</template>


<script setup lang="ts">
import Trigger from "@/components/Trigger.vue"
import { processChests, killProcessChests } from "@/api";

import { useAccount, IAccount } from "@/stores/account";
import { useAccountID } from "@/stores/accountID";
import { ref, watch } from "vue";

import { useRouter, useRoute } from 'vue-router'


const accStore = useAccount()
const accID = useAccountID()
const acc = ref<IAccount>()
acc.value = accStore.currentAccount

const msg = ref('')
const route = useRoute()
const router = useRouter()

const tab = ref('')

watch(() => route.name, () => {
  tab.value = route.name as string
}, { immediate: true })

async function chooseTab(direction: string) {
  router.push(direction)
}

accStore.$subscribe(async (mut, account) => {

  acc.value = accStore.currentAccount

});


async function openChests() {
  if (acc.value?.unavailable && !acc.value!.is_locked) {
    return
  }
  if (acc.value!.is_locked) {
    await killProcessChests(acc.value!.id).then(resp => {
      acc.value!.is_locked = true
      msg.value = "остановлено"
    })
    return // add here stop selenium
  }
  msg.value = "Пожалуйста, подождите. Это может занять продолжительное время. Вы можете закрыть эту вкладку"
  acc.value!.is_locked = true
  await processChests(acc.value!.id).then((resp) => {
    const dt = resp.data
    acc.value!.is_locked = true
    // msg.value = `Открыто ${dt.chests} сундуков и ${dt.banks} премиум сундуков`
    msg.value = dt
  })

}


</script>

<style scoped lang="scss">
.account {
  color: #361e09;

  &-tabs {
    display: flex;

    &__container {
      display: flex;
      width: 678px;
      flex-shrink: 0;
    }
  }

  &_tab {
    font-weight: 500;
    font-size: 20px;
    text-align: center;
    width: 105px;
    background: #c59c51;
    padding: 5px;
    margin: 0 5px;
    cursor: pointer;
    border-top: 3px solid #ab7635;
    border-right: 3px solid #ab7635;
    border-left: 3px solid #ab7635;
    border-radius: 5px 5px 0 0;
    display: flex;
    flex-shrink: 0;

    @include media(mobile) {
      font-size: 15px;
      width: 80px;
    }
  }

  &_tab--active {
    background: #f5d98f;
  }

  &__main {
    background: #f5d98f;
    min-height: 200px;
    max-height: calc(100vh - 260px);
    overflow: auto;
    padding: 5px;
    border-radius: 3px;

    @include media(tablet) {
      padding-left: 20px;
    }

    @include media(mobile) {
      font-size: 14px;
      line-height: 1.2;
      max-height: 73vh;
    }
  }

  &_trigger {
    margin-left: auto;
    width: 230px;
    flex-shrink: 0;
  }
}
</style>