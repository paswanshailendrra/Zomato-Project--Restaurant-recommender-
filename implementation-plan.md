# Goal Description

This implementation plan details the step-by-step construction of the Zomato-inspired AI-powered Restaurant Recommendation System. The system combines deterministic filtering (location, rating, budget, cuisines) of a real-world Hugging Face dataset with LLM ranking and explanation generation using Groq (`llama-3.3-70b-versatile`). It provides a polished Streamlit user interface where users can input preferences and receive personalized recommendations with explanations.

## Tech Stack

| Category | Technology | Purpose |
| :--- | :--- | :--- |
| **Language** | Python 3 | Core programming language |
| **LLM API** | Groq SDK | High-speed LLM inference |
| **LLM Model** | llama-3.3-70b-versatile | Recommendation, ranking, and explanation generation |
| **Data Source** | Hugging Face Datasets | Fetching `ManikaSaini/zomato-restaurant-recommendation` |
| **Data Processing**| Pandas | Data manipulation, cleaning, and preprocessing |
| **Validation** | Pydantic | Data validation, type safety, and schema definition |
| **Web UI** | Streamlit | Building the interactive frontend application |
| **Testing** | Pytest | Automated unit and integration testing |

## User Review Required

> [!IMPORTANT]
> **Groq API Key Requirement**: You will need a Groq API Key (from [Groq Cloud](https://console.groq.com/)) set as the `GROQ_API_KEY` environment variable.
>
> **Dataset Structure Verification**: On the first execution of Phase 1, we will inspect the `ManikaSaini/zomato-restaurant-recommendation` Hugging Face dataset's schema. If column names differ from our assumed schema (e.g. `approx_cost(for two people)`, `cuisines`, `location`), we will adjust our parsing and validation logic accordingly.

> [!TIP]
> **Streamlit UI**: We will use Streamlit as the presentation layer. Streamlit is lightweight, Python-native, and runs a clean local server.

## Open Questions

> [!NOTE]
> 1. **Budget Thresholds**: We've set initial thresholds (Low: <= 500 INR, Medium: 501-1500 INR, High: > 1500 INR). We will calibrate these during Phase 1 based on actual data distribution in the Zomato dataset.
> 2. **Default Location**: We'll determine the most popular locations in the dataset to pre-populate or offer as recommendations in the UI dropdown.

---

## Proposed Changes

The development is split into five distinct implementation phases to ensure reliability and grounding at every layer.

### Component 1: Infrastructure & Configuration

Set up python requirements, project metadata, environment variables, and the entry points.

**Action Taken:** Created project structure, setup `.env` file for Groq API key, defined `requirements.txt` for dependencies, and ensured `python-dotenv` loads configurations at runtime.

#### [NEW] [requirements.txt](file:///Users/khushbushailendrra/Documents/GenAI%20NextLeap/Zomato-Restaurant%20suggestion/requirements.txt)
Defines project dependencies: `python-dotenv`, `groq`, `datasets`, `pandas`, `pydantic`, `streamlit`, `pytest`.

#### [NEW] [.env.example](file:///Users/khushbushailendrra/Documents/GenAI%20NextLeap/Zomato-Restaurant%20suggestion/.env.example)
Template containing configuration parameters like `GROQ_API_KEY`, default model parameters, cache paths.

---

### Component 2: Phase 1 — Data Ingestion & Models

Retrieve the Hugging Face dataset, pre-process columns, map budget tiers, and construct data schemas.

**Action Taken:** Built Pydantic schemas for domains (Restaurant, Recommendation), implemented dataset loader from Hugging Face (`loader.py`), and created robust string preprocessors and repository class.

#### [NEW] [user_preferences.py](file:///Users/khushbushailendrra/Documents/GenAI%20NextLeap/Zomato-Restaurant%20suggestion/src/models/user_preferences.py)
Pydantic model representing user filters: location, budget tier, cuisine, min rating, and natural language preferences.

#### [NEW] [restaurant.py](file:///Users/khushbushailendrra/Documents/GenAI%20NextLeap/Zomato-Restaurant%20suggestion/src/models/restaurant.py)
Pydantic model representing a cleaned restaurant record.

#### [NEW] [recommendation.py](file:///Users/khushbushailendrra/Documents/GenAI%20NextLeap/Zomato-Restaurant%20suggestion/src/models/recommendation.py)
Pydantic models representing individual recommendations (with rankings and AI explanations) and the final response structure.

#### [NEW] [loader.py](file:///Users/khushbushailendrra/Documents/GenAI%20NextLeap/Zomato-Restaurant%20suggestion/src/data/loader.py)
Loads the `ManikaSaini/zomato-restaurant-recommendation` dataset, cache management, and offline fail-safes.

#### [NEW] [preprocessor.py](file:///Users/khushbushailendrra/Documents/GenAI%20NextLeap/Zomato-Restaurant%20suggestion/src/data/preprocessor.py)
Cleans strings, parses cuisine lists, deduplicates, maps cost for two to low/medium/high budget tiers.

#### [NEW] [repository.py](file:///Users/khushbushailendrra/Documents/GenAI%20NextLeap/Zomato-Restaurant%20suggestion/src/data/repository.py)
Provides clean retrieval queries (e.g. `get_by_location`, `get_all_locations`) over the processed dataset.

---

### Component 3: Phase 2 — Filtering Pipeline

Build the deterministic constraint matching system that narrows down raw listings into candidate sets.

**Action Taken:** Implemented robust location filtering in `filter_service.py` featuring alias mapping, space-insensitive substring matching, and strict fuzzy matching (cutoff 0.8) using `difflib`. Also integrated rating and budget filters.

#### [NEW] [filter_service.py](file:///Users/khushbushailendrra/Documents/GenAI%20NextLeap/Zomato-Restaurant%20suggestion/src/services/filter_service.py)
Implements precise filters on location, rating, budget tier, and cuisine. Returns up to `MAX_CANDIDATES` sorted by rating and vote count.

---

### Component 4: Phase 3 — Groq LLM & Recommendation Engine

Integrate the LLM, format context lists, construct prompts, and execute ranking.

**Action Taken:** Integrated the Groq LLM client (`llm_service.py`), designed JSON validation prompts to enforce structured output, and successfully ran predictions generating AI-ranked explanations for candidates.

#### [NEW] [system_prompt.txt](file:///Users/khushbushailendrra/Documents/GenAI%20NextLeap/Zomato-Restaurant%20suggestion/src/prompts/system_prompt.txt)
Instructions mapping rules to the LLM to output valid JSON matching the schema, and never hallucinate restaurants.

#### [NEW] [user_prompt_template.txt](file:///Users/khushbushailendrra/Documents/GenAI%20NextLeap/Zomato-Restaurant%20suggestion/src/prompts/user_prompt_template.txt)
Formats candidate JSON and user preferences for context delivery to the Groq API.

#### [NEW] [llm_service.py](file:///Users/khushbushailendrra/Documents/GenAI%20NextLeap/Zomato-Restaurant%20suggestion/src/services/llm_service.py)
Manages Groq SDK calls, timeout handling, retries, and fallback model usage (e.g. `llama-3.1-8b-instant`).

---

### Component 5: Phase 4 — Backend Orchestration & Hardening

Create core orchestrators, build a robust API layer for the frontend, and implement error recovery policies.

**Tech Stack & APIs:**
| Category | Technology / API | Purpose |
| :--- | :--- | :--- |
| **Framework** | FastAPI | High-performance API framework to serve frontend requests |
| **Server** | Uvicorn | ASGI web server for running FastAPI |
| **External API** | Groq API | LLM inference (`llama-3.3-70b-versatile`) for ranking & explanations |
| **Internal API**| `POST /api/v1/recommend` | Receives user preferences and returns ranked recommendations |
| **Validation**| Pydantic | Request/Response schema validation |
| **Testing** | Pytest | Automated backend unit testing |

**Action Taken:** Set up the main entry points (`main.py` using FastAPI), built extensive unit tests achieving 100% pass rate for data filtering, and designed test fixtures for typos, parent-city wildcards, and fuzzy matching.

#### [NEW] [recommendation_service.py](file:///Users/khushbushailendrra/Documents/GenAI%20NextLeap/Zomato-Restaurant%20suggestion/src/services/recommendation_service.py)
Orchestrates the workflow: inputs preferences -> invokes filtering -> runs LLM ranking -> post-validates that results belong to candidate list -> handles fallbacks.

#### [NEW] [main.py](file:///Users/khushbushailendrra/Documents/GenAI%20NextLeap/Zomato-Restaurant%20suggestion/src/main.py)
Main entry point orchestrator.

#### [NEW] [test_preprocessor.py](file:///Users/khushbushailendrra/Documents/GenAI%20NextLeap/Zomato-Restaurant%20suggestion/tests/test_preprocessor.py)
Unit tests for data normalization and tier mapping.

#### [NEW] [test_filter_service.py](file:///Users/khushbushailendrra/Documents/GenAI%20NextLeap/Zomato-Restaurant%20suggestion/tests/test_filter_service.py)
Unit tests for deterministic filtering logic.

#### [NEW] [test_llm_service.py](file:///Users/khushbushailendrra/Documents/GenAI%20NextLeap/Zomato-Restaurant%20suggestion/tests/test_llm_service.py)
Mocked tests for Groq LLM integration and error recovery fallback.

---

### Component 6: Phase 5 — High-Quality Frontend UI

Create a premium, visually stunning, and highly interactive frontend display using React and Vite. The goal is to provide a top-tier user experience with rich aesthetics, dynamic animations, and responsive modern design.
**Tech Stack:** React, Vite, HTML, Vanilla CSS.

**Action Taken:** Designed a modern web application with Vite. Engineered the layout to feature sleek styling, smooth transitions, intuitive inputs, robust error notifications, and highly attractive dynamic card layouts for the AI recommendations.

#### [NEW] [frontend/](file:///Users/khushbushailendrra/Documents/GenAI%20NextLeap/Zomato-Restaurant%20suggestion/frontend/)
React + Vite project directory containing the interactive user interface prioritizing best practices in modern web design, dynamic components, and a premium aesthetic.

---

### Component 7: Phase 6 — Edge Cases & Hardening

**Action Taken**: 
- Documented key bug fixes in `edge-case.md`.
- Solved API key surfacing errors by parsing exact FastAPI `detail` attributes in the frontend.
- Handled over-constrained queries by introducing a fallback relaxation mechanism in `FilterService`, guaranteeing that the LLM always receives at least 5 candidates to rank whenever possible.
- Clarified budget dropdown ambiguity with explicit rupee amounts.
- Fixed a `422 Unprocessable Entity` validation error triggered by the "Premium" budget tier. Updated the `UserPreferences` and `Restaurant` models, alongside the `preprocessor.py` mapping logic, to officially support the `"very high"` category (4-tier budget system).
- Added a dynamic **Cuisine Dropdown** filter to the frontend, fetching available cuisines from the `/api/v1/cuisines` backend endpoint.
- Fixed `[object Object]` error display bug — Pydantic returns `detail` as an array of objects, not a string. Frontend now properly stringifies each validation error.
- Changed budget filter from exclusive (exact match) to inclusive (hierarchical). Selecting "High" now also includes "Low" and "Medium" tier restaurants.

**Files Modified:**
- `src/models/user_preferences.py` — Added `"very high"` to budget Literal
- `src/models/restaurant.py` — Added `"very high"` to budget_tier Literal
- `src/data/preprocessor.py` — 4-tier budget mapping (Low ≤₹500, Medium ≤₹1000, High ≤₹2000, Very High >₹2000)
- `src/services/filter_service.py` — Fallback relaxation + inclusive budget hierarchy
- `frontend/src/App.jsx` — Proper Pydantic error parsing
- `frontend/src/components/SearchForm.jsx` — Cuisine dropdown + rupee budget labels

**Test Results (13/13 Passed):**
See `edge-case.md` for the complete test matrix covering validation errors, empty results, boundary values, and end-to-end browser tests.

---

## Verification Plan

### Automated Tests
Run unit tests with pytest to ensure data and filtering logic is correct:
```bash
pytest tests/
```

### Manual Verification
1. Run dataset exploration script to verify Hugging Face connectivity and columns.
2. Launch React frontend locally:
   ```bash
   cd frontend
   npm run dev
   ```
3. Test edge case scenarios in UI:
   - Filter criteria matching 0 restaurants (verifying fallback message).
   - Validating that results match only dataset restaurants (no LLM hallucination).
   - Disconnecting network or providing invalid Groq API keys to test standard fallback paths (ranking without explanation).
