import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from src.models.user_preferences import UserPreferences
from src.models.recommendation import RecommendationResponse
from src.data.repository import RestaurantRepository
from src.services.filter_service import FilterService
from src.services.llm_service import GroqLLMService
from src.services.recommendation_service import RecommendationOrchestrator

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s - %(message)s")
logger = logging.getLogger(__name__)

# Global instances
repository = RestaurantRepository()
filter_service = FilterService(repository)
llm_service = None
orchestrator = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    global llm_service, orchestrator
    logger.info("Initializing application services...")
    
    # Initialize repository (loads and preprocesses HF dataset)
    repository.initialize()
    
    # Initialize LLM Service (requires GROQ_API_KEY)
    try:
        llm_service = GroqLLMService()
        orchestrator = RecommendationOrchestrator(filter_service, llm_service)
        logger.info("Successfully initialized all backend services.")
    except Exception as e:
        logger.error(f"Failed to initialize LLM service: {e}")
        # We don't crash, we just let requests fail gracefully later
    
    yield
    # Shutdown logic
    logger.info("Shutting down application...")

# Initialize FastAPI
app = FastAPI(
    title="Zomato Restaurant Recommendation API",
    description="AI-powered restaurant recommendation engine.",
    version="1.0.0",
    lifespan=lifespan
)

# Setup CORS to allow the frontend to connect
cors_origins_env = os.environ.get("CORS_ORIGINS", "*")
origins = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "ok", "dataset_loaded": repository._initialized}

@app.get("/api/v1/locations")
async def get_locations():
    """Returns a list of all unique canonical locations."""
    if not repository._initialized:
        repository.initialize()
    return {"locations": repository.get_all_locations()}

@app.get("/api/v1/cuisines")
async def get_cuisines():
    """Returns a list of all unique cuisines."""
    if not repository._initialized:
        repository.initialize()
    return {"cuisines": repository.get_all_cuisines()}

@app.post("/api/v1/recommend", response_model=RecommendationResponse)
async def get_recommendations(preferences: UserPreferences):
    """
    Returns AI-ranked restaurant recommendations based on deterministic filtering
    and Groq LLM explanations.
    """
    if not orchestrator:
        raise HTTPException(status_code=500, detail="Recommendation orchestrator is not initialized. Check GROQ_API_KEY.")
    
    try:
        return orchestrator.get_recommendations(preferences)
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

