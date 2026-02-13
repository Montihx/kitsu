/**
 * S0 Smoke Test — verify that the test runner starts and exits cleanly.
 *
 * This test does NOT import any application code, components, or libraries.
 * It exists solely to confirm Vitest is configured correctly.
 */
import { describe, it, expect } from "vitest";

describe("S0 smoke", () => {
  it("test runner starts", () => {
    expect(true).toBe(true);
  });
});
