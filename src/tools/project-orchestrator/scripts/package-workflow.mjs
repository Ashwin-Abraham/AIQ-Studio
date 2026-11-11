import { readFile, writeFile } from "node:fs/promises";
import { URL } from "node:url";

const distribution = new URL("../dist/", import.meta.url);
let html = await readFile(new URL("index.html", distribution), "utf8");
const script = html.match(
  /<script type="module"[^>]* src="([^"]+)"[^>]*><\/script>/,
);
const stylesheet = html.match(
  /<link rel="stylesheet"[^>]* href="([^"]+)"[^>]*>/,
);
if (!script || !stylesheet)
  throw new Error("The Vue build must contain one script and stylesheet.");
const javascript = await readFile(new URL(script[1], distribution), "utf8");
const css = await readFile(new URL(stylesheet[1], distribution), "utf8");
// Inline the compiled assets so an exported project also works with file://.
html = html.replace(
  script[0],
  () =>
    `<script type="module">${javascript.replaceAll("</script", "<\\/script")}</script>`,
);
html = html.replace(stylesheet[0], () => `<style>${css}</style>`);
const output = new URL(
  "../../../../plugins/aiq-site-tools/assets/project-workflow.generated.html",
  import.meta.url,
);
await writeFile(
  output,
  `<!-- Generated from src/tools/project-orchestrator. Run npm run build to update. -->\n${html}`,
);
