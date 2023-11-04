<template>
  <div class="account" :class="{ 'account--vip': account.vip }" @click="chooseAccount">
    <img class="account__avatar" :src="API_URL + '/' + account.avatar" alt="" />
    <div v-if="props.account.is_locked" class="account__status" />
  </div>
</template>

<script setup lang="ts">
import { useAccount, IAccount } from "@/stores/account";
import { API_URL } from "@/api"
import { useRouter } from 'vue-router'

const acc = useAccount();
const router = useRouter()
const props = defineProps<{
  account: IAccount;
}>();

function chooseAccount() {
  router.push('list')
  acc.chooseAccount(props.account.id);
}
</script>

<style lang="scss" scoped>
.account {
  margin: 20px;
  cursor: pointer;

  border-radius: 8px;
  overflow: hidden;

  &--vip {
    border: 2px solid gold;
  }

  @include media(tablet) {
    margin: 0;
    // height: 80px;
  }

  &__avatar {
    width: 100%;
  }
}

.account__status {
  position: absolute;
  bottom: -5px;
  right: -5px;
  background: lime;
  border-radius: 50%;
  height: 31px;
  width: 31px;
}
</style>
