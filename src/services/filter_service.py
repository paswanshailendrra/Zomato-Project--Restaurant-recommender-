import os
import logging
import re
import difflib
from typing import List, Optional

from src.models.restaurant import Restaurant
from src.models.user_preferences import UserPreferences
from src.data.repository import RestaurantRepository

logger = logging.getLogger(__name__)


class FilterService:
    """
    Applies deterministic hard filters to narrow restaurant candidates
    before they are sent to the LLM for ranking.

    Filter chain:
        ALL records
          → filter by location  (case-insensitive, alias mapping, parent-city wide, fuzzy)
          → filter by min_rating
          → filter by budget tier
          → filter by cuisine   (if specified — token match)
          → sort by rating desc, votes desc (tie-breaker)
          → limit to top N candidates
    """

    def __init__(
        self,
        repository: RestaurantRepository,
        max_candidates: int = None,
    ):
        self.repository = repository
        self.max_candidates = max_candidates or int(
            os.environ.get("MAX_CANDIDATES", "20")
        )

    # ------------------------------------------------------------------ #
    #  Location normalization and matching helpers                       #
    # ------------------------------------------------------------------ #

    @staticmethod
    def clean_location_string(loc: str) -> str:
        """
        Standardizes spacing, lowercases, and maps common spelling variations/aliases
        for Bangalore neighborhoods.
        """
        loc = loc.strip().lower()
        loc = re.sub(r"\s+", " ", loc)
        # Common replacements/typo fixes
        loc = loc.replace("indra nagar", "indiranagar")
        loc = loc.replace("indira nagar", "indiranagar")
        loc = loc.replace("indranagar", "indiranagar")
        loc = loc.replace("whitefiled", "whitefield")
        loc = loc.replace("white field", "whitefield")
        loc = loc.replace("kormangala", "koramangala")
        loc = loc.replace("koramangla", "koramangala")
        loc = loc.replace("marthahalli", "marathahalli")
        loc = loc.replace("marathahali", "marathahalli")
        loc = loc.replace("marthahali", "marathahalli")
        loc = loc.replace("belandur", "bellandur")
        loc = loc.replace("jpnagar", "jp nagar")
        loc = loc.replace("j p nagar", "jp nagar")
        loc = loc.replace("hsr layout", "hsr")
        loc = loc.replace("btm layout", "btm")
        loc = loc.replace("m g road", "mg road")
        loc = loc.replace("ecity", "electronic city")
        loc = loc.replace("e-city", "electronic city")
        loc = loc.replace("basavangudi", "basavanagudi")
        loc = loc.replace("banasankari", "banashankari")
        loc = loc.replace("kamanahalli", "kammanahalli")
        loc = loc.replace("kalyannagar", "kalyan nagar")
        loc = loc.replace("malleswaram", "malleshwaram")
        loc = loc.replace("maleswaram", "malleshwaram")
        return loc

    @staticmethod
    def is_bangalore(query: str) -> bool:
        """Checks if a query refers to the entire Bangalore parent city."""
        clean = FilterService.clean_location_string(query)
        parent_cities = {
            "bangalore", "bengaluru", "bengalore", "banglore",
            "begalore", "benguluru", "bangaluru", "bengaluru city", "bangalore city"
        }
        return clean in parent_cities

    @staticmethod
    def get_matching_locations(query: str, canonical_list: List[str]) -> List[str]:
        """
        Finds all matching canonical locations for a query string.
        Supports parent city, space-insensitive substring checks, and fuzzy fallbacks.
        """
        if FilterService.is_bangalore(query):
            return canonical_list

        q_clean = FilterService.clean_location_string(query)
        q_super_clean = q_clean.replace(" ", "")

        # 1. Exact or substring match after stripping all spaces (for "jpnagar", "vasanthnagar" etc.)
        matches = []
        for loc in canonical_list:
            loc_clean = FilterService.clean_location_string(loc)
            loc_super_clean = loc_clean.replace(" ", "")
            if q_super_clean == loc_super_clean or q_super_clean in loc_super_clean or loc_super_clean in q_super_clean:
                matches.append(loc)

        if matches:
            return matches

        # 2. Fuzzy match fallback
        cleaned_to_canonical = {FilterService.clean_location_string(loc): loc for loc in canonical_list}
        fuzzy_matches = difflib.get_close_matches(q_clean, cleaned_to_canonical.keys(), n=3, cutoff=0.8)
        if fuzzy_matches:
            return [cleaned_to_canonical[fm] for fm in fuzzy_matches]

        return []

    # ------------------------------------------------------------------ #
    #  Public API                                                         #
    # ------------------------------------------------------------------ #

    def filter(self, preferences: UserPreferences) -> List[Restaurant]:
        """
        Returns up to ``max_candidates`` restaurants that satisfy every
        hard constraint in *preferences*, sorted by rating then votes.
        """
        candidates = self.repository.get_all()
        all_canonical_locations = self.repository.get_all_locations()
        logger.info(
            f"Starting filter pipeline with {len(candidates)} total restaurants. "
            f"Preferences: location={preferences.location}, budget={preferences.budget}, "
            f"cuisine={preferences.cuisine}, min_rating={preferences.min_rating}"
        )

        # 1. Location (required — case-insensitive substring / alias / fuzzy)
        candidates = self._filter_by_location(candidates, preferences.location, all_canonical_locations)
        logger.debug(f"After location filter: {len(candidates)} candidates")

        # 2. Minimum rating
        candidates = self._filter_by_rating(candidates, preferences.min_rating)
        logger.debug(f"After rating filter: {len(candidates)} candidates")

        # 3. Budget tier
        candidates = self._filter_by_budget(candidates, preferences.budget)
        logger.debug(f"After budget filter: {len(candidates)} candidates")

        # 4. Cuisine (optional — skip if not specified)
        if preferences.cuisine:
            candidates = self._filter_by_cuisine(candidates, preferences.cuisine)
            logger.debug(f"After cuisine filter: {len(candidates)} candidates")

        # 5. Sort by rating (desc), then votes (desc) as tie-breaker
        candidates = self._sort_candidates(candidates)

        if len(candidates) < 5:
            logger.info("Less than 5 candidates found. Relaxing budget constraints.")
            # Re-filter by location and rating, relax budget
            relaxed = self._filter_by_location(self.repository.get_all(), preferences.location, all_canonical_locations)
            relaxed = self._filter_by_rating(relaxed, preferences.min_rating)
            
            # Keep cuisine if specified
            if preferences.cuisine:
                relaxed = self._filter_by_cuisine(relaxed, preferences.cuisine)
                
            candidates = self._sort_candidates(relaxed)

        # 6. Cap to max_candidates
        candidates = candidates[: self.max_candidates]

        logger.info(f"Filter pipeline complete. Returning {len(candidates)} candidates.")
        return candidates

    # ------------------------------------------------------------------ #
    #  Individual filter helpers                                          #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _filter_by_location(
        restaurants: List[Restaurant], location: str, all_canonical_locations: List[str]
    ) -> List[Restaurant]:
        """Matches location with city-wide checks, alias mapping, and fuzzy fallbacks."""
        if not location:
            return restaurants

        matched_locs = FilterService.get_matching_locations(location, all_canonical_locations)
        if not matched_locs:
            logger.debug(f"No location matches found for query: '{location}'")
            return []

        matched_locs_set = {loc.lower() for loc in matched_locs}
        return [
            r
            for r in restaurants
            if r.location.lower() in matched_locs_set
        ]

    @staticmethod
    def _filter_by_rating(
        restaurants: List[Restaurant], min_rating: float
    ) -> List[Restaurant]:
        return [r for r in restaurants if r.rating >= min_rating]

    @staticmethod
    def _filter_by_budget(
        restaurants: List[Restaurant], budget: str
    ) -> List[Restaurant]:
        budget_hierarchy = ["low", "medium", "high", "very high"]
        budget_lower = budget.strip().lower()
        try:
            tier_index = budget_hierarchy.index(budget_lower)
        except ValueError:
            tier_index = len(budget_hierarchy) - 1
        allowed_tiers = set(budget_hierarchy[: tier_index + 1])
        return [r for r in restaurants if r.budget_tier in allowed_tiers]

    @staticmethod
    def _filter_by_cuisine(
        restaurants: List[Restaurant], cuisine: str
    ) -> List[Restaurant]:
        """
        Token-level match: a restaurant matches if any of its cuisine
        entries contain the query string (case-insensitive).
        """
        cuisine_lower = cuisine.strip().lower()
        return [
            r
            for r in restaurants
            if any(cuisine_lower in c.lower() for c in r.cuisines)
        ]

    @staticmethod
    def _sort_candidates(restaurants: List[Restaurant]) -> List[Restaurant]:
        """Sort by rating descending, then votes descending as tie-breaker."""
        return sorted(
            restaurants,
            key=lambda r: (r.rating, r.votes or 0),
            reverse=True,
        )
