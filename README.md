# Docker Web Scraper

A Dockerized web scraper that will use Puppeteer to collect page metadata and Flask to serve the resulting JSON. The project is being developed incrementally in five stages.

## Architecture

The planned Docker build uses Node.js 18, Puppeteer, and system Chromium in a build stage to scrape a URL and create `scraped_data.json`. A separate Python 3.10 runtime stage serves that file through a small Flask API. The final runtime image will not include Node.js, Puppeteer, or Chromium.

See `STATUS.md` for local development progress. This file is intentionally excluded from Git.
