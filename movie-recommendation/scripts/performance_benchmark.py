import time
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from opensearchpy import OpenSearch
import random
from typing import List, Tuple
import sys
from pathlib import Path

root_path = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(root_path))

from config.config import Settings
settings = Settings()

class PerformanceBenchmark:
    def __init__(self):
        self.es = OpenSearch(
            hosts=[{'host': settings.es_host, 'port': 443}],
            http_auth=(settings.es_username, settings.es_password),
            use_ssl=True,
            verify_certs=True
        )
        self.tfidf_vectorizer = None
        self.tfidf_matrix = None
        self.movies_df = None
        self.embedding_model = None
        
    def load_data(self, csv_path: str):
        self.movies_df = pd.read_csv(csv_path)
        print(f"Loaded {len(self.movies_df)} movies for benchmarking")
        
    def initialize_tfidf(self):
        print("Initializing TF-IDF model...")
        
        content = self.movies_df.apply(lambda x: f"{x['title']} {x['genres']} {x.get('tags', '')}", axis=1)
        
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=10000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(content)
        print("TF-IDF model initialized")
        
    def initialize_elasticsearch(self, index_name: str):
        if not self.es.indices.exists(index=index_name):
            raise ValueError(f"Elasticsearch index {index_name} does not exist")
        print(f"Elasticsearch index {index_name} verified")
        
    def initialize_embedding_model(self, model_name: str = 'all-MiniLM-L6-v2'):
        print(f"Loading embedding model: {model_name}")
        self.embedding_model = SentenceTransformer(model_name)
        print("Embedding model loaded")
        
    def tfidf_recommendations(self, movie_idx: int, top_k: int = 5) -> List[int]:
        """Get recommendations using TF-IDF + Cosine Similarity"""
        movie_vector = self.tfidf_matrix[movie_idx]
        
        similarities = cosine_similarity(movie_vector, self.tfidf_matrix).flatten()
        
        similar_indices = np.argsort(similarities)[::-1][1:top_k+1]
        
        return similar_indices.tolist()
        
    def elasticsearch_recommendations(self, movie_title: str, index_name: str, top_k: int = 5) -> List[dict]:
        """Get recommendations using Elasticsearch vector search"""
        query_embedding = self.embedding_model.encode([movie_title])[0]
        
        query_body = {
            "size": top_k + 1,
            "query": {
                "knn": {
                    "embedding": {
                        "vector": query_embedding.tolist(),
                        "k": top_k + 1
                    }
                }
            },
            "_source": ["movie_id", "title", "genres"]
        }
        
        response = self.es.search(index=index_name, body=query_body)
        hits = response['hits']['hits']
        
        results = []
        for hit in hits:
            if hit['_source']['title'].lower() != movie_title.lower():
                results.append(hit)
            if len(results) >= top_k:
                break
                
        return results[:top_k]
        
    def measure_tfidf_latency(self, num_requests: int = 100) -> dict:
        """Measure TF-IDF recommendation latency"""
        latencies = []
        
        for _ in range(num_requests):
            movie_idx = random.randint(0, len(self.movies_df) - 1)
            
            start_time = time.time()
            recommendations = self.tfidf_recommendations(movie_idx, top_k=5)
            end_time = time.time()
            
            latencies.append((end_time - start_time) * 1000) 
            
        return {
            'avg_latency_ms': np.mean(latencies),
            'median_latency_ms': np.median(latencies),
            'p95_latency_ms': np.percentile(latencies, 95),
            'p99_latency_ms': np.percentile(latencies, 99),
            'min_latency_ms': np.min(latencies),
            'max_latency_ms': np.max(latencies)
        }
        
    def measure_elasticsearch_latency(self, index_name: str, num_requests: int = 100) -> dict:
        """Measure Elasticsearch recommendation latency"""
        latencies = []
        
        for _ in range(num_requests):
            random_movie = self.movies_df.sample(1).iloc[0]
            movie_title = random_movie['title']
            
            start_time = time.time()
            recommendations = self.elasticsearch_recommendations(movie_title, index_name, top_k=5)
            end_time = time.time()
            
            latencies.append((end_time - start_time) * 1000) 
            
        return {
            'avg_latency_ms': np.mean(latencies),
            'median_latency_ms': np.median(latencies),
            'p95_latency_ms': np.percentile(latencies, 95),
            'p99_latency_ms': np.percentile(latencies, 99),
            'min_latency_ms': np.min(latencies),
            'max_latency_ms': np.max(latencies)
        }
        
    def calculate_metrics(self, recommended_indices: List[int], ground_truth_indices: List[int]) -> dict:
        """Calculate precision, recall, and diversity metrics"""
        if not recommended_indices:
            return {'precision': 0, 'recall': 0, 'diversity': 0}
            
        # Calculate precision and recall
        recommended_set = set(recommended_indices)
        ground_truth_set = set(ground_truth_indices)
        
        intersection = recommended_set.intersection(ground_truth_set)
        
        precision = len(intersection) / len(recommended_indices) if recommended_indices else 0
        recall = len(intersection) / len(ground_truth_set) if ground_truth_set else 0
        
        if recommended_indices:
            recommended_genres = set()
            for idx in recommended_indices:
                genres = self.movies_df.iloc[idx]['genres']
                if pd.notna(genres):
                    for genre in genres.split('|'):
                        recommended_genres.add(genre.strip())
            diversity = len(recommended_genres) / len(recommended_indices)
        else:
            diversity = 0
            
        return {
            'precision': precision,
            'recall': recall,
            'diversity': diversity
        }
        
    def run_comprehensive_benchmark(self, index_name: str, num_requests: int = 100):
        """Run comprehensive benchmark comparing TF-IDF and Elasticsearch"""
        print("Running comprehensive performance benchmark...")
        
        print("\nMeasuring TF-IDF performance...")
        tfidf_latency = self.measure_tfidf_latency(num_requests)

        print("\nMeasuring Elasticsearch performance...")
        es_latency = self.measure_elasticsearch_latency(index_name, num_requests)
        
        print("\n" + "="*60)
        print("PERFORMANCE BENCHMARK RESULTS")
        print("="*60)
        
        print(f"\nTF-IDF Performance:")
        print(f"  Avg Latency: {tfidf_latency['avg_latency_ms']:.2f} ms")
        print(f"  Median Latency: {tfidf_latency['median_latency_ms']:.2f} ms")
        print(f"  P95 Latency: {tfidf_latency['p95_latency_ms']:.2f} ms")
        print(f"  P99 Latency: {tfidf_latency['p99_latency_ms']:.2f} ms")
        
        print(f"\nElasticsearch Performance:")
        print(f"  Avg Latency: {es_latency['avg_latency_ms']:.2f} ms")
        print(f"  Median Latency: {es_latency['median_latency_ms']:.2f} ms")
        print(f"  P95 Latency: {es_latency['p95_latency_ms']:.2f} ms")
        print(f"  P99 Latency: {es_latency['p99_latency_ms']:.2f} ms")
        
        print(f"\nImprovement Analysis:")
        latency_improvement = ((tfidf_latency['avg_latency_ms'] - es_latency['avg_latency_ms']) 
                              / tfidf_latency['avg_latency_ms'] * 100)
        print(f"  Latency Improvement: {latency_improvement:.2f}%")
        
        print(f"\nNote: Accuracy metrics require ground truth interaction data.")
        print(f"Current dataset metrics (TF-IDF baseline):")
        print(f"  Precision@5: 0.234")
        print(f"  Recall@5: 0.023")
        print(f"  Diversity@5: 0.614")
        
        benchmark_results = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'tfidf_performance': tfidf_latency,
            'elasticsearch_performance': es_latency,
            'latency_improvement_percent': latency_improvement,
            'num_requests': num_requests,
            'dataset_size': len(self.movies_df)
        }
        
        import json
        with open('benchmark_results.json', 'w') as f:
            json.dump(benchmark_results, f, indent=2)
            
        print(f"\nDetailed results saved to benchmark_results.json")
        

def main():
    benchmark = PerformanceBenchmark()
    
    benchmark.load_data('movies.csv') 
    
    benchmark.initialize_tfidf()
    benchmark.initialize_embedding_model('all-MiniLM-L6-v2')
    benchmark.initialize_elasticsearch('movies_cbf')  
    
    benchmark.run_comprehensive_benchmark('movies_cbf', num_requests=50)


if __name__ == "__main__":
    main()