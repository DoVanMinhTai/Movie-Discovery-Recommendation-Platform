import pandas as pd
import os

# Paths
BASE_DIR = r"F:\project_SW\Media-Recommender-System\data-enrichment"
MOVIE_LENS_CSV = os.path.join(BASE_DIR, "data", "movielens", "movies.csv")
LINKS_CSV = os.path.join(BASE_DIR, "data", "movielens", "links.csv")
# Use the latest extracted folder or specify yours
EXTRACTED_CSV = os.path.join(BASE_DIR, "data", "etl", "extracted", "20260408", "mediacontent.csv")

def check_missing_ids():
    # 1. Load Source (MovieLens)
    df_movies = pd.read_csv(MOVIE_LENS_CSV)
    df_links = pd.read_csv(LINKS_CSV)
    
    # We only care about movies that HAVE a tmdbId (since we can only crawl those)
    df_source = pd.merge(df_movies, df_links, on='movieId')
    df_source = df_source.dropna(subset=['tmdbId'])
    source_ids = set(df_source['movieId'].unique())
    
    print(f"Total valid movies in MovieLens (with TMDB ID): {len(source_ids)}")

    # 2. Load Crawled Data
    if not os.path.exists(EXTRACTED_CSV):
        print(f"Error: {EXTRACTED_CSV} not found.")
        return

    df_crawled = pd.read_csv(EXTRACTED_CSV)
    # Note: In your current mediacontent.csv, 'media_content_id' contains tmdbIds.
    # After the patch, new entries will have MovieLens IDs.
    # To truly sync, we need to find which MovieLens IDs are missing.
    crawled_ids = set(df_crawled['media_content_id'].unique())
    print(f"Total movies in mediacontent.csv: {len(crawled_ids)}")

    # 3. Find Gaps
    missing_ids = source_ids - crawled_ids
    print(f"Number of missing movies: {len(missing_ids)}")

    if missing_ids:
        print(f"Sample missing IDs: {list(missing_ids)[:10]}")
        # Optionally save to a file for the crawler to use
        # pd.Series(list(missing_ids)).to_csv("missing_ids.csv", index=False)
    else:
        print("Everything is synced!")

if __name__ == "__main__":
    check_missing_ids()
