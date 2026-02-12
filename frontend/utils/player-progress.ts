"use client";

/**
 * Converts fractional values (0-1) to percentages while leaving
 * already-percentage values unchanged.
 */
export const convertFractionToPercent = (value: number | undefined | null) => {
  if (value === undefined || value === null || !Number.isFinite(value)) {
    return undefined;
  }
  if (value <= 1) {
    return value * 100;
  }
  return value;
};

export const CONTINUE_PROGRESS_MIN = 5;
export const CONTINUE_PROGRESS_MAX = 89;
export const COMPLETED_PROGRESS_MIN = 90;

export const parseNumber = (value: unknown): number | undefined => {
  if (value === undefined || value === null) return undefined;
  if (typeof value === "number" && Number.isFinite(value)) return value;
  if (typeof value === "string" && value.trim() !== "") {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : undefined;
  }
  return undefined;
};
