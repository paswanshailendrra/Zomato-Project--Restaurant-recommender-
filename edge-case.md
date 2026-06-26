# Bugs & Edge Cases Addressed

This document logs bugs and edge cases encountered during the integration phase and how they were resolved.

---

### 1. API Key Configuration Errors
**Issue**: The frontend was displaying a generic "Failed to fetch recommendations" error if the Groq API key was missing, malformed, or if the orchestrator failed to initialize, making it hard to debug.
**Resolution**: Updated `App.jsx` to parse and display the exact `detail` error message sent by FastAPI (e.g., "Recommendation orchestrator is not initialized. Check GROQ_API_KEY."). This ensures the user instantly knows if it's an API key configuration issue rather than a generic network failure.

### 2. Ambiguous Budget Filters
**Issue**: The budget dropdown previously only listed textual tiers ("Low", "Medium", "High", "Premium"), leading to ambiguity on the actual cost brackets.
**Resolution**: Modified `SearchForm.jsx` to explicitly include estimated price ranges for clarity:
- Low (₹0 - ₹500)
- Medium (₹500 - ₹1000)
- High (₹1000 - ₹2000)
- Premium (₹2000+)

### 3. Over-constrained Filters Returning Too Few Results
**Issue**: When applying strict hard filters (e.g., highly specific location + lowest budget + very high minimum rating), the `FilterService` would sometimes return 1 or 0 candidates, leading to the LLM generating a single recommendation instead of the intended "Top 5".
**Resolution**: Implemented a fallback relaxation mechanism in `filter_service.py`. If the hard filters yield fewer than 5 candidates, the backend automatically drops the budget and rating constraints (keeping only location and cuisine) to guarantee the LLM receives enough candidates to formulate a complete Top 5 ranking.

### 4. Pydantic Validation 422 Error for "very high" Budget
**Issue**: The frontend was sending `budget: "very high"` when users selected the "Premium" option, but the backend `UserPreferences` and data preprocessor only recognized "low", "medium", and "high", resulting in a `422 Unprocessable Entity` validation error.
**Resolution**: Updated `UserPreferences` schema, `Restaurant` model, and the dataset preprocessor's `map_budget_tier` to support 4 tiers: `"low"`, `"medium"`, `"high"`, and `"very high"`. Cleared the dataset cache to re-apply the newly updated tiers.

### 5. Pydantic Error Displayed as `[object Object]` in Frontend
**Issue**: When the backend returned a Pydantic validation error (422), the `detail` field was an array of objects (not a string). The frontend passed this directly to `new Error()`, resulting in `[object Object]` being shown to the user instead of a readable message.
**Resolution**: Updated `App.jsx` to check the type of `errData.detail`:
- If it's a string, use it directly
- If it's an array, map each item to its `.msg` property and join with semicolons
- Otherwise, `JSON.stringify` it as a fallback

### 6. Budget Filter Was Exclusive Instead of Inclusive
**Issue**: The budget filter was doing an exact-match (`budget_tier == "high"`), which meant selecting "High" would exclude all restaurants categorized as "low" or "medium". Users selecting a higher budget would logically expect to also see cheaper options.
**Resolution**: Updated `_filter_by_budget` in `filter_service.py` to use a hierarchy-based inclusive filter. Selecting "high" now includes restaurants in "low", "medium", AND "high" tiers. This dramatically increases the candidate pool and avoids unnecessary fallback relaxation.

### 7. Non-existent Location Returns Empty Results Gracefully
**Issue**: If a user typed a location that doesn't exist in the dataset (e.g., "XYZNotAPlace123"), the system could potentially crash or return an unhelpful error.
**Tested Result**: The system correctly returns `{"summary": "We couldn't find any restaurants matching your exact filters.", "recommendations": []}` with a 200 status. No crash, no 500.

### 8. Rating Boundary Validation
**Issue**: Users could potentially send rating values outside the valid 0.0-5.0 range.
**Tested Result**: Pydantic correctly rejects `min_rating > 5.0` and `min_rating < 0.0` with clear validation messages like "Input should be less than or equal to 5".

### 9. Missing Required Fields
**Issue**: Users could potentially submit incomplete forms or the frontend could send malformed requests.
**Tested Result**: Pydantic correctly validates that both `location` and `budget` are required, returning descriptive "Field required" errors for each missing field.

---

## Test Results Summary

| # | Test Case | Expected | Result |
|---|-----------|----------|--------|
| 1 | `budget: "very high"` (Brookefield) | 200 OK, 5 results | ✅ PASSED |
| 2 | `budget: "low"` (Brookefield) | 200 OK, 5 results | ✅ PASSED |
| 3 | Cuisine filter (`Chinese`, Brookefield) | 200 OK, 5 results | ✅ PASSED |
| 4 | Invalid budget (`"super_expensive"`) | 422 with clear message | ✅ PASSED |
| 5 | Missing `location` field | 422 with "Field required" | ✅ PASSED |
| 6 | Non-existent location | 200 OK, 0 results, friendly message | ✅ PASSED |
| 7 | Locations endpoint | 200 OK, 93 locations | ✅ PASSED |
| 8 | Cuisines endpoint | 200 OK, 107 cuisines | ✅ PASSED |
| 9 | `min_rating > 5.0` | 422 with validation error | ✅ PASSED |
| 10 | `min_rating < 0` | 422 with validation error | ✅ PASSED |
| 11 | Empty request body `{}` | 422, both fields required | ✅ PASSED |
| 12 | Popular location (Koramangala, high) | 200 OK, 5 results | ✅ PASSED |
| 13 | Frontend E2E (browser test) | All dropdowns populated, 5 results | ✅ PASSED |

### 10. Rating Filter Ignored When Results are Low
**Issue**: When the system found fewer than 5 candidates, it would automatically relax *both* the budget and the minimum rating constraints, leading to the app showing restaurants below the chosen rating.
**Resolution**: Modified `filter_service.py` to preserve the rating constraint while only relaxing the budget constraint when falling back.

### 11. Extraneous Frontend Navigation Elements
**Issue**: The frontend header included "Discover" and "Help" navigation links which were not functional and were not part of the implementation plan.
**Resolution**: Removed these extraneous links from `App.jsx` to keep the UI clean and focused.

### 12. Unwanted "Memory AI Synthesis" Window Component
**Issue**: The frontend was displaying the LLM summary within a large "AI Synthesis Complete" window/panel, which was overly stylized and cluttered the display between inputs and results.
**Resolution**: Removed the "AI Synthesis Complete" `<h1>` element and its heavy styling from `ResultsGrid.jsx`, rendering the summary as a simple, clean text paragraph.

### 13. Unused "Get Started" Button in Header
**Issue**: The frontend header included a "Get Started" button in the top right that was not functional and not required by the design spec.
**Resolution**: Removed the button from `App.jsx` to streamline the user interface.
