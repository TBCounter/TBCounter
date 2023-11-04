import { createRouter, createWebHistory } from "vue-router";
// @ts-ignore
import Login from "../views/Login.vue";
// @ts-ignore
import Register from "../views/Register.vue";
// @ts-ignore

import Report from "../views/Report.vue";
//@ts-ignore
import ChestList from "@/views/ChestList.vue";
//@ts-ignore
import InnerReport from "@/views/InnerReport.vue";
//@ts-ignore
import PlayersList from "@/views/PlayersList.vue";
//@ts-ignore
import ChestScore from "@/views/ChestScore.vue";

import { auth } from "../middleware/auth";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/login",
      name: "login",
      component: Login,
      meta: {
        layout: "login",
      },
    },
    {
      path: "/register",
      name: "register",
      component: Register,
      meta: {
        layout: "login",
      },
    },
    {
      path: "/clan-report/:hash",
      name: "clan-report",
      component: Report,
      meta: {
        layout: "public",
      },
    },
    {
      path: "/",
      name: "home",
      component: ChestList,
      meta: {
        middleware: auth,
        layout: "authorized",
      },
    },
    {
      path: "/list",
      name: "list",
      component: ChestList,
      meta: {
        middleware: auth,
        layout: "authorized",
      },
    },
    {
      path: "/report",
      name: "report",
      component: InnerReport,
      meta: {
        middleware: auth,
        layout: "authorized",
      },
    },
    {
      path: "/players",
      name: "players",
      component: PlayersList,
      meta: {
        middleware: auth,
        layout: "authorized",
      },
    },
    {
      path: "/scores",
      name: "scores",
      component: ChestScore,
      meta: {
        middleware: auth,
        layout: "authorized",
      },
    },
  ],
});

function nextFactory(context: any, middleware: any, index: any) {
  const subsequentMiddleware = middleware[index];
  // If no subsequent Middleware exists,
  // the default `next()` callback is returned.
  if (!subsequentMiddleware) return context.next;

  return (...parameters: any) => {
    // Run the default Vue Router `next()` callback first.
    context.next(...parameters);
    // Then run the subsequent Middleware with a new
    // `nextMiddleware()` callback.
    const nextMiddleware = nextFactory(context, middleware, index + 1);
    subsequentMiddleware({ ...context, next: nextMiddleware });
  };
}

router.beforeEach((to, from, next) => {
  if (to.meta.middleware) {
    const middleware = Array.isArray(to.meta.middleware)
      ? to.meta.middleware
      : [to.meta.middleware];

    const context = {
      from,
      next,
      router,
      to,
    };
    const nextMiddleware = nextFactory(context, middleware, 1);

    return middleware[0]({ ...context, next: nextMiddleware });
  }

  return next();
});

export default router;
