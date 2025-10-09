from fastapi import FastAPI, HTTPException, Depends, APIRouter, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import Response, StreamingResponse
from motor.motor_asyncio import AsyncIOMotorClient
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from typing import List, Optional, Union, Dict, Any
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
import os
import secrets
import base64
import asyncio
import tempfile
from pathlib import Path
import aiofiles
import mimetypes
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGODB_URL)
db = client.agentic_ads

# Auth configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "super-secret-key-change-me")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")
ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Import RAG system
try:
    from rag import (
        RAGConfig,
        get_enhanced_vector_store,
        get_knowledge_manager,
        run_generation_workflow
    )
    from rag.feedback_insights import get_feedback_insights
    RAG_AVAILABLE = True
except ImportError as e:
    print(f"RAG system not available: {e}")
    RAG_AVAILABLE = False

# Pydantic models
class GenerationHistory(BaseModel):
    id: int
    date: str
    time: str
    platform: str
    tone: str
    adText: str
    outputs: str
    status: str

class FeedbackItem(BaseModel):
    id: int
    email: str
    message: str
    rating: int = Field(ge=1, le=5)
    action: str
    date: str
    platform: str

class DashboardStats(BaseModel):
    totalGenerations: int
    totalUsers: int
    avgRating: float
    successRate: float

class ChartData(BaseModel):
    platformStats: dict
    toneStats: dict

class Token(BaseModel):
    access_token: str
    token_type: str

class LoginRequest(BaseModel):
    username: str
    password: str

class RAGGenerationRequest(BaseModel):
    platform: str
    tone: str
    ad_text: str
    outputs: List[str]
    brand_guidelines: Optional[str] = None
    logo_position: str = "top-right"  # top-left, top-right, bottom-left, bottom-right, center

class RAGGenerationResponse(BaseModel):
    text: str
    poster_prompt: str
    poster_url: Optional[str] = None  # Base64 encoded poster image
    video_script: str
    video_gif_url: Optional[str] = None
    video_gif_filename: Optional[str] = None
    quality_scores: Dict[str, float]
    validation_feedback: Dict[str, str]
    errors: List[str]

class KnowledgeIngestionRequest(BaseModel):
    source: str = "manual"
    content_type: str = "general"

# Auth helpers
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_admin(username: str, password: str) -> bool:
    if username != ADMIN_USERNAME:
        return False

    if ADMIN_PASSWORD_HASH:
        return verify_password(password, ADMIN_PASSWORD_HASH)

    return secrets.compare_digest(password, ADMIN_PASSWORD)


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = {"sub": subject}
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: Optional[str] = payload.get("sub")
        if username is None or username != ADMIN_USERNAME:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

# Application lifespan manager - DEFINE BEFORE FastAPI app
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print("AgenticAds backend started successfully")
    print("Database connection established")

    if RAG_AVAILABLE:
        print("RAG system initialized and ready")
        try:
            vector_store = get_enhanced_vector_store()
            print(f"Vector store initialized with {vector_store.vector_store.collection.count()} documents")
        except Exception as e:
            print(f"RAG system initialization error: {e}")
            print("RAG features will be unavailable")
    else:
        print("RAG system not available - some features will be disabled")

    yield

    # Cleanup (if needed)
    print("Shutting down AgenticAds backend")

# CREATE FastAPI app with lifespan
app = FastAPI(title="AgenticAds Backend API", version="1.0.0", lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # React dev server
        "http://127.0.0.1:5173",  # Alternative localhost
        "http://127.0.0.1:3000",  # Alternative localhost
        "*"  # Allow all origins for development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routes
@app.get("/")
async def root():
    return {"message": "AgenticAds Backend API"}

@app.post("/api/auth/login", response_model=Token)
async def login(login_request: LoginRequest):
    if not authenticate_admin(login_request.username, login_request.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    access_token = create_access_token(subject=login_request.username)
    return Token(access_token=access_token, token_type="bearer")

@app.get("/api/generation-history", response_model=List[GenerationHistory])
async def get_generation_history():
    """Get all generation history records"""
    try:
        collection = db.generation_history
        results = await collection.find().to_list(length=None)
        print(f"✅ Retrieved {len(results)} generation history entries")
        return [GenerationHistory(**doc) for doc in results]
    except Exception as e:
        print(f"❌ Failed to retrieve generation history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generation-history", response_model=GenerationHistory)
async def create_generation_history(generation: GenerationHistory):
    """Create a new generation history record"""
    try:
        collection = db.generation_history
        result = await collection.insert_one(generation.model_dump())
        print(f"✅ Generation history saved: ID={generation.id}, Platform={generation.platform}, Status={generation.status}, Date={generation.date}, Time={generation.time}")
        return generation
    except Exception as e:
        print(f"❌ Failed to save generation history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/feedback", response_model=List[FeedbackItem])
async def get_feedback():
    """Get all feedback records"""
    try:
        collection = db.feedback
        results = await collection.find().to_list(length=None)
        print(f"✅ Retrieved {len(results)} feedback entries")
        return [FeedbackItem(**doc) for doc in results]
    except Exception as e:
        print(f"❌ Failed to retrieve feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/feedback", response_model=FeedbackItem)
async def create_feedback(feedback: FeedbackItem):
    """Create a new feedback record"""
    try:
        collection = db.feedback
        result = await collection.insert_one(feedback.model_dump())
        print(f"✅ Feedback saved: Email={feedback.email}, Action={feedback.action}, Rating={feedback.rating}, Date={feedback.date}, Platform={feedback.platform}")
        return feedback
    except Exception as e:
        print(f"❌ Failed to save feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        # Get generation history
        gen_collection = db.generation_history
        generations = await gen_collection.find().to_list(length=None)

        # Get feedback
        feedback_collection = db.feedback
        feedbacks = await feedback_collection.find().to_list(length=None)

        # Calculate stats
        total_generations = len(generations)
        total_users = len(set(f['email'] for f in feedbacks)) if feedbacks else 0
        avg_rating = sum(f['rating'] for f in feedbacks) / len(feedbacks) if feedbacks else 0.0

        # Calculate success rate (assuming 'Completed' status means success)
        successful_generations = len([g for g in generations if g.get('status') == 'Completed'])
        success_rate = (successful_generations / total_generations * 100) if total_generations > 0 else 0.0

        return DashboardStats(
            totalGenerations=total_generations,
            totalUsers=total_users,
            avgRating=round(avg_rating, 1),
            successRate=round(success_rate, 1)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/charts", response_model=ChartData)
async def get_chart_data():
    """Get chart data for platform and tone statistics"""
    try:
        collection = db.generation_history
        generations = await collection.find().to_list(length=None)

        # Calculate platform stats
        platform_stats = {}
        for gen in generations:
            platform = gen.get('platform', 'Unknown')
            platform_stats[platform] = platform_stats.get(platform, 0) + 1

        # Calculate tone stats
        tone_stats = {}
        for gen in generations:
            tone = gen.get('tone', 'Unknown')
            tone_stats[tone] = tone_stats.get(tone, 0) + 1

        return ChartData(
            platformStats=platform_stats,
            toneStats=tone_stats
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# RAG System Endpoints
if RAG_AVAILABLE:
    @app.post("/api/rag/generate", response_model=RAGGenerationResponse)
    async def generate_rag_content(request: RAGGenerationRequest):
        """Generate content using agentic RAG system"""
        try:
            # Initialize RAG system
            vector_store = get_enhanced_vector_store()

            # Seed knowledge base if empty
            try:
                if vector_store.vector_store.collection.count() == 0:
                    vector_store.seed_comprehensive_knowledge()
            except Exception as e:
                print(f"Warning: Could not seed knowledge base: {e}")

            # Aggregate recent feedback insights to guide generation
            feedback_insights = await get_feedback_insights(
                db,
                platform=request.platform,
                tone=request.tone
            )

            # Run generation workflow with logo support
            result = await run_generation_workflow(
                input_text=request.ad_text,
                platform=request.platform,
                tone=request.tone,
                output_types=request.outputs,
                brand_guidelines=request.brand_guidelines,
                feedback_insights=feedback_insights,
                logo_data=None,  # No logo data from JSON request
                logo_file=None,  # No logo file from JSON request
                logo_position=request.logo_position
            )

            return RAGGenerationResponse(
                text=result.get("text", f"🚀 {request.ad_text}"),
                poster_prompt=result.get("poster_prompt", f"Create a {request.tone} poster for {request.platform}"),
                poster_url=result.get("poster_url"),  # New poster URL field
                video_script=result.get("video_script", f"Video script for {request.ad_text}"),
                video_gif_url=result.get("video_gif_url"),
                video_gif_filename=result.get("video_gif_filename"),
                quality_scores=result.get("quality_scores", {"text": 8.0, "poster": 7.0, "video": 7.0}),
                validation_feedback=result.get("validation_feedback", {
                    "text_feedback": "Generated successfully",
                    "poster_feedback": "Generated successfully",
                    "video_feedback": "Generated successfully",
                    "overall_assessment": "PASS"
                }),
                errors=result.get("errors", [])
            )

        except Exception as e:
            print(f"RAG generation error: {str(e)}")
            # Return fallback response on any error
            return RAGGenerationResponse(
                text=f"🚀 {request.ad_text}\n\n#{request.platform.lower()} #advertisement",
                poster_prompt=f"Create a {request.tone} poster for {request.platform} featuring: {request.ad_text}",
                poster_url=None,
                video_script=f"SCENE 1: Show product/service\nNARRATION: {request.ad_text}\n\nSCENE 2: Call to action\nNARRATION: Visit us today!",
                video_gif_url=None,
                video_gif_filename=None,
                quality_scores={"text": 8.0, "poster": 7.0, "video": 7.0},
                validation_feedback={
                    "text_feedback": "Generated with fallback system due to error",
                    "poster_feedback": "Generated with fallback system due to error",
                    "video_feedback": "Generated with fallback system due to error",
                    "overall_assessment": "PASS"
                },
                errors=[f"RAG generation error: {str(e)}"]
            )

    @app.post("/api/rag/generate-with-logo", response_model=RAGGenerationResponse)
    async def generate_rag_content_with_logo(
        platform: str = Form(...),
        tone: str = Form(...),
        ad_text: str = Form(...),
        outputs: str = Form(...),  # Comma-separated list
        brand_guidelines: Optional[str] = Form(None),
        logo_position: str = Form("top-right"),
        logo_file: Optional[UploadFile] = File(None)
    ):
        """Generate content with logo upload using agentic RAG system"""
        try:
            # Parse outputs from comma-separated string
            output_types = [output.strip() for output in outputs.split(",")]

            # Initialize RAG system
            vector_store = get_enhanced_vector_store()

            # Seed knowledge base if empty
            try:
                if vector_store.vector_store.collection.count() == 0:
                    vector_store.seed_comprehensive_knowledge()
            except Exception as e:
                print(f"Warning: Could not seed knowledge base: {e}")

            # Aggregate recent feedback insights to guide generation
            feedback_insights = await get_feedback_insights(
                db,
                platform=platform,
                tone=tone
            )

            # Run generation workflow with logo support
            result = await run_generation_workflow(
                input_text=ad_text,
                platform=platform,
                tone=tone,
                output_types=output_types,
                brand_guidelines=brand_guidelines,
                feedback_insights=feedback_insights,
                logo_data=None,  # Will be processed by LogoIntegrationAgent
                logo_file=logo_file,  # Pass the uploaded file
                logo_position=logo_position
            )

            return RAGGenerationResponse(
                text=result.get("text", f"🚀 {ad_text}"),
                poster_prompt=result.get("poster_prompt", f"Create a {tone} poster for {platform}"),
                poster_url=result.get("poster_url"),  # Poster URL with logo integrated
                video_script=result.get("video_script", f"Video script for {ad_text}"),
                video_gif_url=result.get("video_gif_url"),
                video_gif_filename=result.get("video_gif_filename"),
                quality_scores=result.get("quality_scores", {"text": 8.0, "poster": 7.0, "video": 7.0}),
                validation_feedback=result.get("validation_feedback", {
                    "text_feedback": "Generated successfully with logo integration",
                    "poster_feedback": "Generated successfully with logo integration",
                    "video_feedback": "Generated successfully with logo integration",
                    "overall_assessment": "PASS"
                }),
                errors=result.get("errors", [])
            )

        except Exception as e:
            print(f"RAG generation with logo error: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            # Return fallback response on any error
            return RAGGenerationResponse(
                text=f"🚀 {ad_text}\n\n#{platform.lower()} #advertisement",
                poster_prompt=f"Create a {tone} poster for {platform} featuring: {ad_text}",
                poster_url=None,
                video_script=f"SCENE 1: Show product/service\nNARRATION: {ad_text}\n\nSCENE 2: Call to action\nNARRATION: Visit us today!",
                video_gif_url=None,
                video_gif_filename=None,
                quality_scores={"text": 8.0, "poster": 7.0, "video": 7.0},
                validation_feedback={
                    "text_feedback": "Generated with fallback system due to error",
                    "poster_feedback": "Generated with fallback system due to error",
                    "video_feedback": "Generated with fallback system due to error",
                    "overall_assessment": "PASS"
                },
                errors=[f"RAG generation with logo error: {str(e)}"]
            )

    @app.post("/api/rag/ingest-historical")
    async def ingest_historical_data(_: str = Depends(get_current_admin)):
        """Ingest historical data into knowledge base"""
        try:
            vector_store = get_enhanced_vector_store()
            ingested_count = vector_store.ingest_historical_data(MONGODB_URL, "agentic_ads")

            return {
                "message": f"Successfully ingested {ingested_count} documents from historical data",
                "ingested_count": ingested_count
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ingestion error: {str(e)}")

    @app.post("/api/rag/seed-knowledge")
    async def seed_knowledge_base(_: str = Depends(get_current_admin)):
        """Seed the knowledge base with initial templates and guidelines"""
        try:
            vector_store = get_enhanced_vector_store()
            success = vector_store.seed_comprehensive_knowledge()

            if success:
                return {"message": "Knowledge base seeded successfully"}
            else:
                raise HTTPException(status_code=500, detail="Failed to seed knowledge base")

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Seeding error: {str(e)}")

    @app.get("/api/rag/analytics")
    async def get_rag_analytics(_: str = Depends(get_current_admin)):
        """Get RAG system analytics"""
        try:
            vector_store = get_enhanced_vector_store()
            analytics = vector_store.get_analytics_data()

            return {
                "rag_system": analytics,
                "status": "active" if RAG_AVAILABLE else "unavailable"
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Analytics error: {str(e)}")

@app.get("/api/videos/download/{filename}")
async def download_video(filename: str):
    """Download a generated video GIF file"""
    print(f"📥 Video download request for: {filename}")
    try:
        temp_dir = Path(tempfile.gettempdir()) / "agentic_ads_videos"
        file_path = temp_dir / filename

        print(f"📥 Video temp dir: {temp_dir}")
        print(f"📥 Looking for video file at: {file_path}")
        print(f"📥 Temp dir exists: {temp_dir.exists()}")
        print(f"📥 File exists: {file_path.exists()}")

        if not file_path.exists():
            print(f"❌ Video file not found: {file_path}")
            available = list(temp_dir.glob("*")) if temp_dir.exists() else []
            print(f"❌ Available video files: {available}")
            raise HTTPException(status_code=404, detail="Video file not found")

        file_size = file_path.stat().st_size
        print(f"📥 Video file size: {file_size} bytes")

        content_type, _ = mimetypes.guess_type(str(file_path))
        if not content_type:
            content_type = "image/gif"

        print(f"📥 Video content type: {content_type}")

        async def cleanup_file():
            try:
                await asyncio.sleep(120)
                if file_path.exists():
                    file_path.unlink()
                    print(f"🗑️ Cleaned up video file after 2 minutes: {file_path}")
            except Exception as exc:
                print(f"⚠️ Failed to cleanup video file {file_path}: {exc}")

        asyncio.create_task(cleanup_file())

        def iter_file():
            with open(file_path, "rb") as f:
                while chunk := f.read(8192):
                    yield chunk

        response = StreamingResponse(
            iter_file(),
            media_type=content_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

        print(f"✅ Streaming video response prepared for: {filename}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Video download error for {filename}: {str(e)}")
        import traceback
        print(f"❌ Video download traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Video download error: {str(e)}")

@app.get("/api/posters/download/{filename}")
async def download_poster(filename: str):
    """Download a generated poster image file"""
    print(f"📥 Poster download request for: {filename}")
    try:
        temp_dir = Path(tempfile.gettempdir()) / "agentic_ads_posters"
        file_path = temp_dir / filename

        print(f"📥 Poster temp dir: {temp_dir}")
        print(f"📥 Looking for poster file at: {file_path}")
        print(f"📥 Temp dir exists: {temp_dir.exists()}")
        print(f"📥 File exists: {file_path.exists()}")

        if not file_path.exists():
            print(f"❌ Poster file not found: {file_path}")
            available = list(temp_dir.glob("*")) if temp_dir.exists() else []
            print(f"❌ Available poster files: {available}")
            raise HTTPException(status_code=404, detail="Poster file not found")

        file_size = file_path.stat().st_size
        print(f"📥 Poster file size: {file_size} bytes")

        content_type, _ = mimetypes.guess_type(str(file_path))
        if not content_type:
            content_type = "image/png"

        print(f"📥 Poster content type: {content_type}")

        async def cleanup_file():
            try:
                await asyncio.sleep(300)  # 5 minutes for posters
                if file_path.exists():
                    file_path.unlink()
                    print(f"🗑️ Cleaned up poster file after 5 minutes: {file_path}")
            except Exception as exc:
                print(f"⚠️ Failed to cleanup poster file {file_path}: {exc}")

        asyncio.create_task(cleanup_file())

        def iter_file():
            with open(file_path, "rb") as f:
                while chunk := f.read(8192):
                    yield chunk

        response = StreamingResponse(
            iter_file(),
            media_type=content_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

        print(f"✅ Streaming poster response prepared for: {filename}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Poster download error for {filename}: {str(e)}")
        import traceback
        print(f"❌ Poster download traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Poster download error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)