# AgenticAds - AI-Powered Ad Generation Platform

Transform your ideas into platform-perfect ads with AI-powered multimodal generation. Create stunning text, images, and videos optimized for every platform—all in seconds, completely free.

## 🚀 Features

- **Multi-Platform Support**: Generate ads for Instagram, LinkedIn, Twitter, and YouTube
- **Agentic RAG System**: Advanced Retrieval-Augmented Generation with LangGraph orchestration
- **Multi-Agent Architecture**: Specialized agents for research, copywriting, visual design, and quality assurance
- **Knowledge Base Integration**: Vector database with ChromaDB for enhanced content generation
- **Advanced Admin Dashboard**: Monitor usage, feedback, and analytics with multi-page navigation
- **Real-time Analytics**: Live data visualization with interactive charts and business intelligence
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Secure Admin Access**: JWT-protected admin APIs with session storage
- **Feedback-Driven Improvement Loop**: Continuous learning and adaptation based on user feedback

## 🛠️ Tech Stack

- **Frontend**: React 18 with TypeScript, Vite, Lucide React icons
- **Backend**: FastAPI with Python 3.10+, MongoDB with Motor (async driver)
- **AI/ML Stack**: LangGraph, LangChain, Hugging Face Transformers, ChromaDB
- **Vector Database**: ChromaDB with FAISS for similarity search
- **Authentication**: JWT-based admin login with bcrypt password hashing
- **Styling**: CSS3 with CSS Variables and Glass Morphism effects
- **State Management**: React Hooks (Custom hooks following SOLID principles)
- **Data Persistence**: RESTful API with MongoDB backend
- **Charts & Visualizations**: Custom SVG-based charts for analytics

## 📁 Project Structure

```
backend/
├── main.py                    # FastAPI application with RAG endpoints
├── requirements.txt          # Python dependencies (Python 3.10+ required)
├── .env                      # Environment configuration
├── rag/                      # RAG implementation with LangGraph
│   ├── __init__.py          # RAG system initialization
│   ├── agents.py            # Multi-agent system (Research, Copywriter, Designer, QA)
│   ├── graph.py             # LangGraph workflow orchestration
│   ├── knowledge_base.py    # Knowledge base management
│   ├── enhanced_vector_store.py # ChromaDB vector operations
│   ├── chunking.py          # Text chunking for RAG
│   ├── config.py            # RAG configuration
│   ├── text_generation.py   # Text generation with RAG
│   └── feedback_insights.py # Feedback aggregation and insights
├── data/                     # Data seeding and templates
└── knowledge_base/           # Vector database storage

src/
├── components/               # Reusable UI components
│   ├── ui/                  # Basic UI components (Button, Modal, Input, etc.)
│   ├── Navigation/          # Navigation component
│   ├── AdminLogin/          # Admin login modal
│   └── FeedbackModal/       # User feedback modal
├── pages/                   # Page components
│   ├── WelcomePage/         # Landing page
│   ├── AppPage/             # Main ad generation interface
│   ├── AdminPage/           # Admin dashboard hub
│   ├── ActivityPage/        # Detailed activity view page
│   └── InsightsPage/        # Customer insights page
├── hooks/                   # Custom React hooks
│   ├── useAppState.ts       # Main application state
│   ├── useApiData.ts        # Data fetching and persistence layer
│   ├── useAdGeneration.ts   # Ad generation logic
│   ├── useAdminAuth.ts      # Admin authentication
│   └── useFeedbackHandler.ts # Feedback handling
├── types/                   # TypeScript type definitions
├── styles/                  # Global styles
└── App.tsx                  # Main application component
```

## 🏗️ Agentic AI Architecture & Design Principles

This project implements an advanced **Agentic RAG (Retrieval-Augmented Generation)** system with **LangGraph orchestration** and **Feedback-Driven Improvement Loops**:

### Agentic AI Structure & Flow

```
User Query → Feedback Insights → Multi-Agent System → Knowledge Retrieval → Content Generation → Quality Assurance → Output → Feedback Collection → Pattern Recognition → Adaptation Loop
```

#### Agentic AI Workflow Architecture

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

#### Multi-Agent Specialization

- **Content Researcher Agent**: Retrieves relevant templates, examples, and guidelines from the knowledge base using semantic search
- **Copywriter Agent**: Generates platform-optimized ad copy with tone consistency and brand alignment
- **Visual Designer Agent**: Creates detailed prompts for AI image generation with design specifications
- **Video Scriptwriter Agent**: Develops structured video scripts with scene descriptions and narration
- **Quality Assurance Agent**: Validates outputs against quality criteria and provides refinement suggestions

### Feedback-Driven Pattern Recognition & Improvement Loop

The system implements a sophisticated **Pattern Recognition and Improvement Loop** that continuously learns and adapts:

#### 1. Feedback Collection & Storage
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

#### 2. Pattern Recognition Engine (`feedback_insights.py`)
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

#### 3. Adaptive Generation Process

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

#### 4. Continuous Learning Cycle

```
Generation → User Feedback → Pattern Analysis → Agent Adaptation → Improved Generation
     ↑                                                                      ↓
     └─────────────────── Continuous Improvement Loop ─────────────────────┘
```

### Key Technical Features

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

### SOLID Principles Implementation

- **Single Responsibility Principle (SRP)**: Each component, hook, and service has a single, well-defined purpose
- **Open/Closed Principle (OCP)**: Components are open for extension (new platforms, features) but closed for modification
- **Liskov Substitution Principle (LSP)**: Components can be replaced with their subtypes without affecting functionality
- **Interface Segregation Principle (ISP)**: TypeScript interfaces are specific to client needs, avoiding bloated interfaces
- **Dependency Inversion Principle (DIP)**: High-level modules depend on abstractions (hooks, services) rather than concrete implementations

### Data Flow Architecture

```
User Action → React Component → Custom Hook → API Call → FastAPI → MongoDB → Response → Hook → Component → UI Update
```

- **Frontend Hooks**: `useApiData`, `useAdGeneration`, `useFeedbackHandler` handle API communication
- **Backend Services**: FastAPI endpoints provide CRUD operations for all data
- **Database Layer**: MongoDB stores all generation history, feedback, and analytics data
- **Authentication Middleware**: `get_current_admin()` guards protected endpoints by verifying JWT tokens issued by `/api/auth/login`
- **Real-time Updates**: All dashboard data reflects actual usage from MongoDB

## ⚙️ Setup & Development

Full backend and frontend setup instructions live in [`SETUP.md`](./SETUP.md). **Note: Backend requires Python 3.10 or higher.**

### Quick Start Commands

```bash
# Frontend
npm install
npm run dev

# Backend (Python 3.10+ required)
cd backend
pip install -r requirements.txt
python main.py
```

### Prerequisites
- **Backend**: Python 3.10 or higher (required for AI/ML dependencies)
- **Frontend**: Node.js 16+, npm or yarn
- **Database**: MongoDB (local or Atlas cluster)

Refer to `SETUP.md` for complete end-to-end environment instructions including environment variables and troubleshooting.

## 🎯 Usage

### For Users

1. **Welcome Page**: Learn about features and get started
2. **Ad Generation**:
   - Enter your ad text
   - Select tone and platform
   - Choose output types (text, poster, video)
   - Generate your perfect ad
3. **Download/Copy**: Get your generated content

### For Admins

1. **Login**: Use credentials `admin/admin` (click "Admin" in top-right corner)
2. **Dashboard Hub**: Overview of key metrics and business intelligence
3. **Recent Activity**: Click "Recent Activity" tab to view detailed generation history
4. **Customer Insights**: Click "Customer Insights" tab for comprehensive feedback analysis
5. **RAG Analytics**: Monitor knowledge base performance and generation quality
6. **Business Intelligence**: Track ROI, conversion rates, and platform performance

### Recent Features & Updates

#### Agentic RAG Implementation
- **Multi-Agent System**: 5 specialized agents working in coordinated workflows
- **LangGraph Orchestration**: Advanced workflow management for complex generation tasks
- **Knowledge Base Integration**: Vector database with semantic search capabilities
- **Quality Assurance**: Automated validation and refinement of generated content

#### Advanced Analytics Dashboard
- **Business Intelligence**: Revenue tracking, conversion analytics, and ROI metrics
- **Interactive Visualizations**: SVG charts with hover effects and animations
- **Real-time Data**: Live updates from MongoDB with performance indicators
- **Platform Analytics**: Detailed insights into platform performance and user engagement

#### Enhanced Admin Interface
- **Multi-Page Navigation**: Dedicated pages for activity logs and customer insights
- **Glass Morphism Design**: Premium UI with backdrop blur effects
- **Responsive Layout**: Optimized for all screen sizes and devices
- **Advanced Filtering**: Sort and filter data across multiple dimensions

#### Feedback-Driven Pattern Recognition & Improvement Loop

**Pattern Recognition Engine:**
- Aggregates user feedback from MongoDB database
- Identifies positive highlights, improvement suggestions, and keyword patterns
- Calculates average ratings and sentiment trends per platform/tone combination

**Adaptive Generation Process:**
- Injects feedback insights into agent contexts before generation
- Guides copywriting, visual design, and video scripting based on user preferences
- Continuously improves output quality through iterative learning

**Learning & Adaptation:**
- Each generation incorporates lessons from previous user feedback
- Agents adapt their prompts and styles based on aggregated insights
- Quality assurance validates against learned preferences and patterns

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- React team for the amazing framework
- Lucide for beautiful icons
- Vite for the fast build tool
- The open-source community for inspiration

## 📞 Support

If you have any questions or need help, please contact shree.xai.dev@gmail.com

---

**Built with ❤️ by Shreeraj Mummidivarapu**
