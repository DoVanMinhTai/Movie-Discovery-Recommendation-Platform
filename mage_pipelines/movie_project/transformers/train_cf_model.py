"""CF Flow - Block 2: Train SVD (explicit) + ALS (implicit) and blend scores.

Pipeline:
  1. Train SVD with the `surprise` library on explicit ratings (1-5 stars).
  2. Train ALS with the `implicit` library on the implicit interaction matrix
     (confidence built from rating frequency/strength).
  3. For every user, score all candidate movies with both models.
  4. Normalise both score streams to a common 0-1 scale:
        - SVD: linear map of the 1-5 star scale  ->  (score - 1) / (5 - 1)
        - ALS: sklearn MinMaxScaler over the batch of ALS scores -> 0-1
  5. Blend:  final = 0.4 * svd_norm + 0.6 * als_norm
     (implicit watch behaviour is weighted higher than explicit star ratings).
  6. Keep Top-20 movies per user and write data/gold/cf_predictions.csv with
     columns: user_id, media_content_id, score (the blended 0-1 score).
"""
import numpy as np
import pandas as pd
import scipy.sparse as sp
from sklearn.preprocessing import MinMaxScaler

if "transformer" not in globals():
    from mage_ai.data_preparation.decorators import transformer

try:
    from movie_project.utils.paths import gold_dir
except ImportError:
    from utils.paths import gold_dir


TOP_N = 20
SVD_WEIGHT = 0.4
ALS_WEIGHT = 0.6
RATING_MIN = 1.0
RATING_MAX = 5.0


def _train_svd(df):
    """Train surprise SVD on explicit ratings. Returns (algo, trainset)."""
    from surprise import SVD, Dataset, Reader

    reader = Reader(rating_scale=(RATING_MIN, RATING_MAX))
    dataset = Dataset.load_from_df(
        df[["user_id", "media_content_id", "score"]], reader
    )
    trainset = dataset.build_full_trainset()
    algo = SVD(n_factors=100, n_epochs=20, random_state=42)
    algo.fit(trainset)
    return algo


def _train_als(df, user_ids, movie_ids):
    """Train implicit ALS. Returns (model, user_items_csr, maps)."""
    from implicit.als import AlternatingLeastSquares

    user_index = {uid: i for i, uid in enumerate(user_ids)}
    movie_index = {mid: i for i, mid in enumerate(movie_ids)}

    rows = df["user_id"].map(user_index).to_numpy()
    cols = df["media_content_id"].map(movie_index).to_numpy()
    # Confidence: stronger ratings => stronger implicit signal.
    vals = df["score"].to_numpy(dtype=np.float32)

    user_items = sp.csr_matrix(
        (vals, (rows, cols)), shape=(len(user_ids), len(movie_ids))
    )

    model = AlternatingLeastSquares(
        factors=64, regularization=0.05, iterations=15, random_state=42
    )
    model.fit(user_items)
    return model, user_items, user_index, movie_index


def _svd_score(algo, user_id, movie_id):
    return algo.predict(uid=user_id, iid=movie_id).est


@transformer
def train_cf_model(df, *args, **kwargs):
    if df is None or len(df) == 0:
        print("No interactions to train on")
        return pd.DataFrame(columns=["user_id", "media_content_id", "score"])

    top_n = int(kwargs.get("TOP_N", TOP_N))
    user_ids = sorted(df["user_id"].unique().tolist())
    movie_ids = sorted(df["media_content_id"].unique().tolist())

    print(f"Training SVD + ALS on {len(df)} ratings "
          f"({len(user_ids)} users x {len(movie_ids)} movies)")

    svd = _train_svd(df)
    als, user_items, user_index, movie_index = _train_als(df, user_ids, movie_ids)
    movie_ids_arr = np.array(movie_ids)

    # Movies a user has already interacted with (to exclude from recommendations).
    seen = df.groupby("user_id")["media_content_id"].agg(set).to_dict()

    predictions = []
    for user_id in user_ids:
        u_idx = user_index[user_id]
        already = seen.get(user_id, set())
        candidates = [m for m in movie_ids if m not in already]
        if not candidates:
            continue

        # --- SVD scores (explicit) ---
        svd_raw = np.array([_svd_score(svd, user_id, m) for m in candidates])
        # Normalise 1-5 star scale -> 0-1.
        svd_norm = np.clip((svd_raw - RATING_MIN) / (RATING_MAX - RATING_MIN), 0, 1)

        # --- ALS scores (implicit) ---
        cand_idx = np.array([movie_index[m] for m in candidates])
        user_factor = als.user_factors[u_idx]
        als_raw = als.item_factors[cand_idx] @ user_factor
        # MinMaxScaler over this user's ALS batch -> 0-1.
        if np.ptp(als_raw) == 0:
            als_norm = np.zeros_like(als_raw)
        else:
            als_norm = MinMaxScaler().fit_transform(
                als_raw.reshape(-1, 1)
            ).ravel()

        # --- Weighted blend ---
        final = SVD_WEIGHT * svd_norm + ALS_WEIGHT * als_norm

        top_idx = np.argsort(final)[::-1][:top_n]
        for i in top_idx:
            predictions.append(
                {
                    "user_id": int(user_id),
                    "media_content_id": int(candidates[i]),
                    "score": round(float(final[i]), 6),
                }
            )

    result = pd.DataFrame(predictions)
    out_path = gold_dir() / "cf_predictions.csv"
    result.to_csv(out_path, index=False)
    print(f"Wrote {len(result)} predictions (top {top_n}/user) -> {out_path}")
    return result
