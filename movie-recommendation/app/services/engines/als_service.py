import numpy as np
import scipy.sparse as sp
from typing import Tuple
import logging
from datetime import datetime


class ALSService:
    """Simple ALS implementation for implicit/explicit feedback.

    Note: This is a baseline implementation intended for small-to-medium datasets.
    For large-scale workloads prefer Spark ALS or implicit library.
    """

    def __init__(self, num_factors: int = 128, num_iterations: int = 10, reg: float = 0.1):
        self.num_factors = num_factors
        self.num_iterations = num_iterations
        self.reg = reg
        self.logger = logging.getLogger(__name__)

    def factorize(self, rating_matrix: sp.csr_matrix) -> Tuple[np.ndarray, np.ndarray]:
        num_users, num_items = rating_matrix.shape
        self.logger.info('Starting ALS factorization: users=%d items=%d factors=%d', num_users, num_items, self.num_factors)

        # Initialize factors
        user_factors = np.random.normal(scale=1.0 / np.sqrt(self.num_factors), size=(num_users, self.num_factors))
        item_factors = np.random.normal(scale=1.0 / np.sqrt(self.num_factors), size=(num_items, self.num_factors))

        # Precompute identity
        reg_eye = self.reg * np.eye(self.num_factors)

        # Convert to CSR/CSC
        R = rating_matrix.tocsr()
        RT = rating_matrix.tocsc()

        for it in range(self.num_iterations):
            self.logger.info('ALS iteration %d/%d', it + 1, self.num_iterations)

            # Update user factors
            for u in range(num_users):
                row = R[u]
                idx = row.indices
                if idx.size == 0:
                    continue
                V = item_factors[idx]  # (k_u x f)
                ratings = row.data
                A = V.T @ V + reg_eye * (idx.size)
                b = V.T @ ratings
                try:
                    user_factors[u] = np.linalg.solve(A, b)
                except np.linalg.LinAlgError:
                    user_factors[u] = np.linalg.lstsq(A, b, rcond=None)[0]

            # Update item factors
            for i in range(num_items):
                col = RT[:, i]
                idx = col.indices
                if idx.size == 0:
                    continue
                U = user_factors[idx]
                ratings = col.data
                A = U.T @ U + reg_eye * (idx.size)
                b = U.T @ ratings
                try:
                    item_factors[i] = np.linalg.solve(A, b)
                except np.linalg.LinAlgError:
                    item_factors[i] = np.linalg.lstsq(A, b, rcond=None)[0]

        # Normalize factors
        user_norms = np.linalg.norm(user_factors, axis=1, keepdims=True)
        user_norms[user_norms == 0] = 1.0
        user_factors = user_factors / user_norms

        item_norms = np.linalg.norm(item_factors, axis=1, keepdims=True)
        item_norms[item_norms == 0] = 1.0
        item_factors = item_factors / item_norms

        self.logger.info('ALS factorization completed at %s', datetime.now().isoformat())
        return user_factors, item_factors

    def save_factors(self, user_factors: np.ndarray, item_factors: np.ndarray, output_dir: str):
        import os
        os.makedirs(output_dir, exist_ok=True)
        np.save(f"{output_dir}/user_factors.npy", user_factors)
        np.save(f"{output_dir}/item_factors.npy", item_factors)
        self.logger.info('Saved factors to %s', output_dir)
