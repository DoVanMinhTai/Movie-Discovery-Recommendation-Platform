import numpy as np
import pandas as pd
from elasticsearch import Elasticsearch
from typing import Dict
import logging
from datetime import datetime


class VectorExportService:
    """Export user/item vectors to Elasticsearch as dense_vector fields."""

    def __init__(self, es_client: Elasticsearch):
        self.es = es_client
        self.logger = logging.getLogger(__name__)

    def _create_index(self, index_name: str, dims: int):
        mapping = {
            "mappings": {
                "properties": {
                    "id": {"type": "keyword"},
                    "vector": {
                        "type": "dense_vector",
                        "dims": dims,
                        "index": True,
                        "similarity": "cosine"
                    },
                    "meta": {"type": "object"},
                    "imported_at": {"type": "date"}
                }
            }
        }
        if not self.es.indices.exists(index=index_name):
            self.es.indices.create(index=index_name, body=mapping)
            self.logger.info('Created index %s', index_name)

    def export_item_vectors(self, item_factors: np.ndarray, movie_id_map: Dict[str, int], movies_df: pd.DataFrame, index_name: str = 'movies_vectors'):
        dims = item_factors.shape[1]
        self._create_index(index_name, dims)
        operations = []
        for movie_id, idx in movie_id_map.items():
            vec = item_factors[idx].astype(float).tolist()
            movie = movies_df[movies_df['movie_id'] == movie_id]
            title = movie.iloc[0]['title'] if not movie.empty else ''
            doc = {
                'id': movie_id,
                'title': title,
                'vector': vec,
                'meta': {
                    'source': 'als'
                },
                'imported_at': datetime.utcnow().isoformat()
            }
            operations.append({"index": {"_index": index_name, "_id": movie_id}})
            operations.append(doc)
        if operations:
            res = self.es.bulk(operations=operations)
            if res.get('errors'):
                self.logger.error('Bulk indexing errors when exporting item vectors')
            else:
                self.logger.info('Indexed %d item vectors into %s', len(movie_id_map), index_name)

    def export_user_vectors(self, user_factors: np.ndarray, user_id_map: Dict[str, int], index_name: str = 'users_vectors'):
        dims = user_factors.shape[1]
        self._create_index(index_name, dims)
        operations = []
        for user_id, idx in user_id_map.items():
            vec = user_factors[idx].astype(float).tolist()
            doc = {
                'id': user_id,
                'vector': vec,
                'meta': {'source': 'als'},
                'imported_at': datetime.utcnow().isoformat()
            }
            operations.append({"index": {"_index": index_name, "_id": user_id}})
            operations.append(doc)

        if operations:
            res = self.es.bulk(operations=operations)
            if res.get('errors'):
                self.logger.error('Bulk indexing errors when exporting user vectors')
            else:
                self.logger.info('Indexed %d user vectors into %s', len(user_id_map), index_name)
