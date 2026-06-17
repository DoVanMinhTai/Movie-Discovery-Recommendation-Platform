import os
import time
from typing import List

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from elasticsearch import Elasticsearch, helpers
from sentence_transformers import SentenceTransformer
from sqlalchemy import create_engine

load_dotenv()


class ElasticsearchCBFMigration:
    """Build the Content-Based Filtering index (movies_cbf) with SBERT embeddings.

    Self-contained: reads config from environment variables (same convention as
    sync_postgres_to_es.py) and pulls data straight from PostgreSQL so it can run
    inside the initializer container on first init.
    """

    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL") or \
            "postgresql://postgres:postgres@movie-postgres:5432/postgres"
        self.engine = create_engine(self.db_url)

        es_host = os.getenv("ES_HOST", "elasticsearch")
        es_port = int(os.getenv("ES_PORT_9200", 9200))

        print(f"Connecting to Elasticsearch at http://{es_host}:{es_port}...")
        self.es = Elasticsearch(
            [f"http://{es_host}:{es_port}"],
            request_timeout=60,
        )
        self.index_name = "movies_cbf"
        self.embedding_model = None

    def initialize_embedding_model(self, model_name="all-MiniLM-L6-v2"):
        print("Loading SentenceTransformer model...")
        self.embedding_model = SentenceTransformer(model_name)

    def create_index(self):
        mapping = {
            "mappings": {
                "properties": {
                    "movie_id": {"type": "keyword"},
                    "title": {"type": "text", "analyzer": "standard"},
                    "genres": {"type": "keyword"},
                    "tags": {"type": "text", "analyzer": "standard"},
                    "plot": {"type": "text", "analyzer": "standard"},
                    "embedding": {
                        "type": "dense_vector",
                        "dims": 384,
                        "index": True,
                        "similarity": "cosine",
                        "index_options": {
                            "type": "hnsw",
                            "m": 16,
                            "ef_construction": 100,
                        },
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

        if self.es.indices.exists(index=self.index_name):
            print(f"Deleting existing index: {self.index_name}")
            self.es.indices.delete(index=self.index_name)

        self.es.indices.create(index=self.index_name, body=mapping)
        print(f"Created index: {self.index_name}")

    def load_data_from_postgres(self) -> pd.DataFrame:
        print("Fetching data from PostgreSQL...")
        query = """
            SELECT m.media_content_id, m.title, m.overview as plot,
                   m.director, m."cast",
                   string_agg(g.name, ', ') as genres
            FROM mediacontent m
            LEFT JOIN mediacontent_genres mg ON m.media_content_id = mg.mediacontent_id
            LEFT JOIN genres g ON mg.genre_id = g.id
            WHERE m.is_deleted = false
            GROUP BY m.media_content_id, m.title, m.overview, m.director, m."cast"
        """
        return pd.read_sql(query, self.engine)

    def prepare_document_content(self, row: pd.Series) -> str:
        parts = []
        if row.get("title"):
            parts.append(str(row["title"]))
        if row.get("genres"):
            parts.append(f"Genres: {row['genres']}")
        if row.get("director"):
            parts.append(f"Director: {row['director']}")
        if row.get("cast"):
            parts.append(f"Cast: {row['cast']}")
        if row.get("plot"):
            parts.append(f"Plot: {row['plot']}")
        return ". ".join(parts)

    def generate_embeddings_batch(self, texts: List[str], batch_size: int = 32):
        return self.embedding_model.encode(
            texts, batch_size=batch_size, show_progress_bar=True
        )

    def bulk_index_movies(self, df: pd.DataFrame, batch_size: int = 1000):
        df = df.replace({np.nan: None})
        all_content = df.apply(self.prepare_document_content, axis=1).tolist()

        print("Generating embeddings (SBERT)...")
        embeddings = self.generate_embeddings_batch(all_content)

        def doc_generator():
            for idx, (_, row) in enumerate(df.iterrows()):
                m_id = row["media_content_id"]
                yield {
                    "_index": self.index_name,
                    "_id": str(m_id),
                    "_source": {
                        "movie_id": str(m_id),
                        "title": row.get("title") or "",
                        "plot": row.get("plot") or "",
                        "genres": row.get("genres") or "",
                        "tags": "",
                        "embedding": embeddings[idx].tolist(),
                        "cf_recommendations": [],
                    },
                }

        total_docs = len(df)
        success_count, errors = helpers.bulk(
            self.es,
            doc_generator(),
            chunk_size=batch_size,
            max_retries=3,
            request_timeout=60,
        )

        if errors:
            print(f"Encountered {len(errors)} errors during indexing")
            for error in errors[:5]:
                print(f"Error: {error}")

        print(f"Successfully indexed {success_count}/{total_docs} documents")


def main():
    start_time = time.time()
    migration = ElasticsearchCBFMigration()

    df = migration.load_data_from_postgres()
    if df.empty:
        print("No data found to build CBF index.")
        return
    print(f"Loaded {len(df)} movies from database successfully.")

    migration.initialize_embedding_model("all-MiniLM-L6-v2")
    migration.create_index()
    migration.bulk_index_movies(df, batch_size=1000)

    duration = time.time() - start_time
    print(f"=== CBF index build complete in {duration:.2f}s ===")


if __name__ == "__main__":
    main()
