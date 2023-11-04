<template>
    <div class="trigger__wrap">
        {{ locked? "запущено": "запустить" }}
        <div class="trigger" :class="{ 'trigger--disabled': disabled && !locked }">
            <div class="trigger__image" :class="{ 'trigger__image--active': locked }">
                <img :src="StatusGreen" />
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import StatusGreen from "@/assets/Statusgreen.png";
const props = defineProps<{
    locked: boolean;
    disabled?: boolean
}>();


</script>

<style lang="scss">
.trigger {
    margin-left: 10px;
    width: 62px;
    height: 31px;
    background: #304A54;
    box-shadow: inset 0px -4px 9px rgba(0, 0, 0, 0.25);
    border-radius: 15.5px;
    cursor: pointer;

    &--disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }

    &__wrap {
        display: flex;
        font-size: 24px;
        color: #F9DF9E;
        align-items: center;

        @media(max-width: 900px) {
            position: absolute;
            right: 0;
            bottom: 90px;
        }

        @include media(mobile) {
            font-size: 18px;
            flex-direction: column-reverse;
            right: 20px;
            bottom: 50px;
        }
    }

    &__image {
        position: relative;
        left: 0;
        height: 31px;
        width: 31px;
    }

    &__image--active {
        left: 31px;
    }
}
</style>