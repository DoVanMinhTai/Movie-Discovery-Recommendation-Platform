import os
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from elasticsearch import Elasticsearch, helpers
from sqlalchemy import create_engine
import json
import time
from typing import List, Dict
from dotenv import load_dotenv
import sys
from pathlib import Path

load_dotenv()

class PostgresToElasticSync:
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
        if not self.db_url:
            self.db_url = "postgresql://postgres:postgres@movie-postgres:5432/postgres"
            
        self.engine = create_engine(self.db_url)
        
        es_host = os.getenv("ES_HOST", "elasticsearch")  
        es_port = int(os.getenv("ES_PORT_9200", 9200))
        
        print(f"Connecting to Elasticsearch at http://{es_host}:{es_port}...")
        self.es = Elasticsearch(
            [f"http://{es_host}:{es_port}"],
            request_timeout=60
        )
        
        print("Loading SentenceTransformer model...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index_name = 'media_contents'
        
        self._ensure_index_exists()
    def _ensure_index_exists(self):
        """Đảm bảo index có cấu hình dense_vector chuẩn cho ES 8.x trước khi sync"""
        if not self.es.indices.exists(index=self.index_name):
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
                            "dims": 384,
                            "index": True,
                            "similarity": "cosine",
                            "index_options": {
                                "type": "hnsw",
                                "m": 16,
                                "ef_construction": 100
                            }
                        },
                        "cf_recommendations": {
                            "type": "nested",
                            "properties": {
                                "user_id": {"type": "keyword"},
                                "score": {"type": "float"}
                            }
                        }
                    }
                }
            }
            self.es.indices.create(index=self.index_name, body=mapping)
            print(f"Created Index '{self.index_name}' with dense_vector mapping successfully.")
            
    def load_data_from_postgres(self):
        print("Fetching data from PostgreSQL...")
        query = """
            SELECT m.media_content_id, m.title, m.overview as plot, m.director, m."cast",
                   string_agg(g.name, ', ') as genres
            FROM mediacontent m
            LEFT JOIN mediacontent_genres mg ON m.media_content_id = mg.mediacontent_id
            LEFT JOIN genres g ON mg.genre_id = g.id
            WHERE m.is_deleted = false
            GROUP BY m.media_content_id, m.title, m.overview, m.director, m."cast"
        """
        return pd.read_sql(query, self.engine)


    def prepare_document_content(self, row):
        parts = []
        if row['title']: parts.append(str(row['title']))
        if row['genres']: parts.append(f"Genres: {row['genres']}")
        if row['director']: parts.append(f"Director: {row['director']}")
        if row['cast']: parts.append(f"Cast: {row['cast']}")
        if row['plot']: parts.append(f"Plot: {row['plot']}")
        return ". ".join(parts)

    def sync(self):
        start_time = time.time()
        df = self.load_data_from_postgres()
        if df.empty:
            print("No data found to sync.")
            return

        df = df.replace({np.nan: None})

        print(f"Syncing {len(df)} movies to OpenSearch...")
        
        all_texts = df.apply(self.prepare_document_content, axis=1).tolist()
        
        print("Generating embeddings (SBERT)...")
        embeddings = self.model.encode(all_texts, batch_size=32, show_progress_bar=True)

        def doc_generator():
            for idx, row in df.iterrows():
                yield {
                    '_index': self.index_name,
                    '_id': str(row['media_content_id']),
                    '_source': {
                        'movie_id': str(row['media_content_id']),
                        'title': row['title'],
                        'genres': row['genres'] if row['genres'] else "",
                        'plot': row['plot'] if row['plot'] else "",
                        'director': row['director'] if row['director'] else "",
                        'cast': row['cast'] if row['cast'] else "",
                        'embedding': embeddings[idx].tolist(),
                        'cf_recommendations': []
                    }
                }

        success, _ = helpers.bulk(self.es, doc_generator())
        
        duration = time.time() - start_time
        print(f"=== Sync Complete! Indexed {success} movies in {duration:.2f}s ===")

if __name__ == "__main__":
    sync_tool = PostgresToElasticSync()
    sync_tool.sync()
