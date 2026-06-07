import os
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from opensearchpy import OpenSearch, helpers, RequestsHttpConnection
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
            raise ValueError("DATABASE_URL not found in .env")
        self.engine = create_engine(self.db_url)
        
        host = os.getenv("ES_HOST", "localhost")
        username = os.getenv("ES_USERNAME", "4f4693845a")
        password = os.getenv("ES_PASSWORD", "93cd64cc6ffae49747af")
        
        self.es = OpenSearch(
            hosts=[{'host': host, 'port': 443}], 
            http_auth=(username, password),
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection 
        )
        
        print(f"Connecting to OpenSearch at {host}...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index_name = 'movies_cbf'

    def load_data_from_postgres(self):
        print("Fetching data from PostgreSQL...")
        query = """
            SELECT m.movie_id, m.title, m.overview as plot, m.director, m."cast",
                   string_agg(g.name, ', ') as genres
            FROM mediacontent m
            LEFT JOIN mediacontent_genres mg ON m.movie_id = mg.mediacontent_id
            LEFT JOIN genres g ON mg.genre_id = g.id
            WHERE m.is_deleted = false
            GROUP BY m.movie_id, m.title, m.overview, m.director, m."cast"
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
                    '_id': str(row['movie_id']),
                    '_source': {
                        'movie_id': str(row['movie_id']),
                        'title': row['title'],
                        'genres': row['genres'] if row['genres'] else "",
                        'plot': row['plot'] if row['plot'] else "",
                        'director': row['director'] if row['director'] else "",
                        'cast': row['cast'] if row['cast'] else "",
                        'embedding': embeddings[idx].tolist()
                    }
                }

        success, _ = helpers.bulk(self.es, doc_generator())
        
        duration = time.time() - start_time
        print(f"=== Sync Complete! Indexed {success} movies in {duration:.2f}s ===")

if __name__ == "__main__":
    sync_tool = PostgresToElasticSync()
    sync_tool.sync()
