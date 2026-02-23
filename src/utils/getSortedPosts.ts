import type { CollectionEntry } from "astro:content";
import { postFilter } from "./postFilter";

export function getSortedPosts(
  posts: CollectionEntry<"blog">[],
  { excludeHackathons = true }: { excludeHackathons?: boolean } = {}
): CollectionEntry<"blog">[] {
  return posts
    .filter(postFilter)
    .filter((post) =>
      excludeHackathons ? !post.data.tags.includes("hackathon") : true
    )
    .sort(
      (a, b) =>
        Math.floor(
          new Date(b.data.modDatetime ?? b.data.pubDatetime).getTime() / 1000
        ) -
        Math.floor(
          new Date(a.data.modDatetime ?? a.data.pubDatetime).getTime() / 1000
        )
    );
}
