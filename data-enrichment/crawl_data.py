from dotenv import load_dotenv
from datetime import datetime
import pandas as pd
import requests
import time
import os
import csv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)
TMDB_API_KEY = os.getenv('TMDB_API_KEY')

if not TMDB_API_KEY:
    raise ValueError("Không tìm thấy TMDB_API_KEY trong file .env")

BASE_URL = "https://api.themoviedb.org/3"

def get_data(url):
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        print(f"Lỗi call API: {e}")
    return None

def process_item(tmdb_id, media_type=None):
    movie_url = f"{BASE_URL}/movie/{tmdb_id}?api_key={TMDB_API_KEY}&append_to_response=videos,credits"
    data = get_data(movie_url)
    if data and 'title' in data:
        item = format_media_content(data, "MOVIE")
        item['videoUrl'] = f'https://vidsrc.to/embed/movie/{tmdb_id}'
        return item
    
    tv_url = f"{BASE_URL}/tv/{tmdb_id}?api_key={TMDB_API_KEY}&append_to_response=videos,credits,seasons"
    data = get_data(tv_url)
    if data and 'name' in data:
            series_info = format_media_content(data, "SERIES")
            series_info['seasons'] = []
            series_info['videoUrl'] = ""
            for s in data.get('seasons', []):
                if s['season_number'] == 0: continue 
                
                season_url = f"{BASE_URL}/tv/{tmdb_id}/season/{s['season_number']}?api_key={TMDB_API_KEY}"
                s_data = get_data(season_url)
                if s_data:
                    season_obj = {
                        "tmdbId": s_data.get('id'),
                        "seasonNumber": s_data.get('season_number'),
                        "name": s_data.get('name'),
                        "episodes": [
                            {
                                "tmdbId": ep.get('id'),
                                "episodeNumber": ep.get('episode_number'),
                                "name": ep.get('name'),
                                "overview": ep.get('overview'),
                                "stillPath": ep.get('still_path'),
                                "videoUrl": f'https://vidsrc.to/embed/tv/{tmdb_id}/{s["season_number"]}/{ep["episode_number"]}'
                            } for ep in s_data.get('episodes', [])
                        ]
                    }
                    series_info['seasons'].append(season_obj)
            return series_info
        
    return None

def format_media_content(data, media_type):
    videos = data.get('videos', {}).get('results', [])
    trailer_key = next((v['key'] for v in videos if v['type'] == 'Trailer' and v['site'] == 'YouTube'), None)
    genres_name = [g['name'] for g in data.get('genres', [])]
    
    credits = data.get('credits', {})
    cast_list = credits.get('cast', [])
    cast_names = [c['name'] for c in cast_list[:5]]

    crew_list = credits.get('crew', [])
    directors = [c['name'] for c in crew_list if c['job'] == 'Director']
    director_name = ", ".join(directors) if directors else ""

    return {
        "tmdbId": clean(data.get('id')),
        "type": media_type,
        "title": clean(data.get('title')) if media_type == "MOVIE" else clean(data.get('name')),
        "originalTitle": clean(data.get('original_title')) if media_type == "MOVIE" else clean(data.get('original_name')),
        "overview": clean(data.get('overview')),
        "releaseDate": clean(data.get('release_date')) if media_type == "MOVIE" else clean(data.get('first_air_date')),
        "posterPath": clean(data.get('poster_path')),
        "backdropPath": clean(data.get('backdrop_path')),
        "voteAverage": clean(data.get('vote_average')),
        "voteCount": clean(data.get('vote_count')),
        "popularity": clean(data.get('popularity')),
        "status": clean(data.get('status')),
        "trailerKey": trailer_key,
        "originalLanguage": clean(data.get('original_language')),
        "genres": genres_name,
        "runtime": clean(data.get('runtime')) if media_type == "MOVIE" else None,
        "cast": ", ".join(cast_names),
        "director": director_name
    }

def clean(value):
    if value is None or pd.isna(value):
        return ""
    return str(value).strip()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
ETL_DIR = os.path.join(DATA_DIR, "etl")
EXTRACTED_DIR = os.path.join(ETL_DIR, "extracted")
MOVIE_LENS_DIR = os.path.join(DATA_DIR, "movielens")  
CHECKPOINT_FILE = os.path.join(ETL_DIR, "checkpoint.txt")

folder_name = datetime.now().strftime("%Y%m%d")
SESSION_DIR = os.path.join(EXTRACTED_DIR, folder_name)

if not os.path.exists(SESSION_DIR):
    os.makedirs(SESSION_DIR)

df_movies = pd.read_csv(os.path.join(MOVIE_LENS_DIR, "movies.csv"))
df_links = pd.read_csv(os.path.join(MOVIE_LENS_DIR, "links.csv"))
df_genres_name = pd.read_csv(os.path.join(MOVIE_LENS_DIR, "genres.csv"))
df_merged = pd.merge(df_movies, df_links, on='movieId', how='left')
df_merged = df_merged.dropna(subset=['tmdbId'])

FILES = {
    'media': os.path.join(SESSION_DIR, "mediacontent.csv"),
    'genres': os.path.join(SESSION_DIR, "genres.csv"),
    'media_genres': os.path.join(SESSION_DIR, "media_genres.csv"),
    'movie': os.path.join(SESSION_DIR, "movies.csv"),
    'series': os.path.join(SESSION_DIR, "series.csv"),
    'seasons': os.path.join(SESSION_DIR, "seasons.csv"),
    'episodes': os.path.join(SESSION_DIR, "episodes.csv"),
}

HEADERS = {
    'media': ['movieId', 'tmdbId', 'title', 'original_title', 'overview', 'release_date', 'poster_path', 'backdrop_path', 'tmdb_vote', 'vote_count', 'popularity', 'dtype','originalLanguage', 'cast', 'director'],
    'genres': ['id', 'name'],
    'media_genres': ['mediaContentId', 'genreId'],
    'movie': ['movieId', 'runtime', 'trailerKey','videoUrl'],
    'series': ['movieId', 'status'],
    'seasons': ['id', 'seasonNumber', 'name', 'series_id'],
    'episodes': ['id', 'episodeNumber', 'title', 'overview', 'stillPath', 'season_id', 'videoUrl'],
}

for key, path in FILES.items():
    if not os.path.exists(path):
        with open(path, 'w', encoding='utf-8', newline='') as f:
            csv.writer(f).writerow(HEADERS[key])

def save_row(file_key, row_data):
    with open(FILES[file_key], 'a', encoding='utf-8', newline='') as f:
        csv.DictWriter(f, fieldnames=HEADERS[file_key]).writerow(row_data)
 
def getGenreIdsByListName(item):
    genre_ids = []
    for _, row in df_genres_name.iterrows():
        if row['name'] in item.get('genres', []):
            genre_ids.append(row['genre_id'])
            print(f"Saving genre mapping: mediaContentId={item['tmdbId']}, genreId={row['genre_id']}, genre_ids={genre_ids}")
            save_row('media_genres', {'mediaContentId': item['tmdbId'], 'genreId': row['genre_id']})
    return genre_ids

def start_crawl():
    processed_ids = set()
    last_processed_id = None
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, 'r') as f:
            lines = f.readlines()
            if lines:
                last_processed_id = lines[-1].strip()

    df_links = pd.read_csv(os.path.join(DATA_DIR, "movielens", "links.csv"))
    df_merged = df_links.dropna(subset=['tmdbId']).copy()
    df_merged['tmdbId'] = df_merged['tmdbId'].astype(int)

    start_index = 0
    if last_processed_id:
        last_id_int = int(last_processed_id)
        matching_indices = df_merged.index[df_merged['tmdbId'] == last_id_int].tolist()
        
        if matching_indices:
            start_index = df_merged.index.get_loc(matching_indices[0]) + 1    
    for _, row in df_merged.iloc[start_index:].iterrows():
        tmdb_id = str(int(row['tmdbId']))

        item = process_item(tmdb_id) 
        
        if item:
            getGenreIdsByListName(item)
            save_row('media', {
                'movieId': item['tmdbId'], 'tmdbId': item['tmdbId'],
                'title': item['title'], 'original_title': item['originalTitle'],
                'overview': item['overview'], 'release_date': item['releaseDate'],
                'poster_path': item['posterPath'], 'backdrop_path': item['backdropPath'],
                'tmdb_vote': item['voteAverage'], 'vote_count': item['voteCount'],
                'popularity': item['popularity'], 'dtype': item['type'], 'originalLanguage': item['originalLanguage'],
                'cast': item['cast'], 'director': item['director']
            })
            if item['type'] == 'MOVIE':
                save_row('movie' , {
                    'movieId': item['tmdbId'],
                    'runtime': item.get('runtime', None),
                    'trailerKey': item['trailerKey'],
                    'videoUrl': item['videoUrl']
                })

            if item['type'] == 'SERIES':
                save_row('series', {'movieId': item['tmdbId'], 'status': item['status']})
                for sn in item.get('seasons', []):
                    save_row('seasons', {'id': sn['tmdbId'], 'seasonNumber': sn['seasonNumber'], 'name': sn['name'], 'series_id': item['tmdbId']})
                    for ep in sn.get('episodes', []):
                        save_row('episodes', {
                            'id': clean(ep['tmdbId']), 'episodeNumber': ep['episodeNumber'],
                            'title': clean(ep['name']), 'overview': clean(ep['overview']),
                            'stillPath': clean(ep['stillPath']), 'season_id': clean(sn['tmdbId']),
                            'videoUrl': clean(ep['videoUrl'])
                        })
            
            with open(CHECKPOINT_FILE, 'a') as f: f.write(f"{tmdb_id}\n")
            print(f"Done: {item['title']}")
            print(f"Processed Index {start_index}: {item['title']}")
            start_index += 1
            time.sleep(0.1)

if __name__ == "__main__":
    start_crawl()