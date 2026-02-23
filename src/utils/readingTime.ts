import readingTimeLib from "reading-time";

export function getReadingTime(content: string): string {
  const result = readingTimeLib(content);
  return result.text;
}
