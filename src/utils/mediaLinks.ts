export const MEDIA_LINK_FIELDS = [
  { key: "linkedin", label: "LinkedIn" },
  { key: "x", label: "X" },
  { key: "devpost", label: "Devpost" },
  { key: "lablab", label: "lablab.ai" },
  { key: "video", label: "Demo" },
  { key: "github", label: "GitHub" },
] as const;

export type MediaLinkKey = (typeof MEDIA_LINK_FIELDS)[number]["key"];

export type MediaLinks = Partial<Record<MediaLinkKey, string>>;

export type MediaLinkItem = {
  key: MediaLinkKey;
  label: string;
  href: string;
};

export function listMediaLinks(links?: MediaLinks | null): MediaLinkItem[] {
  if (!links) return [];
  return MEDIA_LINK_FIELDS.flatMap((field) => {
    const href = links[field.key]?.trim();
    return href ? [{ key: field.key, label: field.label, href }] : [];
  });
}
