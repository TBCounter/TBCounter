<template>
  <div class="login-page">
    <RouterView />
  </div>
</template>

<script setup lang="ts">
import { RouterView } from "vue-router";
</script>

<style scoped>
.login-page {
  background: url("../assets/BG-castle.jpg") no-repeat center center fixed;
  background-size: cover;
  height: 100vh;

}
</style>
