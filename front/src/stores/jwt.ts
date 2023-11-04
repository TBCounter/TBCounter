import { defineStore } from "pinia";
import { isValidJwt } from "../../utils";
import { authenticate, register } from "../api";

import { useStorage } from "@vueuse/core";

export const useJWT = defineStore({
  id: "jwt",
  state: () => ({
    jwt: useStorage("jwt", ""),
    userData: {},
    userName: useStorage("userName", ""),
    userID: useStorage("userID", ""),
  }),
  getters: {
    user: (state) => state.userName,
    token: (state) => state.jwt,
    isAuthenticated: (state) => {
      return isValidJwt(state.jwt);
    },
    getUserID: (state) => state.userID,
  },
  actions: {
    setJWT(newToken: any) {
      this.jwt = newToken.token;
      this.userName = newToken.userName;
      this.userID = newToken.userID;
    },
    async login(userData: any) {
      this.userData = userData;
      return authenticate(userData).then((resp) => {
        this.setJWT(resp.data);
        return resp;
      });
    },
    logout() {
      this.userData = "";
      this.setJWT("");
    },

    async register(userData: any) {
      this.userData = userData;
      return register(userData)
        .then(() => {
          this.login(userData);
        })
        .catch((error: Error) => {
          console.log("Error Registering: ", error);
        });
    },
  },
});
