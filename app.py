# Set USER_AGENT before any imports that might need it
import os
os.environ['USER_AGENT'] = 'AdCopyPro/1.0 (https://yourapp.com; contact@yourapp.com)'

# Standard library imports
import asyncio
import logging
import shutil
from typing import TypedDict, List, Optional, Dict, Any

# Third-party imports
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from langchain_google_genai import ChatGoogleGenerativeAI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Check for required API key
gemini_api_key = os.getenv("GOOGLE_API_KEY")
if not gemini_api_key:
    logger.error("GOOGLE_API_KEY not found in environment variables")
    raise ValueError("GOOGLE_API_KEY not found in environment variables or .env file")

# Configure Gemini
# Get the Google API key from environment variables
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    raise ValueError(
        "GOOGLE_API_KEY not found in environment variables. Please check your .env file.")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-lite",
    google_api_key=GOOGLE_API_KEY,
    temperature=0.7
)

# Import dependencies with error handling
try:
    from fastapi import FastAPI, Request, HTTPException
    from fastapi.responses import HTMLResponse, JSONResponse
    from fastapi.templating import Jinja2Templates
    from fastapi.staticfiles import StaticFiles
    from langgraph.graph import StateGraph, END
    from pydantic import BaseModel
    from langchain_community.vectorstores import Chroma
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_core.documents import Document
    from ad_copy_agent import rewrite_node, RewriteState
except ImportError as e:
    logger.error(f"Failed to import required dependencies: {str(e)}")
    raise

# Initialize FastAPI app
app = FastAPI(
    title="Ad Copy Generator",
    description="API for generating and optimizing ad copies",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configure static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Default RAG documents
rag_documents = [
    "Google Ads Best Practices: Keep headlines under 30 characters, include keywords, and have a clear CTA.",
    "Facebook Ad Guidelines: Use eye-catching images, keep text concise, and target specific audiences.",
    "Instagram Marketing Tips: Use high-quality visuals, include relevant hashtags, and post consistently.",
    "LinkedIn Ad Strategy: Focus on professional tone, highlight business value, and target by job title.",
    "Twitter Ad Tips: Keep messages short, use trending hashtags, and include visuals when possible.",
    "Ad Copywriting Tones: Professional (formal, business-like), Casual (conversational, friendly), Witty (clever, humorous), Urgent (time-sensitive, creates FOMO)."
]

# Pydantic models
class AgentRequest(BaseModel):
    """Request model for the agent endpoint"""
    input_text: str
    tone: Optional[str] = "professional"
    platform: Optional[str] = "Google Ads"

class FeedbackInput(BaseModel):
    """Model for receiving feedback on generated content"""
    original_text: str
    rewritten_text: str
    tone: str
    platform: str
    rating: Optional[int] = None
    feedback: Optional[str] = None
    suggested_improvement: Optional[str] = None

# In-memory storage for feedback
feedback_store = []

class SentenceTransformerEmbeddingFunction:
    """Wrapper for SentenceTransformer to work with LangChain's embedding interface"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents using the SentenceTransformer model"""
        embeddings = self.model.encode(texts, show_progress_bar=True)
        return [embedding.tolist() for embedding in embeddings]
    
    def embed_query(self, text: str) -> List[float]:
        """Embed a single query using the SentenceTransformer model"""
        return self.model.encode(text).tolist()

class FeedbackAnalyzer:
    """Analyzes feedback to improve model performance"""
    
    def __init__(self, vectorstore=None):
        self.feedback_data = []
        self.common_issues = {}
        self.vectorstore = vectorstore
        self.feedback_suggestions = []
    
    def add_suggestion_to_rag(self, suggestion: str):
        """Adds a feedback suggestion as a document to the RAG store."""
        if self.vectorstore:
            doc = Document(page_content=suggestion, metadata={"source": "user_feedback"})
            self.vectorstore.add_documents([doc])
            self.feedback_suggestions.append(suggestion)
            logger.info(f"Added feedback suggestion to vector store: {suggestion}")
    
      

    def summarize_suggestions(self) -> Optional[str]:
      """Summarizes feedback suggestions if there are more than 10."""
      if len(self.feedback_suggestions) > 3:
        try:
            prompt = ChatPromptTemplate.from_template(
                "Please summarize the following user feedback suggestions into a single, concise point:\n\n{feedback}"
            )
            formatted_prompt = prompt.format(feedback=', '.join(self.feedback_suggestions))
            response = model.generate_content(formatted_prompt)
            summary = response.text
            self.feedback_suggestions = [summary]
            logger.info(f"Summarized feedback suggestions: {summary}")
            return summary
        except Exception as e:
            logger.error(f"Error summarizing feedback with Gemini: {str(e)}")
            return "Error summarizing feedback."
      return None

    
    def add_feedback(self, feedback: dict):
        """Store and analyze feedback"""
        self.feedback_data.append(feedback)
        self._analyze_feedback(feedback)
    
    def _analyze_feedback(self, feedback: dict):
        """Analyze feedback to identify patterns and common issues"""
        rating = feedback.get('rating', 0)
        if rating < 3:  # Negative feedback
            issues = self._identify_issues(feedback.get('feedback', ''))
            for issue in issues:
                self.common_issues[issue] = self.common_issues.get(issue, 0) + 1
    
    def _identify_issues(self, text: str) -> List[str]:
        """Identify common issues from feedback text"""
        issues = []
        text = text.lower()
        
        if any(word in text for word in ["tone", "sounds", "voice"]):
            issues.append("tone_issue")
        if any(word in text for word in ["platform", "format", "layout"]):
            issues.append("platform_issue")
        if any(word in text for word in ["length", "short", "long"]):
            issues.append("length_issue")
        if any(word in text for word in ["cta", "call to action", "action"]):
            issues.append("cta_issue")
        
        return issues or ["other_issue"]
    
    def get_improvement_suggestions(self) -> dict:
        """Get suggestions for model improvement based on feedback"""
        avg_rating = 0
        if self.feedback_data:
            avg_rating = sum(f.get('rating', 0) for f in self.feedback_data) / len(self.feedback_data)
        
        return {
            "common_issues": self.common_issues,
            "total_feedback_count": len(self.feedback_data),
            "average_rating": avg_rating
        }

def initialize_resources():
    """Initialize vector store and other resources"""
    global rag_documents
    try:
        chroma_dir = "./chroma_db"
        
        # Remove existing directory if it exists
        if os.path.exists(chroma_dir):
            logger.info(f"Removing existing chroma directory: {chroma_dir}")
            shutil.rmtree(chroma_dir, ignore_errors=True)
        
        logger.info(f"Initializing resources with {len(rag_documents)} documents")
        
        # Initialize embedding function
        embedding_function = SentenceTransformerEmbeddingFunction()
        
        # Initialize Chroma DB
        vectorstore = Chroma(
            embedding_function=embedding_function, 
            persist_directory=chroma_dir
        )
        
        # Add initial documents to Chroma DB
        if rag_documents:
            docs = [Document(page_content=doc) for doc in rag_documents]
            vectorstore.add_documents(docs)
            logger.info(f"Added {len(docs)} initial documents to Chroma DB.")
        
        return vectorstore
    
    except Exception as e:
        logger.error(f"Error initializing resources: {str(e)}", exc_info=True)
        raise

# Global variables for resource management
vectorstore = None
feedback_analyzer = None
initialization_lock = asyncio.Lock()
initialization_complete = False

async def get_resources():
    """Get resources with lazy loading"""
    global vectorstore, initialization_complete
    
    if initialization_complete:
        return vectorstore
    
    async with initialization_lock:
        if initialization_complete:
            return vectorstore
        
        try:
            logger.info("Starting resource initialization...")
            vectorstore = initialize_resources()
            initialization_complete = True
            logger.info("Resource initialization complete")
            return vectorstore
        except Exception as e:
            logger.error(f"Failed to initialize resources: {str(e)}", exc_info=True)
            raise

# Graph state definition
class GraphState(TypedDict):
    input_text: str
    tone: str
    platform: str
    rag_context: str
    rewritten_ad: str
    evaluation_result: Optional[str]

# Graph nodes
def tone_selector_node(state: RewriteState) -> RewriteState:
    """Node to handle tone selection for the ad copy"""
    logger.debug("Executing ToneSelector")
    return {**state, "tone": state.get("tone", "professional")}

def platform_selector_node(state: RewriteState) -> RewriteState:
    """Node to handle platform selection for the ad copy"""
    logger.debug("Executing PlatformSelector")
    return {**state, "platform": state.get("platform", "Google Ads")}

def rag_retriever_node(state: RewriteState) -> RewriteState:
    """Node to retrieve relevant context using RAG"""
    logger.info("Executing RAGRetriever")
    try:
        global vectorstore
        
        # Combine tone and platform for a more specific query
        query = f"Best practices for {state.get('tone', 'professional')} tone on {state.get('platform', 'Google Ads')} ads."
        
        # Get the vector store if not available
        if vectorstore is None:
            vectorstore = asyncio.run(get_resources())
        
        # Perform similarity search
        try:
            logger.info(f"Performing similarity search for query: {query}")
            retrieved_docs = vectorstore.similarity_search(query, k=2)
            
            # Extract and format the context
            rag_context = "\n".join([doc.page_content for doc in retrieved_docs])
            
            if not rag_context:
                rag_context = "No specific best practices found. Focus on clear call to actions and concise messaging."
                logger.warning("No specific best practices found for the query")
            else:
                logger.info(f"Retrieved {len(retrieved_docs)} relevant documents")
            
            return {**state, "rag_context": rag_context}
        
        except Exception as search_error:
            logger.error(f"Error in similarity search: {str(search_error)}", exc_info=True)
            return {**state, "rag_context": "Error in similarity search. Using default best practices."}
    
    except Exception as e:
        logger.error(f"Error in RAG retriever: {str(e)}", exc_info=True)
        return {**state, "rag_context": "Error retrieving context. Using default best practices."}

def evaluator_node(state: RewriteState) -> RewriteState:
    """Node to evaluate the quality of the generated ad copy"""
    logger.info("Executing Evaluator")
    try:
        # Simple evaluation - can be enhanced with more sophisticated checks
        rewritten_ad = state.get("rewritten_ad", "")
        
        if rewritten_ad and len(rewritten_ad.strip()) > 0:
            logger.info("Ad passed quality checks")
            return {**state, "evaluation_result": "good"}
        else:
            logger.info("Ad needs refinement")
            return {**state, "evaluation_result": "needs_refinement"}
    
    except Exception as e:
        logger.error(f"Error in evaluator: {str(e)}")
        return {**state, "evaluation_result": "needs_refinement"}

# Build the LangGraph
graph = StateGraph(GraphState)

# Add nodes to the graph
graph.add_node("ToneSelector", tone_selector_node)
graph.add_node("PlatformSelector", platform_selector_node)
graph.add_node("RAGRetriever", rag_retriever_node)
graph.add_node("RewriteAgent", rewrite_node)
graph.add_node("Evaluator", evaluator_node)

# Define the graph flow
graph.set_entry_point("ToneSelector")
graph.add_edge("ToneSelector", "PlatformSelector")
graph.add_edge("PlatformSelector", "RAGRetriever")
graph.add_edge("RAGRetriever", "RewriteAgent")
graph.add_edge("RewriteAgent", "Evaluator")

# Add conditional edge for evaluation
graph.add_conditional_edges(
    "Evaluator",
    lambda state: state.get("evaluation_result", "needs_refinement"),
    {
        "good": END,
        "needs_refinement": "RewriteAgent",
    },
)

# Compile the graph
app.state.graph = graph.compile()

# API endpoints
@app.post("/run-agent/")
async def run_agent(request: AgentRequest):
    """Handle incoming requests to generate ad copy"""
    logger.info(f"Received request: input_text='{request.input_text}' tone='{request.tone}' platform='{request.platform}'")
    
    try:
        # Get resources with lazy loading
        try:
            logger.info("Acquiring resources...")
            vectorstore_resource = await get_resources()
            
            if vectorstore_resource is None:
                logger.error("Vectorstore not initialized")
                return JSONResponse(
                    status_code=503,
                    content={"error": "Service initializing, please try again in a moment"}
                )
            logger.info("Resources acquired successfully")
        
        except Exception as e:
            logger.error(f"Failed to get resources: {str(e)}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={"error": "Failed to initialize resources. Please try again later."}
            )
        
        try:
            # Initialize the state with input data
            initial_state = {
                "input_text": request.input_text,
                "tone": request.tone,
                "platform": request.platform,
                "rag_context": "",
                "rewritten_ad": ""
            }
            
            logger.info("Invoking graph with initial state...")
            
            # Compile and invoke the graph
            workflow = app.state.graph
            final_state = workflow.invoke(initial_state)
            
            if not final_state or "rewritten_ad" not in final_state:
                logger.error("Invalid final state returned from graph")
                raise ValueError("Failed to generate ad copy")
            
            logger.info("Successfully generated ad copy")
            return {"rewritten_ad": final_state["rewritten_ad"]}
        
        except Exception as e:
            logger.error(f"Error during graph execution: {str(e)}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={"error": f"Failed to generate ad copy: {str(e)}"}
            )
    
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "An unexpected error occurred while processing your request."}
        )

@app.post("/api/feedback")
async def receive_feedback(feedback: FeedbackInput):
    """Endpoint to receive and process user feedback"""
    try:
        # Store feedback
        feedback_dict = feedback.model_dump()
        feedback_store.append(feedback_dict)
        
        if feedback_analyzer:
            feedback_analyzer.add_feedback(feedback_dict)
            
            if feedback.suggested_improvement:
                feedback_analyzer.add_suggestion_to_rag(feedback.suggested_improvement)
                summarized_suggestion = feedback_analyzer.summarize_suggestions()
                if summarized_suggestion:
                    logger.info(f"Summarized feedback suggestions: {summarized_suggestion}")
        
        # Log the feedback for analysis
        rating = feedback_dict.get("rating")
        logger.info(f"New feedback received - Rating: {rating}")
        
        return {
            "status": "success",
            "suggestion": "We've noted your feedback and will use it to enhance our model."
        }
    
    except Exception as e:
        logger.error(f"Error processing feedback: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing feedback")

@app.get("/api/feedback/insights")
async def get_feedback_insights():
    """Get insights from collected feedback"""
    try:
        insights = {}
        if feedback_analyzer:
            insights = feedback_analyzer.get_improvement_suggestions()
        
        return {
            "status": "success",
            "insights": insights,
            "recent_feedback": feedback_store[-5:] if feedback_store else []
        }
    
    except Exception as e:
        logger.error(f"Error getting feedback insights: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving feedback insights")

@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/feedback", response_class=HTMLResponse)
async def feedback_page(request: Request):
    return templates.TemplateResponse("feedback_success.html", {"request": request})

@app.get("/documents", response_class=HTMLResponse)
async def documents_page(request: Request):
    return templates.TemplateResponse("rag_docs.html", {"request": request, "documents": rag_documents})

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize resources when the application starts"""
    global feedback_analyzer, vectorstore
    try:
        logger.info("Starting application initialization...")
        vectorstore = initialize_resources()
        feedback_analyzer = FeedbackAnalyzer(vectorstore)
        initialization_complete = True
        logger.info("Application initialization complete")
    except Exception as e:
        logger.error(f"Error during application startup: {str(e)}", exc_info=True)
        raise