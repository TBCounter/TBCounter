import { defineStore } from "pinia";
import { getReport, saveReport } from "@/api";
import { useAccount } from "./account";

export const useReport = defineStore({
  id: "report",
  state: () => ({
    query: {
      from: "",
      to: "",
      from_time: "00:00",
      to_time: "23:59",
    },
    schema: [],
    data: [] as any[], //all tables
  }),
  actions: {
    async getReportWithQuery() {
      const accStore = useAccount();
      const acc = accStore.currentAccount;
      this.schema = [];
      this.data = [] as any[]; //all tables
      await getReport({ account_id: acc!.id, ...this.query }).then((ans) => {
        if (ans.data.result) {
          this.data = ans.data.result.map((table: any) => ({
            data: JSON.parse(table.data).data,
            level: table.level,
          }));
          this.schema = ans.data.schema;
        }
      });
    },
    async saveReportQuery() {
      const accStore = useAccount();
      const acc = accStore.currentAccount;
      let link = "";
      await saveReport({ account_id: acc!.id, ...this.query }).then((ans) => {
        link = ans.data;
      });
      return link;
    },
  },
});
