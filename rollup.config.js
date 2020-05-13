import resolve from "@rollup/plugin-node-resolve"
import commonjs from "@rollup/plugin-commonjs"
import babel from "@rollup/plugin-babel"
import replace from "@rollup/plugin-replace"
import json from "@rollup/plugin-json"
import outputManifest from "rollup-plugin-output-manifest"
import includePaths from "rollup-plugin-includepaths"
import postcss from "rollup-plugin-postcss"
import del from "rollup-plugin-delete"

import tailwindcss from "tailwindcss"
import autoprefixer from "autoprefixer"
import matched from "matched"

const SRC_ROOT = "./src/property_app/js"
const DIST_ROOT = "./dist"

const REACT_EXPORTS = [
  "Children",
  "createRef",
  "Component",
  "PureComponent",
  "createContext",
  "forwardRef",
  "lazy",
  "memo",
  "useCallback",
  "useContext",
  "useEffect",
  "useImperativeHandle",
  "useDebugValue",
  "useLayoutEffect",
  "useMemo",
  "useReducer",
  "useRef",
  "useState",
  "Fragment",
  "Profiler",
  "StrictMode",
  "Suspense",
  "createElement",
  "cloneElement",
  "isValidElement",
  "createFactory",
  "useTransition",
  "useDeferredValue",
  "SuspenseList",
  "unstable_withSuspenseConfig",
  "block",
  "unstable_createFundamental",
  "unstable_createScope",
  "jsx",
  "jsxs",
]

const REACT_SCHEDULER_EXPORTS = [
  "unstable_ImmediatePriority",
  "unstable_UserBlockingPriority",
  "unstable_NormalPriority",
  "unstable_IdlePriority",
  "LowPriority",
  "unstable_runWithPriority",
  "unstable_next",
  "unstable_scheduleCallback",
  "unstable_cancelCallback",
  "unstable_wrapCallback",
  "unstable_getCurrentPriorityLevel",
  "unstable_shouldYield",
  "unstable_requestPaint",
  "unstable_continueExecution",
  "unstable_pauseExecution",
  "unstable_getFirstCallbackNode",
  "unstable_now",
  "unstable_forceFrameRate",
]

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
    json(),
    includePaths({
      paths: [`${SRC_ROOT}`],
      extensions: [".js", ".css"],
    }),
    commonjs({
      dynamicRequireTargets: [],
      namedExports: {
        "node_modules/react/index.js": REACT_EXPORTS,
        "node_modules/scheduler/index.js": REACT_SCHEDULER_EXPORTS,
      },
      exclude: ["node_modules/lodash-es/**"],
    }),
    postcss({
      plugins: [tailwindcss, autoprefixer],
    }),
    replace({ "process.env.NODE_ENV": JSON.stringify(process.env.NODE_ENV) }),
    outputManifest(),
  ],
}

export default config
