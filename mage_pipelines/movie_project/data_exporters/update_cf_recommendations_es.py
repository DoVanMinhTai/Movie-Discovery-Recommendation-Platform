"""CF Flow - Block 3: Push CF recommendations into Elasticsearch (per-movie).

The training block produces Top-N movies per user. The app stores the data
per-movie -> list of users, so here we invert the table:

    grouped by media_content_id:
        cf_recommendations = [
            {"user_id": "991",  "score": 0.95},
            {"user_id": "1002", "score": 0.78},
            ...
        ]

Each movie document in the `media_contents` index is updated (doc_as_upsert)
so the CBF embedding written by the other flow is preserved.
"""
import pandas as pd
from elasticsearch import Elasticsearch, helpers

if "data_exporter" not in globals():
    from mage_ai.data_preparation.decorators import data_exporter

try:
    from movie_project.utils.paths import es_url, ES_INDEX
except ImportError:
    from utils.paths import es_url, ES_INDEX


@data_exporter
def update_cf_recommendations_es(df, *args, **kwargs):
    if df is None or len(df) == 0:
        print("No CF predictions to push")
        return df

    es = Elasticsearch([es_url()], request_timeout=60)

    # Invert: per-movie list of {user_id, score}, sorted by score desc.
    def _build_recs(group):
        ordered = group.sort_values("score", ascending=False)
        return [
            {"user_id": str(int(r.user_id)), "score": float(r.score)}
            for r in ordered.itertuples()
        ]

    grouped = df.groupby("media_content_id", group_keys=False)

    def doc_generator():
        for movie_id, group in grouped:
            yield {
                "_op_type": "update",
                "_index": ES_INDEX,
                "_id": str(int(movie_id)),
                "doc": {"cf_recommendations": _build_recs(group)},
                "doc_as_upsert": True,
            }

    success, errors = helpers.bulk(es, doc_generator(), chunk_size=500, max_retries=3)
    if errors:
        print(f"{len(errors)} errors during CF update; first: {errors[:3]}")
    print(f"Updated cf_recommendations for {success} movies in '{ES_INDEX}'")
    return df
