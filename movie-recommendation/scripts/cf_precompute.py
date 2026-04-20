import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy import create_engine
import time
from typing import List, Tuple

class CFPrecompute:
    def __init__(self, db_url: str):
        self.engine = create_engine(db_url)
        
    def load_ratings(self) -> pd.DataFrame:
        query = "SELECT user_id, movie_id, rating FROM ratings"
        return pd.read_sql(query, self.engine)
    
    def compute_item_similarity(self, ratings_df: pd.DataFrame, top_k: int = 100) -> List[Tuple]:
        print("Creating ratings matrix...")
        ratings_matrix = ratings_df.pivot_table(
            index='user_id',
            columns='movie_id',
            values='rating',
            fill_value=0
        )
        
        print(f"Matrix shape: {ratings_matrix.shape}")
        print("Computing cosine similarity...")
        
        item_similarity = cosine_similarity(ratings_matrix.T)
        
        print("Extracting top-K similar items...")
        similarities = []
        movie_ids = ratings_matrix.columns.tolist()
        
        for i, movie_id_1 in enumerate(movie_ids):
            sim_scores = item_similarity[i]
            
            top_indices = np.argsort(sim_scores)[::-1][1:top_k+1]
            
            for j in top_indices:
                movie_id_2 = movie_ids[j]
                similarity = float(sim_scores[j])
                
                if similarity > 0.01:
                    similarities.append((movie_id_1, movie_id_2, similarity))
            
            if (i + 1) % 1000 == 0:
                print(f"Processed {i+1}/{len(movie_ids)} movies...")
        
        return similarities
    
    def batch_insert_similarities(self, similarities: List[Tuple], method: str = 'item_cf', batch_size: int = 10000):
        print(f"Inserting {len(similarities)} similarity pairs...")
        
        with self.engine.connect() as conn:
            conn.execute(f"DELETE FROM item_similarity WHERE method = '{method}'")
            conn.commit()
        
        df = pd.DataFrame(similarities, columns=['movie_id_1', 'movie_id_2', 'similarity'])
        df['method'] = method
        
        for i in range(0, len(df), batch_size):
            batch = df[i:i+batch_size]
            batch.to_sql('item_similarity', self.engine, if_exists='append', index=False)
            print(f"Inserted {min(i+batch_size, len(df))}/{len(df)} rows...")
        
        print("Insert complete!")
    
    def save_metadata(self, method: str, total_items: int, total_pairs: int, avg_sim: float, compute_time: int):
        metadata = pd.DataFrame([{
            'method': method,
            'total_items': total_items,
            'total_pairs': total_pairs,
            'avg_similarity': avg_sim,
            'computation_time_seconds': compute_time
        }])
        metadata.to_sql('cf_metadata', self.engine, if_exists='append', index=False)
    
    def run_full_precompute(self, top_k: int = 100):
        """Run full pre-computation pipeline"""
        start_time = time.time()
        
        print("Loading ratings...")
        ratings_df = self.load_ratings()
        print(f"Loaded {len(ratings_df)} ratings")
        
        similarities = self.compute_item_similarity(ratings_df, top_k)
        
        total_items = ratings_df['movie_id'].nunique()
        total_pairs = len(similarities)
        avg_sim = np.mean([s[2] for s in similarities])
        
        self.batch_insert_similarities(similarities, method='item_cf')
        
        compute_time = int(time.time() - start_time)
        self.save_metadata('item_cf', total_items, total_pairs, avg_sim, compute_time)
        
        print(f"\n=== Pre-computation Complete ===")
        print(f"Total items: {total_items}")
        print(f"Total pairs: {total_pairs}")
        print(f"Avg similarity: {avg_sim:.4f}")
        print(f"Computation time: {compute_time}s")


def main():
    # Should use Elastic Search Or PostgreSQL connection string from environment variable or config
    # DB_URL = "postgresql://user:password@localhost:5432/movie_recommender"
    DB_URL = os.getenv("DB_URL")
    
    cf = CFPrecompute(DB_URL)
    
    cf.run_full_precompute(top_k=100)


if __name__ == "__main__":
    main()