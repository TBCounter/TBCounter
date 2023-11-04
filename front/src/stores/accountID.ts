import { defineStore } from "pinia";

export interface IAccountIDState {
  currentID: number;
}

export const useAccountID = defineStore({
  id: "accountID",
  state: (): IAccountIDState => ({
    currentID: 0,
  }),

  actions: {
    chooseAccount(id: number) {
      this.currentID = id;
    },
  },
});
