import resolve from "@rollup/plugin-node-resolve";
import commonjs from "@rollup/plugin-commonjs";
import babel from "@rollup/plugin-babel";
import replace from "@rollup/plugin-replace";

const config = {
  input: "src/main.js",
  output: [
    {
      file: "../property_app/static/dist/index.js",
      format: "iife",
      sourcemap: true,
    },
  ],
  plugins: [
    babel({
      exclude: "node_modules/**",
      babelHelpers: "bundled",
      presets: ["@babel/preset-env", "@babel/preset-react"],
    }),
    commonjs(),
    replace({ "process.env.NODE_ENV": JSON.stringify(process.env.NODE_ENV) }),
    resolve(),
  ],
};

export default config;
