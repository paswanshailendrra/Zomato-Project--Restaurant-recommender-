import os
import json
import time
import logging
from pathlib import Path
from typing import List, Optional, Set

from groq import Groq
from groq import APIError, RateLimitError, APITimeoutError

from src.models.restaurant import Restaurant
from src.models.user_preferences import UserPreferences
from src.models.recommendation import Recommendation, RecommendationResponse

logger = logging.getLogger(__name__)

# Resolve prompt file paths relative to this module
_PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"
_SYSTEM_PROMPT_PATH = _PROMPTS_DIR / "system_prompt.txt"
_USER_PROMPT_TEMPLATE_PATH = _PROMPTS_DIR / "user_prompt_template.txt"


class GroqLLMService:
    """
    Manages Groq API interactions for restaurant ranking and explanation.

    Responsibilities:
    - Build system + user prompts from templates
    - Call the Groq chat completions API with structured JSON output
    - Retry with exponential backoff on rate-limit errors
    - Fall back to a smaller model on persistent failures
    - Validate that every returned restaurant ID exists in the candidate set
    """

    def __init__(
        self,
        api_key: str = None,
        model: str = None,
        fallback_model: str = None,
        top_k: int = None,
    ):
        self.api_key = api_key or os.environ.get("GROQ_API_KEY", "")
        if not self.api_key:
            raise ValueError(
                "GROQ_API_KEY is required. Set it via environment variable or "
                "pass api_key to GroqLLMService()."
            )
        self.model = model or os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
        self.fallback_model = fallback_model or os.environ.get(
            "GROQ_FALLBACK_MODEL", "llama-3.1-8b-instant"
        )
        self.top_k = top_k or int(os.environ.get("TOP_K_RECOMMENDATIONS", "5"))
        self.client = Groq(api_key=self.api_key)

        # Load prompt templates once
        self._system_prompt = self._load_prompt(_SYSTEM_PROMPT_PATH)
        self._user_prompt_template = self._load_prompt(_USER_PROMPT_TEMPLATE_PATH)

    # ------------------------------------------------------------------ #
    #  Prompt helpers                                                      #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _load_prompt(path: Path) -> str:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    @staticmethod
    def _format_candidates(candidates: List[Restaurant]) -> str:
        """Convert candidate restaurants into compact JSON for the prompt."""
        records = []
        for r in candidates:
            records.append(
                {
                    "id": r.id,
                    "name": r.name,
                    "cuisines": r.cuisines,
                    "rating": r.rating,
                    "cost_for_two": r.cost_for_two,
                    "budget_tier": r.budget_tier,
                    "location": r.location,
                    "votes": r.votes,
                }
            )
        return json.dumps(records, indent=2)

    def _build_user_prompt(
        self, preferences: UserPreferences, candidates: List[Restaurant]
    ) -> str:
        return self._user_prompt_template.format(
            location=preferences.location,
            budget=preferences.budget,
            cuisine=preferences.cuisine or "Any",
            min_rating=preferences.min_rating,
            additional_preferences=preferences.additional_preferences or "None",
            candidate_json=self._format_candidates(candidates),
            top_k=min(self.top_k, len(candidates)),
        )

    # ------------------------------------------------------------------ #
    #  API call with retry logic                                           #
    # ------------------------------------------------------------------ #

    def _call_groq(self, system_prompt: str, user_prompt: str, model: str) -> dict:
        """
        Send a chat completion request to Groq and return the parsed JSON.
        Retries up to 2 times on rate-limit errors with exponential backoff.
        """
        max_retries = 2
        for attempt in range(max_retries + 1):
            try:
                logger.info(f"Calling Groq model={model} (attempt {attempt + 1})")
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.3,
                    max_tokens=2048,
                    response_format={"type": "json_object"},
                )
                raw = response.choices[0].message.content
                try:
                    return json.loads(raw)
                except json.JSONDecodeError as e:
                    logger.warning(
                        f"LLM returned invalid JSON on model={model} "
                        f"(attempt {attempt + 1}): {e}. Raw: {raw[:200]}"
                    )
                    if attempt < max_retries:
                        continue
                    raise

            except RateLimitError as e:
                wait = 2 ** (attempt + 1)  # 2s, 4s
                logger.warning(
                    f"Rate limited on model={model}. "
                    f"Retrying in {wait}s (attempt {attempt + 1}/{max_retries + 1}): {e}"
                )
                if attempt < max_retries:
                    time.sleep(wait)
                else:
                    raise

            except APITimeoutError as e:
                logger.warning(f"Groq API timeout on model={model}: {e}")
                if attempt < max_retries:
                    time.sleep(1)
                else:
                    raise

    # ------------------------------------------------------------------ #
    #  Post-validation                                                     #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _validate_response(
        raw: dict, candidate_ids: Set[int]
    ) -> RecommendationResponse:
        """
        Parse the raw LLM JSON into a RecommendationResponse, discarding
        any recommendation whose id is not in the candidate set.
        """
        recs_raw = raw.get("recommendations", [])
        valid_recs: List[Recommendation] = []

        for item in recs_raw:
            rec_id = item.get("id")
            if rec_id not in candidate_ids:
                logger.warning(
                    f"Discarding hallucinated restaurant id={rec_id} "
                    f"name='{item.get('name')}' — not in candidate set."
                )
                continue
            
            # Ensure cuisines is a list
            cuisines = item.get("cuisines", [])
            if isinstance(cuisines, str):
                cuisines = [c.strip() for c in cuisines.split(",") if c.strip()]

            try:
                valid_recs.append(
                    Recommendation(
                        id=rec_id,
                        rank=item.get("rank", len(valid_recs) + 1),
                        name=item.get("name", "Unknown"),
                        cuisines=cuisines,
                        rating=float(item.get("rating", 0.0)),
                        estimated_cost=item.get("estimated_cost"),
                        explanation=item.get("explanation", ""),
                    )
                )
            except Exception as e:
                logger.warning(f"Skipping malformed recommendation item: {e}")

        # Re-number ranks sequentially
        for i, rec in enumerate(valid_recs, start=1):
            rec.rank = i

        return RecommendationResponse(
            summary=raw.get("summary"),
            recommendations=valid_recs,
        )

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    def get_recommendations(
        self,
        preferences: UserPreferences,
        candidates: List[Restaurant],
    ) -> RecommendationResponse:
        """
        Rank and explain *candidates* using the Groq LLM, returning a
        validated ``RecommendationResponse``.

        Fallback chain:
        1. Primary model  (e.g. llama-3.3-70b-versatile)
        2. Fallback model (e.g. llama-3.1-8b-instant)
        3. Deterministic rating-sorted list without explanations
        """
        if not candidates:
            return RecommendationResponse(
                summary="No candidate restaurants to rank.",
                recommendations=[],
            )

        candidate_ids = {r.id for r in candidates}
        user_prompt = self._build_user_prompt(preferences, candidates)

        # --- Try primary model ---
        try:
            raw = self._call_groq(self._system_prompt, user_prompt, self.model)
            result = self._validate_response(raw, candidate_ids)
            if result.recommendations:
                logger.info(
                    f"Primary model returned {len(result.recommendations)} recommendations."
                )
                return result
            logger.warning("Primary model returned 0 valid recommendations; trying fallback.")
        except Exception as e:
            logger.warning(f"Primary model failed: {e}. Trying fallback model.")

        # --- Try fallback model ---
        if self.fallback_model and self.fallback_model != self.model:
            try:
                raw = self._call_groq(self._system_prompt, user_prompt, self.fallback_model)
                result = self._validate_response(raw, candidate_ids)
                if result.recommendations:
                    logger.info(
                        f"Fallback model returned {len(result.recommendations)} recommendations."
                    )
                    return result
            except Exception as e:
                logger.warning(f"Fallback model also failed: {e}. Using deterministic fallback.")

        # --- Deterministic fallback (no LLM) ---
        logger.info("Using deterministic rating-sorted fallback (no AI explanations).")
        return self._deterministic_fallback(candidates)

    def _deterministic_fallback(
        self, candidates: List[Restaurant]
    ) -> RecommendationResponse:
        """
        Return the top-K candidates sorted by rating/votes with template
        explanations — used when both LLM models are unavailable.
        """
        sorted_candidates = sorted(
            candidates,
            key=lambda r: (r.rating, r.votes or 0),
            reverse=True,
        )
        top = sorted_candidates[: self.top_k]

        recs = []
        for i, r in enumerate(top, start=1):
            recs.append(
                Recommendation(
                    id=r.id,
                    rank=i,
                    name=r.name,
                    cuisines=r.cuisines,
                    rating=r.rating,
                    estimated_cost=r.cost_for_two,
                    explanation=(
                        f"Recommended based on its high rating of {r.rating} "
                        f"and {r.votes or 0} votes."
                    ),
                )
            )

        return RecommendationResponse(
            summary="Recommendations sorted by rating (AI explanations unavailable).",
            recommendations=recs,
        )
