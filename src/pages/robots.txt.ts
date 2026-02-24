import type { APIRoute } from "astro";

const siteUrl = import.meta.env.SITE;
const robotsTxt = `
User-agent: *
Allow: /
Disallow: /pagefind/

Sitemap: ${new URL("sitemap-index.xml", siteUrl).href}
Host: ${siteUrl}
`.trim();

export const GET: APIRoute = () => {
  return new Response(robotsTxt, {
    headers: {
      "Content-Type": "text/plain; charset=utf-8",
    },
  });
};
