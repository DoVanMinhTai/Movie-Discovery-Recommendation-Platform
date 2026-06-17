"""CF Flow - Block 1: Load user-item interactions (ratings) from PostgreSQL.

Reads from the real `ratings` table (see backup_movieDatabase_final.sql):

    ratings(score, created_at, id, mediacontent_id, user_id, comment)

Returns a tidy dataframe with columns: user_id, media_content_id, score.
This single dataframe feeds both the SVD (explicit) and ALS (implicit) models.
"""
import pandas as pd
from sqlalchemy import create_engine

if "data_loader" not in globals():
    from mage_ai.data_preparation.decorators import data_loader

try:
    from movie_project.utils.paths import database_url
except ImportError:
    from utils.paths import database_url


@data_loader
def load_interactions(*args, **kwargs):
    engine = create_engine(database_url())
    query = """
        SELECT user_id,
               mediacontent_id AS media_content_id,
               score
        FROM ratings
        WHERE user_id IS NOT NULL
          AND mediacontent_id IS NOT NULL
          AND score IS NOT NULL
    """
    df = pd.read_sql(query, engine)
    df["user_id"] = df["user_id"].astype(int)
    df["media_content_id"] = df["media_content_id"].astype(int)
    df["score"] = pd.to_numeric(df["score"], errors="coerce")
    df = df.dropna(subset=["score"]).reset_index(drop=True)

    print(f"Loaded {len(df)} ratings, "
          f"{df['user_id'].nunique()} users, "
          f"{df['media_content_id'].nunique()} movies")
    return df
