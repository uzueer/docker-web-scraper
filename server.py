"""Serve scraped page data through a small Flask JSON API."""

import json
import logging
import os
from pathlib import Path

from flask import Flask, jsonify


def create_app(data_file=None):
    """Create the Flask app, optionally using a specific scraped data file."""
    app = Flask(__name__)
    app.logger.setLevel(logging.INFO)
    app.config["SCRAPED_DATA_FILE"] = Path(
        data_file or os.environ.get("SCRAPED_DATA_FILE", Path(__file__).with_name("scraped_data.json"))
    )

    @app.get("/")
    def get_scraped_data():
        data_path = app.config["SCRAPED_DATA_FILE"]
        try:
            with data_path.open("r", encoding="utf-8") as data_stream:
                data = json.load(data_stream)
        except FileNotFoundError:
            app.logger.warning("Scraped data file not found: %s", data_path)
            return jsonify({"error": "Scraped data is not available."}), 404
        except json.JSONDecodeError:
            app.logger.exception("Scraped data file contains invalid JSON: %s", data_path)
            return jsonify({"error": "Scraped data file contains invalid JSON."}), 500
        except OSError:
            app.logger.exception("Could not read scraped data file: %s", data_path)
            return jsonify({"error": "Could not read scraped data."}), 500

        return jsonify(data)

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"}), 200

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
