import { chromium } from "playwright";
import AxeBuilder from "@axe-core/playwright";
import fs from "node:fs";
fs.mkdirSync("reports/screenshots", { recursive: true });
const browser = await chromium.launch({ headless: true });
const failures = [],
  reports = [],
  externalPlayerIssues = [];
for (const width of [1440, 390]) {
  const context = await browser.newContext({
    viewport: { width, height: 1000 },
    deviceScaleFactor: 1,
  });
  const page = await context.newPage();
  page.on("pageerror", (error) => failures.push({ width, error: error.message }));
  for (const { route } of JSON.parse(fs.readFileSync("content/navigation.json", "utf8")).pages) {
    await page.goto("http://127.0.0.1:8000/" + route, { waitUntil: "domcontentloaded" });
    await page.evaluate(async () => {
      await document.fonts.ready;
      await Promise.all(
        [...document.images].map(async (i) => {
          i.loading = "eager";
          try {
            await i.decode();
          } catch {}
        }),
      );
    });
    const issues = await page.evaluate(() => ({
      overflow: document.documentElement.scrollWidth > innerWidth,
      images: [...document.images]
        .filter((i) => !i.complete || i.naturalWidth === 0)
        .map((i) => i.src),
      h1: document.querySelectorAll("h1").length,
      alignedArticle: [...document.querySelectorAll(".article-content > article > p")]
        .filter((node) => !node.querySelector("img"))
        .every(
          (node) =>
            Math.abs(
              node.getBoundingClientRect().width - node.parentElement.getBoundingClientRect().width,
            ) < 2,
        ),
      contactImageUncropped: (() => {
        const image = document.querySelector(".contact-image img");
        if (!image) return true;
        return (
          Math.abs(
            image.clientWidth / image.clientHeight - image.naturalWidth / image.naturalHeight,
          ) < 0.01
        );
      })(),
    }));
    if (
      issues.overflow ||
      issues.images.length ||
      issues.h1 !== 1 ||
      !issues.alignedArticle ||
      !issues.contactImageUncropped
    )
      failures.push({ route, width, ...issues });
    if (
      [
        "index.html",
        "sl/index.html",
        "research.html",
        "sl/research.html",
        "tular.html",
        "sl/tular.html",
        "contact.html",
      ].includes(route)
    ) {
      const axe = await new AxeBuilder({ page })
        .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
        .analyze();
      for (const violation of axe.violations) {
        const external = violation.nodes.filter((node) => node.target.length > 1);
        const local = violation.nodes.filter((node) => node.target.length === 1);
        const issue = (nodes) => ({
          route,
          width,
          id: violation.id,
          impact: violation.impact,
          nodes: nodes.map((node) => ({ target: node.target, html: node.html.slice(0, 200) })),
        });
        if (external.length) externalPlayerIssues.push(issue(external));
        if (local.length) failures.push(issue(local));
      }
    }
    reports.push({ route, width, ...issues });
    if (
      [
        "index.html",
        "sl/index.html",
        "research.html",
        "tular.html",
        "sl/tular.html",
        "contact.html",
      ].includes(route)
    )
      await page.screenshot({
        path:
          "reports/screenshots/" +
          (route === "index.html"
            ? width === 1440
              ? "desktop"
              : "mobile"
            : route.replaceAll("/", "-").replace(".html", "") + "-" + width) +
          ".png",
        fullPage: true,
      });
  }
  await page.goto("http://127.0.0.1:8000/research.html");
  await page.locator("#archive").scrollIntoViewIfNeeded();
  await page.screenshot({ path: `reports/screenshots/research-detail-${width}.png` });
  await page.locator("#archive-search").fill("no-such-research-xy987");
  if (!(await page.locator(".no-results").isVisible()))
    failures.push({ search: "missing empty state" });
  await page.locator("#archive-search").fill("Recknagel");
  if ((await page.locator(".publication-year:visible").count()) === 0)
    failures.push({ search: "missing author match" });
  await page.locator("#archive-year").selectOption("2022");
  if ((await page.locator(".publication:not([hidden])").count()) !== 1) {
    failures.push({ search: "combined year and author filter failed" });
  }
  await page.locator('button[type="reset"]').click();
  await page.waitForFunction(
    () => document.querySelectorAll(".publication:not([hidden])").length === 51,
  );
  if ((await page.locator(".publication:not([hidden])").count()) !== 51) {
    failures.push({ search: "reset did not restore all entries" });
  }
  await page.locator(".publication-details").first().locator("summary").click();
  if (
    !(await page.locator(".publication-details").first().getAttribute("open")) &&
    (await page.locator(".publication-details").first().getAttribute("open")) !== ""
  ) {
    failures.push({ details: "affiliations did not expand" });
  }
  await page.locator(".language").click();
  if (!page.url().endsWith("/sl/research.html")) failures.push({ language: "lost route" });
  if (width === 390) {
    await page.locator(".menu-toggle").click();
    if (!(await page.locator("#navigation").isVisible())) failures.push({ menu: "not open" });
    await page.keyboard.press("Escape");
    if (await page.locator("#navigation").isVisible()) failures.push({ menu: "not closed" });
  }
  await context.close();
}
const nojs = await browser.newPage({
  javaScriptEnabled: false,
  viewport: { width: 390, height: 844 },
});
await nojs.goto("http://127.0.0.1:8000/sl/research.html");
if (
  !(await nojs.locator("#navigation").isVisible()) ||
  !(await nojs.locator(".publication-year").first().isVisible())
)
  failures.push({ nojs: "content or navigation unavailable" });
await browser.close();
fs.writeFileSync(
  "reports/browser-check.json",
  JSON.stringify({ checks: reports.length, failures, externalPlayerIssues, reports }, null, 2),
);
console.log(
  JSON.stringify(
    { checks: reports.length, failures, externalPlayerIssues: externalPlayerIssues.length },
    null,
    2,
  ),
);
process.exitCode = failures.length ? 1 : 0;
