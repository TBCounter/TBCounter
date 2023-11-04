import { defineStore } from "pinia";
import { getAccounts } from "@/api";
import { useAccountID } from "./accountID";
export interface IAccount {
  name: string;
  clan: string;
  id: number;
  is_locked: boolean;
  avatar: string;
  chest_count: number;
  unavailable?: boolean;
  vip: boolean;
}

export interface IAccountState {
  currentID: number;
  accounts: IAccount[];
}

export const useAccount = defineStore({
  id: "account",
  state: (): IAccountState => ({
    currentID: 0,
    accounts: [
      {
        name: "",
        clan: "",
        id: 0,
        is_locked: false,
        avatar: "",
        chest_count: 0,
        unavailable: false,
        vip: false,
      },
    ],
  }),
  getters: {
    currentAccount: (state) => {
      return state.accounts.find((account) => account.id === state.currentID);
    },
  },
  actions: {
    chooseAccount(id: number) {
      this.currentID = id;
      const accID = useAccountID();
      accID.chooseAccount(id);
    },
    updateAccount(newAccountsData: IAccount[]) {
      this.accounts = newAccountsData;
    },
  },
});
