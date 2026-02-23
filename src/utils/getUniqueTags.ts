import type { CollectionEntry } from "astro:content";
import { postFilter } from "./postFilter";
import { slugify } from "./slugify";

export interface TagCount {
  tag: string;
  tagSlug: string;
  count: number;
}

export function getUniqueTags(
  posts: CollectionEntry<"blog">[],
  { excludeHackathons = true }: { excludeHackathons?: boolean } = {}
): TagCount[] {
  const tagMap = new Map<string, { tag: string; count: number }>();

  posts
    .filter(postFilter)
    .filter((post) =>
      excludeHackathons ? !post.data.tags.includes("hackathon") : true
    )
    .forEach((post) => {
    post.data.tags.forEach((tag) => {
      const slug = slugify(tag);
      const existing = tagMap.get(slug);
      if (existing) {
        existing.count++;
      } else {
        tagMap.set(slug, { tag, count: 1 });
      }
    });
  });

  return Array.from(tagMap.entries())
    .map(([tagSlug, { tag, count }]) => ({ tag, tagSlug, count }))
    .sort((a, b) => a.tag.localeCompare(b.tag));
}
