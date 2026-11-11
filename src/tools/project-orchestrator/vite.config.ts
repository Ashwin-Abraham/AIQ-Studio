import { fileURLToPath } from "node:url";
import { readdirSync } from "node:fs";
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

const exampleRoot = fileURLToPath(
  new URL("../../../examples/site-planning-project/", import.meta.url),
).replaceAll("\\", "/");

export default defineConfig(({ command }) => ({
  plugins: [vue()],
  base: "./",
  server: { host: "127.0.0.1", port: 5174, strictPort: true },
  define: {
    __EXAMPLE_BASE__: JSON.stringify(
      command === "serve" ? `/@fs/${exampleRoot}` : "./",
    ),
    __EXAMPLE_FOLDER__: JSON.stringify({
      name: "site-planning-project",
      subfolders: readdirSync(exampleRoot, { withFileTypes: true })
        .filter((entry) => entry.isDirectory())
        .map((entry) => entry.name)
        .sort(),
    }),
  },
  build: { modulePreload: false },
}));
