from typing import List, Set
import asyncio
import logging
from src.models.restaurant import Restaurant
from src.data.loader import DatasetLoader
from src.data.preprocessor import Preprocessor

logger = logging.getLogger(__name__)

class RestaurantRepository:
    def __init__(self, loader: DatasetLoader = None, preprocessor: Preprocessor = None):
        self.loader = loader or DatasetLoader()
        self.preprocessor = preprocessor or Preprocessor()
        self._restaurants: List[Restaurant] = []
        self._initialized = False
        self._loading = False

    def initialize(self):
        """Loads and preprocesses the dataset (blocking)."""
        if self._initialized:
            return
        logger.info("Initializing RestaurantRepository...")
        self._loading = True
        try:
            raw_df = self.loader.load()
            self._restaurants = self.preprocessor.preprocess(raw_df)
            self._initialized = True
            logger.info(f"RestaurantRepository initialized with {len(self._restaurants)} restaurants.")
        finally:
            self._loading = False

    async def initialize_async(self):
        """Loads and preprocesses the dataset in a background thread (non-blocking)."""
        if self._initialized:
            return
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.initialize)

    def get_all(self) -> List[Restaurant]:
        self.initialize()
        return self._restaurants

    def get_all_locations(self) -> List[str]:
        self.initialize()
        # Extract unique locations, sort them, filter out empty/Unknown
        locations = {r.location for r in self._restaurants if r.location and r.location.lower() != "unknown"}
        return sorted(list(locations))

    def get_all_cuisines(self) -> List[str]:
        self.initialize()
        # Extract unique cuisines
        cuisines: Set[str] = set()
        for r in self._restaurants:
            for c in r.cuisines:
                cuisines.add(c)
        return sorted(list(cuisines))
