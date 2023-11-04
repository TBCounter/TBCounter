<template>
    <div>
        <w-table :headers="[
            { label: 'Имя', key: 'name' },
            { label: 'Скриншот', key: 'path', width: '195' },
            { label: 'Уровень', key: 'level', width: '100' },
            { label: 'Удалить', key: 'delete', width: '70' },
        ]" :items="tableDataExpanded" :ref="itemRefs" :mobile-breakpoint="640" sort='+name'>
            <template #header-label="{ header, label }">
                <w-icon v-if="header.key === 'delete'" class="mr1" xl color="warning-dark2">
                    material-icons delete
                </w-icon>
                <span v-else>{{ label }}</span>
            </template>

            <template #item-cell.path="{ item, label, header, index }">
                <img :src="API_URL + '/' + label" />
            </template>
            <template #item-cell.name="{ item, label, header, index }">
                <w-icon class="mr1 clickable" @click="editCell(item)" v-if="!item.editing" xl color="primary-light1">
                    material-icons
                    edit
                </w-icon>

                <span v-if="!item.editing" @dblclick="editCell(item)">
                    {{ label }}
                </span>

                <w-icon class="mr1 clickable" v-if="item.editing" @click="saveCell(item)" xl color="primary-light1">
                    material-icons
                    save
                </w-icon>

                <input v-if="item.editing" v-model="item.name">



            </template>

            <template #item-cell.level="{ item, label, header, index }">
                <div class="player-list__cell">
                    <w-icon class="mr1 clickable" xl @click="changeLevel(item.id, 'add')" color="warning-dark2">
                        material-icons add
                    </w-icon>
                    <div>
                        {{ label }}
                    </div>
                    <w-icon class="mr1 clickable" xl @click="changeLevel(item.id, 'remove')" color="warning-dark2">
                        material-icons remove
                    </w-icon>
                </div>
            </template>

            <template #item-cell.delete="{ item, label, header, index }">
                <w-icon @click="showModal(item)" class="mr1 clickable" xl color="warning-dark2">
                    material-icons delete
                </w-icon>
            </template>

        </w-table>

        <SureDeleteModal :allPlayers="tableDataExpanded" :chosenPlayer="chosenPlayer" v-if="isModalVisible"
            @close="closeModal">
        </SureDeleteModal>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { getClanPlayers, changePlayerLevel, changePlayerName, API_URL } from "@/api"
import { useAccount, IAccount } from "@/stores/account";
import SureDeleteModal from "@/components/SureDeleteModal.vue";
const accStore = useAccount()
const acc = ref<IAccount>()
acc.value = accStore.currentAccount

const isModalVisible = ref(false);

const chosenPlayer = ref(0)

function closeModal() {
    isModalVisible.value = false
    chosenPlayer.value = 0
}

async function showModal(item: any) {
    chosenPlayer.value = item.id
    isModalVisible.value = true;
    const playersResponse = await getClanPlayers(acc.value!.id)
    tableData.value = playersResponse.data
}


const itemRefs = ref([])

const tableDataExpanded = computed(() => {
    return tableData.value.map((element: any) => { element['editing'] = false; return element })
})

const tableData = ref([])

async function saveCell(item: any) {
    item.editing = false
    await changePlayerName(acc.value!.id, item.id, item.name).then(
        (playersResponse) => tableData.value = playersResponse.data
    ).catch(
        () => { item.editing = true }
    )

}

function editCell(item: any) {
    item.editing = true
}

async function changeLevel(id: number, action: 'add' | 'remove') {
    const playersResponse = await changePlayerLevel(acc.value!.id, id, action)
    tableData.value = playersResponse.data
}

onMounted(async () => {
    const playersResponse = await getClanPlayers(acc.value!.id)
    tableData.value = playersResponse.data
})
</script> 

<style scoped lang="scss">
.player-list__cell {
    display: flex;
    justify-content: space-around;
}

.clickable {
    cursor: pointer;
}
</style>