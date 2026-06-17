# Mage Pipelines for Media Recommender

Project: `movie_project`. Two independent flows that both write into the
`media_contents` Elasticsearch index (one document per movie).

## Data layout (medallion)

```
data/
├── bronze/               # Raw crawl cache (temporary)
│   └── raw_movies.json
├── silver/               # Cleaned data for CBF (overwritten each run)
│   └── movies_clean.csv
└── gold/                 # Model outputs
    ├── cbf_embeddings.npy # Backup of the CBF embedding matrix
    └── cf_predictions.csv # Top-20 CF recommendations per user
```

## Elasticsearch document shape (`media_contents`)

```json
{
  "movie_id": "105",
  "title": "Inception",
  "genres": "Action, Sci-Fi",
  "plot": "A thief who steals corporate secrets...",
  "director": "Christopher Nolan",
  "embedding": [0.023, -0.045, 0.112, "..."],
  "cf_recommendations": [
    { "user_id": "991",  "score": 0.95 },
    { "user_id": "1002", "score": 0.78 }
  ]
}
```

Both flows use `doc_as_upsert`, so the CBF flow never wipes `cf_recommendations`
and the CF flow never wipes the `embedding`.

## Flow 1 — CBF (`movie_cbf_pipeline`)

`load_raw_movies` (crawl TMDB → `bronze/raw_movies.json`)
→ `clean_movies_data` (clean → `silver/movies_clean.csv`)
→ `upsert_movies_postgres` (upsert into `mediacontent` — source of truth)
→ `index_cbf_embeddings_es` (SBERT embeddings → `gold/cbf_embeddings.npy` + index to ES)

## Flow 2 — CF (`movie_cf_pipeline`)

`load_interactions` (read `ratings` from Postgres)
→ `train_cf_model` (train SVD with `surprise` + ALS with `implicit`)
→ `update_cf_recommendations_es` (push per-movie user lists to ES)

### Score blending

Raw SVD (1–5 stars) and raw ALS (unbounded implicit confidence) live on different
scales, so we normalise both to `0–1` before combining:

- **SVD:** `(score - 1) / (5 - 1)`
- **ALS:** sklearn `MinMaxScaler` over each user's candidate batch

Final blended score (implicit weighted higher than explicit):

```
final = 0.4 * svd_norm + 0.6 * als_norm
```

Top-20 movies per user are written to `gold/cf_predictions.csv`, then inverted to
per-movie user lists for Elasticsearch.

## Running

The `mage` service in `docker-compose.yml` mounts `./mage_pipelines` and `./data`
and sets `DATABASE_URL`, `ES_HOST`, `ES_INDEX`, `TMDB_API_KEY`, and `DATA_DIR`.

```bash
docker compose up -d mage
# open http://localhost:6789 and run movie_cbf_pipeline then movie_cf_pipeline
```

Install extra Python deps (SVD/ALS) inside the container if needed:

```bash
pip install -r /home/src/mage_pipelines/movie_project/requirements.txt
```
