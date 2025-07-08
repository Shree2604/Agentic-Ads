# Set USER_AGENT before any imports that might need it
from dotenv import load_dotenv
import os
import asyncio
import logging
from typing import TypedDict, Annotated, List, Optional, Dict, Any
from sentence_transformers import SentenceTransformer
from datetime import datetime

os.environ['USER_AGENT'] = 'AdCopyPro/1.0 (https://yourapp.com; contact@yourapp.com)'

# Configure logging first
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
    raise ValueError(
        "GOOGLE_API_KEY not found in environment variables or .env file")

# Import other dependencies
try:
    from fastapi import FastAPI, Request, HTTPException, Depends, status
    from fastapi.responses import HTMLResponse, JSONResponse
    from fastapi.templating import Jinja2Templates
    from fastapi.staticfiles import StaticFiles
    from langgraph.graph import StateGraph, END
    from pydantic import BaseModel
    from langchain_core.messages import BaseMessage
    from langchain_core.prompts import PromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    from langchain_community.document_loaders import WebBaseLoader
    from langchain_community.vectorstores import FAISS, Chroma
    from langchain_community.embeddings import SentenceTransformerEmbeddings
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_core.documents import Document
    import numpy as np
    import shutil
except ImportError as e:
    logger.error(f"Failed to import required dependencies: {str(e)}")
    raise

# Import from ad_copy_agent
try:
    from ad_copy_agent import rewrite_node, RewriteState
    from feedback_summarizer import summarize_feedback
except ImportError as e:
    logger.error(f"Failed to import from ad_copy_agent: {str(e)}")
    # Create placeholder implementations if modules don't exist
    logger.warning("Creating placeholder implementations for missing modules")
    
    class RewriteState(TypedDict):
        input_text: str
        tone: str
        platform: str
        rag_context: str
        user_feedback: str
        rewritten_ad: str
        evaluation_result: Optional[str]
    
    def rewrite_node(state: RewriteState) -> RewriteState:
        """Placeholder rewrite node - replace with actual implementation"""
        logger.info("Executing RewriteAgent (placeholder)")
        # Simple placeholder implementation
        input_text = state.get("input_text", "")
        tone = state.get("tone", "professional")
        platform = state.get("platform", "Google Ads")
        
        # Create a simple rewritten ad
        rewritten_ad = f"Transform your business with our solution! Perfect for {platform} with {tone} tone. {input_text[:100]}... Act now!"
        
        return {**state, "rewritten_ad": rewritten_ad}
    
    def summarize_feedback(docs: List[Document]) -> str:
        """Placeholder feedback summarizer - replace with actual implementation"""
        if not docs:
            return ""
        
        # Simple concatenation of document content
        feedback_text = " ".join([doc.page_content for doc in docs])
        return feedback_text[:500] + "..." if len(feedback_text) > 500 else feedback_text

# Initialize FastAPI app
app = FastAPI(
    title="Ad Copy Generator",
    description="API for generating and optimizing ad copies",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configure static files (with error handling)
try:
    if os.path.exists("static"):
        app.mount("/static", StaticFiles(directory="static"), name="static")
    else:
        logger.warning("Static directory not found, skipping static files mounting")
except Exception as e:
    logger.warning(f"Could not mount static files: {str(e)}")

# Create templates instance (with error handling)
try:
    if os.path.exists("templates"):
        templates = Jinja2Templates(directory="templates")
    else:
        logger.warning("Templates directory not found")
        templates = None
except Exception as e:
    logger.warning(f"Could not initialize templates: {str(e)}")
    templates = None

# In-memory store for RAG documents
rag_documents = [
    "Google Ads Best Practices: Keep headlines under 30 characters, include keywords, and have a clear CTA.",
    "Facebook Ad Guidelines: Use eye-catching images, keep text concise, and target specific audiences.",
    "Instagram Marketing Tips: Use high-quality visuals, include relevant hashtags, and post consistently.",
    "LinkedIn Ad Strategy: Focus on professional tone, highlight business value, and target by job title.",
    "Twitter Ad Tips: Keep messages short, use trending hashtags, and include visuals when possible.",
    "Ad Copywriting Tones: Professional (formal, business-like), Casual (conversational, friendly), Witty (clever, humorous), Urgent (time-sensitive, creates FOMO)."
]

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
feedback_vectorstore = None

class FeedbackAnalyzer:
    """Analyzes feedback to improve model performance"""

    def __init__(self):
        self.feedback_data = []
        self.common_issues = {}

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
        return {
            "common_issues": self.common_issues,
            "total_feedback_count": len(self.feedback_data),
            "average_rating": sum(f.get('rating', 0) for f in self.feedback_data) / len(self.feedback_data) if self.feedback_data else 0
        }

# Initialize feedback analyzer
feedback_analyzer = FeedbackAnalyzer()

class SentenceTransformerEmbeddingFunction:
    """Wrapper for SentenceTransformer to work with LangChain's embedding interface"""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents using the SentenceTransformer model"""
        embeddings = self.model.encode(texts, show_progress_bar=False)
        return [embedding.tolist() for embedding in embeddings]

    def embed_query(self, text: str) -> List[float]:
        """Embed a single query using the SentenceTransformer model"""
        return self.model.encode(text).tolist()

def initialize_resources():
    """Initialize vector store and other resources"""
    global rag_documents, feedback_vectorstore
    try:
        chroma_dir = "./chroma_db"
        feedback_chroma_dir = "./feedback_chroma_db"

        # Try to remove existing directory if it exists
        try:
            if os.path.exists(chroma_dir):
                logger.info(f"Removing existing chroma directory: {chroma_dir}")
                shutil.rmtree(chroma_dir, ignore_errors=True)
            if os.path.exists(feedback_chroma_dir):
                logger.info(f"Removing existing feedback chroma directory: {feedback_chroma_dir}")
                shutil.rmtree(feedback_chroma_dir, ignore_errors=True)
        except Exception as e:
            logger.warning(f"Could not remove directories: {str(e)}")

        logger.info(f"Initializing resources with {len(rag_documents)} documents")

        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            length_function=len,
            add_start_index=True
        )

        # Create document objects
        docs = [Document(page_content=x) for x in rag_documents]
        splits = text_splitter.split_documents(docs)
        logger.info(f"Split documents into {len(splits)} chunks")

        # Initialize the embedding model
        model_name = "all-MiniLM-L6-v2"
        logger.info(f"Loading embeddings model: {model_name}")

        # Create embedding function
        embeddings = SentenceTransformerEmbeddingFunction(model_name)
        logger.info("Embedding function created successfully")

        # Create Chroma vector store
        logger.info("Creating Chroma vector store...")
        vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=embeddings,
            persist_directory=chroma_dir
        )

        logger.info("Creating Feedback Chroma vector store...")
        # Initialize feedback_vectorstore as empty (no documents yet)
        feedback_vectorstore = Chroma(
            embedding_function=embeddings,
            persist_directory=feedback_chroma_dir
        )

        logger.info("Chroma vector store created successfully")
        return embeddings, vectorstore

    except Exception as e:
        logger.error(f"Error initializing resources: {str(e)}", exc_info=True)
        raise

# Initialize resources (will be loaded when needed)
embeddings = None
vectorstore = None
initialization_lock = asyncio.Lock()
initialization_complete = False

async def get_resources():
    global embeddings, vectorstore, initialization_complete

    # If already initialized, return the resources
    if initialization_complete:
        return embeddings, vectorstore

    async with initialization_lock:
        # Double-check in case another coroutine initialized while we were waiting
        if initialization_complete:
            return embeddings, vectorstore

        try:
            # Initialize resources
            logger.info("Starting resource initialization...")
            model, vs = initialize_resources()
            embeddings = model
            vectorstore = vs
            initialization_complete = True
            logger.info("Resource initialization complete")
            return model, vs

        except Exception as e:
            logger.error(f"Failed to initialize resources: {str(e)}", exc_info=True)
            raise

@app.post("/run-agent/")
async def run_agent_endpoint(request: AgentRequest):
    """Handle incoming requests to generate ad copy"""
    logger.info(f"Received request: input_text='{request.input_text}' tone='{request.tone}' platform='{request.platform}'")

    try:
        # Get resources with lazy loading
        try:
            logger.info("Acquiring resources...")
            model, vs = await get_resources()

            if model is None or vs is None:
                logger.error("Model or vectorstore not initialized")
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
            initial_state = RewriteState(
                input_text=request.input_text,
                tone=request.tone,
                platform=request.platform,
                rag_context="",
                user_feedback="",
                rewritten_ad="",
                evaluation_result=None
            )

            logger.info("Invoking graph with initial state...")
            final_state = compiled_graph.invoke(initial_state)

            if not final_state or "rewritten_ad" not in final_state:
                logger.error("Invalid final state returned from graph")
                raise ValueError("Failed to generate ad copy")

            logger.info("Successfully generated ad copy")
            return {"rewritten_ad": final_state["rewritten_ad"]}

        except Exception as e:
            logger.error(f"Error during graph execution: {str(e)}", exc_info=True)
            raise
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": "An unexpected error occurred while processing your request."}
        )

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
            try:
                _, vectorstore = asyncio.run(get_resources())
            except Exception as e:
                logger.error(f"Failed to get vectorstore: {str(e)}")
                return {**state, "rag_context": "Error retrieving context. Using default best practices."}

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
        # Simple evaluation logic - can be enhanced with more sophisticated checks
        rewritten_ad = state.get("rewritten_ad", "").lower()

        # Check for common elements of a good ad
        has_call_to_action = any(phrase in rewritten_ad
                               for phrase in ["buy now", "shop now", "learn more", "sign up", "get started"])

        # Check for appropriate length
        word_count = len(rewritten_ad.split())
        appropriate_length = 10 <= word_count <= 200

        if has_call_to_action and appropriate_length:
            logger.info("Ad passed quality checks")
            return {**state, "evaluation_result": "good"}
        else:
            logger.info("Ad needs refinement")
            return {**state, "evaluation_result": "needs_refinement"}
    except Exception as e:
        logger.error(f"Error in evaluator: {str(e)}")
        # Default to good if there's an error to avoid infinite loops
        return {**state, "evaluation_result": "good"}

def feedback_retriever_node(state: RewriteState) -> RewriteState:
    """Node to retrieve relevant feedback using RAG"""
    logger.info("Executing FeedbackRetriever")
    try:
        global feedback_vectorstore

        # Combine tone and platform for a more specific query
        query = f"Feedback for {state.get('tone', 'professional')} tone on {state.get('platform', 'Google Ads')} ads."

        # Get the vector store if not available
        if feedback_vectorstore is None:
            try:
                _, _ = asyncio.run(get_resources())
            except Exception as e:
                logger.error(f"Failed to get feedback vectorstore: {str(e)}")
                return {**state, "user_feedback": "Error retrieving user feedback."}

        # Perform similarity search
        try:
            logger.info(f"Performing similarity search for query: {query}")
            retrieved_docs = feedback_vectorstore.similarity_search(query, k=5)

            # Summarize feedback if necessary
            user_feedback = summarize_feedback(retrieved_docs)

            if not user_feedback:
                user_feedback = "No specific user feedback found."
                logger.warning("No specific user feedback found for the query")
            else:
                logger.info(f"Retrieved {len(retrieved_docs)} relevant documents and processed feedback.")

            return {**state, "user_feedback": user_feedback}

        except Exception as search_error:
            logger.error(f"Error in similarity search: {str(search_error)}", exc_info=True)
            return {**state, "user_feedback": "Error in similarity search."}

    except Exception as e:
        logger.error(f"Error in feedback retriever: {str(e)}", exc_info=True)
        return {**state, "user_feedback": "Error retrieving user feedback."}

# Build the LangGraph
graph = StateGraph(RewriteState)

graph.add_node("ToneSelector", tone_selector_node)
graph.add_node("PlatformSelector", platform_selector_node)
graph.add_node("RAGRetriever", rag_retriever_node)
graph.add_node("FeedbackRetriever", feedback_retriever_node)
graph.add_node("RewriteAgent", rewrite_node)
graph.add_node("Evaluator", evaluator_node)

# Define the graph flow
graph.set_entry_point("ToneSelector")
graph.add_edge("ToneSelector", "PlatformSelector")
graph.add_edge("PlatformSelector", "RAGRetriever")
graph.add_edge("RAGRetriever", "FeedbackRetriever")
graph.add_edge("FeedbackRetriever", "RewriteAgent")
graph.add_edge("RewriteAgent", "Evaluator")

# Add a conditional edge from the Evaluator
graph.add_conditional_edges(
    "Evaluator",
    lambda state: state.get("evaluation_result", "good"),
    {
        "good": END,
        "needs_refinement": "RewriteAgent",
    },
)

# Compile the graph
compiled_graph = graph.compile()

@app.post("/api/feedback")
async def receive_feedback(feedback: FeedbackInput):
    """Endpoint to receive and process user feedback"""
    try:
        # Convert feedback to dictionary and add timestamp
        feedback_dict = feedback.model_dump()
        feedback_dict['timestamp'] = datetime.now().strftime("%B %d, %Y %H:%M")
        
        # Store the feedback
        feedback_store.append(feedback_dict)
        
        # Add to feedback analyzer
        feedback_analyzer.add_feedback(feedback_dict)
        
        logger.info(f"New feedback received for {feedback.platform} - Rating: {feedback.rating or 'N/A'}")
        
        # Return success response
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "Thank you for your feedback!",
                "redirect": "/feedback/list"
            }
        )
    except Exception as e:
        logger.error(f"Error processing feedback: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing feedback")

@app.get("/api/feedback/insights")
async def get_feedback_insights():
    """Get insights from collected feedback"""
    try:
        return {
            "status": "success",
            "insights": feedback_analyzer.get_improvement_suggestions(),
            "recent_feedback": feedback_store[-5:] if feedback_store else []
        }
    except Exception as e:
        logger.error(f"Error getting feedback insights: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving feedback insights")

@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    if templates is None:
        return HTMLResponse("<h1>Ad Copy Generator</h1><p>Templates not available</p>")
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/feedback", response_class=HTMLResponse)
async def feedback_page(request: Request):
    if templates is None:
        return HTMLResponse("<h1>Feedback</h1><p>Thank you for your feedback!</p>")
    return templates.TemplateResponse("feedback_success.html", {"request": request})

@app.get("/feedback/list", response_class=HTMLResponse)
async def feedback_list_page(request: Request):
    """Endpoint to display all submitted feedback"""
    # Process feedback store
    feedback_list = []
    for fb in feedback_store:
        if hasattr(fb, 'dict'):
            fb_dict = fb.dict()
        elif isinstance(fb, dict):
            fb_dict = fb
        else:
            continue
            
        # Ensure all required fields are present
        fb_dict['original_text'] = fb_dict.get('original_text', 'No original text provided')
        fb_dict['rewritten_text'] = fb_dict.get('rewritten_text', 'No rewritten text provided')
        fb_dict['platform'] = fb_dict.get('platform', 'Unknown Platform')
        fb_dict['tone'] = fb_dict.get('tone', 'Not specified')
        fb_dict['rating'] = fb_dict.get('rating', 0)
        fb_dict['feedback'] = fb_dict.get('feedback', '')
        
        # Add timestamp if not present
        if 'timestamp' not in fb_dict:
            fb_dict['timestamp'] = datetime.now().strftime("%B %d, %Y %H:%M")
            
        feedback_list.append(fb_dict)
    
    # Sort feedback by timestamp, newest first
    feedback_list.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    
    if templates is None:
        # Return simple HTML if templates not available
        html_content = "<h1>Feedback List</h1>"
        for fb in feedback_list:
            html_content += f"<div><h3>{fb['platform']} - {fb['tone']}</h3><p>Rating: {fb['rating']}</p><p>{fb['feedback']}</p></div>"
        return HTMLResponse(html_content)
    
    return templates.TemplateResponse(
        "feedback_list.html", 
        {"request": request, "feedback_list": feedback_list}
    )

@app.get("/documents", response_class=HTMLResponse)
async def documents_page(request: Request):
    if templates is None:
        html_content = "<h1>RAG Documents</h1><ul>"
        for doc in rag_documents:
            html_content += f"<li>{doc}</li>"
        html_content += "</ul>"
        return HTMLResponse(html_content)
    return templates.TemplateResponse("rag_docs.html", {"request": request, "documents": rag_documents})

@app.get("/health", response_class=HTMLResponse)
async def health_page(request: Request):
    if templates is None:
        return HTMLResponse("<h1>Health Check</h1><p>Service is running</p>")
    return templates.TemplateResponse("health.html", {"request": request})

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "initialized": embeddings is not None}

# Add startup event to initialize resources
@app.on_event("startup")
async def startup_event():
    """Initialize resources when the application starts"""
    try:
        logger.info("Starting application initialization...")
        # This will trigger the lazy loading of resources when the first request comes in
        logger.info("Application initialization complete")
    except Exception as e:
        logger.error(f"Error during application startup: {str(e)}", exc_info=True)
        raise

# Add shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources when the application shuts down"""
    try:
        logger.info("Application shutting down...")
        # Add any cleanup logic here
        logger.info("Application shutdown complete")
    except Exception as e:
        logger.error(f"Error during application shutdown: {str(e)}", exc_info=True)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)