import logging
from typing import List

from src.models.user_preferences import UserPreferences
from src.models.recommendation import RecommendationResponse
from src.services.filter_service import FilterService
from src.services.llm_service import GroqLLMService

logger = logging.getLogger(__name__)

class RecommendationOrchestrator:
    """
    Orchestrates the end-to- natural language ranking pipeline.
    Connects FilterService (deterministic candidate generation)
    to GroqLLMService (AI ranking & explanation).
    """

    def __init__(
        self,
        filter_service: FilterService,
        llm_service: GroqLLMService,
    ):
        self.filter_service = filter_service
        self.llm_service = llm_service

    def get_recommendations(self, preferences: UserPreferences) -> RecommendationResponse:
        """
        1. Parse and apply hard constraints (FilterService).
        2. Pass candidates to the LLM for ranking and explanation (GroqLLMService).
        3. Return the final RecommendationResponse.
        """
        logger.info(f"Orchestrating recommendation request for location: {preferences.location}")
        
        # 1. Deterministic Filtering
        candidates = self.filter_service.filter(preferences)
        
        if not candidates:
            logger.info("No candidates found matching hard constraints.")
            return RecommendationResponse(
                summary="We couldn't find any restaurants matching your exact filters.",
                recommendations=[]
            )
            
        logger.info(f"Filtering yielded {len(candidates)} candidates. Sending to LLM...")
        
        # 2. LLM Ranking & Explanation
        response = self.llm_service.get_recommendations(preferences, candidates)
        
        logger.info("Successfully generated AI recommendations.")
        return response
