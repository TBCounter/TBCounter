<template>
  <div class="modal-backdrop" @click="close">
    <div class="modal" @click.stop="">
      <header class="modal-header">
        <slot name="header"> Настройки аккаунта </slot>
      </header>

      <section class="modal-body">
        <form>
          <label for="login">логин </label>
          <input id="login" disabled v-model="login" class="modal-input" type="login" name="login" />
          <label for="password">пароль (введите новый)</label>
          <input id="password" v-model="password" autocomplete="on" class="modal-input" type="password" name="password" />

          <label for="name">имя</label>
          <input id="name" v-model="name" class="modal-input" type="text" name="name" />
          <label for="clan">клан</label>
          <input id="clan" v-model="clan" class="modal-input" type="text" name="clan" />

          <label for="triumph">триумф
            <input type="checkbox" v-model="isTriumph" name="triumph" id=""></label>
          <input class="modal-input modal-button" :disabled="loading || !login" type="button" name="check"
            :value="loading ? 'подождите...' : ' сохранить'" @click="saveAccountSettings" />
          <input class="modal-input modal-button modal-button--delete" :disabled="loading" type="button" name="check"
            value="УДАЛИТЬ" @click="deleteThisAccount" />
          <div style="color: red">{{ error_msg }}</div>
        </form>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { setNewAccountSettings, deleteAccount, getMyLogin } from "@/api";
import { useAccount, IAccount } from "@/stores/account";

import { ref, onMounted } from "vue";

const emit = defineEmits(["close"]);

const accStore = useAccount()

const acc = ref<IAccount>()
acc.value = accStore.currentAccount


function close() {
  emit("close");
}

onMounted(async () => {
  name.value = acc.value!.name
  clan.value = acc.value!.clan
  await getMyLogin(acc.value!.id).then(response => {
    login.value = response.data
  })
})

async function saveAccountSettings() {
  loading.value = true;
  await setNewAccountSettings({ login: login.value, password: password.value, isTriumph: isTriumph.value, name: name.value, clan: clan.value })
    .then(() => {
      close();
    })
    .catch((error: any) => {
      loading.value = false;
      error_msg.value = error.response.data.message;
    });
}

async function deleteThisAccount() {
  const result = confirm('точно удалить?');
  if (result) {
    loading.value = true;

    await deleteAccount({ id: acc.value!.id }).then(() => {
      close()
    })
  }
}



const error_msg = ref("");
const login = ref("");
const password = ref("");

const name = ref('')
const clan = ref('')

const isTriumph = ref(false);
const loading = ref(false);
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
