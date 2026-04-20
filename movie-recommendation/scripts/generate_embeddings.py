import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from opensearchpy import OpenSearch, helpers, RequestsHttpConnection
import json
import time
from typing import List, Dict, Generator
import sys
from pathlib import Path

root_path = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(root_path))

from config.config import settings

class ElasticsearchCBFMigration:
    def __init__(self, es_host='localhost', es_port=430):
        host = settings.es_host
        
        self.es = OpenSearch(
            hosts=[{'host': host, 'port': 443}], 
            http_auth=(settings.es_username, settings.es_password),
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection 
        )
        self.embedding_model = None
        
        
    def initialize_embedding_model(self, model_name='all-MiniLM-L6-v2'):
        self.embedding_model = SentenceTransformer(model_name)
        
    def create_index(self, index_name: str, mapping_path: str = None):
        if mapping_path:
            with open(mapping_path, 'r') as f:
                mapping = json.load(f)
        else:
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
                            "similarity": "cosine"
                        }
                    }
                }
            }
        
        if self.es.indices.exists(index=index_name):
            print(f"Deleting existing index: {index_name}")
            self.es.indices.delete(index=index_name)
            
        self.es.indices.create(index=index_name, body=mapping)
        print(f"Created index: {index_name}")
        
    def prepare_document_content(self, row: pd.Series) -> str:
        content_parts = []
        
        if pd.notna(row.get('title')):
            content_parts.append(str(row['title']))
            
        if pd.notna(row.get('genres')):
            content_parts.append(f"Genres: {row['genres']}")
            
        if pd.notna(row.get('tags')):
            content_parts.append(f"Tags: {row['tags']}")
            
        if pd.notna(row.get('plot')):
            content_parts.append(f"Plot: {row['plot']}")
            
        return ". ".join(content_parts)
    
    def generate_embeddings_batch(self, texts: List[str], batch_size: int = 32) -> List[np.ndarray]:
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]
            batch_embeddings = self.embedding_model.encode(batch_texts)
            embeddings.extend(batch_embeddings)
            
        return embeddings
    
    def bulk_index_movies(self, df: pd.DataFrame, index_name: str, batch_size: int = 1000):        
        all_content = df.apply(self.prepare_document_content, axis=1).tolist()
        
        print("Generating embeddings...")
        embeddings = self.generate_embeddings_batch(all_content)
        
        def doc_generator():
            for idx, (_, row) in enumerate(df.iterrows()):
                doc = {
                    '_index': index_name,
                    '_id': str(row.get('movieId', idx)),
                    '_source': {
                        'movie_id': str(row.get('movieId', idx)),
                        'title': row.get('title', ''),
                        'genres': row.get('genres', ''),
                        'tags': row.get('tags', '') if pd.notna(row.get('tags')) else '',
                        'plot': row.get('plot', '') if pd.notna(row.get('plot')) else '',
                        'embedding': embeddings[idx].tolist()
                    }
                }
                yield doc
        
        success_count = 0
        total_docs = len(df)
        
        success_count, errors = helpers.bulk(
            self.es, 
            doc_generator(), 
            chunk_size=batch_size, 
            max_retries=3,
            request_timeout=60
        )

        if errors:
            print(f"Encountered {len(errors)} errors during indexing")
            for error in errors[:5]: 
                print(f"Error: {error}")
                
        print(f"Successfully indexed {success_count}/{total_docs} documents")
        
    def vector_search(self, query_embedding: np.ndarray, index_name: str, size: int = 5) -> List[Dict]:
        query_body = {
            "size": size,
            "query": {
                "knn": {
                    "embedding": {
                        "vector": query_embedding.tolist(),
                        "k": size
                    }
                }
            },
            "_source": ["movie_id", "title", "genres"]
        }
        
        response = self.es.search(index=index_name, body=query_body)
        return response['hits']['hits']
    
    def hybrid_search(self, query_text: str, query_embedding: np.ndarray, index_name: str, size: int = 5) -> List[Dict]:
        query_body = {
            "size": size,
            "query": {
                "bool": {
                    "should": [
                        {
                            "multi_match": {
                                "query": query_text,
                                "fields": ["title^2", "genres^1.5", "tags", "plot"]
                            }
                        },
                        {
                            "knn": {
                                "embedding": {
                                    "vector": query_embedding.tolist(),
                                    "k": size
                                }
                            }
                        }
                    ]
                }
            },
            "_source": ["movie_id", "title", "genres"]
        }
        
        response = self.es.search(index=index_name, body=query_body)
        return response['hits']['hits']
    
    def search_similar_movies(self, movie_title: str, index_name: str, size: int = 5) -> List[Dict]:
        search_body = {
            "query": {
                "match": {
                    "title": movie_title
                }
            },
            "_source": ["movie_id", "title", "genres", "embedding"],
            "size": 1
        }
        
        result = self.es.search(index=index_name, body=search_body)
        
        if not result['hits']['hits']:
            print(f"Movie '{movie_title}' not found in index")
            return []
            
        movie_doc = result['hits']['hits'][0]['_source']
        query_embedding = np.array(movie_doc['embedding'])
        
        similar_movies = self.vector_search(query_embedding, index_name, size + 1)
        
        similar_movies = [hit for hit in similar_movies if hit['_source']['title'] != movie_title]
        
        return similar_movies[:size]


def main():
    migration = ElasticsearchCBFMigration()
    
    print("Loading movie data...")
    df = pd.read_csv('movies.csv')

    migration.initialize_embedding_model('all-MiniLM-L6-v2')
    
    migration.create_index('movies_cbf', 'elasticsearch_mapping_opensearch.json')
    
    migration.bulk_index_movies(df, 'movies_cbf', batch_size=1000)
    
    print("\nExample: Finding similar movies to 'Toy Story'")
    similar_movies = migration.search_similar_movies('Toy Story', 'movies_cbf', size=5)
    
    for i, hit in enumerate(similar_movies):
        source = hit['_source']
        print(f"{i+1}. {source['title']} (ID: {source['movie_id']})")


if __name__ == "__main__":
    main()