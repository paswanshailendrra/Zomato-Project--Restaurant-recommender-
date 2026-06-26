# Deployment Plan

This document outlines the step-by-step strategy for deploying the AI-Powered Restaurant Recommendation System. We will use a decoupled deployment approach:
- **Backend (FastAPI)** will be deployed on **Railway**.
- **Frontend (React + Vite)** will be deployed on **Vercel**.

---

## 1. Prerequisites

Before starting the deployment process, ensure you have:
1. Pushed the complete code to a **GitHub repository**.
2. Created a [Railway](https://railway.app/) account.
3. Created a [Vercel](https://vercel.com/) account.
4. Have your `GROQ_API_KEY` ready.

---

## 2. Backend Deployment (Railway)

Railway is an excellent platform for hosting Python applications. It will automatically detect your `requirements.txt` and install dependencies.

### Step-by-Step Guide

1. **Create a New Project:**
   - Log in to your Railway dashboard.
   - Click **"New Project"** -> **"Deploy from GitHub repo"**.
   - Select your project repository.

2. **Configure Environment Variables:**
   - Once the service is created, go to the **"Variables"** tab for your backend service.
   - Add the following variable:
     - `GROQ_API_KEY`: *(Paste your Groq API key here)*

3. **Set the Start Command:**
   - Go to the **"Settings"** tab.
   - Scroll down to the **"Deploy"** section.
   - Under **"Custom Start Command"**, enter:
     ```bash
     python -m uvicorn src.main:app --host 0.0.0.0 --port $PORT
     ```
   - *Note: Railway automatically provides the `$PORT` variable.*

4. **Generate a Public URL:**
   - Still in the **"Settings"** tab, scroll to **"Networking"**.
   - Click **"Generate Domain"** to get a public URL (e.g., `https://your-app-production.up.railway.app`).
   - **Important:** Save this URL. You will need it for the frontend deployment.

5. **Wait for Deployment:**
   - Railway will now build and deploy your app. The first deployment might take a minute or two as it downloads the Hugging Face dataset upon startup.
   - Verify it's working by navigating to `https://<YOUR_RAILWAY_URL>/health`.

---

## 3. Frontend Deployment (Vercel)

Vercel is optimized for frontend frameworks like React and Vite, offering seamless global CDN delivery.

### Step-by-Step Guide

1. **Import the Project:**
   - Log in to your Vercel dashboard.
   - Click **"Add New..."** -> **"Project"**.
   - Import your GitHub repository.

2. **Configure the Project Settings:**
   Since your frontend is located in a subfolder (`frontend/`), you must tell Vercel where to look:
   - **Framework Preset:** Vercel should automatically detect **Vite**.
   - **Root Directory:** Click "Edit" and type `frontend`. This tells Vercel that the `package.json` and code live in this folder.
   - **Build Command:** `npm run build` (Should be auto-detected)
   - **Output Directory:** `dist` (Should be auto-detected)

3. **Configure Environment Variables:**
   - Expand the **"Environment Variables"** section.
   - Add the variable that tells your frontend where the backend is hosted:
     - **Name:** `VITE_API_BASE_URL`
     - **Value:** `https://<YOUR_RAILWAY_URL>` *(Replace with the domain generated in Railway, ensuring no trailing slash)*

4. **Deploy:**
   - Click the **"Deploy"** button.
   - Vercel will install dependencies, build the React app, and assign it a public domain (e.g., `https://zomato-ai-frontend.vercel.app`).

---

## 4. Post-Deployment Checks

Once both services are deployed, we need to ensure they can talk to each other.

### Updating Backend CORS (Critical Step)
By default, web browsers block frontend apps from making API calls to different domains (CORS policy). 

1. Once Vercel gives you your frontend URL, you need to update the CORS settings in your backend.
2. In `src/main.py`, locate the CORS configuration:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://your-vercel-frontend-url.vercel.app", "http://localhost:5173"], 
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```
   *(Currently, our `allow_origins=["*"]` permits all traffic, which works out-of-the-box, but restricting it to your Vercel domain is best practice for production).*

### Testing the Application
1. Open your Vercel frontend URL.
2. The initial load might take a second as it fetches locations/cuisines.
3. Fill out the preferences and click "Find Restaurants".
4. If you receive results, your full-stack deployment is successful!

---

## Troubleshooting

- **Dataset Load Timeout on Railway:** The Hugging Face dataset is downloaded on the first boot. If the Railway instance times out or crashes due to RAM limits on the free tier, you may need to upgrade the instance tier or cache the dataset locally before pushing.
- **"Failed to Fetch" Error in UI:** This almost always means the `VITE_API_BASE_URL` in Vercel is incorrect, or the Railway backend went to sleep/is crashing. Check your Railway logs.
