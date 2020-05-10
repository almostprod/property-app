import resolve from "@rollup/plugin-node-resolve";
import commonjs from "@rollup/plugin-commonjs";
import babel from "@rollup/plugin-babel";
import replace from "@rollup/plugin-replace";
import json from "@rollup/plugin-json";
import outputManifest from "rollup-plugin-output-manifest";

import postcss from "rollup-plugin-postcss";
import tailwindcss from "tailwindcss";
import autoprefixer from "autoprefixer";
import matched from "matched";

const config = {
  input: matched.sync(["src/entry.js", "src/pages/*.js"]),
  output: {
    dir: "../property_app/static/dist/",
    entryFileNames: "entry-[name].[hash].js",
  },
  plugins: [
    babel({
      exclude: "node_modules/**",
      babelHelpers: "bundled",
      presets: ["@babel/preset-env", "@babel/preset-react"],
      plugins: ["@babel/plugin-syntax-dynamic-import"],
    }),
    resolve({ browser: true }),
    commonjs(),
    postcss({
      plugins: [tailwindcss, autoprefixer],
    }),
    json(),
    replace({ "process.env.NODE_ENV": JSON.stringify(process.env.NODE_ENV) }),
    outputManifest(),
  ],
};

export default config;
