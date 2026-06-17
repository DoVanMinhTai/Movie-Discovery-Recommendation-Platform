"""CBF Flow - Block 2: Clean raw crawled movies.

Takes the raw records from the crawl block, normalises fields, drops empties and
duplicates, builds a single text field for embedding, and writes the cleaned set
to data/silver/movies_clean.csv (always overwritten to keep the latest version).
"""
import pandas as pd

if "transformer" not in globals():
    from mage_ai.data_preparation.decorators import transformer

try:
    from movie_project.utils.paths import silver_dir
except ImportError:
    from utils.paths import silver_dir


def _normalise_genres(value):
    if isinstance(value, list):
        return ", ".join([str(g).strip() for g in value if str(g).strip()])
    return str(value or "").strip()


@transformer
def clean_movies_data(data, *args, **kwargs):
    if not data:
        print("No raw movies received, returning empty frame")
        return pd.DataFrame()

    df = pd.DataFrame(data)

    # media_content_id is the canonical id used across Postgres + Elasticsearch.
    # We use the MovieLens id when available (matches the original crawler).
    if "movie_lens_id" in df.columns:
        df["media_content_id"] = df["movie_lens_id"]
    else:
        df["media_content_id"] = df["tmdb_id"]

    df["genres"] = df["genres"].apply(_normalise_genres)

    for col in ["title", "overview", "director", "cast", "original_title",
                "original_language", "poster_path", "backdrop_path",
                "release_date", "status", "trailer_key", "video_url"]:
        if col not in df.columns:
            df[col] = ""
        df[col] = df[col].fillna("").astype(str).str.strip()

    for col in ["tmdb_vote", "vote_count", "popularity", "runtime"]:
        if col not in df.columns:
            df[col] = None
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Drop rows without a title and de-duplicate on the canonical id.
    df = df[df["title"] != ""]
    df = df.drop_duplicates(subset=["media_content_id"]).reset_index(drop=True)

    # Single text blob used to build the CBF embedding downstream.
    def _content(row):
        parts = [row["title"]]
        if row["genres"]:
            parts.append(f"Genres: {row['genres']}")
        if row["director"]:
            parts.append(f"Director: {row['director']}")
        if row["cast"]:
            parts.append(f"Cast: {row['cast']}")
        if row["overview"]:
            parts.append(f"Plot: {row['overview']}")
        return ". ".join(parts)

    df["content"] = df.apply(_content, axis=1)

    out_path = silver_dir() / "movies_clean.csv"
    df.to_csv(out_path, index=False)  # overwrite to keep the latest snapshot
    print(f"Cleaned {len(df)} movies -> {out_path}")

    return df
