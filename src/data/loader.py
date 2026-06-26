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
        Loads the dataset. Tries local cache first, then Hugging Face,
        and finally falls back to a mock/fallback CSV if offline.
        """
        # 1. Try Parquet Cache
        if os.path.exists(self.cache_file):
            try:
                logger.info(f"Loading dataset from local cache: {self.cache_file}")
                df = pd.read_parquet(self.cache_file)
                if not df.empty:
                    return df
            except Exception as e:
                logger.warning(f"Failed to read parquet cache: {e}. Trying Hugging Face.")

        # 2. Try Hugging Face
        try:
            logger.info(f"Downloading dataset from Hugging Face: {self.dataset_name}")
            dataset = load_dataset(self.dataset_name)
            split = 'train'
            if split not in dataset:
                split = list(dataset.keys())[0]
            
            df = dataset[split].to_pandas()
            
            # Save to parquet cache
            try:
                df.to_parquet(self.cache_file, index=False)
                logger.info(f"Cached dataset to {self.cache_file}")
            except Exception as cache_err:
                logger.warning(f"Could not cache dataset to parquet: {cache_err}")
                
            return df
        except Exception as e:
            logger.warning(f"Hugging Face download failed: {e}. Trying fallback CSV.")

        # 3. Try Fallback CSV
        if os.path.exists(self.fallback_file):
            try:
                logger.info(f"Loading dataset from local fallback: {self.fallback_file}")
                return pd.read_csv(self.fallback_file)
            except Exception as csv_err:
                logger.error(f"Failed to read fallback CSV: {csv_err}")
        
        # 4. Create a minimal mock dataset if absolutely nothing is available
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
