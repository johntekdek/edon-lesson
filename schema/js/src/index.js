import { readFileSync } from "node:fs";
import Ajv2020Import from "ajv/dist/2020.js";

// ESM-CJS interop: ajv ships CJS; the class may arrive as the default export or the module itself.
const Ajv2020 = Ajv2020Import.default ?? Ajv2020Import;

// The major version this package's schema documents describe. Scripts with a
// HIGHER major short-circuit to unsupportedMajor before any schema validation
// (the Player maps that to the designed can't-play state). Same-major future
// minors validate: unknown block types and unknown fields pass through.
export const SUPPORTED_MAJOR = 1;

const SCHEMA_DIR = new URL("../../lesson/1.0/", import.meta.url);
const VERSION_PATTERN = /^\d+\.\d+$/;

function loadSchema(relativePath) {
  return JSON.parse(readFileSync(new URL(relativePath, SCHEMA_DIR), "utf8"));
}

const lessonSchema = loadSchema("lesson.schema.json");
const referencedSchemas = [
  loadSchema("defs.schema.json"),
  loadSchema("blocks/slide.schema.json"),
  loadSchema("blocks/narration.schema.json"),
  loadSchema("blocks/quiz.schema.json"),
  loadSchema("blocks/diagram.schema.json"),
  loadSchema("blocks/model3d.schema.json"),
  loadSchema("blocks/simulation.schema.json"),
];

const ajv = new Ajv2020({ allErrors: true, strict: false });
for (const schema of referencedSchemas) {
  ajv.addSchema(schema);
}
const validateAgainstSchema = ajv.compile(lessonSchema);

// Referential rules JSON Schema cannot express. Both wrappers (js + py)
// implement these inside validate() with identical semantics.
function referentialErrors(script) {
  const errors = [];
  if (!script || !Array.isArray(script.blocks)) return errors;
  script.blocks.forEach((block, blockIndex) => {
    if (!block || block.type !== "quiz" || !Array.isArray(block.questions)) return;
    block.questions.forEach((question, questionIndex) => {
      if (
        question &&
        question.type === "multipleChoice" &&
        Array.isArray(question.options) &&
        typeof question.correctOptionId === "string"
      ) {
        const optionIds = question.options
          .filter((option) => option && typeof option === "object")
          .map((option) => option.id);
        if (!optionIds.includes(question.correctOptionId)) {
          errors.push({
            path: `/blocks/${blockIndex}/questions/${questionIndex}/correctOptionId`,
            message: "must reference the id of one of the question's options",
          });
        }
      }
    });
  });
  return errors;
}

export function validate(script) {
  if (
    script !== null &&
    typeof script === "object" &&
    typeof script.schema === "string" &&
    VERSION_PATTERN.test(script.schema)
  ) {
    const major = Number.parseInt(script.schema.split(".")[0], 10);
    if (major > SUPPORTED_MAJOR) {
      return { ok: false, unsupportedMajor: true, errors: [] };
    }
  }

  const errors = [];
  if (!validateAgainstSchema(script)) {
    for (const error of validateAgainstSchema.errors) {
      errors.push({ path: error.instancePath || "/", message: error.message });
    }
  }
  errors.push(...referentialErrors(script));

  return { ok: errors.length === 0, unsupportedMajor: false, errors };
}
