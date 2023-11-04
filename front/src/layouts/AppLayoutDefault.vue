<template>
  <div class="default-page">

    <div class="left-menu">
      <div class="left-menu__monogram--top"></div>
      <div class="left-menu__accounts">
        <div class="left-menu__accounts--item" v-for="account in myAccounts">
          <div class="left-menu__cursor" v-if="account.id == accStore.currentID"></div>
          <Account :account="account" />
        </div>
        <div class="left-menu__accounts--item">
          <div @click="showModal" class="add_account">+</div>
        </div>
      </div>
      <div class="left-menu__monogram--bottom"></div>
    </div>
    <div class="main-page" v-if="acc!.name">
      <div class="main-page__top">
        <div class="main-page__header">
          <h1>{{ acc!.name }}</h1>
          <h3>{{ acc!.clan }}</h3>
        </div>
        <w-icon @click="isChangelogVisible = true" class="main-page__settings mt1 mr1" xl>
          material-icons list
        </w-icon>
        <w-icon @click="showQueue" class=" mt1 mr1" xl>
          material-icons cloud_queue
        </w-icon>
        <w-icon @click="showSettings" class=" mt1 mr1" xl>
          material-icons settings
        </w-icon>
      </div>

      <div class="main-page__main">
        <ListHeader>
          <RouterView />
        </ListHeader>
      </div>

    </div>
    <Modal v-show="isModalVisible" @close="closeModal"></Modal>
    <ModalSettings v-if="isSettingsVisible" @close="closeSettings"></ModalSettings>
    <ModalQueue v-if="isQueueVisible" @close="isQueueVisible = false"></ModalQueue>
    <ModalChangelog v-if="isChangelogVisible" @close="isChangelogVisible = false"></ModalChangelog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from "vue";
import { getAccounts, WS_URL } from "@/api";
import { useAccount, IAccount } from "@/stores/account";
import { useJWT } from "@/stores/jwt";
import Modal from "@/components/Modal.vue";
import ModalSettings from "@/components/ModalSettings.vue";
import ModalQueue from "@/components/ModalQueue.vue";
import ModalChangelog from "@/components/ModalChangelog.vue";
import ListHeader from "@/components/ListHeader.vue"
import { useAccountID } from "@/stores/accountID";

import Account from "@/components/Account.vue";

const myAccounts = ref([] as any);
const isModalVisible = ref(false);
const isSettingsVisible = ref(false);
const isQueueVisible = ref(false);
const isChangelogVisible = ref(false);
const accStore = useAccount()
const wsConnection = ref<WebSocket>()
const jwt = useJWT();

const acc = ref<IAccount>()
acc.value = accStore.currentAccount

function showModal() {
  isModalVisible.value = true;
}

async function closeModal() {
  isModalVisible.value = false;
}


function showSettings() {
  isSettingsVisible.value = true;
}

async function closeSettings() {
  isSettingsVisible.value = false;
}

function showQueue() {
  isQueueVisible.value = true
}


const accID = useAccountID()

accID.$subscribe(async (mut, account) => {

  acc.value = accStore.currentAccount
  myAccounts.value = accStore.accounts
});

onMounted(async () => {
  await getAccounts().then((res) => {
    myAccounts.value = res.data;
  });
  if (myAccounts.value && myAccounts.value.length > 0) {
    accStore.updateAccount(myAccounts.value)
    accStore.chooseAccount(myAccounts.value[0].id)
  }
  wsConnection.value = new WebSocket(WS_URL + 'info/' + jwt.getUserID)
  wsConnection.value.onmessage = async function (event) {

    accStore.updateAccount(JSON.parse(event.data))
    myAccounts.value = accStore.accounts
  }

  wsConnection.value.onopen = function (event) {
  }

});

onUnmounted(() => {
  wsConnection.value?.close()
})

</script>

<style scoped lang="scss">
.default-page {
  background: url("../assets/BG-marble.jpg") no-repeat center center fixed;
  background-size: cover;
  height: 100vh;
  width: 100vw;
  color: #f9df9e;
  overflow-x: hidden;
  overflow-y: hidden;

  display: flex;

  @include media(tablet) {
    display: block;
  }
}


.main-page {
  flex: auto;

  &__main {
    padding: 30px;
    padding-top: 60px;

    @include media(tablet) {
      padding: 0;
      z-index: 4;
      position: relative;
      bottom: 45px;
    }
  }

  &__settings {
    margin-left: auto;
    cursor: pointer;
  }

  &__top {
    height: 135px;
    width: 100%;
    background: #132e38;
    border-bottom: 3px solid #b79338;
    font-size: 20px;
    padding: 10px;
    padding-left: 40px;
    display: flex;

    @include media(tablet) {
      height: 200px;
      padding: 40px;
      padding-left: 45px;
    }

    @include media(mobile) {
      height: 150px;
      padding: 20px;
      padding-left: 30px;
      font-size: 15px;
    }
  }
}



.left-menu {
  background: url("../assets/BG-belt.jpg");
  border-right: 2px dashed #ffcc18;
  width: 130px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;

  @include media(tablet) {
    width: 100%;
    height: 110px;
    border-right: 0px;
    border-bottom: 2px dashed #ffcc18;
    z-index: 4;
  }

  @include media(mobile) {
    height: 90px;
  }

  &__cursor {
    position: absolute;
    height: 110px;
    width: 150px;
    background: red;
    top: -10px;
    background: url("../assets/Cursor.png");
    background-size: cover;

    @include media(tablet) {
      transform: rotate(90deg);
      left: -38px;
    }

    @include media(mobile) {
      top: -20px;
    }
  }

  &__accounts {
    flex: auto;

    @include media(tablet) {
      display: flex;
      justify-content: flex-start;
      align-items: center;
      padding-left: 45px;
    }

    @include media(mobile) {
      padding-left: 30px;
    }
  }

  &__accounts--item {

    @include media(tablet) {
      padding-right: 15px;
    }

    @include media(mobile) {
      padding-right: 5px;
    }
  }

  &__monogram--bottom {
    background: url("../assets/monogram.png") no-repeat;
    height: 110px;
    width: 110px;
    margin: 10px;

    @include media(tablet) {
      background: none;
      display: none;
    }
  }

  &__monogram--top {
    background: url("../assets/monogram.png") no-repeat;
    height: 110px;
    width: 110px;
    transform: scaleY(-1);
    margin: 10px;

    @include media(tablet) {
      background: none;
      display: none;
    }
  }
}

.add_account {
  height: 80px;
  width: 80px;
  margin: 20px;
  background: rgba(0, 0, 0, 0.5);
  color: gold;
  font-size: 50px;
  line-height: 70px;
  padding: 0 auto;
  text-align: center;
  cursor: pointer;

  @include media(tablet) {
    margin: 0;
  }
}
</style>
