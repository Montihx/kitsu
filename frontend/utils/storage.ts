/**
 * Safe localStorage utilities with SSR support
 * Prevents crashes when accessing localStorage during server-side rendering
 */

import { safeLocalStorageGet, safeLocalStorageSet } from "@/shared/storage";

/**
 * Checks if localStorage is available (client-side only)
 */
export function isLocalStorageAvailable(): boolean {
  return typeof window !== "undefined" && typeof window.localStorage !== "undefined";
}

/**
 * Safely gets an item from localStorage
 * @param key - The localStorage key
 * @returns The value or null if not found or SSR
 */
export function getLocalStorageItem(key: string): string | null {
  return safeLocalStorageGet<string | null>(key, null, false);
}

/**
 * Safely sets an item in localStorage
 * @param key - The localStorage key
 * @param value - The value to store
 * @returns true if successful, false otherwise
 */
export function setLocalStorageItem(key: string, value: string): boolean {
  const ok = safeLocalStorageSet(key, value);
  if (!ok) {
    console.error(`Error writing localStorage key "${key}"`);
  }
  return ok;
}

/**
 * Safely removes an item from localStorage
 * @param key - The localStorage key
 * @returns true if successful, false otherwise
 */
export function removeLocalStorageItem(key: string): boolean {
  if (!isLocalStorageAvailable()) {
    return false;
  }
  try {
    localStorage.removeItem(key);
    return true;
  } catch (error) {
    console.error(`Error removing localStorage key "${key}":`, error);
    return false;
  }
}

/**
 * Safely parses JSON from localStorage
 * @param key - The localStorage key
 * @param defaultValue - The default value to return if parsing fails
 * @returns The parsed value or defaultValue
 */
export function getLocalStorageJSON<T>(key: string, defaultValue: T): T {
  const item = getLocalStorageItem(key);
  if (item === null) {
    return defaultValue;
  }
  try {
    return JSON.parse(item) as T;
  } catch (error) {
    console.error(`Error parsing JSON from localStorage key "${key}":`, error);
    // Remove corrupted data
    removeLocalStorageItem(key);
    return defaultValue;
  }
}

/**
 * Safely sets JSON in localStorage
 * @param key - The localStorage key
 * @param value - The value to store
 * @returns true if successful, false otherwise
 */
export function setLocalStorageJSON<T>(key: string, value: T): boolean {
  try {
    const jsonString = JSON.stringify(value);
    return setLocalStorageItem(key, jsonString);
  } catch (error) {
    console.error(`Error stringifying value for localStorage key "${key}":`, error);
    return false;
  }
}
