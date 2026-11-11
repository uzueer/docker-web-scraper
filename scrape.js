const fs = require('node:fs');
const path = require('node:path');
const puppeteer = require('puppeteer');

const OUTPUT_FILE = path.resolve(process.env.SCRAPED_DATA_FILE || 'scraped_data.json');
const NAVIGATION_TIMEOUT_MS = Number(process.env.NAVIGATION_TIMEOUT_MS || 30000);
const CHROMIUM_PATHS = [
  '/usr/bin/chromium',
  '/usr/bin/chromium-browser',
  '/usr/bin/google-chrome',
  '/usr/bin/google-chrome-stable',
];

function getScrapeUrl(value) {
  if (!value) {
    throw new Error('SCRAPE_URL is required.');
  }

  let url;
  try {
    url = new URL(value);
  } catch {
    throw new Error('SCRAPE_URL must be a valid absolute URL.');
  }

  if (!['http:', 'https:'].includes(url.protocol)) {
    throw new Error('SCRAPE_URL must use HTTP or HTTPS.');
  }

  return url.toString();
}

function getChromiumPath() {
  const configuredPath = process.env.PUPPETEER_EXECUTABLE_PATH;
  if (configuredPath) {
    if (!fs.existsSync(configuredPath)) {
      throw new Error(`Configured Chromium executable was not found: ${configuredPath}`);
    }
    return configuredPath;
  }

  return CHROMIUM_PATHS.find((candidate) => fs.existsSync(candidate));
}

async function main() {
  let browser;

  try {
    const url = getScrapeUrl(process.env.SCRAPE_URL);
    const executablePath = getChromiumPath();
    if (!executablePath) {
      throw new Error(
        'System Chromium was not found. Set PUPPETEER_EXECUTABLE_PATH to its executable path.'
      );
    }

    console.log(`Starting headless Chromium at ${executablePath}`);
    browser = await puppeteer.launch({
      executablePath,
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox'],
    });

    const page = await browser.newPage();
    page.setDefaultNavigationTimeout(NAVIGATION_TIMEOUT_MS);
    console.log(`Navigating to ${url}`);
    const response = await page.goto(url, { waitUntil: 'domcontentloaded' });

    const result = await page.evaluate(() => ({
      title: document.title || '',
      h1: document.querySelector('h1')?.innerText?.trim() || '',
    }));

    const data = {
      url,
      title: result.title,
      h1: result.h1,
      status: response ? response.status() : null,
      scrapedAt: new Date().toISOString(),
    };

    fs.writeFileSync(OUTPUT_FILE, `${JSON.stringify(data, null, 2)}\n`);
    console.log(`Scraped page data written to ${OUTPUT_FILE}`);
  } catch (error) {
    const failure = {
      error: {
        name: error.name || 'Error',
        message: error.message || String(error),
      },
      scrapedAt: new Date().toISOString(),
    };

    try {
      fs.writeFileSync(OUTPUT_FILE, `${JSON.stringify(failure, null, 2)}\n`);
    } catch (writeError) {
      console.error(`Could not write error output: ${writeError.message}`);
    }

    console.error(JSON.stringify(failure));
    process.exitCode = 1;
  } finally {
    if (browser) {
      await browser.close();
      console.log('Chromium closed');
    }
  }
}

main();
