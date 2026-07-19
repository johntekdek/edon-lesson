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
// ASCII [0-9] to mirror the py wrapper exactly (Python's \d is Unicode-aware).
const VERSION_PATTERN = /^[0-9]+\.[0-9]+$/;

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
// implement these inside validate() with identical semantics: correctOptionId
// membership, and uniqueness of block ids, question ids (per quiz block), and
// option ids (per question). Loop structure mirrors the py wrapper so both
// languages emit the same errors in the same order.
function referentialErrors(script) {
  const errors = [];
  if (!script || !Array.isArray(script.blocks)) return errors;
  const seenBlockIds = new Set();
  script.blocks.forEach((block, blockIndex) => {
    if (!block || typeof block !== "object") return;
    if (typeof block.id === "string") {
      if (seenBlockIds.has(block.id)) {
        errors.push({
          path: `/blocks/${blockIndex}/id`,
          message: "must not duplicate another block's id",
        });
      }
      seenBlockIds.add(block.id);
    }
    if (block.type !== "quiz" || !Array.isArray(block.questions)) return;
    const seenQuestionIds = new Set();
    block.questions.forEach((question, questionIndex) => {
      if (!question || typeof question !== "object") return;
      if (typeof question.id === "string") {
        if (seenQuestionIds.has(question.id)) {
          errors.push({
            path: `/blocks/${blockIndex}/questions/${questionIndex}/id`,
            message:
              "must not duplicate another question's id in the same quiz block",
          });
        }
        seenQuestionIds.add(question.id);
      }
      if (!Array.isArray(question.options)) {
        return;
      }
      const seenOptionIds = new Set();
      question.options.forEach((option, optionIndex) => {
        if (
          !option ||
          typeof option !== "object" ||
          typeof option.id !== "string"
        )
          return;
        if (seenOptionIds.has(option.id)) {
          errors.push({
            path: `/blocks/${blockIndex}/questions/${questionIndex}/options/${optionIndex}/id`,
            message:
              "must not duplicate another option's id in the same question",
          });
        }
        seenOptionIds.add(option.id);
      });
      if (
        question.type === "multipleChoice" &&
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
      // ajv reports a `must match "then" schema` echo (keyword "if") for every
      // failed if/then dispatch on top of the real leaf error; the py wrapper
      // has no such cascade, so drop it to keep the payloads identical.
      if (error.keyword === "if") continue;
      errors.push({ path: error.instancePath || "/", message: error.message });
    }
  }
  errors.push(...referentialErrors(script));

  return { ok: errors.length === 0, unsupportedMajor: false, errors };
}
