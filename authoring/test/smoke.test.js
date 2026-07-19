import { describe, expect, it } from "vitest";

import { PACKAGE } from "../src/index.js";

describe("workspace wiring", () => {
  it("imports the package module", () => {
    expect(PACKAGE).toBe("@edon/authoring");
  });
});
