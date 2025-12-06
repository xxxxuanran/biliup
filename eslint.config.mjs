import { FlatCompat } from "@eslint/eslintrc";
import js from "@eslint/js";
import path from "path";
import { fileURLToPath } from "url";
import globals from "globals";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const compat = new FlatCompat({
    baseDirectory: __dirname,
    recommendedConfig: js.configs.recommended,
    allConfig: js.configs.all
});

const eslintConfig = [
    ...compat.extends("google", "next/core-web-vitals", "prettier"),
    {
        languageOptions: {
            globals: {
                ...globals.browser,
                ...globals.node,
            },
            ecmaVersion: "latest",
            sourceType: "module",
        },
        rules: {
            // Add any custom rule overrides here
            "require-jsdoc": "off", // Often too strict for modern React apps, can be enabled if desired
            "valid-jsdoc": "off",
        },
    },
];

export default eslintConfig;
