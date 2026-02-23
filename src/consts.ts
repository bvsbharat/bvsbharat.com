export const NAVIGATION = [
  { name: "Blog", href: "/posts" },
  { name: "Open Source", href: "/opensource" },
  { name: "Hackathons", href: "/hackathons" },
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
    href: "https://linkedin.com/in/bvsbharat",
    icon: "linkedin",
    active: true,
  },
  {
    name: "Email",
    href: "mailto:bharatbvs@gmail.com",
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
