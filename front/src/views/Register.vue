<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useJWT } from "@/stores/jwt";
import router from "../router";
// async function register_request() {
// await jwt.login({ email: email.value, password: password.value }).then(() => {
//   router.push("/");
// });
// }

async function register_request() {
  await jwt.register({ email: email.value, password: password.value }).then(() => {
    router.push("/");
  });
}

const email = ref("");
const password = ref("");
const allOK = ref("");

const jwt = useJWT();
onMounted(() => {
  jwt.logout();
});
</script>

<template>
  <div class="register_bg">
    <div class="greetings">
      <form>
        <div class="register__wrap">
          <label class="register__label" for="email">Register</label>
          <input class="register__input" v-model="email" type="email" name="email" />
        </div>
        <div class="register__wrap">
          <label class="register__label" for="password">Password</label>
          <input class="register__input" autocomplete="current-password" v-model="password" type="password"
            name="password" />
        </div>
        <div class="register__button" @click="register_request">Sign On</div>
      </form>
    </div>
  </div>
</template>

<style lang="scss">
.register {
  &_bg {
    display: flex;
    height: 100vh;
    width: 100vw;
    max-width: 1280px;
    margin: 0 auto;
    padding: 2rem;

    font-weight: normal;
    background: url("../assets/BG-castle.jpg") no-repeat center center fixed;
    background-size: cover;

    @include media(tablet) {
      padding: 3rem;
    }

    @include media(mobile) {
      padding: 2rem 1rem;
    }

    .greetings {
      margin: auto;
      height: 85vh;
      width: 538px;
      background: rgba(0, 0, 0, 0.63);
      border-radius: 20px;
      box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
      color: white;
      display: flex;
      justify-content: center;
      flex-direction: column;
      align-items: center;

      @include media(tablet) {
        height: 100%;
        width: 100%;
      }
    }
  }


  &__label {
    font-size: 24px;

    @include media(tablet) {
      font-size: 20px;
    }

    @include media(mobile) {
      font-size: 18px;
    }

  }

  &__input {
    background-color: #232323;
    width: 380px;
    height: 85px;

    padding: 11px;
    border-color: #ffcc18;
    border-radius: 19px;
    box-sizing: border-box;
    font-size: 24px;
    font-family: "FontinSansCR-Bold", sans-serif;
    color: #fff7bf;

    @include media(tablet) {
      width: 350px;
      height: 70px;
      font-size: 20px;
    }

    @include media(mobile) {
      width: 270px;
      height: 55px;
      font-size: 18px;
    }
  }

  &__button {
    background: radial-gradient(73.71% 73.71% at 49.87% 50.52%,
        rgba(0, 0, 0, 0.2) 41.67%,
        rgba(0, 0, 0, 0) 100%),
      #a02801;
    box-shadow: inset 9px 9px 4px rgba(0, 0, 0, 0.25),
      inset -9px -9px 6px rgba(0, 0, 0, 0.25);
    border-radius: 15px;
    width: 381px;
    height: 97px;
    font-family: "Goblin One";
    font-style: normal;
    font-weight: 400;
    font-size: 48px;
    line-height: 60px;

    color: #ffffff;
    text-align: center;
    padding: 15px;
    margin-top: 50px;
    cursor: pointer;

    @include media(tablet) {
      width: 351px;
      height: 82px;
      font-size: 44px;
      line-height: 45px;
      margin-top: 35px;
    }

    @include media(mobile) {
      width: 271px;
      height: 67px;
      font-size: 40px;
      line-height: 30px;
      margin-top: 30px;
    }
  }

  &__wrap {
    margin-top: 20px;
    display: flex;
    flex-direction: column;
  }

  @include media(tablet) {
    margin-top: 10px;
  }

  @include media(mobile) {
    margin-top: 5px;
  }
}
</style>
