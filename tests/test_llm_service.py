import pytest
import json
from unittest.mock import patch, MagicMock

from src.models.restaurant import Restaurant
from src.models.user_preferences import UserPreferences
from src.models.recommendation import RecommendationResponse
from src.services.llm_service import GroqLLMService


# ------------------------------------------------------------------ #
#  Fixtures                                                            #
# ------------------------------------------------------------------ #

SAMPLE_CANDIDATES = [
    Restaurant(id=1, name="Truffles", location="Koramangala", cuisines=["Italian", "American"], rating=4.5, cost_for_two=800, budget_tier="medium", votes=1200),
    Restaurant(id=2, name="Empire", location="Koramangala", cuisines=["North Indian", "Mughlai"], rating=4.0, cost_for_two=400, budget_tier="low", votes=1500),
    Restaurant(id=3, name="Toit", location="Indiranagar", cuisines=["Italian", "American"], rating=4.6, cost_for_two=1500, budget_tier="medium", votes=3500),
]

SAMPLE_PREFS = UserPreferences(
    location="Koramangala",
    budget="medium",
    cuisine="Italian",
    min_rating=4.0,
    additional_preferences="family-friendly",
)

VALID_LLM_RESPONSE = {
    "summary": "Great Italian picks in Koramangala for your family!",
    "recommendations": [
        {
            "id": 1,
            "rank": 1,
            "name": "Truffles",
            "cuisines": ["Italian", "American"],
            "rating": 4.5,
            "estimated_cost": 800,
            "explanation": "A highly rated Italian spot within your medium budget, known for a family-friendly vibe.",
        },
        {
            "id": 3,
            "rank": 2,
            "name": "Toit",
            "cuisines": ["Italian", "American"],
            "rating": 4.6,
            "estimated_cost": 1500,
            "explanation": "Top-rated Italian restaurant with excellent reviews and lively atmosphere.",
        },
    ],
}


@pytest.fixture
def service():
    """Create a GroqLLMService with a dummy API key (calls will be mocked)."""
    with patch.dict("os.environ", {"GROQ_API_KEY": "test-key-123"}):
        return GroqLLMService(api_key="test-key-123")


# ------------------------------------------------------------------ #
#  Validation tests                                                    #
# ------------------------------------------------------------------ #

class TestValidation:
    def test_valid_response_parsed(self, service):
        candidate_ids = {1, 2, 3}
        result = service._validate_response(VALID_LLM_RESPONSE, candidate_ids)
        assert isinstance(result, RecommendationResponse)
        assert len(result.recommendations) == 2
        assert result.recommendations[0].name == "Truffles"
        assert result.summary is not None

    def test_hallucinated_ids_discarded(self, service):
        hallucinated = {
            "summary": "Here are my picks.",
            "recommendations": [
                {"id": 1, "rank": 1, "name": "Truffles", "cuisines": ["Italian"], "rating": 4.5, "estimated_cost": 800, "explanation": "Great!"},
                {"id": 999, "rank": 2, "name": "Fake Restaurant", "cuisines": ["Fake"], "rating": 5.0, "estimated_cost": 100, "explanation": "Invented."},
            ],
        }
        candidate_ids = {1, 2, 3}
        result = service._validate_response(hallucinated, candidate_ids)
        assert len(result.recommendations) == 1
        assert result.recommendations[0].id == 1

    def test_empty_recommendations(self, service):
        empty = {"summary": "Nothing found.", "recommendations": []}
        result = service._validate_response(empty, {1, 2, 3})
        assert len(result.recommendations) == 0

    def test_ranks_renumbered(self, service):
        """After discarding hallucinated entries, ranks should be sequential."""
        data = {
            "summary": "Picks",
            "recommendations": [
                {"id": 3, "rank": 1, "name": "Toit", "cuisines": ["Italian"], "rating": 4.6, "estimated_cost": 1500, "explanation": "Top rated."},
                {"id": 999, "rank": 2, "name": "Ghost", "cuisines": [], "rating": 0, "estimated_cost": 0, "explanation": "X"},
                {"id": 1, "rank": 3, "name": "Truffles", "cuisines": ["Italian"], "rating": 4.5, "estimated_cost": 800, "explanation": "Solid."},
            ],
        }
        result = service._validate_response(data, {1, 2, 3})
        assert len(result.recommendations) == 2
        assert result.recommendations[0].rank == 1
        assert result.recommendations[1].rank == 2

    def test_cuisines_string_to_list(self, service):
        """If the LLM returns cuisines as a comma-separated string, it should be split."""
        data = {
            "summary": "Picks",
            "recommendations": [
                {"id": 1, "rank": 1, "name": "Truffles", "cuisines": "Italian, American", "rating": 4.5, "estimated_cost": 800, "explanation": "Great!"},
            ],
        }
        result = service._validate_response(data, {1, 2, 3})
        assert result.recommendations[0].cuisines == ["Italian", "American"]


# ------------------------------------------------------------------ #
#  Deterministic fallback tests                                        #
# ------------------------------------------------------------------ #

class TestDeterministicFallback:
    def test_returns_top_k(self, service):
        service.top_k = 2
        result = service._deterministic_fallback(SAMPLE_CANDIDATES)
        assert len(result.recommendations) == 2
        # Highest rated first: Toit (4.6) then Truffles (4.5)
        assert result.recommendations[0].name == "Toit"
        assert result.recommendations[1].name == "Truffles"

    def test_explanation_template(self, service):
        service.top_k = 1
        result = service._deterministic_fallback(SAMPLE_CANDIDATES)
        assert "4.6" in result.recommendations[0].explanation
        assert "3500" in result.recommendations[0].explanation

    def test_summary_mentions_unavailable(self, service):
        result = service._deterministic_fallback(SAMPLE_CANDIDATES)
        assert "unavailable" in result.summary.lower()


# ------------------------------------------------------------------ #
#  End-to-end with mocked Groq                                        #
# ------------------------------------------------------------------ #

class TestGetRecommendations:
    def test_primary_model_success(self, service):
        with patch.object(service, "_call_groq", return_value=VALID_LLM_RESPONSE):
            result = service.get_recommendations(SAMPLE_PREFS, SAMPLE_CANDIDATES)
            assert len(result.recommendations) == 2
            assert result.recommendations[0].name == "Truffles"

    def test_fallback_on_primary_failure(self, service):
        call_count = {"n": 0}

        def side_effect(sys_p, usr_p, model):
            call_count["n"] += 1
            if call_count["n"] == 1:
                raise Exception("Primary model down")
            return VALID_LLM_RESPONSE

        with patch.object(service, "_call_groq", side_effect=side_effect):
            result = service.get_recommendations(SAMPLE_PREFS, SAMPLE_CANDIDATES)
            assert len(result.recommendations) == 2
            assert call_count["n"] == 2  # primary + fallback

    def test_deterministic_fallback_on_total_failure(self, service):
        with patch.object(service, "_call_groq", side_effect=Exception("All models down")):
            result = service.get_recommendations(SAMPLE_PREFS, SAMPLE_CANDIDATES)
            assert len(result.recommendations) > 0
            assert "unavailable" in result.summary.lower()

    def test_empty_candidates(self, service):
        result = service.get_recommendations(SAMPLE_PREFS, [])
        assert len(result.recommendations) == 0
        assert "no candidate" in result.summary.lower()


# ------------------------------------------------------------------ #
#  Prompt building tests                                               #
# ------------------------------------------------------------------ #

class TestPromptBuilding:
    def test_user_prompt_contains_preferences(self, service):
        prompt = service._build_user_prompt(SAMPLE_PREFS, SAMPLE_CANDIDATES)
        assert "Koramangala" in prompt
        assert "medium" in prompt
        assert "Italian" in prompt
        assert "family-friendly" in prompt

    def test_user_prompt_contains_candidates(self, service):
        prompt = service._build_user_prompt(SAMPLE_PREFS, SAMPLE_CANDIDATES)
        assert "Truffles" in prompt
        assert "Empire" in prompt
        assert "Toit" in prompt

    def test_format_candidates_json(self, service):
        json_str = service._format_candidates(SAMPLE_CANDIDATES)
        parsed = json.loads(json_str)
        assert len(parsed) == 3
        assert parsed[0]["id"] == 1
