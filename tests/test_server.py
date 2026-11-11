import json
import tempfile
import unittest
from pathlib import Path

from server import create_app


class ServerRoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.data_file = Path(self.temp_dir.name) / "scraped_data.json"
        self.app = create_app(self.data_file)
        self.client = self.app.test_client()

    def test_get_root_returns_scraped_json(self):
        expected = {
            "url": "https://example.com/",
            "title": "Example Domain",
            "h1": "Example Domain",
            "status": 200,
            "scrapedAt": "2026-11-11T00:00:00.000Z",
        }
        self.data_file.write_text(json.dumps(expected), encoding="utf-8")

        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        self.assertEqual(response.get_json(), expected)

    def test_get_root_returns_valid_json_response(self):
        self.data_file.write_text('{"title":"Example"}', encoding="utf-8")

        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"title": "Example"})

    def test_get_health_reports_server_health(self):
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"status": "ok"})

    def test_missing_json_file_returns_not_found(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json(), {"error": "Scraped data is not available."})

    def test_invalid_json_file_returns_server_error(self):
        self.data_file.write_text("{not valid JSON", encoding="utf-8")

        response = self.client.get("/")

        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            response.get_json(),
            {"error": "Scraped data file contains invalid JSON."},
        )


if __name__ == "__main__":
    unittest.main()
