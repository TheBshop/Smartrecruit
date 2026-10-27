// Build: copia los datos pesados (datos/*.json) a dist/data/ con hash en el nombre (cache inmutable) y empaqueta el código.
import { build } from "esbuild";
import fs from "fs";
import crypto from "crypto";
import { execSync } from "child_process";

fs.rmSync("dist", { recursive: true, force: true });
fs.mkdirSync("dist/data", { recursive: true });
execSync("cp -r public/. dist/");
const manifest = {};
for (const f of fs.readdirSync("datos").filter((x) => x.endsWith(".json") && !x.startsWith("_"))) {
  const name = f.replace(/\.json$/, "");
  const buf = fs.readFileSync(`datos/${f}`);
  const hash = crypto.createHash("sha1").update(buf).digest("hex").slice(0, 10);
  const out = `${name}.${hash}.json`;
  fs.writeFileSync(`dist/data/${out}`, buf);
  manifest[name] = out;
}
await build({
  entryPoints: ["main.jsx"],
  bundle: true,
  minify: true,
  format: "iife",
  jsx: "automatic",
  outfile: "dist/assets/index.js",
  define: { "process.env.NODE_ENV": '"production"', DATA_MANIFEST: JSON.stringify(manifest) },
});
const V = Date.now().toString(36);
for (const f of ["dist/index.html", "dist/privacidad/index.html", "dist/terminos/index.html"]) {
  fs.writeFileSync(f, fs.readFileSync(f, "utf8").replace(/\?v=[0-9a-z]*/g, `?v=${V}`));
}
console.log("ok", Object.keys(manifest).length, "archivos de datos");
