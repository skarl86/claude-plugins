#!/usr/bin/env node
// Usage: node screenshot.mjs <html-path> <output-dir> [total-slides]
//
// Captures each <section class="slide" data-slide="NN"> in the HTML
// as a 3840x2160 PNG (viewport 1920x1080, deviceScaleFactor 2).
// If total-slides is omitted, it auto-detects from the DOM.

import { chromium } from 'playwright';
import path from 'path';
import { fileURLToPath, pathToFileURL } from 'url';
import fs from 'fs';

const [, , htmlPathArg, outDirArg, totalArg] = process.argv;

if (!htmlPathArg || !outDirArg) {
  console.error('Usage: node screenshot.mjs <html-path> <output-dir> [total-slides]');
  process.exit(1);
}

const htmlAbs = path.resolve(htmlPathArg);
const outAbs = path.resolve(outDirArg);

if (!fs.existsSync(htmlAbs)) {
  console.error(`HTML not found: ${htmlAbs}`);
  process.exit(1);
}
fs.mkdirSync(outAbs, { recursive: true });

const url = pathToFileURL(htmlAbs).toString();

(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    deviceScaleFactor: 2,
  });
  const page = await ctx.newPage();
  await page.goto(url, { waitUntil: 'networkidle' });
  // Give web fonts and any deferred styles time to settle.
  await page.waitForTimeout(800);

  let total;
  if (totalArg) {
    total = parseInt(totalArg, 10);
  } else {
    total = await page.locator('.slide').count();
  }

  if (!total || Number.isNaN(total)) {
    console.error('Could not determine slide count.');
    await browser.close();
    process.exit(1);
  }

  for (let i = 1; i <= total; i++) {
    const num = String(i).padStart(2, '0');
    const sel = `.slide[data-slide="${num}"]`;
    const loc = page.locator(sel);
    const exists = (await loc.count()) > 0;
    if (!exists) {
      console.warn(`skip ${num} (selector not found)`);
      continue;
    }
    const file = path.join(outAbs, `slide-${num}.png`);
    await loc.screenshot({ path: file });
    console.log('saved', file);
  }

  await browser.close();
})();
