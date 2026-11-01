// Remove stale build output before `astro build`.
// @astrojs/vercel can fail with ENOTEMPTY when a previous
// .vercel/output/static directory is left behind.
import { rmSync } from "node:fs";

for (const dir of [".vercel/output", "dist"]) {
  rmSync(dir, { recursive: true, force: true });
}
