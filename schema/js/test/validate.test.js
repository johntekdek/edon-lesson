import { readFileSync, readdirSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { validate } from "../src/index.js";

const FIXTURES_DIR = new URL("../../fixtures/", import.meta.url);
const CORPUS_DIRS = ["valid", "invalid", "forward-compat"];
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
  for (const [fixture, spec] of Object.entries(expectations)) {
    const expected = typeof spec === "string" ? spec : spec.outcome;
    it(`${fixture} → ${expected}`, () => {
      const result = validate(loadFixture(fixture));
      expect(classify(result)).toBe(expected);
      if (typeof spec === "object") {
        // Negative-space DoD: the fixture must fail for its documented reason.
        const hit = result.errors.find(
          (error) =>
            error.path === spec.errorPath &&
            (!spec.messageContains ||
              error.message.includes(spec.messageContains)),
        );
        expect(
          hit,
          `expected an error at ${spec.errorPath}, got ${JSON.stringify(result.errors)}`,
        ).toBeTruthy();
      }
    });
  }

  it("every fixture on disk has an expectations entry", () => {
    const onDisk = CORPUS_DIRS.flatMap((dir) =>
      readdirSync(new URL(`${dir}/`, FIXTURES_DIR))
        .filter((name) => name.endsWith(".json"))
        .map((name) => `${dir}/${name}`),
    );
    expect(onDisk.sort()).toEqual(Object.keys(expectations).sort());
  });

  it("unsupportedMajor short-circuits with empty errors even when the script is also schema-invalid", () => {
    const result = validate(
      loadFixture("forward-compat/future-major-invalid.json"),
    );
    expect(result).toEqual({ ok: false, unsupportedMajor: true, errors: [] });
  });
});

describe("version-string engine parity", () => {
  // Python's re lets $ match before a trailing newline and \d match Unicode
  // digits; ECMA does neither. Both wrappers must reject these identically
  // as plain invalid (never valid, never unsupportedMajor).
  for (const version of ["2.0\n", "1.0\n", "١.٠"]) {
    it(`rejects schema ${JSON.stringify(version)} as plain invalid`, () => {
      const script = loadFixture("valid/minimal-slide-quiz.json");
      script.schema = version;
      const result = validate(script);
      expect(result.unsupportedMajor).toBe(false);
      expect(result.ok).toBe(false);
      expect(result.errors.some((error) => error.path === "/schema")).toBe(
        true,
      );
    });
  }
});

describe("error attribution", () => {
  it("pins a missing citation excerpt to the citation's path", () => {
    const result = validate(
      loadFixture("invalid/citation-missing-excerpt.json"),
    );
    expect(result.ok).toBe(false);
    expect(
      result.errors.some((error) =>
        error.path.startsWith("/blocks/0/citations/0"),
      ),
    ).toBe(true);
  });

  it("pins a dangling correctOptionId to the question field", () => {
    const result = validate(
      loadFixture("invalid/quiz-mc-dangling-correct-option.json"),
    );
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
    expect(
      result.errors.some((error) => error.message.includes("tenantId")),
    ).toBe(true);
  });
});
