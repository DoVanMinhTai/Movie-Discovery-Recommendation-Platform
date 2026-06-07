import pandas as pd
import os
import re
from sqlalchemy import create_engine, text
import traceback
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
ETL_DIR = os.path.join(DATA_DIR, 'etl')
MOVIE_DATA_DIR = os.path.join(DATA_DIR, 'movielens')
EXTRACTED_DATA_DIR = os.path.join(ETL_DIR, 'extracted')
# folder_name = datetime.now().strftime("%Y%m%d")
folder_name = '20260508'  # Sử dụng folder tạm thời để test
SESSION_DIR = os.path.join(EXTRACTED_DATA_DIR, folder_name)
DB_URL = os.getenv("DB_URL")

def auto_import_data():
    if not DB_URL:
        print("Lỗi: Không tìm thấy DB_URL trong file .env")
        return

    try:
        file_path = os.path.join(SESSION_DIR, 'mediacontent.csv')
        file_path_media_genres = os.path.join(SESSION_DIR, 'media_genres.csv')
        file_path_series = os.path.join(SESSION_DIR, 'series.csv')
        file_path_season = os.path.join(SESSION_DIR, 'seasons.csv')
        file_path_episode = os.path.join(SESSION_DIR, 'episodes.csv')
        file_path_genres = os.path.join(MOVIE_DATA_DIR, 'genres.csv')

        print(f"--- Đang đọc dữ liệu từ: {file_path}")

        df = pd.read_csv(file_path)
        df_media_genres = pd.read_csv(file_path_media_genres)
        df_series = pd.read_csv(file_path_series)
        df_season = pd.read_csv(file_path_season)
        df_episode = pd.read_csv(file_path_episode)
        df_movies = pd.read_csv(os.path.join(SESSION_DIR, 'movies.csv'))
        df_genres = pd.read_csv(file_path_genres)
        
        print("--- Đang dọn dẹp dữ liệu...")

        def clean_line_breaks(text):
            if isinstance(text, str):
               return re.sub(r'[\r\n]+', ' ', text).strip()
            return text
        
        # Xóa trùng lặp
        df.drop_duplicates(subset=['mediaContentId'], keep='first', inplace=True)
        df_movies.drop_duplicates(subset=['media_content_id'], keep='first', inplace=True)
        df_series.drop_duplicates(subset=['media_content_id'], keep='first', inplace=True)
        df_season.drop_duplicates(subset=['id'], keep='first', inplace=True)
        df_episode.drop_duplicates(subset=['id'], keep='first', inplace=True)

        # Chuẩn hóa tên cột và làm sạch text
        def process_df(df_target):
            df_target = df_target.map(clean_line_breaks)
            df_target.columns = [re.sub(r'(?<!^)(?=[A-Z])', '_', c).lower() for c in df_target.columns]
            return df_target

        df = process_df(df)
        df_series = process_df(df_series)
        df_season = process_df(df_season)
        df_episode = process_df(df_episode)
        df_movies = process_df(df_movies)
        df_genres = process_df(df_genres)
        
        # Kết nối DB và import
        engine = create_engine(DB_URL)
        # with engine.connect() as conn:
        #     # Thực hiện xóa bảng và tất cả các ràng buộc liên quan
        #     conn.execute(text("DROP TABLE IF EXISTS mediacontent CASCADE"))
        #     conn.commit()
        df_genres.to_sql('genres', engine, if_exists='append', index=False)
        df.to_sql('mediacontent', engine, if_exists='append', index=False)
        df_media_genres.to_sql('mediacontent_genres', engine, if_exists='append', index=False)
        df_series.to_sql('series', engine, if_exists='append', index=False)
        df_season.to_sql('seasons', engine, if_exists='append', index=False)
        df_episode.to_sql('episodes', engine, if_exists='append', index=False)
        df_movies.to_sql('movies', engine, if_exists='append', index=False)
        
        print("✅ Thành công! Dữ liệu đã được import vào Database.")

    except Exception as e:
        print(f"❌ Có lỗi xảy ra: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    auto_import_data()
