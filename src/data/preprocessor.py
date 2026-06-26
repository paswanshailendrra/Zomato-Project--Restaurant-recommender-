import pandas as pd
import re
from typing import List
import logging
from src.models.restaurant import Restaurant

logger = logging.getLogger(__name__)

class Preprocessor:
    @staticmethod
    def clean_rating(val) -> float:
        """
        Parses rating string (e.g. "4.1/5", "4.1", "NEW", "-") into float.
        """
        if pd.isna(val):
            return 0.0
        val_str = str(val).strip()
        if val_str in ("NEW", "-", ""):
            return 0.0
        
        # Try to extract the first numeric float
        match = re.match(r"^([0-9.]+)", val_str)
        if match:
            try:
                rating = float(match.group(1))
                if 0.0 <= rating <= 5.0:
                    return rating
            except ValueError:
                pass
        return 0.0

    @staticmethod
    def clean_cost(val) -> int:
        """
        Parses cost (e.g. "1,200", 800) into integer.
        """
        if pd.isna(val):
            return 0
        val_str = str(val).strip()
        # Remove commas and non-numeric chars except digits
        cleaned = re.sub(r"[^\d]", "", val_str)
        if cleaned:
            try:
                return int(cleaned)
            except ValueError:
                pass
        return 0

    @staticmethod
    def clean_cuisines(val) -> List[str]:
        """
        Splits comma-separated cuisines into list of cleaned strings.
        """
        if pd.isna(val):
            return []
        val_str = str(val)
        return [c.strip() for c in val_str.split(",") if c.strip()]

    @staticmethod
    def clean_location(val) -> str:
        """
        Cleans location, strips whitespaces.
        """
        if pd.isna(val):
            return "Unknown"
        return str(val).strip()

    @staticmethod
    def map_budget_tier(cost: int) -> str:
        """
        Low: <= 500
        Medium: 501 - 1000
        High: 1001 - 2000
        Very High: > 2000
        """
        if cost <= 500:
            return "low"
        elif cost <= 1000:
            return "medium"
        elif cost <= 2000:
            return "high"
        else:
            return "very high"

    def preprocess(self, df: pd.DataFrame) -> List[Restaurant]:
        """
        Standardizes raw DataFrame columns and converts rows into Restaurant models.
        """
        logger.info("Starting preprocessing of dataset...")
        
        # Identify columns dynamically
        cols = {c.lower(): c for c in df.columns}
        
        # Mapping helpers based on observed variations
        name_col = cols.get("name") or cols.get("restaurant_name") or df.columns[0]
        loc_col = cols.get("location") or cols.get("city") or cols.get("address") or df.columns[1]
        cuisine_col = cols.get("cuisines") or cols.get("cuisine") or df.columns[2]
        rating_col = cols.get("rate") or cols.get("rating") or cols.get("rating_number")
        cost_col = cols.get("approx_cost(for two people)") or cols.get("approx_cost") or cols.get("cost_for_two") or cols.get("price_range")
        votes_col = cols.get("votes") or cols.get("vote_count")

        restaurants = []
        # Keep track of unique names and locations to avoid duplicate entries
        seen_keys = set()

        for idx, row in df.iterrows():
            name = str(row[name_col]).strip() if name_col in df.columns else f"Restaurant {idx}"
            location = self.clean_location(row[loc_col]) if loc_col in df.columns else "Unknown"
            
            # Key for deduplication
            unique_key = (name.lower(), location.lower())
            
            cuisines_raw = row[cuisine_col] if cuisine_col in df.columns else ""
            cuisines = self.clean_cuisines(cuisines_raw)
            
            rating_raw = row[rating_col] if rating_col and rating_col in df.columns else 0.0
            rating = self.clean_rating(rating_raw)
            
            cost_raw = row[cost_col] if cost_col and cost_col in df.columns else 0
            cost = self.clean_cost(cost_raw)
            budget_tier = self.map_budget_tier(cost)
            
            votes_raw = row[votes_col] if votes_col and votes_col in df.columns else 0
            try:
                votes = int(votes_raw) if not pd.isna(votes_raw) else 0
            except (ValueError, TypeError):
                votes = 0

            # Skip entry if it doesn't have a valid name or location
            if not name or name.lower() == "nan" or location.lower() == "unknown":
                continue

            # Deduplication: keep the record with higher votes if duplicate exists
            if unique_key in seen_keys:
                # Find the existing restaurant and update it if this one has more votes
                for existing in restaurants:
                    if existing.name.lower() == name.lower() and existing.location.lower() == location.lower():
                        if votes > (existing.votes or 0):
                            existing.rating = rating
                            existing.cost_for_two = cost
                            existing.budget_tier = budget_tier
                            existing.votes = votes
                            existing.cuisines = cuisines
                        break
                continue

            seen_keys.add(unique_key)
            restaurants.append(Restaurant(
                id=idx,
                name=name,
                location=location,
                cuisines=cuisines,
                rating=rating,
                cost_for_two=cost,
                budget_tier=budget_tier,
                votes=votes
            ))

        logger.info(f"Preprocessing complete. Standardized {len(restaurants)} unique restaurant records.")
        return restaurants
