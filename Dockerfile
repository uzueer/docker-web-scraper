FROM node:18-slim AS scraper

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        chromium \
        fonts-liberation \
        fonts-noto-color-emoji \
    && rm -rf /var/lib/apt/lists/*

ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true \
    PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium

COPY package.json ./
RUN npm install --omit=dev --no-audit --no-fund

COPY scrape.js ./
ARG SCRAPE_URL
RUN test -n "${SCRAPE_URL}" \
    && SCRAPE_URL="${SCRAPE_URL}" node scrape.js

FROM python:3.10-slim AS runtime

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && useradd --system --uid 10001 --create-home --no-log-init appuser

COPY --chown=appuser:appuser server.py ./server.py
COPY --from=scraper --chown=appuser:appuser /app/scraped_data.json ./scraped_data.json

USER appuser
EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD ["python", "-c", "from urllib.request import urlopen; urlopen('http://127.0.0.1:5000/health', timeout=2).read()"]

CMD ["python", "server.py"]
