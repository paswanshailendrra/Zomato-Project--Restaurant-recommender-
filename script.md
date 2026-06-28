# Zomato AI Restaurant Recommender - Project Script & FAQ

This document serves as a comprehensive master script detailing the entire lifecycle of the Zomato AI Restaurant Recommender project. It is designed to help you answer any questions during a presentation, interview, or project defense.

---

## 1. Problem Statement
**The Goal:** To build an intelligent, full-stack restaurant recommendation engine that leverages the Zomato dataset. 
**The Challenge:** Traditional recommendation systems rely on basic filtering. We wanted to build a system that not only filters restaurants based on user constraints (location, budget, cuisine, minimum rating) but also uses a Large Language Model (LLM) to synthesize these options and present them to the user with highly personalized, human-readable explanations.

---

## 2. Technology Stack
- **Frontend:** React + Vite + Vanilla CSS (Custom design system featuring glassmorphism, glowing neon borders, and dark mode aesthetics inspired by premium AI interfaces).
- **Backend:** FastAPI (Python). Chosen for its asynchronous capabilities, speed, and automatic Pydantic data validation.
- **Data Processing:** Pandas and PyArrow. Used for lightning-fast deterministic filtering of the dataset in memory.
- **AI/LLM Provider:** Groq API running the `llama-3.3-70b-versatile` model. Chosen for its ultra-low latency inference, which is critical for a real-time web UI.
- **Deployment:** 
  - **Vercel:** Hosting the React frontend for global CDN delivery.
  - **Railway:** Hosting the FastAPI backend (configured via a custom `Procfile`).

---

## 3. Architecture & Prompts

### The Two-Stage Pipeline
To prevent AI hallucinations and keep costs low, we implemented a hybrid architecture:
1. **Deterministic Filtering (Stage 1):** The backend receives the user's preferences and uses Pandas to strictly filter the Zomato dataset. It finds the top 5 restaurants that exactly match the criteria (falling back gracefully if constraints are too strict).
2. **Generative AI (Stage 2):** The filtered subset is injected into a prompt and sent to the LLM. The LLM's only job is to rank, format, and creatively explain *why* these specific restaurants are good choices.

### The Prompts
**System Prompt:**
> "You are an elite AI culinary curator. You receive a list of restaurants that have already been filtered. Your job is to present them in a sophisticated, engaging way, explaining why they are a great fit based on the user's preferences. Do not invent new restaurants."

**User Prompt Template:**
> "User is looking for a {budget} dining experience in {location}. They prefer {cuisine} food with a minimum rating of {min_rating}. Here are the top candidates we found: {restaurant_data}. Please synthesize a recommendation."

---

## 4. Key Challenges, Bugs & Corrections

During development and deployment, we encountered and solved several complex engineering problems:

### A. The "Railway OOM (Out of Memory) Death Loop"
- **The Problem:** During deployment to Railway's Free Tier (which has a 500MB RAM limit), the backend would constantly crash and restart every 5 seconds.
- **The Diagnosis:** We originally used the Hugging Face `datasets` library to download the 51,000+ row dataset on startup. Processing massive text columns (like `reviews_list`) spiked the memory usage to **571 MB**, triggering Railway's OOM killer.
- **The Fix:** We wrote a script to aggressively prune the dataset, dropping all unused heavy columns (`reviews_list`, `url`, `menu_item`). We compressed the remaining data into a GZIP `.parquet` file. 
- **The Result:** Memory usage dropped to **17 MB** and the file size shrank to **412 KB**. The app now boots instantly on Railway.

### B. Over-Constrained Filter Relaxation
- **The Problem:** If a user asked for a "Low Budget" restaurant with a "5.0 Rating", the system found 0 results, breaking the UI.
- **The Fix:** We implemented a dynamic relaxation algorithm in `filter_service.py`. If fewer than 5 restaurants are found, the system automatically broadens the budget constraint to include more options, ensuring the LLM always has data to work with. (We strictly enforced the rating constraint to ensure quality didn't drop).

### C. Frontend API Connectivity in Production
- **The Problem:** The frontend was hardcoded to `http://localhost:8000`, which broke when deployed to Vercel.
- **The Fix:** We implemented environment variable injection using Vite (`import.meta.env.VITE_API_BASE_URL`). This dynamically points the frontend to localhost during development, and to the Railway URL in production. We also secured the backend CORS configuration to accept requests specifically from the Vercel domain.

### D. UI/UX Refinements
- **The Problem:** The UI felt cluttered with unnecessary navigation links ("Discover", "Help") and a large, bulky "Memory AI Synthesis" window.
- **The Fix:** We stripped out the non-functional elements and simplified the AI response container into clean, readable text to match the premium, minimalistic "Antigravity" aesthetic you requested.

---

## 5. Potential Interview/Defense Questions

**Q: Why didn't you just use the LLM to search for the restaurants?**
*A: LLMs are prone to hallucinations (making up fake restaurants or fake ratings). By using a deterministic Pandas filter first, we guarantee the restaurants actually exist in that location with those exact prices. We only use the LLM for what it's best at: natural language generation.*

**Q: Why Parquet instead of CSV for the dataset?**
*A: Parquet is a columnar storage format. It is significantly faster to read into Pandas and offers massive compression benefits. Our optimized Parquet file is only ~400KB, whereas a CSV would be much larger and slower to parse on boot.*

**Q: How did you handle the backend deployment failing to find a start command?**
*A: Railway relies on Nixpacks to auto-detect environments. Because our entry point was nested inside `src/main.py`, the auto-detection failed. We fixed this by creating an industry-standard `Procfile` containing `web: uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}`, overriding the buildpacks.*

**Q: How do you handle missing API keys?**
*A: If the Groq API key is missing, the backend catches the error during the FastAPI lifespan initialization. Instead of crashing the whole server, it stays alive so that the `/health` checks pass, but returns a clean `500` error to the frontend indicating the exact issue, which the React UI displays gracefully.*
