# bvsbharat.com

Personal blog of Bharat BVS, built with Astro 5.

## Tech Stack

- **Framework**: Astro 5 with TypeScript
- **Styling**: Tailwind CSS 4 with Typography plugin
- **Content**: MDX with content collections (Zod schema validation)
- **Search**: Pagefind (static search, indexed at build time)
- **Deployment**: Vercel (static output)
- **Interactive**: React (used for mobile menu and other interactive components)

## Commands

- `npm run dev` — Start dev server on localhost:4321
- `npm run build` — Build for production (includes Pagefind indexing)
- `npm run preview` — Preview production build locally

## Project Structure

- `src/content/blog/` — Blog posts in Markdown/MDX, organized by year
- `src/pages/` — Astro pages (file-based routing)
- `src/components/` — Reusable Astro components
- `src/layouts/` — Page layouts (Layout, BlogPostLayout, Main)
- `src/utils/` — Utility functions (sorting, filtering, slugify)
- `src/config.ts` — Site configuration (author, URL, settings)
- `src/consts.ts` — Navigation links and social links
- `src/content.config.ts` — Content collection schema

## Blog Post Frontmatter

```yaml
title: "Post Title"
description: "Short description"
pubDatetime: 2026-01-01T00:00:00Z
modDatetime: null # optional
tags: [tag1, tag2]
featured: false # optional
draft: false # optional
heroImage: "" # optional
ogImage: "" # optional
```

## Key Patterns

- Posts are filtered by `postFilter` (excludes drafts and future-scheduled posts)
- Tags are slugified for URL consistency
- Dark/light mode via CSS variables and `.dark` class on `<html>`
- Pagefind search only works after build (indexes the `dist/` folder)
- Path alias `@/` maps to `src/`
