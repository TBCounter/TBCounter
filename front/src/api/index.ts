import axios from "axios";
import { Buffer } from "buffer";
import { useJWT } from "@/stores/jwt";

export const API_URL = "https://tbapi.omegasoft.keenetic.name";
export const WS_URL = "wss://tbapi.omegasoft.keenetic.name/";
// export const API_URL = "http://localhost:8000";
// export const WS_URL = "ws://localhost:8000/ws/";
axios.defaults.baseURL = API_URL;
axios.interceptors.request.use((request) => {
  if (request.url == "/login/") {
    return request;
  }
  const jwt = useJWT();
  if (request.headers && jwt.jwt) {
    request.headers.Authorization = `Bearer ${jwt.jwt}`;
  }
  return request;
});

export function authenticate(userData: any) {
  return axios.post(`/login/`, userData);
}

export function loadChangeLog() {
  return axios.get(`/changelog/`);
}

export function register(userData: any) {
  return axios.post(`/register/`, userData);
}

export function getReport(payload: any) {
  return axios.post("/report/", {
    ...payload,
  });
}

export function saveReport(payload: any) {
  return axios.post("/save-report/", {
    ...payload,
  });
}

export function setNewAccount(payload: any) {
  return axios.post(`/info/`, payload);
}

export function setNewAccountSettings(payload: any) {
  return axios.patch(`/info/`, payload);
}

export function deleteAccount(payload: any) {
  return axios.delete(`/info/`, {
    data: {
      id: payload.id,
    },
  });
}
export function getMyLogin(id: any) {
  return axios.get(`/my-login/?id=` + id);
}

export function getAccounts() {
  return axios.get(`/info/`);
}

export function getList(id: number, page: number, sort: string) {
  return axios.get(`/list/`, {
    params: { account_id: id, page, sort },
  });
}

export function getListFile(payload: any) {
  return axios.post(
    `/list/`,
    {
      ...payload,
    },
    { responseType: "blob" }
  );
}

export function processChests(id: number) {
  return axios.post("/process/", { account_id: id });
}

export function killProcessChests(id: number) {
  return axios.post("/kill_process/", { account_id: id });
}

export function getClanReport(hash: string) {
  return axios.get(`/clan-report/?hash=${hash}`);
}

export function getClanPlayers(account_id: number) {
  return axios.get(`/clan-players/?account_id=${account_id}`);
}

export function deleteClanPlayers(
  account_id: number,
  player_id: number,
  with_chests: boolean
) {
  return axios.post(`/clan-players-delete/`, {
    account_id,
    player_id,
    with_chests,
  });
}

export function mergeClanPlayers(
  account_id: number,
  player_id: number,
  player_merge_id: number
) {
  return axios.post(`/clan-players-merge/`, {
    account_id,
    player_id,
    player_merge_id,
  });
}

export function changePlayerLevel(
  account_id: number,
  player_id: number,
  action: "add" | "remove"
) {
  return axios.post(`/clan-players-level/`, { account_id, player_id, action });
}

export function changePlayerName(
  account_id: number,
  player_id: number,
  name: string
) {
  return axios.post(`/clan-players-edit/`, { account_id, player_id, name });
}

export function getClanPlayersChestsCount(player_id: number) {
  return axios.get(`/clan-player-bounded-chests/?player_id=${player_id}`);
}

export function getScoresRulesList(account_id: number) {
  return axios.get(`/scores-rules/?account_id=${account_id}`);
}

export function saveScoresRulesList(account_id: number, rules: any) {
  return axios.post(`/scores-rules/`, { account_id, rules });
}

export function saveChestRequest(chest_id: number) {
  return axios.post(`/save-chest/`, { chest_id });
}

export function deleteChestRequest(chest_id: number) {
  return axios.post(`/delete-chest/`, { chest_id });
}

export function getChestTypes() {
  return axios.get("/chest-types/");
}

export function getChestNames() {
  return axios.get(`/chest-names/`);
}

export function getAccountStateImage(account_id: number) {
  return axios
    .get("/current_state/?account_id=" + account_id, {
      responseType: "arraybuffer",
    })
    .then((response) =>
      Buffer.from(response.data, "binary").toString("base64")
    );
}
