import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { validate } from "../src/index.js";

const FIXTURES_DIR = new URL("../../fixtures/", import.meta.url);
const expectations = JSON.parse(
  readFileSync(new URL("expectations.json", FIXTURES_DIR), "utf8"),
);

function loadFixture(relativePath) {
  return JSON.parse(readFileSync(new URL(relativePath, FIXTURES_DIR), "utf8"));
}

function classify(result) {
  if (result.unsupportedMajor) return "unsupportedMajor";
  return result.ok ? "valid" : "invalid";
}

describe("fixture corpus agreement", () => {
  for (const [fixture, expected] of Object.entries(expectations)) {
    it(`${fixture} → ${expected}`, () => {
      const result = validate(loadFixture(fixture));
      expect(classify(result)).toBe(expected);
    });
  }

  it("unsupportedMajor short-circuits with empty errors even when the script is also schema-invalid", () => {
    const result = validate(loadFixture("forward-compat/future-major-invalid.json"));
    expect(result).toEqual({ ok: false, unsupportedMajor: true, errors: [] });
  });
});

describe("error attribution", () => {
  it("pins a missing citation excerpt to the citation's path", () => {
    const result = validate(loadFixture("invalid/citation-missing-excerpt.json"));
    expect(result.ok).toBe(false);
    expect(
      result.errors.some((error) => error.path.startsWith("/blocks/0/citations/0")),
    ).toBe(true);
  });

  it("pins a dangling correctOptionId to the question field", () => {
    const result = validate(loadFixture("invalid/quiz-mc-dangling-correct-option.json"));
    expect(result.ok).toBe(false);
    expect(result.errors).toEqual([
      {
        path: "/blocks/0/questions/0/correctOptionId",
        message: "must reference the id of one of the question's options",
      },
    ]);
  });

  it("pins missing lesson-level required fields to the root", () => {
    const result = validate(loadFixture("invalid/missing-tenant.json"));
    expect(result.ok).toBe(false);
    expect(result.errors.some((error) => error.message.includes("tenantId"))).toBe(true);
  });
});
