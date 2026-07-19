// CI stub for the budgets contract (AD-11): validates budgets.json against its
// JSON Schema. Later budget *measurement* (player bundle sizes at Story 4.1, perf
// gates at 11.2) plugs into the same file — this stub is the schema tripwire.
import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import Ajv2020 from "ajv/dist/2020.js";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const schema = JSON.parse(readFileSync(path.join(root, "schema/budgets/budgets.schema.json"), "utf8"));
const budgets = JSON.parse(readFileSync(path.join(root, "budgets.json"), "utf8"));

const ajv = new Ajv2020({ allErrors: true });
const validate = ajv.compile(schema);

if (!validate(budgets)) {
  console.error("budgets.json FAILED schema validation:");
  for (const err of validate.errors) {
    console.error(`  ${err.instancePath || "/"} ${err.message}`);
  }
  process.exit(1);
}
console.log("budgets.json validates against schema/budgets/budgets.schema.json");
