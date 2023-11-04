<script setup lang="ts">
export interface Log {
  Date: string,
  Text: string[]
}

import { ref, onMounted } from "vue";
import { useJWT } from "@/stores/jwt";
import router from "../router";
import { loadChangeLog } from "@/api";
import Changelog from '@/components/Changelog.vue'

async function login_request() {
  allOK.value = ''


  if (email.value.length < 2) {
    allOK.value = 'Логин слишком короткий'
    return
  }
  if (password.value.length < 2) {
    allOK.value = 'Пароль слишком короткий'
    return
  }


  await jwt.login({ email: email.value, password: password.value }).then((response: any) => {
    if (response.status === 200) {
      router.push("/");
    }
  }).catch(error => {
    if (error.response.status == 401) {
      allOK.value = 'неверный логин или пароль'
    }
    if (error.response.status == 500) {
      allOK.value = 'Ошибка сервера'
    }
  })
}

// async function register_request() {
//   await jwt.register({ email: email.value, password: password.value });
// }


const changelog = ref([] as Log[])

const email = ref("");
const password = ref("");
const allOK = ref("");

const jwt = useJWT();
onMounted(async () => {
  jwt.logout();
  await loadChangeLog().then(
    (resp: any) => {
      changelog.value = resp.data
    }
  ).catch(reason => {
    allOK.value = 'Сервер не отвечает!'
  })
});
</script>

<template>
  <div class="login_bg">
    <div class="greetings">
      <form class="login__form">
        <div class="login__wrap">
          <label class="login__label" for="email">Login</label>
          <input class="login__input" v-model="email" type="email" name="email" />
        </div>
        <div class="login__wrap">
          <label class="login__label" for="password">Password</label>
          <input class="login__input" autocomplete="current-password" v-model="password" type="password"
            name="password" />
        </div>
        <div class="login__button" @click="login_request">войти</div>
        <router-link class="login__link" to="/register">Зарегистрироваться</router-link>
        <div class="login__message">{{ allOK }}</div>
      </form>
      <Changelog :changelog="changelog"></Changelog>
    </div>
  </div>
</template>

<style lang="scss">
.login {
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

      width: 538px;
      background: rgba(0, 0, 0, 0.63);
      border-radius: 20px;
      box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
      color: white;
      display: flex;
      flex-direction: column;
      align-items: center;

      @include media(tablet) {
        width: 100%;
      }
    }
  }

  &__link {
    color: #66a4d2;
  }

  &__form {
    margin: 20px;
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
    height: 65px;

    padding: 11px;
    border-color: #ffcc18;
    border-radius: 19px;
    box-sizing: border-box;
    font-size: 24px;
    font-family: "FontinSansCR-Bold", sans-serif;
    color: #fff7bf;

    @include media(tablet) {
      width: 350px;
      height: 50px;
      font-size: 20px;
    }

    @include media(mobile) {
      width: 270px;
      height: 35px;
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
    height: 67px;
    font-family: "FontinSansCR-Bold", sans-serif;
    font-style: normal;
    font-weight: 400;
    font-size: 40px;
    color: #ffffff;
    text-align: center;
    margin-top: 50px;
    cursor: pointer;

    &:hover {
      background: radial-gradient(73.71% 73.71% at 49.87% 50.52%,
          rgba(0, 0, 0, 0.2) 41.67%,
          rgba(0, 0, 0, 0) 100%),
        #a93610;
    }

    &:active {
      background: radial-gradient(73.71% 73.71% at 49.87% 50.52%,
          rgba(0, 0, 0, 0.2) 41.67%,
          rgba(0, 0, 0, 0) 100%),
        #be6446;
      box-shadow: rgba(0, 0, 0, .06) 0 2px 4px;
      transform: translateY(0);
    }

    @include media(tablet) {
      width: 351px;
      height: 72px;
      font-size: 44px;
      margin-top: 35px;
    }

    @include media(mobile) {
      width: 271px;
      height: 47px;
      font-size: 29px;
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
