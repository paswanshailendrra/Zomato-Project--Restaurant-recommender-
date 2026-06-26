import os
import pandas as pd
from datasets import load_dataset
import logging

logger = logging.getLogger(__name__)

class DatasetLoader:
    def __init__(self, dataset_name: str = "ManikaSaini/zomato-restaurant-recommendation", cache_dir: str = None):
        self.dataset_name = dataset_name
        self.cache_dir = cache_dir or os.environ.get("DATASET_CACHE_PATH", "./data/cache")
        os.makedirs(self.cache_dir, exist_ok=True)
        self.cache_file = os.path.join(self.cache_dir, "zomato_cached.parquet")
        self.fallback_file = os.path.join(self.cache_dir, "zomato_fallback.csv")

    def load(self) -> pd.DataFrame:
        """
        Loads the dataset. Uses the bundled gzip-compressed parquet file 
        to avoid Hugging Face downloads and OOM issues during deployment.
        """
        bundled_file = os.path.join(os.path.dirname(__file__), "zomato_dataset.parquet")
        
        if os.path.exists(bundled_file):
            try:
                logger.info(f"Loading bundled dataset: {bundled_file}")
                return pd.read_parquet(bundled_file)
            except Exception as e:
                logger.error(f"Failed to load bundled dataset: {e}")

        # Fallback to local cache if bundled file doesn't exist (e.g. local dev fallback)
        if os.path.exists(self.cache_file):
            try:
                logger.info(f"Loading dataset from local cache: {self.cache_file}")
                return pd.read_parquet(self.cache_file)
            except Exception as e:
                logger.error(f"Failed to read parquet cache: {e}")

        # Try Fallback CSV
        if os.path.exists(self.fallback_file):
            try:
                logger.info(f"Loading dataset from local fallback: {self.fallback_file}")
                return pd.read_csv(self.fallback_file)
            except Exception as csv_err:
                logger.error(f"Failed to read fallback CSV: {csv_err}")
        
        # Create a minimal mock dataset if absolutely nothing is available
        logger.warning("No dataset sources available. Creating minimal mock dataset for emergency fallback.")
        mock_data = {
            "name": ["Truffles", "Glen's Bakehouse", "Toit", "Empire Restaurant", "MTR"],
            "location": ["Bangalore", "Bangalore", "Bangalore", "Bangalore", "Bangalore"],
            "cuisines": ["Italian, American", "Bakery, Desserts", "Italian, American", "North Indian, Mughlai", "South Indian"],
            "rate": ["4.5/5", "4.2/5", "4.6/5", "4.0/5", "4.7/5"],
            "approx_cost(for two people)": ["800", "600", "1,500", "500", "300"],
            "votes": [1200, 800, 3500, 1500, 2000]
        }
        df_mock = pd.DataFrame(mock_data)
        try:
            df_mock.to_csv(self.fallback_file, index=False)
        except Exception as write_err:
            logger.warning(f"Failed to write mock fallback CSV: {write_err}")
        return df_mock
