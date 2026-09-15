#!/usr/bin/env bash
# Runs the full pipeline end-to-end: generate -> validate & load -> analyze.
# Stops immediately if any step fails.

set -e

echo "[1/3] Generating raw data..."
py generate_data.py

echo "[2/3] Running data-quality checks and loading into SQLite..."
py load_to_db.py

echo "[3/3] Running business SQL queries..."
py run_queries.py

echo "Pipeline finished. See reports/ for the data-quality report and SQL findings."
