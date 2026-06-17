"""CBF Flow - Block 4: Build embeddings and index them into Elasticsearch.

Generates SBERT vectors for the cleaned movies, backs up the matrix to
data/gold/cbf_embeddings.npy, then bulk-indexes per-movie documents into the
`media_contents` index. Each document keeps the shape expected by the app:

    {
      "movie_id": "105",
      "title": "...",
      "genres": "Action, Sci-Fi",
      "plot": "...",
      "director": "...",
      "embedding": [...384 floats...],
      "cf_recommendations": []   # filled later by the CF flow
    }

The embedding is upserted via `doc_as_upsert` so re-running the CBF flow never
wipes the cf_recommendations written by the CF flow.
"""
import numpy as np
import pandas as pd
from elasticsearch import Elasticsearch, helpers

if "data_exporter" not in globals():
    from mage_ai.data_preparation.decorators import data_exporter

try:
    from movie_project.utils.paths import es_url, gold_dir, ES_INDEX
except ImportError:
    from utils.paths import es_url, gold_dir, ES_INDEX


_EMBED_DIMS = 384
_MODEL_NAME = "all-MiniLM-L6-v2"


def _ensure_index(es: Elasticsearch, index_name: str):
    if es.indices.exists(index=index_name):
        return
    mapping = {
        "mappings": {
            "properties": {
                "movie_id": {"type": "keyword"},
                "title": {"type": "text", "analyzer": "standard"},
                "genres": {"type": "keyword"},
                "plot": {"type": "text", "analyzer": "standard"},
                "director": {"type": "keyword"},
                "cast": {"type": "text", "analyzer": "standard"},
                "embedding": {
                    "type": "dense_vector",
                    "dims": _EMBED_DIMS,
                    "index": True,
                    "similarity": "cosine",
                    "index_options": {"type": "hnsw", "m": 16, "ef_construction": 100},
                },
                "cf_recommendations": {
                    "type": "nested",
                    "properties": {
                        "user_id": {"type": "keyword"},
                        "score": {"type": "float"},
                    },
                },
            }
        }
    }
    es.indices.create(index=index_name, body=mapping)
    print(f"Created ES index '{index_name}'")


@data_exporter
def index_cbf_embeddings_es(df, *args, **kwargs):
    if df is None or len(df) == 0:
        print("No movies to embed/index")
        return df

    from sentence_transformers import SentenceTransformer

    df = df.replace({np.nan: None})
    texts = df["content"].fillna("").astype(str).tolist()

    print(f"Loading {_MODEL_NAME} and encoding {len(texts)} documents...")
    model = SentenceTransformer(_MODEL_NAME)
    embeddings = model.encode(texts, batch_size=32, show_progress_bar=True)

    # Backup matrix to gold layer.
    backup_path = gold_dir() / "cbf_embeddings.npy"
    np.save(backup_path, embeddings)
    print(f"Saved embedding backup -> {backup_path}")

    es = Elasticsearch([es_url()], request_timeout=60)
    _ensure_index(es, ES_INDEX)

    def doc_generator():
        for idx, (_, row) in enumerate(df.iterrows()):
            movie_id = str(int(row["media_content_id"]))
            yield {
                "_op_type": "update",
                "_index": ES_INDEX,
                "_id": movie_id,
                "doc": {
                    "movie_id": movie_id,
                    "title": row.get("title") or "",
                    "genres": row.get("genres") or "",
                    "plot": row.get("overview") or "",
                    "director": row.get("director") or "",
                    "cast": row.get("cast") or "",
                    "embedding": embeddings[idx].tolist(),
                },
                # create the doc if missing; never overwrite cf_recommendations
                "doc_as_upsert": True,
            }

    success, errors = helpers.bulk(es, doc_generator(), chunk_size=500, max_retries=3)
    if errors:
        print(f"{len(errors)} errors during indexing; first: {errors[:3]}")
    print(f"Indexed embeddings for {success}/{len(df)} movies into '{ES_INDEX}'")
    return df
