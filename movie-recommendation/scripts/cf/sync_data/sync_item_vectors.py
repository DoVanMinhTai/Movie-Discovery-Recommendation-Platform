import os
import pickle
import logging
from elasticsearch import Elasticsearch, helpers
from dotenv import load_dotenv

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("VectorSync")

load_dotenv()

class VectorSyncer:
    def __init__(self):
        host = os.getenv("ES_HOST") # Example: https://host:443
        username = os.getenv("ES_USERNAME")
        password = os.getenv("ES_PASSWORD")
        
        # Parse host if it contains https://
        clean_host = host.replace("https://", "").replace("http://", "").split(":")[0]
        
        self.client = Elasticsearch(
            f"https://{clean_host}:443",
            basic_auth=(username, password),
            verify_certs=True,
        )
        self.index_name = "movies_cf"
        self.vector_file = "item_vectors.pkl"

    def create_index_with_mapping(self):
        """Khởi tạo index với field dense_vector để hỗ trợ tìm kiếm vector"""
        logger.info(f"Checking index mapping for: {self.index_name}")
        
        mapping = {
            "settings": {
                "index": {
                    "knn": True,
                    "knn.algo_param.ef_search": 100
                }
            },
            "mappings": {
                "properties": {
                    "movie_id": { "type": "keyword" },
                    "movie_vector": {
                        "type": "knn_vector",
                        "dimension": 100,
                        "method": {
                            "name": "hnsw",
                            "space_type": "cosinesimil",
                            "engine": "nmslib",
                            "parameters": {
                                "ef_construction": 128,
                                "m": 24
                            }
                        }
                    }
                }
            }
        }

        if not self.client.indices.exists(index=self.index_name):
            self.client.indices.create(index=self.index_name, body=mapping)
            logger.info(f"Created index {self.index_name} with KNN mapping.")
        else:
            logger.info(f"Index {self.index_name} already exists.")

    def sync_vectors(self):
        if not os.path.exists(self.vector_file):
            logger.error(f"Vector file {self.vector_file} not found!")
            return

        with open(self.vector_file, "rb") as f:
            movie_vectors = pickle.load(f)

        logger.info(f"Starting sync of {len(movie_vectors)} vectors to Elasticsearch...")

        actions = []
        for movie_id, vector in movie_vectors.items():
            action = {
                "_index": self.index_name,
                "_id": str(movie_id),
                "_source": {
                    "movie_id": str(movie_id),
                    "movie_vector": vector
                }
            }
            actions.append(action)

            # Bulk index in batches of 500
            if len(actions) >= 500:
                helpers.bulk(self.client, actions)
                actions = []

        if actions:
            helpers.bulk(self.client, actions)

        logger.info("Successfully synced all vectors to Elasticsearch.")

    def run(self):
        try:
            self.create_index_with_mapping()
            self.sync_vectors()
        except Exception as e:
            logger.error(f"Error during synchronization: {e}")

if __name__ == "__main__":
    syncer = VectorSyncer()
    syncer.run()
