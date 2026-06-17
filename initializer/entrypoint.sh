#!/bin/sh
set -e

echo "=== [1/3] Syncing PostgreSQL -> Elasticsearch (media_contents) ==="
python sync_postgres_to_es.py

echo "=== [2/3] Importing MovieLens ratings into PostgreSQL ==="
python import_ratings.py

echo "=== [3/3] Building Content-Based Filtering index (movies_cbf) ==="
python generate_embeddings.py

echo "=== Initialization complete ==="
