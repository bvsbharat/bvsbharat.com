import type { CollectionEntry } from "astro:content";
import { getSortedPosts } from "./getSortedPosts";
import { slugify } from "./slugify";

export function getPostsByTag(
  posts: CollectionEntry<"blog">[],
  tag: string
): CollectionEntry<"blog">[] {
  return getSortedPosts(
    posts.filter((post) => post.data.tags.map(slugify).includes(slugify(tag)))
  );
}
