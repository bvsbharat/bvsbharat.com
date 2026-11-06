import { defineCollection, z } from "astro:content";
import { glob } from "astro/loaders";

const blog = defineCollection({
  loader: glob({ pattern: "**/*.{md,mdx}", base: "./src/content/blog" }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDatetime: z.coerce.date(),
    modDatetime: z.coerce.date().optional().nullable(),
    tags: z.array(z.string()).default([]),
    featured: z.boolean().optional().default(false),
    draft: z.boolean().optional().default(false),
    heroImage: z.string().optional(),
    ogImage: z.string().optional(),
    canonicalURL: z.string().url().optional(),
    // Optional related-media chips. Rendered only for fields that are set.
    links: z
      .object({
        linkedin: z.string().url().optional(),
        x: z.string().url().optional(),
        devpost: z.string().url().optional(),
        lablab: z.string().url().optional(),
        video: z.string().url().optional(),
        github: z.string().url().optional(),
      })
      .optional(),
  }),
});

export const collections = { blog };
