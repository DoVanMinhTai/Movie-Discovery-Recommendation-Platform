"""CBF Flow - Block 3: Upsert cleaned movies into PostgreSQL.

We upsert into the real `mediacontent` table (see backup_movieDatabase_final.sql)
before anything is pushed to Elasticsearch, so Postgres stays the source of truth.
The cleaned dataframe flows through unchanged so the next block can build vectors.
"""
import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text

if "data_exporter" not in globals():
    from mage_ai.data_preparation.decorators import data_exporter

try:
    from movie_project.utils.paths import database_url
except ImportError:
    from utils.paths import database_url


# Columns of public.mediacontent we manage from the CBF flow.
_UPSERT_SQL = text(
    """
    INSERT INTO mediacontent (
        media_content_id, tmdb_id, title, original_title, overview,
        release_date, poster_path, backdrop_path, tmdb_vote, vote_count,
        popularity, dtype, original_language, "cast", director,
        is_deleted, movie_lens_id
    ) VALUES (
        :media_content_id, :tmdb_id, :title, :original_title, :overview,
        :release_date, :poster_path, :backdrop_path, :tmdb_vote, :vote_count,
        :popularity, :dtype, :original_language, :cast, :director,
        false, :movie_lens_id
    )
    ON CONFLICT (media_content_id) DO UPDATE SET
        tmdb_id = EXCLUDED.tmdb_id,
        title = EXCLUDED.title,
        original_title = EXCLUDED.original_title,
        overview = EXCLUDED.overview,
        release_date = EXCLUDED.release_date,
        poster_path = EXCLUDED.poster_path,
        backdrop_path = EXCLUDED.backdrop_path,
        tmdb_vote = EXCLUDED.tmdb_vote,
        vote_count = EXCLUDED.vote_count,
        popularity = EXCLUDED.popularity,
        original_language = EXCLUDED.original_language,
        "cast" = EXCLUDED."cast",
        director = EXCLUDED.director,
        movie_lens_id = EXCLUDED.movie_lens_id
    """
)


def _ensure_unique_constraint(conn):
    # media_content_id has no PK/unique constraint in the dump, but ON CONFLICT
    # needs one. Create it once (idempotent) so upserts work reliably.
    conn.execute(
        text(
            """
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_constraint WHERE conname = 'mediacontent_media_content_id_key'
                ) THEN
                    ALTER TABLE mediacontent
                    ADD CONSTRAINT mediacontent_media_content_id_key UNIQUE (media_content_id);
                END IF;
            END$$;
            """
        )
    )


@data_exporter
def upsert_movies_postgres(df, *args, **kwargs):
    if df is None or len(df) == 0:
        print("No movies to upsert")
        return df

    engine = create_engine(database_url())
    df = df.replace({np.nan: None})

    rows = []
    for _, row in df.iterrows():
        rows.append(
            {
                "media_content_id": int(row["media_content_id"]),
                "tmdb_id": int(row["tmdb_id"]) if row.get("tmdb_id") not in (None, "") else None,
                "title": row.get("title"),
                "original_title": row.get("original_title"),
                "overview": row.get("overview"),
                "release_date": row.get("release_date"),
                "poster_path": row.get("poster_path"),
                "backdrop_path": row.get("backdrop_path"),
                "tmdb_vote": row.get("tmdb_vote"),
                "vote_count": int(row["vote_count"]) if row.get("vote_count") not in (None, "") else None,
                "popularity": row.get("popularity"),
                "dtype": row.get("type") or "MOVIE",
                "original_language": row.get("original_language"),
                "cast": row.get("cast"),
                "director": row.get("director"),
                "movie_lens_id": int(row["movie_lens_id"]) if row.get("movie_lens_id") not in (None, "") else None,
            }
        )

    with engine.begin() as conn:
        _ensure_unique_constraint(conn)
        conn.execute(_UPSERT_SQL, rows)

    print(f"Upserted {len(rows)} movies into Postgres (mediacontent)")
    return df
