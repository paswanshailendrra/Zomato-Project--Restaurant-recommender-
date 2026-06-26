import pytest
from unittest.mock import MagicMock

from src.models.restaurant import Restaurant
from src.models.user_preferences import UserPreferences
from src.services.filter_service import FilterService


# ------------------------------------------------------------------ #
#  Fixtures                                                            #
# ------------------------------------------------------------------ #

def _make_restaurant(**overrides) -> Restaurant:
    """Helper to build a Restaurant with sensible defaults."""
    defaults = dict(
        id=1,
        name="Test Restaurant",
        location="Koramangala",
        cuisines=["North Indian"],
        rating=4.0,
        cost_for_two=800,
        budget_tier="medium",
        votes=100,
    )
    defaults.update(overrides)
    return Restaurant(**defaults)


SAMPLE_RESTAURANTS = [
    _make_restaurant(id=1, name="Truffles", location="Koramangala", cuisines=["Italian", "American"], rating=4.5, cost_for_two=800, budget_tier="medium", votes=1200),
    _make_restaurant(id=2, name="Empire", location="Koramangala", cuisines=["North Indian", "Mughlai"], rating=4.0, cost_for_two=400, budget_tier="low", votes=1500),
    _make_restaurant(id=3, name="Glen's Bakehouse", location="Indiranagar", cuisines=["Bakery", "Desserts"], rating=4.2, cost_for_two=600, budget_tier="medium", votes=800),
    _make_restaurant(id=4, name="Toit", location="Indiranagar", cuisines=["Italian", "American"], rating=4.6, cost_for_two=1500, budget_tier="medium", votes=3500),
    _make_restaurant(id=5, name="MTR", location="Basavanagudi", cuisines=["South Indian"], rating=4.7, cost_for_two=300, budget_tier="low", votes=2000),
    _make_restaurant(id=6, name="Luxury Dine", location="Koramangala", cuisines=["Continental", "Italian"], rating=3.5, cost_for_two=2500, budget_tier="high", votes=50),
]

CANONICAL_LOCS = ["Koramangala", "Indiranagar", "Basavanagudi"]


@pytest.fixture
def mock_repo():
    repo = MagicMock()
    repo.get_all.return_value = SAMPLE_RESTAURANTS
    repo.get_all_locations.return_value = CANONICAL_LOCS
    return repo


@pytest.fixture
def service(mock_repo):
    return FilterService(repository=mock_repo, max_candidates=20)


# ------------------------------------------------------------------ #
#  Location filter tests                                               #
# ------------------------------------------------------------------ #

class TestLocationFilter:
    def test_exact_match(self):
        result = FilterService._filter_by_location(SAMPLE_RESTAURANTS, "Koramangala", CANONICAL_LOCS)
        assert len(result) == 3
        assert all("koramangala" in r.location.lower() for r in result)

    def test_case_insensitive(self):
        result = FilterService._filter_by_location(SAMPLE_RESTAURANTS, "koramangala", CANONICAL_LOCS)
        assert len(result) == 3

    def test_substring_match(self):
        result = FilterService._filter_by_location(SAMPLE_RESTAURANTS, "Indira", CANONICAL_LOCS)
        assert len(result) == 2
        assert all("indiranagar" in r.location.lower() for r in result)

    def test_parent_city_match(self):
        # Queries for the entire parent city should return all restaurants
        for q in ["begalore", "bangalore", "bengaluru", "bengalore", "banglore"]:
            result = FilterService._filter_by_location(SAMPLE_RESTAURANTS, q, CANONICAL_LOCS)
            assert len(result) == len(SAMPLE_RESTAURANTS)

    def test_typo_alias_match(self):
        # "indra nagar" should map to Indiranagar
        result_indira = FilterService._filter_by_location(SAMPLE_RESTAURANTS, "indra nagar", CANONICAL_LOCS)
        assert len(result_indira) == 2
        assert all(r.location == "Indiranagar" for r in result_indira)

        # "basavangudi" should map to Basavanagudi
        result_basavan = FilterService._filter_by_location(SAMPLE_RESTAURANTS, "basavangudi", CANONICAL_LOCS)
        assert len(result_basavan) == 1
        assert result_basavan[0].name == "MTR"

    def test_fuzzy_match_fallback(self):
        # "kormangala" / "koramangla" should fuzzy match Koramangala
        for q in ["kormangala", "koramangla"]:
            result = FilterService._filter_by_location(SAMPLE_RESTAURANTS, q, CANONICAL_LOCS)
            assert len(result) == 3
            assert all(r.location == "Koramangala" for r in result)

    def test_no_match(self):
        result = FilterService._filter_by_location(SAMPLE_RESTAURANTS, "Jayanagar", CANONICAL_LOCS)
        assert len(result) == 0


# ------------------------------------------------------------------ #
#  Rating filter tests                                                 #
# ------------------------------------------------------------------ #

class TestRatingFilter:
    def test_all_pass(self):
        result = FilterService._filter_by_rating(SAMPLE_RESTAURANTS, 0.0)
        assert len(result) == 6

    def test_some_pass(self):
        result = FilterService._filter_by_rating(SAMPLE_RESTAURANTS, 4.5)
        assert len(result) == 3  # Truffles 4.5, Toit 4.6, MTR 4.7

    def test_none_pass(self):
        result = FilterService._filter_by_rating(SAMPLE_RESTAURANTS, 5.0)
        assert len(result) == 0


# ------------------------------------------------------------------ #
#  Budget filter tests                                                 #
# ------------------------------------------------------------------ #

class TestBudgetFilter:
    def test_low(self):
        result = FilterService._filter_by_budget(SAMPLE_RESTAURANTS, "low")
        assert len(result) == 2  # Empire, MTR

    def test_medium(self):
        result = FilterService._filter_by_budget(SAMPLE_RESTAURANTS, "medium")
        assert len(result) == 3  # Truffles, Glen's, Toit

    def test_high(self):
        result = FilterService._filter_by_budget(SAMPLE_RESTAURANTS, "high")
        assert len(result) == 1  # Luxury Dine


# ------------------------------------------------------------------ #
#  Cuisine filter tests                                                #
# ------------------------------------------------------------------ #

class TestCuisineFilter:
    def test_exact_cuisine(self):
        result = FilterService._filter_by_cuisine(SAMPLE_RESTAURANTS, "Italian")
        assert len(result) == 3  # Truffles, Toit, Luxury Dine

    def test_case_insensitive(self):
        result = FilterService._filter_by_cuisine(SAMPLE_RESTAURANTS, "italian")
        assert len(result) == 3

    def test_partial_match(self):
        result = FilterService._filter_by_cuisine(SAMPLE_RESTAURANTS, "South")
        assert len(result) == 1  # MTR

    def test_no_match(self):
        result = FilterService._filter_by_cuisine(SAMPLE_RESTAURANTS, "Japanese")
        assert len(result) == 0


# ------------------------------------------------------------------ #
#  Sorting tests                                                       #
# ------------------------------------------------------------------ #

class TestSorting:
    def test_sort_by_rating_desc(self):
        result = FilterService._sort_candidates(SAMPLE_RESTAURANTS)
        assert result[0].name == "MTR"       # 4.7
        assert result[1].name == "Toit"      # 4.6
        assert result[2].name == "Truffles"  # 4.5

    def test_votes_tiebreak(self):
        tied = [
            _make_restaurant(id=10, name="A", rating=4.0, votes=200),
            _make_restaurant(id=11, name="B", rating=4.0, votes=500),
        ]
        result = FilterService._sort_candidates(tied)
        assert result[0].name == "B"  # higher votes


# ------------------------------------------------------------------ #
#  End-to-end pipeline tests                                           #
# ------------------------------------------------------------------ #

class TestFilterPipeline:
    def test_basic_pipeline(self, service):
        prefs = UserPreferences(
            location="Koramangala",
            budget="medium",
            cuisine="Italian",
            min_rating=4.0,
        )
        result = service.filter(prefs)
        assert len(result) == 1
        assert result[0].name == "Truffles"

    def test_no_cuisine_filter(self, service):
        prefs = UserPreferences(
            location="Koramangala",
            budget="medium",
            min_rating=0.0,
        )
        result = service.filter(prefs)
        assert len(result) == 1  # Only Truffles is medium + Koramangala

    def test_zero_results(self, service):
        prefs = UserPreferences(
            location="Jayanagar",
            budget="low",
            min_rating=4.5,
        )
        result = service.filter(prefs)
        assert len(result) == 0

    def test_max_candidates_cap(self, mock_repo):
        """Verify results are capped to max_candidates."""
        svc = FilterService(repository=mock_repo, max_candidates=2)
        prefs = UserPreferences(location="bangalore", budget="medium", min_rating=0.0)
        # location="bangalore" matches everything via wildcard
        result = svc.filter(prefs)
        assert len(result) <= 2
