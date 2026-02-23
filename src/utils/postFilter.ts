import { SITE } from "@/config";
import type { CollectionEntry } from "astro:content";

export function postFilter({ data }: CollectionEntry<"blog">): boolean {
  const isPublishTimePassed =
    Date.now() >
    new Date(data.pubDatetime).getTime() - SITE.scheduledPostMargin;
  return !data.draft && isPublishTimePassed;
}
