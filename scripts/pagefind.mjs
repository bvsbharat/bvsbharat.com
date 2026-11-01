// Build the Pagefind search index and make sure it ships with the deploy.
// `astro build` writes static HTML to dist/ and the Vercel adapter copies it
// to .vercel/output/static/ (what Vercel actually serves). Pagefind used to
// run only against dist/, so /pagefind/* 404'd in production.
import { execSync } from "node:child_process";
import { cpSync, existsSync } from "node:fs";

execSync("npx pagefind --site dist", { stdio: "inherit" });

const vercelStatic = ".vercel/output/static";
if (existsSync(vercelStatic)) {
  cpSync("dist/pagefind", `${vercelStatic}/pagefind`, { recursive: true });
  console.log(`Copied Pagefind index to ${vercelStatic}/pagefind`);
}
