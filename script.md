# Zomato AI Restaurant Recommender - Master Project Script & FAQ

This document is an exhaustive master script detailing the entire lifecycle of the Zomato AI Restaurant Recommender project. It includes the problem statement, all user prompts that guided the AI development, every technical issue faced and corrected, and the full technology stack. It is designed to act as your ultimate reference guide for any questions, presentations, or technical deep-dives.

---

## 1. Problem Statement
**The Goal:** To build a full-stack, AI-powered restaurant recommendation engine leveraging a real-world Zomato dataset (over 51,000 restaurants). 
**The Challenge:** Traditional recommendation systems rely on basic filtering. We wanted to build a hybrid system that filters restaurants based on user constraints (location, budget, cuisine, minimum rating) using deterministic logic, and then uses a Large Language Model (LLM) to synthesize these options and present them to the user with highly personalized, human-readable explanations.

---

## 2. Technology Stack Used
- **Frontend:** React + Vite + HTML + Vanilla CSS (No Tailwind/Bootstrap). Custom design system featuring glassmorphism, glowing neon borders, and dark mode aesthetics inspired by premium AI interfaces (like Antigravity/Stitch).
- **Backend:** FastAPI (Python). Chosen for its asynchronous capabilities, extreme speed, and automatic Pydantic data validation.
- **Data Processing:** Pandas & PyArrow. Used for lightning-fast deterministic filtering of the dataset in memory, reading from highly compressed `.parquet` files.
- **AI/LLM Provider:** Groq API running the `llama-3.3-70b-versatile` model. Chosen for its ultra-low latency inference, which is critical for a real-time web UI.
- **Deployment:** 
  - **Vercel:** Hosting the React frontend for global CDN edge delivery.
  - **Railway:** Hosting the FastAPI backend (configured via a custom `Procfile`).

---

## 3. The Development Journey: Exact Prompts Used
The project was iteratively developed through the following core prompts that shaped the architecture, UI, and fixes:

1. *"using context.md and Docs/architecture.md generate a prompt for google stitch for designing the frontend"*
2. *"techstack is again wrong, below is the tech stack as per implementation-plan.md use that. Tech Stack: React, Vite, HTML, Vanilla CSS."*
3. *"i want color combination nd visuals like antigravity or stitch a, make those changes in prompt"*
4. *"wht the locsl host is not running and throwing any output ?"*
5. *"Creat a deployment-plan.md for this project and i want to deploy backend on railway and frontend in vercel."*
6. *"Before deploying, I found few bugs, app is showing restaurants below the ratings i have chosen. it shows discover and help option which was never discussed and not in implementation plan. it shows memory AI sysnthesis window between input column and result column which should not be part of the display. Check all the bugs, correct them, test them and make it part of the edge-case.md... Also dont ask permission to accept and submit evertime. Ask once and make it yes for all the time."*
7. *"Thanks, missed the getting started logo in right top, not functioning and not requried. do the same actiin as above."*
8. *"Do the necessary code changes as per deployment-plan.md"*
9. *"Push the changes on github https://github.com/paswanshailendrra/Zomato-Project--Restaurant-recommender-.git"*
10. *"I can see all the md files as well the frontend file, backend files have been pushed ? I cannot view it."* (Fixing the Git root tracking issue).
11. *"Set the start command to uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000} to fix this build failure. Railpack could not auto-detect a start command..."*
12. *"have you amde the necessary changes ? railway error : I'll get the full deployment details and build logs to diagnose the error comprehensively."*
13. *"Do the rest... Perfect. I'll implement Option 3: Async background loading... Merge the PR Redeploy"*
14. *"deploment on railway is still failing.: ... Failed to initialize LLM service ... Generating train split: 19% ... (Crash loop OOM error)"*
15. *"remove the untitled page from github, it has api key details."*
16. *"why bsckend is crashing again and again :"*
17. *"Don’t ask permission and allow everything for complete project"*
18. *"Create script.md which shall contain everything we did from problem statement to prompts the corrections and the technology usefd , which shall help me any questions."*

---

## 4. Comprehensive List of Issues Faced & Corrections Made
We encountered and solved 17 distinct bugs, edge cases, and deployment hurdles:

### Backend Logic & Filtering Bugs
1. **Ambiguous Budget Filters:** The frontend dropdown only showed "Low/Medium/High", which was ambiguous. **Fix:** Added precise price ranges to the UI (e.g., Medium (₹500 - ₹1000)).
2. **Pydantic Validation 422 Error for "Premium" Budget:** The frontend sent `"very high"`, but the backend only accepted `"low", "medium", "high"`. **Fix:** Updated the Pydantic schema and data mapper to support 4 tiers.
3. **Pydantic Error Displayed as `[object Object]`:** Validation errors crashed the frontend UI parser. **Fix:** Added proper recursive string parsing in `App.jsx` for HTTP 422 validation details.
4. **Budget Filter Was Exclusive Instead of Inclusive:** Selecting "High" budget blocked all "Low" and "Medium" options. **Fix:** Rewrote `_filter_by_budget` to be hierarchical (selecting "High" includes cheaper options).
5. **Over-constrained Filters Returning Zero Results:** Highly specific filters caused the LLM to hallucinate or return empty responses. **Fix:** Implemented a fallback algorithm that dynamically broadens the budget constraint if fewer than 5 candidates are found.
6. **Rating Filter Ignored When Results are Low:** The fallback algorithm accidentally relaxed the *rating* constraint along with the budget. **Fix:** Modified the logic to strictly enforce the user's minimum rating to preserve quality, only relaxing the budget.
7. **Missing Required Fields & Boundary Validation:** Handled malformed requests by ensuring Pydantic correctly rejects invalid ratings (e.g. `< 0` or `> 5.0`) and throws readable "Field Required" errors.
8. **Non-existent Locations:** Handled edge cases where locations typed didn't exist in the DB, returning a graceful 200 OK with a friendly "No results found" summary instead of a 500 Server Error.

### Frontend UI Refinements
9. **Extraneous Navigation Elements:** Removed non-functional "Discover" and "Help" links from the header to match the minimalist design.
10. **Unused "Get Started" Button:** Removed a stray, non-functional button in the top right.
11. **Unwanted "Memory AI Synthesis" Window:** The LLM output was wrapped in an overly styled, heavy box. **Fix:** Stripped the window UI and rendered the AI summary as clean, elegant text.
12. **Frontend API Connectivity in Production:** The frontend was hardcoded to `localhost`. **Fix:** Implemented `VITE_API_BASE_URL` environment variables for dynamic switching between local dev and the Vercel production build.

### Deployment, Git, and Security Hurdles
13. **API Key Configuration Error Masking:** Missing Groq keys triggered generic 500 errors. **Fix:** Added graceful exception handling in `src/main.py` so the server stays alive, but clearly logs `GROQ_API_KEY is required`.
14. **GitHub Push Root Directory Misalignment:** The initial push tracked the parent folder (`GenAI NextLeap`), hiding backend files inside a sub-directory on GitHub. **Fix:** Re-initialized `.git` specifically inside the `Zomato-Restaurant suggestion` folder and force-pushed a clean tree to GitHub.
15. **Railway Procfile Auto-Detection Failure:** Railway couldn't find the entry point because it was nested in `src/main.py`. **Fix:** Created a custom `Procfile` (`web: uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}`) at the root to force Railway to boot the correct file.
16. **Railway OOM (Out of Memory) Death Loop:** 
    - *The Issue:* Railway's free tier has a 500MB RAM limit. When `loader.py` downloaded the 51,000+ row dataset from Hugging Face on startup, `pandas` expanded it to **571 MB** in RAM (largely due to massive `reviews_list` columns). This caused Railway to instantly kill the container with an OOM error, causing an endless restart loop every 5 seconds.
    - *The Fix:* We ran a script to aggressively prune the dataset, completely dropping heavy text columns not needed by the backend (`reviews_list`, `url`, `menu_item`). We compressed it into `zomato_dataset.parquet`. Memory usage plummeted from **571 MB** to **17 MB**, and file size from **79 MB** to **412 KB**, fixing the crash permanently.
17. **Accidental API Key Leak:** An `Untitled.pages` file containing API keys was accidentally pushed to GitHub. **Fix:** Used `git rm -f` to wipe it from the codebase and instructed the user to immediately revoke/rotate the compromised API key via the Groq console.

---

## 5. Potential Interview/Defense Questions

**Q: Why didn't you just use the LLM to search for the restaurants directly?**
*A: LLMs are prone to hallucinations (making up fake restaurants or fake ratings). By using a deterministic Pandas filter first, we guarantee the restaurants actually exist in that location with those exact prices. We only use the LLM for what it's best at: natural language generation.*

**Q: Why Parquet instead of CSV for the dataset?**
*A: Parquet is a columnar storage format. It is significantly faster to read into Pandas and offers massive compression benefits. After dropping heavy columns, our optimized Parquet file is only ~412KB and consumes just ~17MB of RAM, which was the key to successfully deploying on Railway's restrictive 500MB Free Tier.*

**Q: How did you debug the constant crashing loop on Railway?**
*A: We originally thought it was a health check timeout, so we implemented async background loading. When it still crashed, we checked the container memory logs and realized the `datasets` library was spiking to nearly 600MB of RAM during data parsing. We bypassed this by bundling a pre-processed, lightweight Parquet file directly into the GitHub repository.*
