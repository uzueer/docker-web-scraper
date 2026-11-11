# Docker Web Scraper

A Dockerized application that visits a URL with Puppeteer and system Chromium, saves a small JSON summary of the page, and serves that JSON through Flask. The image uses a multi-stage build: Node.js, Puppeteer, and Chromium are used only while building the scraper stage; the final runtime contains Python, Flask, and the generated data file.

## Technologies

- Node.js 18 and Puppeteer
- System-installed Chromium
- Python 3.10 and Flask
- Docker multi-stage builds

## Architecture

1. The `scraper` build stage installs Chromium and Puppeteer, then runs `scrape.js` with the URL supplied through `SCRAPE_URL`.
2. The scraper writes `scraped_data.json`.
3. The `runtime` stage copies that JSON and the Flask server into a Python 3.10 image. It runs as a non-root user and does not include Node.js, Puppeteer, or Chromium.

Scraping happens during `docker build`. Build a new image to refresh the captured page data.

## Project structure

```text
.
├── Dockerfile
├── README.md
├── package.json
├── requirements.txt
├── scrape.js
├── server.py
└── tests/
    └── test_server.py
```

`STATUS.md` is a local development tracker and is intentionally ignored by Git.

## Prerequisites

- Docker with permission to build and run containers
- Internet access from the Docker build so it can download base images, dependencies, and the requested page

Node.js and Chromium do not need to be installed on the host to use the Docker workflow.

## Build the image

Set `SCRAPE_URL` to the page to scrape:

```bash
docker build --build-arg SCRAPE_URL=https://example.com -t web-scraper .
```

The URL must be a valid absolute HTTP or HTTPS URL. The build fails if scraping fails.

## Run the container

```bash
docker run -d -p 5000:5000 --name scraper-container web-scraper
```

The Flask service listens on container port `5000`; `-p 5000:5000` makes it available on port `5000` of the host. Open `http://localhost:5000` or use `curl`:

```bash
curl http://localhost:5000/
curl http://localhost:5000/health
```

To inspect the container and its logs:

```bash
docker ps
docker logs scraper-container
```

To stop and remove it:

```bash
docker stop scraper-container
docker rm scraper-container
```

## API endpoints

| Method | Path | Response |
| --- | --- | --- |
| `GET` | `/` | The scraped page JSON. Returns `404` when the data file is missing and `500` when it cannot be read or parsed. |
| `GET` | `/health` | `{"status":"ok"}` while the Flask service is responding. |

Example response from `/`:

```json
{
  "url": "https://example.com/",
  "title": "Example Domain",
  "h1": "",
  "status": 200,
  "scrapedAt": "2026-11-11T06:41:58.686Z"
}
```

The `h1` value is an empty string when the page has no first-level heading. `scrapedAt` is the scrape time in UTC using ISO 8601 format.

## Run tests

Python 3.10 or newer is needed to run the Flask unit tests locally. Install the dependency and run unittest discovery:

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

The tests use Flask's test client and temporary data files; they do not contact external websites or require Docker.

## Troubleshooting

- **Docker cannot connect to the daemon:** Start Docker and ensure your user can access its socket.
- **The build reports an invalid or missing `SCRAPE_URL`:** Pass a valid absolute `http://` or `https://` URL with `--build-arg SCRAPE_URL=...`.
- **The build cannot reach the page:** Check that the Docker build has internet access and that the site is reachable from the build environment.
- **Port 5000 is already in use:** Map another host port, for example `-p 8000:5000`, and open `http://localhost:8000`.
- **The API returns a data-file error:** Check the build output for scraper errors and rebuild the image after correcting the URL or network access.
