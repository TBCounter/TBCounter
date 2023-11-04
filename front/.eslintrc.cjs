/* eslint-env node */ require("@rushstack/eslint-patch/modern-module-resolution");
module.exports = {
  root: true,
  env: {
    browser: true,
    node: true,
  },
  extends: ["plugin:prettier/recommended"],
  plugins: [],
  // add your custom rules here
  rules: {
    "max-len": ["error", { code: 120, ignoreStrings: true }],
    "arrow-body-style": "off",
    "prefer-arrow-callback": "off",
    curly: "error",
    "no-unused-vars": 1,
    "vue/component-name-in-template-casing": [
      "error",
      "PascalCase",
      {
        registeredComponentsOnly: false,
        ignores: [
          "quill-editor",
          "client-only",
          "modals-container",
          "transition-group",
          "v-calendar",
        ],
      },
    ],
    "vue/no-static-inline-styles": [
      "error",
      {
        allowBinding: true,
      },
    ],
  },
};
