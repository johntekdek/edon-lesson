// Playwright scaffold (Story 1.2; AR-25). The smoke suite uses the request fixture
// only — no browser binaries needed yet. Browser projects and the advisory low-spec
// profile arrive with the Player stories (addendum §5: low-spec CI is advisory).
import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: ".",
  use: {
    baseURL: "http://127.0.0.1:8100",
  },
  webServer: {
    command:
      "uv run uvicorn edon.api.app:create_app --factory --host 127.0.0.1 --port 8100",
    url: "http://127.0.0.1:8100/api/v1/health",
    reuseExistingServer: !process.env.CI,
    timeout: 30_000,
  },
});
