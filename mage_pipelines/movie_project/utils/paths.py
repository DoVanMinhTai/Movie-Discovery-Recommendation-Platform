"""Shared helpers for path resolution and connections across Mage blocks.

These helpers keep every block self-contained but consistent. Paths follow the
medallion layout requested for the project:

    data/
      bronze/raw_movies.json     # raw crawl cache
      silver/movies_clean.csv    # cleaned data for CBF (overwritten each run)
      gold/cbf_embeddings.npy    # backup of the CBF embedding matrix
      gold/cf_predictions.csv    # Top-N CF recommendations per user
"""
import os
from pathlib import Path


def repo_root() -> Path:
    # mage_pipelines/movie_project/utils/paths.py -> parents[3] == repo root
    return Path(__file__).resolve().parents[3]


def data_dir() -> Path:
    # In docker, set DATA_DIR=/home/src/data (mount ./data into the mage container)
    return Path(os.getenv("DATA_DIR", str(repo_root() / "data")))


def bronze_dir() -> Path:
    d = data_dir() / "bronze"
    d.mkdir(parents=True, exist_ok=True)
    return d


def silver_dir() -> Path:
    d = data_dir() / "silver"
    d.mkdir(parents=True, exist_ok=True)
    return d


def gold_dir() -> Path:
    d = data_dir() / "gold"
    d.mkdir(parents=True, exist_ok=True)
    return d


def database_url() -> str:
    return os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@movie-postgres:5432/postgres",
    )


def es_url() -> str:
    host = os.getenv("ES_HOST", "elasticsearch").replace("http://", "").replace("https://", "")
    if ":" in host:
        host, port = host.split(":")
    else:
        port = os.getenv("ES_PORT_9200", "9200")
    return f"http://{host}:{port}"


# Elasticsearch index that stores the per-movie documents (CBF embedding +
# nested CF recommendations). Must match initializer/sync_postgres_to_es.py.
ES_INDEX = os.getenv("ES_INDEX", "media_contents")
