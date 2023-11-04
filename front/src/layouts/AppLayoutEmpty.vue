<template>
  <div class="empty-page">
    <RouterView />
  </div>
</template>

<script setup lang="ts">
import { RouterView } from "vue-router";
</script>

<style scoped>
.empty-page {
  background: url("../assets/BG-castle.jpg") no-repeat center center fixed;
  background-size: cover;
  height: 100vh;
  display: flex;
  padding: 10px 20px;
}
</style>
