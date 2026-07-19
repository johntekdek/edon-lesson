import js from "@eslint/js";
import globals from "globals";
import react from "eslint-plugin-react";

export default [
  {
    ignores: [
      "node_modules/**",
      "**/node_modules/**",
      "_bmad/**",
      "_bmad-output/**",
      ".agents/**",
      ".venv/**",
      "**/build/**",
      "**/dist/**",
      "coverage/**",
      "playwright-report/**",
      "test-results/**",
    ],
  },
  js.configs.recommended,
  {
    languageOptions: {
      ecmaVersion: 2024,
      sourceType: "module",
      globals: { ...globals.node },
    },
  },
  {
    // The i18n lint gate, JSX half (AD-20): no bare string literals in JSX text
    // positions. Armed now, before any JSX exists — every future component lands
    // against it. schema/js is exempt (toolchain code, no UI strings).
    files: ["player/src/**/*.{js,jsx}", "authoring/src/**/*.{js,jsx}"],
    plugins: { react },
    settings: { react: { version: "19.2" } },
    rules: { "react/jsx-no-literals": "error" },
  },
];
