# Agentic AI Architecture & Design Principles

This project implements an advanced **Agentic RAG (Retrieval-Augmented Generation)** system with **LangGraph orchestration** and **Feedback-Driven Improvement Loops**.

## Agentic AI Structure & Flow

```
User Query → Feedback Insights → Multi-Agent System → Knowledge Retrieval → Content Generation → Quality Assurance → Output → Feedback Collection → Pattern Recognition → Adaptation Loop
```

## Agentic AI Workflow Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Input    │───▶│  Feedback        │───▶│   Content       │
│   (Platform,    │    │  Insights        │    │   Researcher    │
│    Tone, Text)  │    │  Aggregation     │    │   Agent         │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Copywriter    │◀───│   Knowledge      │───▶│   Visual        │
│   Agent         │    │   Base (RAG)     │    │   Designer      │
│   (Text Gen)    │    │   Retrieval      │    │   Agent         │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Video Script  │───▶│   Quality        │───▶│   Final         │
│   Writer Agent  │    │   Assurance      │    │   Output        │
│   (Script Gen)  │    │   Agent          │    │   (Multi-modal) │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Multi-Agent Specialization

- **Content Researcher Agent**: Retrieves relevant templates, examples, and guidelines from the knowledge base using semantic search
- **Copywriter Agent**: Generates platform-optimized ad copy with tone consistency and brand alignment
- **Visual Designer Agent**: Creates detailed prompts for AI image generation with design specifications
- **Video Scriptwriter Agent**: Develops structured video scripts with scene descriptions and narration
- **Quality Assurance Agent**: Validates outputs against quality criteria and provides refinement suggestions

## Feedback-Driven Pattern Recognition & Improvement Loop

The system implements a sophisticated **Pattern Recognition and Improvement Loop** that continuously learns and adapts:

### 1. Feedback Collection & Storage

```python
# Feedback stored in MongoDB with rich metadata
{
    "email": "user@example.com",
    "platform": "Instagram",
    "tone": "professional",
    "rating": 5,
    "message": "Perfect tone and length!",
    "action": "generated",
    "date": "2024-01-15"
}
```

### 2. Pattern Recognition Engine (`feedback_insights.py`)

```python
async def get_feedback_insights(db, platform: str, tone: str) -> Dict[str, Any]:
    """Aggregates feedback patterns for intelligent adaptation"""
    feedback_docs = await db.feedback.find({
        "platform": platform,
        "tone": tone
    }).sort("_id", -1).limit(15).to_list(None)

    # Analyze patterns
    avg_rating = calculate_average_rating(feedback_docs)
    positive_highlights = extract_positive_feedback(feedback_docs)
    improvement_suggestions = extract_criticism(feedback_docs)
    common_keywords = extract_keywords(feedback_docs)

    return {
        "avg_rating": avg_rating,
        "positive_highlights": positive_highlights,
        "improvement_suggestions": improvement_suggestions,
        "common_keywords": common_keywords,
        "summary": generate_insight_summary(...)
    }
```

### 3. Adaptive Generation Process

**Feedback Integration in Agent Context:**
```python
@dataclass
class AgentContext:
    platform: str
    tone: str
    brand_guidelines: Optional[str]
    input_text: str
    vector_store: Any
    embedding_model: Any
    # NEW: Feedback-driven adaptation fields
    feedback_summary: Optional[str] = None
    feedback_highlights: Optional[List[str]] = None
    feedback_suggestions: Optional[List[str]] = None
    feedback_keywords: Optional[List[str]] = None
    feedback_avg_rating: Optional[float] = None
```

**Agent Adaptation Examples:**

- **Copywriter Agent**: Incorporates user-loved phrases and avoids criticized elements
- **Visual Designer Agent**: Uses feedback keywords in design prompts and addresses visual complaints
- **Video Scriptwriter Agent**: Adapts pacing and style based on engagement feedback

### 4. Continuous Learning Cycle

```
Generation → User Feedback → Pattern Analysis → Agent Adaptation → Improved Generation
     ↑                                                                      ↓
     └─────────────────── Continuous Improvement Loop ─────────────────────┘
```

## Key Technical Features

1. **Vector Database Integration**: ChromaDB with FAISS for semantic search and context retrieval
2. **Knowledge Base Management**: Document chunking and embedding storage with feedback integration
3. **Multi-Agent Coordination**: LangGraph for complex workflow orchestration with feedback loops
4. **Feedback-Driven Adaptation**: Real-time learning from user ratings and comments
5. **Pattern Recognition**: Automated analysis of feedback trends and keyword extraction
6. **Real-time Analytics**: Live dashboard with business intelligence and feedback insights
7. **Full-Stack Separation**: Clear separation between React frontend and FastAPI backend
8. **API-First Design**: All data flows through RESTful API endpoints with MongoDB persistence
9. **Component Modularity**: Atomic, reusable components with clear responsibilities
10. **Custom Hooks Pattern**: Business logic extracted into focused, testable hooks
11. **Type Safety**: Comprehensive TypeScript implementation with strict interfaces
12. **CSS Architecture**: Component-scoped styling for maintainability and isolation

## SOLID Principles Implementation

- **Single Responsibility Principle (SRP)**: Each component, hook, and service has a single, well-defined purpose
- **Open/Closed Principle (OCP)**: Components are open for extension (new platforms, features) but closed for modification
- **Liskov Substitution Principle (LSP)**: Components can be replaced with their subtypes without affecting functionality
- **Interface Segregation Principle (ISP)**: TypeScript interfaces are specific to client needs, avoiding bloated interfaces
- **Dependency Inversion Principle (DIP)**: High-level modules depend on abstractions (hooks, services) rather than concrete implementations

## Data Flow Architecture

```
User Action → React Component → Custom Hook → API Call → FastAPI → MongoDB → Response → Hook → Component → UI Update
```

- **Frontend Hooks**: `useApiData`, `useAdGeneration`, `useFeedbackHandler` handle API communication
- **Backend Services**: FastAPI endpoints provide CRUD operations for all data
- **Database Layer**: MongoDB stores all generation history, feedback, and analytics data
- **Authentication Middleware**: `get_current_admin()` guards protected endpoints by verifying JWT tokens issued by `/api/auth/login`
- **Real-time Updates**: All dashboard data reflects actual usage from MongoDB
