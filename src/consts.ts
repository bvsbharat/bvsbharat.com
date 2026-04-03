export const NAVIGATION = [
  { name: "Blog", href: "/posts" },
  { name: "About", href: "/about" },
] as const;

export const SOCIALS = [
  {
    name: "GitHub",
    href: "https://github.com/bvsbharat",
    icon: "github",
    active: true,
  },
  {
    name: "Twitter",
    href: "https://x.com/bvsbharat",
    icon: "twitter",
    active: true,
  },
  {
    name: "LinkedIn",
    href: "https://www.linkedin.com/in/bharatsatya/",
    icon: "linkedin",
    active: true,
  },
  {
    name: "YouTube",
    href: "https://www.youtube.com/@bharatbvs",
    icon: "youtube",
    active: true,
  },
  {
    name: "Email",
    href: "https://cal.id/bvsbharat",
    icon: "email",
    active: true,
  },
  {
    name: "RSS",
    href: "/rss.xml",
    icon: "rss",
    active: false,
  },
] as const;

export type SocialLink = (typeof SOCIALS)[number];
