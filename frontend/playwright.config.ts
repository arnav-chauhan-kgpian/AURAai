import { defineConfig, devices } from "@playwright/test";

/**
 * Playwright E2E config.
 *
 * Smoke-tests the public surface (landing, privacy, navigation, responsive
 * layout) against a locally-built production server. It boots `next start` via
 * `webServer` and reuses an already-running instance in dev, so `npm run e2e`
 * is one command. Auth-gated flows are intentionally out of scope here — they
 * need a Clerk test user; these guard the routes that must always render.
 */
const PORT = Number(process.env.PORT ?? 3000);
const BASE_URL = process.env.E2E_BASE_URL ?? `http://127.0.0.1:${PORT}`;

export default defineConfig({
  testDir: "./tests/e2e",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  reporter: process.env.CI ? "github" : "list",
  use: {
    baseURL: BASE_URL,
    trace: "on-first-retry",
  },
  projects: [
    { name: "desktop", use: { ...devices["Desktop Chrome"] } },
    { name: "mobile", use: { ...devices["Pixel 5"] } },
  ],
  webServer: process.env.E2E_BASE_URL
    ? undefined
    : {
        command: "npm run start",
        url: BASE_URL,
        timeout: 120_000,
        reuseExistingServer: true,
      },
});
