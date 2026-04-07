import pandas as pd
import os
import re
from sqlalchemy import create_engine
import traceback
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
ETL_DIR = os.path.join(DATA_DIR, 'etl')
EXTRACTED_DATA_DIR = os.path.join(ETL_DIR, 'extracted')

DB_URL = ""

def auto_import_data():
    try:
        file_path = os.path.join(EXTRACTED_DATA_DIR, 'mediacontent.csv')
        file_path_media_genres = os.path.join(EXTRACTED_DATA_DIR, 'media_genres.csv')
        file_path_series = os.path.join(EXTRACTED_DATA_DIR, 'series.csv')
        file_path_season = os.path.join(EXTRACTED_DATA_DIR, 'seasons.csv')
        file_path_episode = os.path.join(EXTRACTED_DATA_DIR, 'episodes.csv')
        print(f"--- Đang đọc dữ liệu từ: {file_path}")
        df = pd.read_csv(file_path)
        df_media_genres = pd.read_csv(file_path_media_genres)
        # joined_df = pd.merge(df, df_media_genres, on='movieId', how='left')
        df_series = pd.read_csv(file_path_series)
        df_season = pd.read_csv(file_path_season)
        df_episode = pd.read_csv(file_path_episode)
        df_movies = pd.read_csv(os.path.join(EXTRACTED_DATA_DIR, 'movies.csv'))
        print("--- Đang dọn dẹp dữ liệu...")
        def clean_line_breaks(text):
            if isinstance(text, str):
               return re.sub(r'[\r\n]+', ' ', text).strip()
            return text
        
        # df = df.map(clean_line_breaks)
        # df.drop_duplicates(subset=['movieId'], keep='first', inplace=True)
        df.columns = [re.sub(r'(?<!^)(?=[A-Z])', '_', c).lower() for c in df.columns]
        df_media_genres = df_media_genres.map(clean_line_breaks)
        df_media_genres.columns = [re.sub(r'(?<!^)(?=[A-Z])', '_', c).lower() for c in df_media_genres.columns]
        df_series = df_series.map(clean_line_breaks)
        df_series.columns = [re.sub(r'(?<!^)(?=[A-Z])', '_', c).lower() for c in df_series.columns]
        df_season = df_season.map(clean_line_breaks)
        df_season.columns = [re.sub(r'(?<!^)(?=[A-Z])', '_', c).lower() for c in df_season.columns]
        df_episode = df_episode.map(clean_line_breaks)
        df_episode.columns = [re.sub(r'(?<!^)(?=[A-Z])', '_', c).lower() for c in df_episode.columns]
        df_movies = df_movies.map(clean_line_breaks)
        df_movies.columns = [re.sub(r'(?<!^)(?=[A-Z])', '_', c).lower() for c in df_movies.columns]
        engine = create_engine(DB_URL)
        
        # print(f"--- Đang import {len(df)} dòng vào table 'mediacontent'...")
        
        # df.to_sql('mediacontent', engine, if_exists='append', index=False)
        # df_media_genres.to_sql('mediacontent_genres', engine, if_exists='append', index=False)
        # df_series.to_sql('series', engine, if_exists='append', index=False)
        # df_season.to_sql('seasons', engine, if_exists='append', index=False)
        # df_episode.to_sql('episodes', engine, if_exists='append', index=False)
        df_movies.to_sql('movies', engine, if_exists='append', index=False)
        print("Thành công! Dữ liệu đã nằm gọn trong Database.")

    except Exception as e:
        print(f"Có lỗi xảy ra: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    auto_import_data()