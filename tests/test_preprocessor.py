import pytest
import pandas as pd
from src.data.preprocessor import Preprocessor
from src.models.restaurant import Restaurant

def test_clean_rating():
    assert Preprocessor.clean_rating("4.5/5") == 4.5
    assert Preprocessor.clean_rating("4.0") == 4.0
    assert Preprocessor.clean_rating("NEW") == 0.0
    assert Preprocessor.clean_rating("-") == 0.0
    assert Preprocessor.clean_rating(None) == 0.0

def test_clean_cost():
    assert Preprocessor.clean_cost("1,200") == 1200
    assert Preprocessor.clean_cost("800") == 800
    assert Preprocessor.clean_cost("invalid") == 0
    assert Preprocessor.clean_cost(None) == 0

def test_clean_cuisines():
    assert Preprocessor.clean_cuisines("Italian, Continental, American") == ["Italian", "Continental", "American"]
    assert Preprocessor.clean_cuisines("") == []
    assert Preprocessor.clean_cuisines(None) == []

def test_map_budget_tier():
    assert Preprocessor.map_budget_tier(300) == "low"
    assert Preprocessor.map_budget_tier(500) == "low"
    assert Preprocessor.map_budget_tier(800) == "medium"
    assert Preprocessor.map_budget_tier(1500) == "medium"
    assert Preprocessor.map_budget_tier(2000) == "high"

def test_preprocess():
    raw_data = {
        "name": ["Truffles", "Truffles", "Glen's Bakehouse"],
        "location": ["Koramangala", "Koramangala", "Indiranagar"],
        "cuisines": ["Italian, American", "Italian", "Bakery, Desserts"],
        "rate": ["4.5/5", "4.2/5", "4.0/5"],
        "approx_cost(for two people)": ["800", "800", "600"],
        "votes": [1200, 500, 800]
    }
    df = pd.DataFrame(raw_data)
    preprocessor = Preprocessor()
    restaurants = preprocessor.preprocess(df)
    
    # Check duplicate handling: only 2 unique restaurants should exist
    assert len(restaurants) == 2
    
    # Truffles should have the version with higher votes (1200 votes, rating 4.5, cuisines: ["Italian", "American"])
    truffles = next(r for r in restaurants if r.name == "Truffles")
    assert truffles.rating == 4.5
    assert truffles.votes == 1200
    assert "Italian" in truffles.cuisines
    assert "American" in truffles.cuisines
