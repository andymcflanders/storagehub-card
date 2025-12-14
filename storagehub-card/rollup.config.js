import resolve from "@rollup/plugin-node-resolve";
import typescript from "@rollup/plugin-typescript";
import terser from "@rollup/plugin-terser";

const production = !process.env.ROLLUP_WATCH;

export default {
  input: "src/storagehub-card.ts",
  output: {
    file: "dist/storagehub-card.js",
    format: "es",
    sourcemap: !production,
  },
  plugins: [
    resolve(),
    typescript({
      sourceMap: !production,
      inlineSources: !production,
    }),
    production && terser(),
  ],
};
