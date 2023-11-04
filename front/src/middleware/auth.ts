import { isValidJwt } from "../../utils";

export function auth({ next, router }: any) {
  if (
    !localStorage.getItem("jwt") ||
    !isValidJwt(localStorage.getItem("jwt"))
  ) {
    return next({ name: "login" });
  }
  return next();
}

export function logout({ next }: any) {
  localStorage.clear();
  return next();
}
