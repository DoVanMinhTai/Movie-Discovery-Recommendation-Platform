import numpy as np
import scipy.sparse as sp
import pandas as pd
from typing import Tuple, Dict
import logging


class RatingMatrixBuilder:
    """Build user-movie interaction sparse matrix from events DataFrame.

    Expected `events_df` columns: [user_id, movie_id, rating]
    Returns: (csr_matrix, user_id_map, movie_id_map)
    """

    def __init__(self, min_interactions: int = 1):
        self.min_interactions = min_interactions
        self.logger = logging.getLogger(__name__)
        self.user_id_map: Dict[str, int] = {}
        self.movie_id_map: Dict[str, int] = {}
        self.reverse_user_map: Dict[int, str] = {}
        self.reverse_movie_map: Dict[int, str] = {}

    def build_matrix(self, events_df: pd.DataFrame) -> Tuple[sp.csr_matrix, Dict[str, int], Dict[str, int]]:
        # Filter
        events_df = events_df.copy()
        if 'rating' not in events_df.columns:
            # create implicit weight column
            events_df['rating'] = 1.0

        user_counts = events_df['user_id'].value_counts()
        movie_counts = events_df['movie_id'].value_counts()

        valid_users = user_counts[user_counts >= self.min_interactions].index.tolist()
        valid_movies = movie_counts[movie_counts >= self.min_interactions].index.tolist()

        events_df = events_df[events_df['user_id'].isin(valid_users) & events_df['movie_id'].isin(valid_movies)]

        # Build maps
        self.user_id_map = {uid: i for i, uid in enumerate(sorted(valid_users))}
        self.movie_id_map = {mid: i for i, mid in enumerate(sorted(valid_movies))}
        self.reverse_user_map = {i: uid for uid, i in self.user_id_map.items()}
        self.reverse_movie_map = {i: mid for mid, i in self.movie_id_map.items()}

        rows = events_df['user_id'].map(self.user_id_map).astype(int).to_numpy()
        cols = events_df['movie_id'].map(self.movie_id_map).astype(int).to_numpy()
        data = events_df['rating'].astype(float).to_numpy()

        num_users = len(self.user_id_map)
        num_movies = len(self.movie_id_map)

        if num_users == 0 or num_movies == 0:
            self.logger.warning('No users or movies after filtering')
            mat = sp.csr_matrix((0, 0))
            return mat, self.user_id_map, self.movie_id_map

        mat = sp.csr_matrix((data, (rows, cols)), shape=(num_users, num_movies))
        sparsity = 1.0 - (mat.nnz / float(num_users * num_movies))
        self.logger.info('Built matrix %dx%d nnz=%d sparsity=%.4f', num_users, num_movies, mat.nnz, sparsity)

        return mat, self.user_id_map, self.movie_id_map

    def get_user_id(self, idx: int) -> str:
        return self.reverse_user_map.get(idx)

    def get_movie_id(self, idx: int) -> str:
        return self.reverse_movie_map.get(idx)
