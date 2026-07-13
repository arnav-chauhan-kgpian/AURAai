import { expect, test } from "@playwright/test";

/**
 * Public-surface smoke tests.
 *
 * These run on both desktop and mobile projects (see playwright.config.ts) so a
 * broken layout or a crashed route fails CI. They only touch routes that render
 * without authentication.
 */

// Suppress the first-visit onboarding overlay so it can't intercept clicks.
test.beforeEach(async ({ context }) => {
  await context.addInitScript(() => {
    window.localStorage.setItem("aura-onboarded", "1");
  });
});

test("landing page renders the hero and primary CTA", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveTitle(/AuraAI/i);
  // The brand wordmark is always present in the header.
  await expect(page.getByRole("link", { name: /AuraAI/i }).first()).toBeVisible();
  // A call-to-action into the product exists.
  await expect(page.getByRole("link", { name: /Start Analysis/i }).first()).toBeVisible();
});

test("privacy policy page renders its heading and controls", async ({ page }) => {
  await page.goto("/privacy");
  await expect(page.getByRole("heading", { name: /Privacy & Data Use/i })).toBeVisible();
  await expect(page.getByRole("link", { name: /Settings/i }).first()).toBeVisible();
});

test("footer exposes a privacy link that navigates", async ({ page }) => {
  await page.goto("/");
  const privacy = page.getByRole("link", { name: /^Privacy$/ }).first();
  await privacy.scrollIntoViewIfNeeded();
  await privacy.click();
  await expect(page).toHaveURL(/\/privacy/);
});

test("no console errors on the landing page", async ({ page }) => {
  const errors: string[] = [];
  page.on("console", (msg) => {
    if (msg.type() === "error") errors.push(msg.text());
  });
  await page.goto("/", { waitUntil: "networkidle" });
  // Allow benign auth/network noise, fail on real runtime errors.
  const real = errors.filter(
    (e) => !/clerk|401|403|network|favicon/i.test(e),
  );
  expect(real).toEqual([]);
});
