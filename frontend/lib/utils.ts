import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Converts total seconds into a MM:SS formatted string.
 * Handles invalid inputs by returning '00:00'.
 *
 * @param totalSeconds The number of seconds to format.
 * @returns A string in MM:SS format (e.g., "05:30", "30:00").
 */
export function formatSecondsToMMSS(
  totalSeconds: number | null | undefined,
): string {
  // 1. Validate Input
  if (
    typeof totalSeconds !== "number" ||
    totalSeconds < 0 ||
    isNaN(totalSeconds)
  ) {
    return "00:00"; // Return default for invalid input
  }

  // 2. Calculate Minutes and Seconds
  // Get whole minutes by dividing by 60 and flooring
  const minutes = Math.floor(totalSeconds / 60);

  // Get remaining seconds using the modulo operator
  // Use Math.round or Math.floor depending on desired precision if input could have decimals
  const seconds = Math.round(totalSeconds % 60);

  // 3. Format with Padding (Add leading zeros if needed)
  // Convert minutes/seconds to strings and pad with '0' if they are single digit
  const formattedMinutes = String(minutes).padStart(2, "0");
  const formattedSeconds = String(seconds).padStart(2, "0");

  // 4. Combine and Return
  return `${formattedMinutes}:${formattedSeconds}`;
}

const ALLOWED_IFRAME_HOSTS = [
  "youtube.com",
  "www.youtube.com",
  "m.youtube.com",
  "youtu.be",
  "vimeo.com",
  "player.vimeo.com",
  "youtube-nocookie.com",
  "www.youtube-nocookie.com",
];

export function isSafeIframeUrl(url: string | null | undefined): boolean {
  if (!url) return false;
  try {
    const parsedUrl = new URL(url);
    const protocol = parsedUrl.protocol.toLowerCase();
    if (protocol !== "https:") {
      return false;
    }

    const hostname = parsedUrl.hostname.toLowerCase();
    return ALLOWED_IFRAME_HOSTS.some(
      (allowedHost) =>
        hostname === allowedHost || hostname.endsWith(`.${allowedHost}`),
    );
  } catch {
    return false;
  }
}
