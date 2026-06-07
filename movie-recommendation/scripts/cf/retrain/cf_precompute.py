import os
import pandas as pd
import numpy as np
import pickle
from surprise import SVD, Dataset, Reader, accuracy
from sqlalchemy import create_engine
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("SVDRetrain")

load_dotenv()

class SVDRetrainer:
    def __init__(self):
        db_url = os.getenv("DB_URL") or os.getenv("DATABASE_URL")
        self.engine = create_engine(db_url)
        self.params = {
            'n_epochs': 20,
            'lr_all': 0.005,
            'reg_all': 0.4,
            'n_factors': 100 
        }

    def fetch_data(self) -> pd.DataFrame:
        logger.info("Step 1: Fetching ratings from database...")
        query = "SELECT user_id, mediacontent_id as movie_id, score as rating FROM ratings"
        return pd.read_sql(query, self.engine)

    def train_svd(self, df: pd.DataFrame):
        logger.info("Step 2: Training SVD model with optimized parameters...")
        reader = Reader(rating_scale=(1, 10)) 
        data = Dataset.load_from_df(df[['user_id', 'movie_id', 'rating']], reader)
        trainset = data.build_full_trainset()

        algo = SVD(
            n_factors=self.params['n_factors'],
            n_epochs=self.params['n_epochs'],
            lr_all=self.params['lr_all'],
            reg_all=self.params['reg_all'],
            verbose=True
        )
        
        algo.fit(trainset)
        return algo, trainset

    def export_item_factors(self, algo, trainset):
        logger.info("Step 3: Exporting Item Factors (qi matrix)...")
        item_factors = algo.qi 
        movie_vectors = {}

        for inner_id in trainset.all_items():
            raw_id = trainset.to_raw_id(inner_id)
            vector = item_factors[inner_id].tolist()
            movie_vectors[raw_id] = vector
        
        return movie_vectors

    def save_vectors_locally(self, movie_vectors):
        with open("item_vectors.pkl", "wb") as f:
            pickle.dump(movie_vectors, f)
        logger.info(f"Successfully exported {len(movie_vectors)} item vectors.")

    def run(self):
        try:
            df = self.fetch_data()
            if df.empty:
                logger.warning("No data found in ratings table.")
                return

            algo, trainset = self.train_svd(df)
            movie_vectors = self.export_item_factors(algo, trainset)
            self.save_vectors_locally(movie_vectors)
            
            logger.info("SVD Training and Vector Export completed successfully!")
        except Exception as e:
            logger.error(f"Error in SVD Pipeline: {e}")

if __name__ == "__main__":
    trainer = SVDRetrainer()
    trainer.run()
