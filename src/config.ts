export const SITE = {
  website: "https://bvsbharat.com",
  author: "Bharat Bhavnasi",
  profile: "https://bvsbharat.com/about",
  jobTitle: "Staff AI Engineer",
  // Name variants people search for; used as schema.org alternateName.
  alternateNames: [
    "Bharat Bhavanasi",
    "Bharath Bhavanasi",
    "Bharat Kumar Bhavnasi",
    "Bharat BVS",
    "bvsbharat",
  ],
  // Optimized square headshot used for Person schema / Knowledge Panel photo.
  image: "/images/bharat-bhavnasi.jpg",
  location: "San Francisco Bay Area, CA",
  twitterHandle: "@bvsbharat",
  desc: "Staff AI Engineer building Voice AI Agents, Multi-Agent Systems, and Developer Tools. With 30+ hackathon wins, I love turning bold ideas into real products at the intersection of AI and engineering.",
  title: "Bharat Bhavnasi",
  ogImage: "/og-default.png",
  lightAndDarkMode: true,
  postPerIndex: 4,
  postPerPage: 10,
  featuredPerIndex: 3,
  scheduledPostMargin: 15 * 60 * 1000, // 15 minutes
  showArchives: true,
  showBackButton: true,
  editPost: {
    enabled: true,
    url: "https://github.com/bvsbharat/bvsbharat.com/edit/main/",
    text: "Suggest changes",
    appendFilePath: true,
  },
} as const;
