import resolve from "@rollup/plugin-node-resolve";
import commonjs from "@rollup/plugin-commonjs";
import babel from "@rollup/plugin-babel";
import replace from "@rollup/plugin-replace";
import json from "@rollup/plugin-json";
import outputManifest from "rollup-plugin-output-manifest";
import includePaths from "rollup-plugin-includepaths";
import postcss from "rollup-plugin-postcss";
import del from "rollup-plugin-delete";

import tailwindcss from "tailwindcss";
import autoprefixer from "autoprefixer";
import matched from "matched";

const SRC_ROOT = "./src/property_app/js";
const DIST_ROOT = "./dist";

const config = {
  input: matched.sync([`${SRC_ROOT}/entry.js`, `${SRC_ROOT}/pages/*.js`]),
  output: {
    dir: `${DIST_ROOT}/assets/`,
    entryFileNames: "[name].[hash].js",
  },
  plugins: [
    del({
      targets: "dist/*",
      runOnce: true,
    }),
    babel({
      exclude: "node_modules/**",
      babelHelpers: "bundled",
      presets: ["@babel/preset-env", "@babel/preset-react"],
      plugins: ["@babel/plugin-syntax-dynamic-import"],
    }),
    resolve({ browser: true }),
    includePaths({
      paths: [`${SRC_ROOT}`],
      extensions: [".js", ".css"],
    }),
    commonjs({
      namedExports: {
        "node_modules/react/index.js": [
          "Children",
          "Component",
          "PureComponent",
          "PropTypes",
          "createElement",
          "Fragment",
          "cloneElement",
          "StrictMode",
          "createFactory",
          "createRef",
          "createContext",
          "isValidElement",
          "isValidElementType",
          "useRef",
          "useEffect",
          "useContext",
          "useState",
        ],
      },
    }),
    postcss({
      plugins: [tailwindcss, autoprefixer],
    }),
    json(),
    replace({ "process.env.NODE_ENV": JSON.stringify(process.env.NODE_ENV) }),
    outputManifest(),
  ],
};

export default config;
