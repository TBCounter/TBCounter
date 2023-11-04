<template>
  <div class="modal-backdrop" @click="close">
    <div class="modal" @click.stop="">
      <header class="modal-header">
        <slot name="header"> Действителньо удалить игрока? </slot>
      </header>

      <section class="modal-body">
        <template v-if="!loading">
          <p> У игрока {{ player_name }} {{ chests_count }} сундуков. </p>
          <p> удалить игрока и сундуки?</p>
        </template>
        <div class="modal__buttons">

          <div class="mt5" style="display: flex;">
            <input class="modal-input modal-button"
              :disabled="loading || sureDelete.toUpperCase() != player_name.toUpperCase()" type="button" name="check"
              :value="loading ? 'подождите...' : 'удалить игрока'" @click="deletePlayer(false)" />
            <w-input v-model="sureDelete" class="ml2" round placeholder="введите имя игрока, чтобы удалить"></w-input>
          </div>
          <div class="mt5" style="display: flex;">
            <input class="modal-input modal-button" :disabled="loading || playerToMerge == 0" type="button" name="check"
              :value="loading ? 'подождите...' : 'объединить с игроком'" @click="mergePlayers()" />
            <w-select item-value-key="id" v-model="playerToMerge" :disabled="loading" round class="ml2"
              item-label-key="name" :items="allPlayersSorted"></w-select>
          </div>
          <input class="modal-input modal-button mt5" :disabled="loading" type="button" name="check"
            :value="loading ? 'подождите...' : 'отмена'" @click="close" />
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { deleteClanPlayers, getClanPlayersChestsCount, mergeClanPlayers } from '@/api'
import { ref, onMounted, computed } from "vue";
import { useAccount, IAccount } from "@/stores/account";

const accStore = useAccount()
const acc = ref<IAccount>()
acc.value = accStore.currentAccount

const loading = ref(false);

const props = defineProps({
  chosenPlayer: {
    type: Number,
    default: 0
  },
  allPlayers: {
    type: Object
  }
})

const playerToMerge = ref(0)
const sureDelete = ref('')
const emit = defineEmits(["close"]);

const player_name = ref('')
const chests_count = ref('')
function close() {
  emit("close");
}

const allPlayersSorted = computed(() => {
  return props?.allPlayers?.sort((a: any, b: any) => {
    const nameA = a.name.toUpperCase();
    const nameB = b.name.toUpperCase();
    if (nameA < nameB) {
      return -1;
    }
    if (nameA > nameB) {
      return 1;
    }
    return 0;
  }).filter((elem: any) => elem.id != props.chosenPlayer);
})


onMounted(async () => {
  loading.value = true
  console.log(props.allPlayers)
  if (props.chosenPlayer) {
    await getClanPlayersChestsCount(props.chosenPlayer).then(
      resp => {
        player_name.value = resp.data.name
        chests_count.value = resp.data.chests_count
        loading.value = false
      }
    )
  }

})

async function deletePlayer(withChests: boolean) {
  await deleteClanPlayers(acc.value!.id, props.chosenPlayer, withChests)
  close()
}

async function mergePlayers() {
  await mergeClanPlayers(acc.value!.id, props.chosenPlayer, playerToMerge.value)
  // console.log(props.chosenPlayer, playerToMerge.value)
  close()
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
}

.modal {
  background: #ffffff;
  overflow-x: auto;
  display: flex;
  flex-direction: column;
  height: 440px;
  width: 600px;
  background: url("../assets/Papirus.png");
  padding: 55px;

  @media (max-width: 640px) {
    background: url("../assets/Papirus-mobile.png");
    width: 320px;
    height: 400px;
  }

  &__buttons {
    display: flex;
    flex-direction: column;
  }
}

.modal-header,
.modal-footer {
  padding: 15px;
  display: flex;
}

.modal-header {
  position: relative;
  border-bottom: 1px solid #eeeeee;
  justify-content: space-between;
}

.modal-body form {
  padding: 20px 10px;
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
  padding-right: 10px;

  &:disabled {
    background-color: grey !important;
  }
}

.modal-button {
  color: #ffbf1c !important;
  background: #132e38;
  cursor: pointer;
}
</style>
