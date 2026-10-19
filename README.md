# bvsbharat.com

Personal site and blog of **Bharat Bhavnasi**, Staff AI Engineer. Live at [bvsbharat.com](https://bvsbharat.com).

Built with [Astro 5](https://astro.build), MDX, Tailwind CSS 4, and Pagefind. Deployed on Vercel.

## Develop

```bash
npm install
npm run dev      # http://localhost:4321
npm run build    # clean, astro build, Pagefind index
```

## Where things live

- `src/content/blog/`: blog posts (Markdown/MDX)
- `src/pages/`: routes (`about.mdx`, `index.astro`, `posts/`, `robots.txt.ts`, `rss.xml.ts`)
- `src/config.ts`: site identity (name, job title, name variants, headshot, description). This is the single source for SEO metadata.
- `src/consts.ts`: navigation and social profile links (also used as schema.org `sameAs`)
- `src/components/JsonLD.astro`: structured data (WebSite, Person, ProfilePage, BlogPosting, BreadcrumbList)
- `public/og-default.png`: default 1200×630 social share image
- `scripts/`: build helpers (stale `.vercel/output` cleanup, Pagefind copy into the Vercel output)

## SEO

- Sitemap: `/sitemap-index.xml` (via `@astrojs/sitemap`), referenced from `/robots.txt`
- JSON-LD Person with `@id` `https://bvsbharat.com/#person` on every page, plus `ProfilePage` on `/about`
- Canonical, Open Graph, and Twitter card tags in `src/layouts/Layout.astro`
