<template>
  <div class="modal-backdrop" @click="close">
    <div class="modal" @click.stop="">
      <header class="modal-header">
        <slot name="header"> Очередь </slot>
      </header>

      <section class="modal-body">
        <div v-for="acc in queue" class="modal-item">

          <div v-if="acc.active">-</div>
          <div>поставлен: {{ new Date(acc.timestamp).toLocaleString() }}</div>
          <div v-if="accountsList.includes(acc.id)">- ваш аккаунт</div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">

import { WS_URL } from "@/api";

import { ref, onMounted, onUnmounted, computed } from "vue";
import { useAccount, IAccount } from "@/stores/account";

const emit = defineEmits(["close"]);

const accountStore = useAccount()

function close() {
  emit("close");
}

const accountsList = computed(() => {
  return accountStore.accounts.map((acc) => acc.id)
})

const wsConnection = ref<WebSocket>()

interface IQueue {
  id: number,
  timestamp: string,
  active: boolean
}

const queue = ref<IQueue[]>([])

onMounted(async () => {

  wsConnection.value = new WebSocket(WS_URL + 'queue')
  wsConnection.value.onmessage = async function (event) {
    queue.value = JSON.parse(event.data)
  }

  wsConnection.value.onopen = function (event) {
  }

});

onUnmounted(() => {
  wsConnection.value?.close()
})

</script>

<style scoped lang="scss">
.modal-backdrop {
  position: fixed;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  background-color: rgba(0, 0, 0, 0.3);
  color: #361e09;
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 80;
}

.modal {
  background: #ffffff;
  overflow-x: auto;
  display: flex;
  flex-direction: column;
  height: 520px;
  width: 600px;
  background: url("../assets/Papirus.png");
  background-repeat: no-repeat;
  padding: 55px;

  @media (max-width: 640px) {
    background: url("../assets/Papirus-mobile.png");
    width: 320px;
    height: 400px;
  }

  &-item {
    display: flex;
  }
}

.modal-header,
.modal-footer {
  display: flex;
}

.modal-header {
  position: relative;
  border-bottom: 1px solid #eeeeee;
  justify-content: space-between;
}

.modal-body form {
  padding: 10px 10px;
  position: relative;
  display: flex;
  flex-direction: column;
}

.modal-input {
  background: transparent;
  border: 1px solid #cc9917;
  border-radius: 16px;
  height: 32px;
  padding-left: 10px;

  &:disabled {
    background-color: grey
  }
}

.modal-button {
  color: #ffbf1c;
  background: #132e38;
  cursor: pointer;
  margin-top: 20px;

  &--delete {
    background: red;
  }
}
</style>
