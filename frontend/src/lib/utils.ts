import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatPrice(price: number, locale: string = "en"): string {
  if (locale === "fa") {
    return new Intl.NumberFormat("fa-IR").format(price);
  }
  return new Intl.NumberFormat("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(price);
}

export function formatNumber(num: number, locale: string = "en"): string {
  if (locale === "fa") {
    return new Intl.NumberFormat("fa-IR").format(num);
  }
  return new Intl.NumberFormat("en-US").format(num);
}

export function formatPercent(value: number): string {
  const sign = value >= 0 ? "+" : "";
  return `${sign}${value.toFixed(2)}%`;
}

export function formatCompactNumber(num: number): string {
  if (num >= 1_000_000_000) return `${(num / 1_000_000_000).toFixed(1)}B`;
  if (num >= 1_000_000) return `${(num / 1_000_000).toFixed(1)}M`;
  if (num >= 1_000) return `${(num / 1_000).toFixed(1)}K`;
  return num.toString();
}

export function getChangeColor(change: number): string {
  if (change > 0) return "text-stock-up";
  if (change < 0) return "text-stock-down";
  return "text-muted-foreground";
}

export function getChangeBgColor(change: number): string {
  if (change > 0) return "bg-stock-up-bg text-stock-up";
  if (change < 0) return "bg-stock-down-bg text-stock-down";
  return "bg-muted text-muted-foreground";
}

export function generateRandomPrice(base: number, volatility: number = 0.02): number {
  const change = (Math.random() - 0.5) * 2 * volatility;
  return +(base * (1 + change)).toFixed(2);
}

export function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/** Build full URL for avatar/media from API response */
export function getAvatarUrl(avatar: string | null | undefined): string | undefined {
  if (!avatar) return undefined;
  if (avatar.startsWith("http") || avatar.startsWith("/")) return avatar;
  return `/${avatar.startsWith("media/") ? avatar : `media/${avatar}`}`;
}
