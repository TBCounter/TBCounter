<template>
  <div>
    <p>Добавьте правила для подсчета очков</p>
    <p>По-умолчанию каждый сундук стоит 1 очко</p>
  </div>
  <div>
    <w-button class="mr1" @click="addNewRule">добавить правило</w-button>
    <w-button :disabled="rulesSaved" @click="saveRules">сохранить правила</w-button>
  </div>
  <div class="scores__rulesList">
    <div class="scores__rule" v-for="rule in rulesList">
      <div class="scores__rule-select">
        <w-select :items="group" label="Label" label-position="left" v-model="rule.group">
          Для
        </w-select>
      </div>
      <div class="scores__rule-select">
        <w-select :items="remoteChestType" label-position="left" v-model="rule.ideal_chest_type">
        </w-select>
      </div>
      <div class="scores__rule-select">
        <w-select :disabled="!rule.ideal_chest_type" v-if="
        //@ts-ignore 
        remoteChestNames[rule.ideal_chest_type]" :items="
  //@ts-ignore 
  remoteChestNames[rule.ideal_chest_type]" label-position="left" v-model="rule.ideal_chest_name">
        </w-select>
      </div>
      <div class="scores__rule-select">
        <w-input label="стоимость" v-model="rule.scores"></w-input>
      </div>
      <w-button @click="makeImportant(rule)">сделать важнее</w-button>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, watch, onMounted, nextTick } from "vue";
import { getScoresRulesList, saveScoresRulesList, getChestTypes, getChestNames } from "@/api";
import { group, chestType, chestName } from "@/components/utils/chests"
import { useAccount, IAccount } from "@/stores/account";
const accStore = useAccount()
const acc = ref<IAccount>()
acc.value = accStore.currentAccount
interface Rule {
  // id: Number
  group: Number
  scores: Number
  ideal_chest_type: String
  ideal_chest_name: String
}

const rulesSaved = ref(true)

const rulesList = ref([] as Rule[])

const remoteChestType = ref([] as Rule[])

const remoteChestNames = ref({} as any)


function addNewRule() {

  rulesList.value.unshift(
    {
      // id: 0,
      group: 99,
      scores: 1,
      ideal_chest_type: "Склеп 5 уровня",
      ideal_chest_name: 'all'
    }
  )
}
onMounted(async () => {
  await getScoresRulesList(acc.value!.id).then((response) => {
    rulesList.value = response.data as Rule[]
  }).then(() => {
    rulesSaved.value = true
  })

  await getChestTypes().then((response) => {
    remoteChestType.value = response.data as Rule[]
  })

  await getChestNames().then((response: any) => {
    remoteChestNames.value = response.data
  })
})
function makeImportant(rule: Rule) {
  const oldIndex = rulesList.value.indexOf(rule)
  rulesList.value.splice(oldIndex, 1)
  rulesList.value.unshift(rule)
}

async function saveRules() {
  await saveScoresRulesList(acc.value!.id, rulesList.value).then((response) => {
    rulesList.value = response.data as Rule[]

  }).then(() => {
    rulesSaved.value = true
  })
}

watch(rulesList,
  async (newRulesList, oldRulesList) => {
    rulesSaved.value = false
  },
  { deep: true }
)


</script>

<style lang="scss">
.scores {
  &__rule {
    margin-top: 10px;
    display: flex;
    align-items: flex-end;

    &-select {
      width: 230px;
      margin-right: 8px;
    }
  }
}
</style>
