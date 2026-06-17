"""CBF Flow - Block 1: Crawl raw movie data from TMDB.

Reads MovieLens links to know which TMDB ids to fetch, calls TMDB, and caches
the raw payload to data/bronze/raw_movies.json (bronze layer / temp cache).

Environment variables:
    TMDB_API_KEY   (required) - TMDB v3 api key
    CRAWL_LIMIT    (optional) - max number of titles to crawl per run (default 200)
    MOVIELENS_DIR  (optional) - folder containing links.csv (default data/movielens)
"""
import json
import os
import time

import pandas as pd
import requests

if "custom" not in globals():
    from mage_ai.data_preparation.decorators import custom

try:
    from movie_project.utils.paths import bronze_dir, data_dir
except ImportError:
    from utils.paths import bronze_dir, data_dir


BASE_URL = "https://api.themoviedb.org/3"


def _clean(value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    return str(value).strip()


def _get(url, timeout=5):
    try:
        resp = requests.get(url, timeout=timeout)
        if resp.status_code == 200:
            return resp.json()
    except Exception as exc:  # noqa: BLE001 - network best effort
        print(f"TMDB call failed: {exc}")
    return None


def _format_movie(data, tmdb_id):
    videos = data.get("videos", {}).get("results", [])
    trailer_key = next(
        (v["key"] for v in videos if v.get("type") == "Trailer" and v.get("site") == "YouTube"),
        None,
    )
    credits = data.get("credits", {})
    cast_names = [c["name"] for c in credits.get("cast", [])[:5]]
    directors = [c["name"] for c in credits.get("crew", []) if c.get("job") == "Director"]

    return {
        "tmdb_id": tmdb_id,
        "type": "MOVIE",
        "title": _clean(data.get("title")),
        "original_title": _clean(data.get("original_title")),
        "overview": _clean(data.get("overview")),
        "release_date": _clean(data.get("release_date")),
        "poster_path": _clean(data.get("poster_path")),
        "backdrop_path": _clean(data.get("backdrop_path")),
        "tmdb_vote": data.get("vote_average"),
        "vote_count": data.get("vote_count"),
        "popularity": data.get("popularity"),
        "status": _clean(data.get("status")),
        "original_language": _clean(data.get("original_language")),
        "genres": [g["name"] for g in data.get("genres", [])],
        "runtime": data.get("runtime"),
        "cast": ", ".join(cast_names),
        "director": ", ".join(directors),
        "trailer_key": trailer_key or "",
        "video_url": f"https://vidsrc.to/embed/movie/{tmdb_id}",
    }


@custom
def load_raw_movies(*args, **kwargs):
    api_key = os.getenv("TMDB_API_KEY")
    if not api_key:
        raise ValueError("TMDB_API_KEY is not set in the environment")

    limit = int(kwargs.get("CRAWL_LIMIT", os.getenv("CRAWL_LIMIT", 200)))
    movielens_dir = kwargs.get("MOVIELENS_DIR", os.getenv("MOVIELENS_DIR"))
    if movielens_dir:
        links_path = os.path.join(movielens_dir, "links.csv")
    else:
        links_path = str(data_dir() / "movielens" / "links.csv")

    df_links = pd.read_csv(links_path).dropna(subset=["tmdbId"])
    df_links["tmdbId"] = df_links["tmdbId"].astype(int)
    df_links = df_links.head(limit)

    records = []
    for _, row in df_links.iterrows():
        tmdb_id = int(row["tmdbId"])
        movie_lens_id = int(row["movieId"])
        data = _get(f"{BASE_URL}/movie/{tmdb_id}?api_key={api_key}&append_to_response=videos,credits")
        if data and data.get("title"):
            item = _format_movie(data, tmdb_id)
            item["movie_lens_id"] = movie_lens_id
            records.append(item)
            print(f"Crawled: {item['title']}")
        time.sleep(0.1)

    out_path = bronze_dir() / "raw_movies.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False)

    print(f"Saved {len(records)} raw movies to {out_path}")
    return records
