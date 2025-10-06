from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from motor.motor_asyncio import AsyncIOMotorClient
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from typing import List, Optional, Union
from datetime import datetime, timedelta
import os
import secrets
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="AgenticAds Backend API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        username: str | None = payload.get("sub")
        if username is None or username != ADMIN_USERNAME:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")


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
async def get_generation_history(_: str = Depends(get_current_admin)):
    """Get all generation history records"""
    try:
        collection = db.generation_history
        results = await collection.find().to_list(length=None)
        return [GenerationHistory(**doc) for doc in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generation-history", response_model=GenerationHistory)
async def create_generation_history(generation: GenerationHistory, _: str = Depends(get_current_admin)):
    """Create a new generation history record"""
    try:
        collection = db.generation_history
        result = await collection.insert_one(generation.dict())
        return generation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/feedback", response_model=List[FeedbackItem])
async def get_feedback(_: str = Depends(get_current_admin)):
    """Get all feedback records"""
    try:
        collection = db.feedback
        results = await collection.find().to_list(length=None)
        return [FeedbackItem(**doc) for doc in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/feedback", response_model=FeedbackItem)
async def create_feedback(feedback: FeedbackItem, _: str = Depends(get_current_admin)):
    """Create a new feedback record"""
    try:
        collection = db.feedback
        result = await collection.insert_one(feedback.dict())
        return feedback
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(_: str = Depends(get_current_admin)):
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
async def get_chart_data(_: str = Depends(get_current_admin)):
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

@app.on_event("startup")
async def startup_event():
    """Application startup - no longer seeding sample data"""
    print("AgenticAds backend started successfully")
    print("Database connection established")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
