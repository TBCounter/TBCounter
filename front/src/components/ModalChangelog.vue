<template>
  <div class="modal-backdrop" @click="close">
    <div class="modal" @click.stop="">
      <header class="modal-header">
        <slot name="header"> Список изменений </slot>
      </header>

      <section class="modal-body">
        <Changelog class="modal-body" :changelog="changelog"></Changelog>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">

import { loadChangeLog } from "@/api";

import { ref, onMounted } from "vue";
import Changelog from '@/components/Changelog.vue'

const emit = defineEmits(["close"]);
interface Log {
  Date: string,
  Text: string[]
}


onMounted(async () => {
  await loadChangeLog().then(
    (resp: any) => {
      changelog.value = resp.data
    }
  )
});

const changelog = ref<Log[]>([])

function close() {
  emit("close");
}



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

  &-body {
    height: 200px;
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
